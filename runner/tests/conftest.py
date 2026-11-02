from typing import Any

import pytest
from fastmcp import FastMCP


def request_entry(request_id: str, url: str | None, has_post: bool = False) -> dict[str, Any]:
    return {"requestId": request_id, "url": url, "hasPostData": has_post}


class FakeNodriverServer:
    """In-memory MCP server exposing the tool shapes the runner talks to."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.wait_for_response: dict[str, Any] = {"status": "success", "data": {}}
        self.stop_response: dict[str, Any] = {"status": "success", "data": {}}
        self.new_targets: list[list[dict[str, Any]]] = []
        self.network: dict[str, list[dict[str, Any]]] = {}
        self.post_data: dict[str, dict[str, Any]] = {}
        self.dropped = 0
        self.list_response: dict[str, Any] | None = None
        self.tabs_response: dict[str, Any] | None = None
        self.mcp = self._build()

    def _build(self) -> FastMCP:
        mcp = FastMCP("fake-nodriver")

        @mcp.tool
        def start_browser() -> dict[str, Any]:
            self.calls.append(("start_browser", {}))
            return {"status": "success", "data": {}}

        @mcp.tool
        def stop_browser() -> dict[str, Any]:
            self.calls.append(("stop_browser", {}))
            self.network = {}
            return self.stop_response

        @mcp.tool
        def list_tabs() -> dict[str, Any]:
            self.calls.append(("list_tabs", {}))
            if self.tabs_response is not None:
                return self.tabs_response
            tabs = [{"targetId": target} for target in self.network]
            return {"status": "success", "data": {"tabs": tabs}}

        @mcp.tool
        def list_network_requests(
            limit: int | None = None,
            url_max_length: int | None = 200,
            target_id: str | None = None,
        ) -> dict[str, Any]:
            args = {"limit": limit, "url_max_length": url_max_length, "target_id": target_id}
            self.calls.append(("list_network_requests", args))
            if self.list_response is not None:
                return self.list_response
            requests = self.network.get(target_id, [])
            data = {"requests": requests, "total_count": len(requests), "dropped": self.dropped}
            return {"status": "success", "data": data}

        @mcp.tool
        def get_network_request(
            request_id: str, include_record: bool = True, target_id: str | None = None
        ) -> dict[str, Any]:
            args = {"request_id": request_id, "include_record": include_record}
            self.calls.append(("get_network_request", {**args, "target_id": target_id}))
            if request_id not in self.post_data:
                return {"status": "fail", "data": {"request_id": "no post data"}}
            return {"status": "success", "data": {"post_data": self.post_data[request_id]}}

        @mcp.tool
        def navigate(url: str) -> dict[str, Any]:
            self.calls.append(("navigate", {"url": url}))
            return {"status": "success", "data": {}}

        @mcp.tool
        def click_element(selector: str) -> dict[str, Any]:
            self.calls.append(("click_element", {"selector": selector}))
            opened = self.new_targets.pop(0) if self.new_targets else []
            return {"status": "success", "data": {"new_targets": opened}}

        @mcp.tool
        def wait_for(selector: str, target_id: str | None = None) -> dict[str, Any]:
            self.calls.append(("wait_for", {"selector": selector, "target_id": target_id}))
            return self.wait_for_response

        return mcp

    @property
    def called_tools(self) -> list[str]:
        return [name for name, _ in self.calls]


@pytest.fixture(autouse=True)
def no_goal_wait(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("run.GOAL_WAIT_SECONDS", 0)


@pytest.fixture
def server() -> FakeNodriverServer:
    return FakeNodriverServer()
