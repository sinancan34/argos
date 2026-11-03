import json
import re
from pathlib import Path
from typing import Any

import pytest
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

SELECTORS_IN_MATCHER = re.compile(r"=> (\[.*?\])\.map\(")
SNAPSHOT_UIDS = ["1_0", "1_1", "1_2"]
# Accessible names of the snapshot's buttons, SNAPSHOT_UIDS[1:] in order.
SNAPSHOT_NAMES = ["Buy", "Share"]


def request_entry(request_id: int, url: str, method: str = "GET") -> dict[str, Any]:
    return {"requestId": request_id, "method": method, "url": url, "status": "200"}


def page(page_id: int, url: str = "about:blank", title: str = "", selected: bool | None = None) -> dict[str, Any]:
    return {"id": page_id, "url": url, "title": title, "selected": page_id == 1 if selected is None else selected}


def _script_result(value: Any) -> dict[str, Any]:
    return {"message": f"Script ran on page and returned:\n```json\n{json.dumps(value)}\n```"}


class FakeDevtoolsServer:
    """In-memory MCP server exposing the chrome-devtools-mcp tool shapes the runner talks to."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.pages: list[dict[str, Any]] = [page(1)]
        # Selectors that match no element of the snapshot; the i-th other selector matches SNAPSHOT_UIDS[i].
        self.missing: set[str] = set()
        self.uid_selectors: dict[str, str] = {}
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

    def _select(self, page_id: int) -> dict[str, Any]:
        self.pages = [{**entry, "selected": entry["id"] == page_id} for entry in self.pages]
        return {"pages": self.pages}

    def _match(self, function: str, uids: list[str]) -> dict[str, Any]:
        selectors = json.loads(SELECTORS_IN_MATCHER.search(function).group(1))
        found = [-1 if selector in self.missing else index for index, selector in enumerate(selectors)]
        matched = {uids[index]: selector for index, selector in zip(found, selectors) if index >= 0}
        self.uid_selectors = {**self.uid_selectors, **matched}
        return _script_result(found)

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
        def new_page(url: str) -> dict[str, Any]:
            self._record("new_page", {"url": url})
            self.pages = [*self.pages, page(max(entry["id"] for entry in self.pages) + 1, url)]
            return self._select(self.pages[-1]["id"])

        @mcp.tool
        def select_page(pageId: int) -> dict[str, Any]:
            self._record("select_page", {"pageId": pageId})
            return self._select(pageId)

        @mcp.tool
        def take_snapshot(pageId: int) -> dict[str, Any]:
            self._record("take_snapshot", {"pageId": pageId})
            # Some text nodes come without a uid.
            buttons = [{"id": uid, "role": "button", "name": name} for uid, name in zip(SNAPSHOT_UIDS[1:], SNAPSHOT_NAMES)]
            children = [{"role": "StaticText", "name": "•"}, *buttons]
            return {"snapshot": {"id": SNAPSHOT_UIDS[0], "role": "RootWebArea", "children": children}}

        @mcp.tool
        def evaluate_script(
            pageId: int, function: str, waitForStableDom: bool = True, args: list[str] | None = None
        ) -> dict[str, Any]:
            uids = {"args": args} if args is not None else {}
            call = {"pageId": pageId, "function": function, "waitForStableDom": waitForStableDom, **uids}
            self._record("evaluate_script", call)
            if args is not None:
                return self._match(function, args)
            if self.script_result is not None:
                return self.script_result
            if "performance" in function:
                return _script_result(self.page_resources.get(pageId, []))
            return _script_result(True)

        @mcp.tool
        def click(pageId: int, uid: str) -> dict[str, Any]:
            self._record("click", {"pageId": pageId, "uid": uid})
            self._send(self.uid_selectors.get(uid, uid))
            return {"message": "Successfully clicked on the element"}

        @mcp.tool
        def drag(pageId: int, from_uid: str, to_uid: str) -> dict[str, Any]:
            self._record("drag", {"pageId": pageId, "from_uid": from_uid, "to_uid": to_uid})
            return {"message": "Successfully dragged an element"}

        @mcp.tool
        def fill_form(pageId: int, elements: list[dict[str, Any]]) -> dict[str, Any]:
            self._record("fill_form", {"pageId": pageId, "elements": elements})
            return {"message": "Successfully filled out the form"}

        @mcp.tool
        def wait_for(pageId: int, text: list[str], timeout: int = 0) -> dict[str, Any]:
            self._record("wait_for", {"pageId": pageId, "text": text, "timeout": timeout})
            return {"message": f"Element matching one of {text} found."}

        @mcp.tool
        def list_extensions() -> dict[str, Any]:
            self._record("list_extensions", {})
            return {"extensions": []}

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
    monkeypatch.setattr("step_criteria.CRITERIA_WAIT_SECONDS", 0)
    monkeypatch.setattr("step_runner.ACTION_DELAY_RANGE_SECONDS", (0.0, 0.0))


@pytest.fixture
def server() -> FakeDevtoolsServer:
    return FakeDevtoolsServer()
