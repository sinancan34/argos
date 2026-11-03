import json
import re
from pathlib import Path
from typing import Any

import pytest
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

SELECTOR_IN_SCRIPT = re.compile(r"querySelector\((.*?)\);")


def request_entry(request_id: int, url: str, method: str = "GET") -> dict[str, Any]:
    return {"requestId": request_id, "method": method, "url": url, "status": "200"}


def page(page_id: int, url: str = "about:blank", title: str = "") -> dict[str, Any]:
    return {"id": page_id, "url": url, "title": title, "selected": page_id == 1}


def _script_result(value: Any) -> dict[str, Any]:
    return {"message": f"Script ran on page and returned:\n```json\n{json.dumps(value)}\n```"}


class FakeDevtoolsServer:
    """In-memory MCP server exposing the chrome-devtools-mcp tool shapes the runner talks to."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.pages: list[dict[str, Any]] = [page(1)]
        self.missing: set[str] = set()
        self.vanishing: set[str] = set()
        self.absent_checks = 0
        self.opened_by_click: list[list[dict[str, Any]]] = []
        self.network: dict[int, list[dict[str, Any]]] = {}
        # Requests that pages send once a navigation to the URL or a click on the selector happens.
        self.sent_on: dict[str, dict[int, list[dict[str, Any]]]] = {}
        self.bodies: dict[int, str] = {}
        # Whole bodies the server writes to requestFilePath; inline bodies may be cut off.
        self.full_bodies: dict[int, str] = {}
        self.page_resources: dict[int, list[str]] = {}
        self.script_result: dict[str, Any] | None = None
        self.errors: dict[str, str] = {}
        self.mcp = self._build()

    def _record(self, name: str, args: dict[str, Any]) -> None:
        self.calls.append((name, args))
        if name in self.errors:
            raise ToolError(self.errors[name])

    def _send(self, trigger: str) -> None:
        for page_id, entries in self.sent_on.get(trigger, {}).items():
            self.network = {**self.network, page_id: [*self.network.get(page_id, []), *entries]}

    def _check_selector(self, function: str) -> dict[str, Any]:
        selector = json.loads(SELECTOR_IN_SCRIPT.search(function).group(1))
        if self.absent_checks > 0:
            self.absent_checks -= 1
            return _script_result(False)
        if selector in self.missing:
            return _script_result(False)
        if ".click()" not in function:
            return _script_result(True)
        if selector in self.vanishing:
            return _script_result(False)
        opened = self.opened_by_click.pop(0) if self.opened_by_click else []
        self.pages = [*self.pages, *opened]
        self._send(selector)
        return {**_script_result(True), **({"openedPages": opened} if opened else {})}

    def _build(self) -> FastMCP:
        mcp = FastMCP("fake-chrome-devtools")

        @mcp.tool
        def list_pages() -> dict[str, Any]:
            self._record("list_pages", {})
            return {"pages": self.pages}

        @mcp.tool
        def navigate_page(pageId: int, url: str, type: str = "url") -> dict[str, Any]:
            self._record("navigate_page", {"pageId": pageId, "url": url, "type": type})
            self._send(url)
            return {"message": f"Successfully navigated to {url}.", "pages": self.pages}

        @mcp.tool
        def evaluate_script(pageId: int, function: str, waitForStableDom: bool = True) -> dict[str, Any]:
            args = {"pageId": pageId, "function": function, "waitForStableDom": waitForStableDom}
            self._record("evaluate_script", args)
            if self.script_result is not None:
                return self.script_result
            if "performance" in function:
                return _script_result(self.page_resources.get(pageId, []))
            return self._check_selector(function)

        @mcp.tool
        def list_network_requests(pageId: int, includePreservedRequests: bool = False) -> dict[str, Any]:
            self._record("list_network_requests", {"pageId": pageId, "includePreservedRequests": includePreservedRequests})
            return {"networkRequests": self.network.get(pageId, [])}

        @mcp.tool
        def get_network_request(pageId: int, reqid: int, requestFilePath: str | None = None) -> dict[str, Any]:
            saving = {"requestFilePath": requestFilePath} if requestFilePath else {}
            self._record("get_network_request", {"pageId": pageId, "reqid": reqid, **saving})
            entry = next(entry for entry in self.network[pageId] if entry["requestId"] == reqid)
            if requestFilePath:
                if reqid not in self.full_bodies:
                    return {"networkRequest": entry}
                Path(requestFilePath).write_text(self.full_bodies[reqid], encoding="utf-8")
                return {"networkRequest": {**entry, "requestBodyFilePath": requestFilePath}}
            body = {"requestBody": self.bodies[reqid]} if reqid in self.bodies else {}
            return {"networkRequest": {**entry, **body}}

        return mcp

    @property
    def called_tools(self) -> list[str]:
        return [name for name, _ in self.calls]


@pytest.fixture(autouse=True)
def no_waits(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("step_goals.GOAL_WAIT_SECONDS", 0)
    monkeypatch.setattr("step_runner.STEP_DELAY_RANGE_SECONDS", (0.0, 0.0))
    monkeypatch.setattr("page_actions.POLL_SECONDS", 0.0)


@pytest.fixture
def server() -> FakeDevtoolsServer:
    return FakeDevtoolsServer()
