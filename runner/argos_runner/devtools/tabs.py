import re
from dataclasses import dataclass
from typing import Any

from fastmcp import Client

from argos_runner.devtools.mcp_call import RESULT, call_tool

TABS_TOOL = "browser_tabs"
# `- 1: (current) [Title](https://…)`: a tab as browser_tabs lists it, numbered from 0.
_TAB = re.compile(r"^- (\d+): (\(current\) )?\[(.*)\]\((.*)\)$", re.MULTILINE)


@dataclass(frozen=True)
class Tab:
    index: int
    url: str
    title: str
    current: bool


def parse_tabs(listed: str) -> list[Tab]:
    return [
        Tab(index=int(index), url=url, title=title, current=bool(current))
        for index, current, title, url in _TAB.findall(listed)
    ]


def current_index(tabs: list[Tab]) -> int:
    """The tab tools act on; the first one if none is marked."""
    return next((tab.index for tab in tabs if tab.current), tabs[0].index if tabs else 0)


async def list_tabs(client: Client) -> dict[str, Any]:
    """The open tabs under `data.tabs`; listing them is what launches the browser."""
    response = await call_tool(client, TABS_TOOL, {"action": "list"})
    if response["status"] != "success":
        return response
    return {"status": "success", "data": {"tabs": parse_tabs(response["data"].get(RESULT, ""))}}


async def select_tab(client: Client, index: int) -> dict[str, Any]:
    """Makes the tab the one tools act on."""
    return await call_tool(client, TABS_TOOL, {"action": "select", "index": index})
