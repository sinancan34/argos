import json
from dataclasses import dataclass
from typing import Any, Callable

from fastmcp import Client

from mcp_call import call_tool

# The most records the MCP server keeps per tab; without a limit it lists only 100.
REQUEST_LIMIT = 5000


@dataclass(frozen=True)
class CapturedRequest:
    url: str
    body: str | None


class NetworkCapture:
    """Reads recorded requests from every open tab; must run before stop_browser deletes them.

    It can be called repeatedly: each call adds only requests it has not seen yet.
    """

    def __init__(self, client: Client, wanted: Callable[[str], bool]) -> None:
        self._client = client
        self._wanted = wanted
        self._seen: frozenset[tuple[str, str]] = frozenset()
        self._recorded: dict[str, int] = {}
        self._dropped: dict[str, int] = {}
        self._body_warnings: list[str] = []
        self.requests: list[CapturedRequest] = []
        self.error: str | None = None

    @property
    def recorded_requests(self) -> int:
        return sum(self._recorded.values())

    @property
    def warnings(self) -> list[str]:
        dropped = sum(self._dropped.values())
        dropped_warning = [f"{dropped} older requests were dropped by the recorder"] if dropped else []
        return [*self._body_warnings, *dropped_warning]

    async def __call__(self) -> None:
        tabs = await call_tool(self._client, "list_tabs", {})
        if tabs["status"] != "success":
            self.error = f"cannot list tabs: {json.dumps(tabs, ensure_ascii=False)}"
            return
        for tab in tabs["data"]["tabs"]:
            await self._read_tab(tab["targetId"])

    async def _read_tab(self, target_id: str) -> None:
        params = {"limit": REQUEST_LIMIT, "url_max_length": None, "target_id": target_id}
        listed = await call_tool(self._client, "list_network_requests", params)
        if listed["status"] != "success":
            self.error = f"cannot list requests: {json.dumps(listed, ensure_ascii=False)}"
            return
        self._recorded = {**self._recorded, target_id: listed["data"]["total_count"]}
        self._dropped = {**self._dropped, target_id: listed["data"]["dropped"]}
        for entry in listed["data"]["requests"]:
            await self._add_if_new(entry, target_id)

    async def _add_if_new(self, entry: dict[str, Any], target_id: str) -> None:
        identity = (target_id, entry["requestId"])
        if identity in self._seen or not entry["url"] or not self._wanted(entry["url"]):
            return
        self._seen = self._seen | {identity}
        body = await self._read_body(entry, target_id)
        self.requests = [*self.requests, CapturedRequest(url=entry["url"], body=body)]

    async def _read_body(self, entry: dict[str, Any], target_id: str) -> str | None:
        if not entry["hasPostData"]:
            return None
        params = {"request_id": entry["requestId"], "include_record": False, "target_id": target_id}
        response = await call_tool(self._client, "get_network_request", params)
        if response["status"] != "success":
            self._body_warnings = [*self._body_warnings, f"could not read the POST body of {entry['url']}"]
            return None
        post_data = response["data"]["post_data"]
        if not post_data or post_data["base64Encoded"]:
            return None
        return post_data["postData"]
