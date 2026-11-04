"""Reads the requests the page sent through the server's own network tools, as a user's DevTools would show them."""

import re
from dataclasses import dataclass
from types import MappingProxyType

from argos_agent.playwright_mcp.client import PlaywrightMCP

# `2. [POST] https://…/g/collect?v=2 => [204] No Content`
REQUEST_LINE = re.compile(r"^(\d+)\. \[([A-Z]+)\] (\S+)", re.MULTILINE)
RESULT_SECTION = "Result"
LIST_ARGUMENTS = MappingProxyType(
    {
        # gtm.js is a script; without static it is left out of the list.
        "static": True,
        # Since the session began, so a hit sent right before a navigation is not dropped and indexes stay put.
        "all": True,
    }
)
BODY_PART = "request-body"


class NetworkError(RuntimeError):
    """The server could not list the requests or read a request body."""


@dataclass(frozen=True)
class Listed:
    index: int
    method: str
    url: str


def parse_requests(text: str) -> list[Listed]:
    return [Listed(int(index), method, url) for index, method, url in REQUEST_LINE.findall(text)]


async def list_requests(mcp: PlaywrightMCP) -> list[Listed]:
    """Every request of the current tab since the session began, in the order they were sent."""
    # ponytail: the current tab only; collect from every tab with browser_tabs once a scenario opens a popup.
    result = await mcp.call("browser_network_requests", LIST_ARGUMENTS)
    if result.is_error:
        raise NetworkError(f"browser_network_requests: {result.error}")
    return parse_requests(result.sections.get(RESULT_SECTION, ""))


async def request_body(mcp: PlaywrightMCP, index: int) -> str:
    """The request body by its listed index; a request without a body gives ''."""
    result = await mcp.call("browser_network_request", {"index": index, "part": BODY_PART})
    if result.is_error:
        raise NetworkError(f"browser_network_request #{index}: {result.error}")
    return result.sections.get(RESULT_SECTION, "")
