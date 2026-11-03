import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from fastmcp import Client

from argos_runner.devtools.mcp_call import call_tool, evaluate

# Resource times count from the page's own start; timeOrigin turns them into epoch milliseconds.
PAGE_RESOURCES_JS = (
    "() => performance.getEntriesByType('resource')"
    ".filter(e => performance.timeOrigin + e.startTime >= {since_ms}).map(e => e.name)"
)
UNAVAILABLE_BODY = "<Request body not available anymore>"
# Inline bodies stop at 10000 characters and end with this; the whole body is then read from a file.
TRUNCATED_BODY_SUFFIX = "... <truncated>"
# A read that meets a page mid-navigation fails with this; the next read tries again.
NAVIGATION_ERROR = "Execution context was destroyed"


@dataclass(frozen=True)
class CapturedRequest:
    url: str
    body: str | None


def _resource_urls(response: dict[str, Any]) -> list[str] | None:
    if response["status"] != "success":
        return None
    urls = response["data"]["result"]
    is_url_list = isinstance(urls, list) and all(isinstance(url, str) for url in urls)
    return urls if is_url_list else None


def _is_navigating(response: dict[str, Any]) -> bool:
    return response["status"] != "success" and NAVIGATION_ERROR in response["message"]


class NetworkCapture:
    """Reads recorded requests from every open page; must run before the browser closes.

    It can be called repeatedly: each call adds only requests it has not seen yet.
    """

    def __init__(self, client: Client, wanted: Callable[[str], bool]) -> None:
        self._client = client
        self._wanted = wanted
        self._seen: frozenset[tuple[int, int]] = frozenset()
        self._recorded: dict[int, int] = {}
        self.warnings: list[str] = []
        self.requests: list[CapturedRequest] = []
        self.error: str | None = None

    @property
    def recorded_requests(self) -> int:
        return sum(self._recorded.values())

    async def __call__(self) -> None:
        pages = await call_tool(self._client, "list_pages", {})
        if _is_navigating(pages):
            self._warn("could not list pages while a page was navigating; the next read tries again")
            return
        if pages["status"] != "success":
            self.error = f"cannot list pages: {json.dumps(pages, ensure_ascii=False)}"
            return
        for page in pages["data"].get("pages", []):
            await self._read_page(page["id"])

    async def read_page_urls(self, since_ms: float) -> list[str]:
        """Reads what each page says it requested since `since_ms` (epoch), to compare with the recorder."""
        pages = await call_tool(self._client, "list_pages", {})
        if pages["status"] != "success":
            self._warn("could not list pages to read page resources")
            return []
        found: list[str] = []
        script = PAGE_RESOURCES_JS.replace("{since_ms}", repr(float(since_ms)))
        for page in pages["data"].get("pages", []):
            urls = _resource_urls(await evaluate(self._client, page["id"], script))
            if urls is None:
                self._warn(f"could not read page resources of {page.get('url')}")
            else:
                found = [*found, *urls]
        return found

    def _warn(self, message: str) -> None:
        self.warnings = [*self.warnings, message]

    async def _read_page(self, page_id: int) -> None:
        params = {"pageId": page_id, "includePreservedRequests": True}
        listed = await call_tool(self._client, "list_network_requests", params)
        if _is_navigating(listed):
            self._warn(f"could not list requests of page {page_id} while it was navigating; the next read tries again")
            return
        if listed["status"] != "success":
            self.error = f"cannot list requests: {json.dumps(listed, ensure_ascii=False)}"
            return
        entries = listed["data"].get("networkRequests", [])
        self._recorded = {**self._recorded, page_id: len(entries)}
        for entry in entries:
            await self._add_if_new(entry, page_id)

    async def _add_if_new(self, entry: dict[str, Any], page_id: int) -> None:
        identity = (page_id, entry["requestId"])
        if identity in self._seen or not entry["url"] or not self._wanted(entry["url"]):
            return
        self._seen = self._seen | {identity}
        body = await self._read_body(entry, page_id) if entry["method"] == "POST" else None
        self.requests = [*self.requests, CapturedRequest(url=entry["url"], body=body)]

    async def _read_body(self, entry: dict[str, Any], page_id: int) -> str | None:
        params = {"pageId": page_id, "reqid": entry["requestId"]}
        response = await call_tool(self._client, "get_network_request", params)
        body = response["data"]["networkRequest"].get("requestBody") if response["status"] == "success" else None
        if response["status"] != "success" or body == UNAVAILABLE_BODY:
            self._warn(f"could not read the POST body of {entry['url']}")
            return None
        if body is not None and body.endswith(TRUNCATED_BODY_SUFFIX):
            return await self._read_whole_body(entry, page_id)
        return body

    async def _read_whole_body(self, entry: dict[str, Any], page_id: int) -> str | None:
        """Has the server write the body to a file, which keeps it whole; the file is removed after."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "body.network-request"
            params = {"pageId": page_id, "reqid": entry["requestId"], "requestFilePath": str(path)}
            response = await call_tool(self._client, "get_network_request", params)
            if response["status"] != "success":
                return self._cut_off(entry, f"server: {response['message']}")
            if not response["data"]["networkRequest"].get("requestBodyFilePath"):
                return self._cut_off(entry, "the server saved no body file")
            try:
                return path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                return self._cut_off(entry, f"body file: {exc}")

    def _cut_off(self, entry: dict[str, Any], reason: str) -> None:
        self._warn(f"the POST body of {entry['url']} was cut off and could not be read whole ({reason}), so it was not used")
        return None
