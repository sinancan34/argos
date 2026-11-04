import json
import re
from pathlib import Path
from typing import Any

import pytest
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

# Raw @playwright/mcp@0.0.84 results recorded on a local page; the parsers are tested against them.
RECORDED = json.loads((Path(__file__).parent / "fixtures" / "playwright_mcp_0.0.84.json").read_text(encoding="utf-8"))

SELECTORS_IN_MATCHER = re.compile(r"return (\[.*?\])\.map\(s => roots\(document\)")
FIRST_VISIBLE = " >> visible=true >> nth=0"
# Accessible names of the snapshot's buttons and their refs, in document order.
SNAPSHOT_NAMES = {"Buy": "e2", "Share": "e3"}


def request_entry(url: str, method: str = "GET", body: str | None = None, status: str = "[204] No Content") -> dict:
    return {"url": url, "method": method, "body": body, "status": status}


def tab(url: str = "about:blank", title: str = "") -> dict[str, str]:
    return {"url": url, "title": title}


def _result(text: str) -> str:
    return f"### Result\n{text}"


class FakePlaywrightServer:
    """In-memory MCP server answering with the Playwright MCP text results the runner reads."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.tabs: list[dict[str, str]] = [tab()]
        self.current = 0
        # CSS selectors that name no visible element; every other one does.
        self.missing: set[str] = set()
        # Requests of each tab by its index, numbered from 1 in order.
        self.network: dict[int, list[dict[str, Any]]] = {}
        # How many requests of each tab came before its last navigation; listed only with `all`.
        self.navigated_at: dict[int, int] = {}
        # Requests that tabs send once a navigation to the URL or a click on the selector happens.
        self.sent_on: dict[str, dict[int, list[dict[str, Any]]]] = {}
        self.page_resources: dict[int, list[str]] = {}
        self.script_result: str | None = None
        self.errors: dict[str, str] = {}
        self.mcp = self._build()

    def _record(self, name: str, args: dict[str, Any]) -> None:
        self.calls.append((name, args))
        if name in self.errors:
            raise ToolError(f"### Error\n{self.errors[name]}")

    def _send(self, trigger: str) -> None:
        for index, entries in self.sent_on.get(trigger, {}).items():
            self.network = {**self.network, index: [*self.network.get(index, []), *entries]}

    def _tab_list(self) -> str:
        return "\n".join(
            f"- {index}: {'(current) ' if index == self.current else ''}[{entry['title']}]({entry['url']})"
            for index, entry in enumerate(self.tabs)
        )

    def _page(self) -> str:
        return f"### Page\n- Page URL: {self.tabs[self.current]['url']}\n### Snapshot\n- [Snapshot](.playwright-mcp/page.yml)"

    def _close(self, index: int) -> None:
        def renumbered(entries: dict[int, Any]) -> dict[int, Any]:
            return {key - (key > index): value for key, value in entries.items() if key != index}

        self.tabs = [entry for number, entry in enumerate(self.tabs) if number != index]
        self.network = renumbered(self.network)
        self.navigated_at = renumbered(self.navigated_at)
        self.page_resources = renumbered(self.page_resources)
        self.current = min(self.current - (self.current > index), len(self.tabs) - 1)

    def _tabs(self, action: str, index: int | None, url: str | None) -> str:
        if action in ("select", "close") and index is not None and not 0 <= index < len(self.tabs):
            raise ToolError(f"### Error\nTab {index} not found")
        if action == "select":
            self.current = index
        elif action == "new":
            self.tabs = [*self.tabs, tab(url or "about:blank")]
            self.current = len(self.tabs) - 1
        elif action == "close":
            self._close(self.current if index is None else index)
        return _result(self._tab_list())

    def _evaluate(self, function: str) -> str:
        matcher = SELECTORS_IN_MATCHER.search(function)
        if matcher:
            return _result(json.dumps([selector not in self.missing for selector in json.loads(matcher.group(1))]))
        if self.script_result is not None:
            return self.script_result
        if "performance" in function:
            return _result(json.dumps(self.page_resources.get(self.current, [])))
        return _result("true")

    def _requests(self, static: bool, every: bool) -> str:
        # Like Playwright MCP, a successful request is listed only with `static`, and one sent before the
        # tab's last navigation only with `all`.
        start = 0 if every else self.navigated_at.get(self.current, 0)
        listed = [
            f"{number}. [{entry['method']}] {entry['url']} => {entry['status']}"
            for number, entry in enumerate(self.network.get(self.current, []), start=1)
            if number > start and (static or not entry["status"].startswith("[2"))
        ]
        return _result("\n".join(listed))

    def _request_body(self, index: int) -> str:
        entries = self.network.get(self.current, [])
        if not 1 <= index <= len(entries):
            raise ToolError(f"### Error\nRequest #{index} not found. Use browser_network_requests to see available indexes.")
        body = entries[index - 1]["body"]
        return _result(body) if body else ""

    def _build(self) -> FastMCP:
        mcp = FastMCP("fake-playwright-mcp")

        @mcp.tool
        def browser_tabs(action: str, index: int | None = None, url: str | None = None) -> str:
            self._record("browser_tabs", {"action": action, **({"index": index} if index is not None else {})})
            # `browser_tabs select 2` fails alone under this key.
            if f"browser_tabs select {index}" in self.errors:
                raise ToolError(f"### Error\n{self.errors[f'browser_tabs select {index}']}")
            return self._tabs(action, index, url)

        @mcp.tool
        def browser_navigate(url: str) -> str:
            self._record("browser_navigate", {"url": url})
            self.tabs = [{**entry, "url": url} if number == self.current else entry for number, entry in enumerate(self.tabs)]
            self.navigated_at = {**self.navigated_at, self.current: len(self.network.get(self.current, []))}
            self._send(url)
            return self._page()

        @mcp.tool
        def browser_snapshot() -> str:
            self._record("browser_snapshot", {})
            buttons = "\n".join(f'  - button "{name}" [ref={ref}]' for name, ref in SNAPSHOT_NAMES.items())
            return f"### Snapshot\n```yaml\n- generic [active] [ref=e1]:\n  - text: •\n{buttons}\n```"

        @mcp.tool
        def browser_evaluate(function: str, target: str | None = None) -> str:
            self._record("browser_evaluate", {"function": function, **({"target": target} if target else {})})
            return self._evaluate(function)

        @mcp.tool
        def browser_click(target: str, element: str | None = None) -> str:
            self._record("browser_click", {"target": target, **({"element": element} if element else {})})
            self._send(target.removesuffix(FIRST_VISIBLE))
            return self._page()

        @mcp.tool
        def browser_drag(startTarget: str, endTarget: str) -> str:
            self._record("browser_drag", {"startTarget": startTarget, "endTarget": endTarget})
            return self._page()

        @mcp.tool
        def browser_fill_form(fields: list[dict[str, Any]]) -> str:
            self._record("browser_fill_form", {"fields": fields})
            return self._page()

        @mcp.tool
        def browser_wait_for(text: str | None = None, time: float | None = None) -> str:
            self._record("browser_wait_for", {key: value for key, value in (("text", text), ("time", time)) if value})
            return _result(f"Waited for {text}")

        @mcp.tool
        def browser_mouse_wheel(deltaX: float, deltaY: float) -> str:
            self._record("browser_mouse_wheel", {"deltaX": deltaX, "deltaY": deltaY})
            return ""

        @mcp.tool
        def browser_close() -> str:
            self._record("browser_close", {})
            self.tabs, self.current, self.network, self.page_resources, self.navigated_at = [tab()], 0, {}, {}, {}
            return _result("No open tabs.")

        @mcp.tool
        def browser_network_requests(static: bool, all: bool = False) -> str:
            self._record("browser_network_requests", {"static": static, "all": all})
            return self._requests(static, all)

        @mcp.tool
        def browser_network_request(index: int, part: str | None = None) -> str:
            self._record("browser_network_request", {"index": index, **({"part": part} if part else {})})
            return self._request_body(index)

        return mcp

    @property
    def called_tools(self) -> list[str]:
        return [name for name, _ in self.calls]


@pytest.fixture(autouse=True)
def no_waits(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("argos_runner.criteria.step_criteria.CRITERIA_WAIT_SECONDS", 0)
    monkeypatch.setattr("argos_runner.step_runner.ACTION_DELAY_RANGE_SECONDS", (0.0, 0.0))


@pytest.fixture
def server() -> FakePlaywrightServer:
    return FakePlaywrightServer()
