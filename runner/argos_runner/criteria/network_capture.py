import json
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, TypeVar

from fastmcp import Client

from argos_runner.devtools.mcp_call import RESULT, call_tool, evaluate
from argos_runner.devtools.tabs import TABS_TOOL, Tab, current_index, list_tabs, select_tab
from argos_runner.scenario.model import Action

# Resource times count from the page's own start; timeOrigin turns them into epoch milliseconds.
PAGE_RESOURCES_JS = (
    "() => performance.getEntriesByType('resource')"
    ".filter(e => performance.timeOrigin + e.startTime >= {since_ms}).map(e => e.name)"
)
# A read that meets a page mid-navigation fails with this; the next read tries again.
NAVIGATION_ERROR = "Execution context was destroyed"
# Successful requests, pings and beacons among them, are listed only with `static`; those of earlier
# navigations of the tab only with `all`.
LIST_PARAMS = {"static": True, "all": True}
# `3. [POST] https://… => [204] No Content`: a request as browser_network_requests lists it, numbered from 1
# within its tab; one still waiting for its response has no ` => …` part.
_REQUEST = re.compile(r"^(\d+)\. \[([A-Z]+)\] (\S+)(?: => .*)?$", re.MULTILINE)
# What an action that closes tabs closes, besides a tab index.
EVERY_TAB = "every tab"
CURRENT_TAB = "current tab"
TAB_CLOSED_BY_PAGE = (
    "a tab closed without a scenario action closing it; requests of the tabs after it may be missed or read twice"
)

T = TypeVar("T")


@dataclass(frozen=True)
class CapturedRequest:
    url: str
    body: str | None


def parse_requests(listed: str) -> list[tuple[int, str, str]]:
    """Each listed request as (number, method, url)."""
    return [(int(number), method, url) for number, method, url in _REQUEST.findall(listed)]


def _resource_urls(response: dict[str, Any]) -> list[str] | None:
    if response["status"] != "success":
        return None
    urls = response["data"]["result"]
    is_url_list = isinstance(urls, list) and all(isinstance(url, str) for url in urls)
    return urls if is_url_list else None


def _is_navigating(response: dict[str, Any]) -> bool:
    return response["status"] != "success" and NAVIGATION_ERROR in response["message"]


def _closes(action: Action) -> int | str | None:
    """The tab the action closes: its index, CURRENT_TAB or EVERY_TAB; None for an action that closes none."""
    if action.action == "browser_close":
        return EVERY_TAB
    if action.action == TABS_TOOL and action.params.get("action") == "close":
        index = action.params.get("index")
        return CURRENT_TAB if index is None else int(index)
    return None


class NetworkCapture:
    """Reads recorded requests from every open tab; must run before the browser closes.

    It can be called repeatedly: each call adds only requests it has not seen yet. A request is known by
    its tab's index and its number in that tab, so closing a tab, which renumbers the tabs after it,
    has to run through `around_action`.
    """

    def __init__(self, client: Client, wanted: Callable[[str], bool]) -> None:
        self._client = client
        self._wanted = wanted
        self._seen: frozenset[tuple[int, int]] = frozenset()
        self._recorded: dict[int, int] = {}
        self._closed_recorded = 0
        self._current = 0
        self._tab_count: int | None = None
        self.warnings: list[str] = []
        self.requests: list[CapturedRequest] = []
        self.error: str | None = None

    @property
    def recorded_requests(self) -> int:
        return self._closed_recorded + sum(self._recorded.values())

    async def __call__(self) -> None:
        await self._read_all()

    async def _read_all(self) -> bool:
        """Reads every tab; False if the tabs could not be listed, which leaves the keys as they were."""
        listed = await list_tabs(self._client)
        if _is_navigating(listed):
            self._warn("could not list tabs while a page was navigating; the next read tries again")
            return False
        if listed["status"] != "success":
            self.error = f"cannot list tabs: {json.dumps(listed, ensure_ascii=False)}"
            return False
        tabs = listed["data"]["tabs"]
        # ponytail: a tab the page closes itself (window.close) renumbers the tabs after it unseen, so their
        # requests may be skipped or read twice; aligning the tab lists by URL could tell which one closed.
        if self._tab_count is not None and len(tabs) < self._tab_count:
            self._warn(TAB_CLOSED_BY_PAGE)
        self._tab_count = len(tabs)
        self._current = current_index(tabs)
        _, problem = await self._each_tab(tabs, self._read_tab)
        if problem:
            self.error = problem
        return True

    async def around_action(self, action: Action, run: Callable[[], Awaitable[dict[str, Any]]]) -> dict[str, Any]:
        """Runs `run`, the action; one that closes tabs is wrapped so the requests read so far keep their keys.

        Every tab is read right before the close, while the numbers still hold; after it the closed tab's
        keys are dropped and those of the tabs after it move down by one, as those tabs did. A close whose
        tabs cannot be read first is not run: which tab it closes could not be told.
        """
        closes = _closes(action)
        if closes is None:
            return await run()
        if not await self._read_all():
            return {"status": "error", "message": f"cannot read the tabs before {action.action} closes one"}
        closed = self._current if closes == CURRENT_TAB else closes
        response = await run()
        if response["status"] == "success":
            self._forget(closed)
        return response

    async def read_page_urls(self, since_ms: float) -> list[str]:
        """Reads what each tab says it requested since `since_ms` (epoch), to compare with the recorder."""
        listed = await list_tabs(self._client)
        if listed["status"] != "success":
            self._warn("could not list tabs to read page resources")
            return []
        script = PAGE_RESOURCES_JS.replace("{since_ms}", repr(float(since_ms)))

        async def read(tab: Tab) -> list[str]:
            urls = _resource_urls(await evaluate(self._client, script))
            if urls is None:
                self._warn(f"could not read page resources of {tab.url}")
                return []
            return urls

        found, problem = await self._each_tab(listed["data"]["tabs"], read)
        if problem:
            self._warn(problem)
        return [url for urls in found for url in urls]

    async def _each_tab(self, tabs: list[Tab], read: Callable[[Tab], Awaitable[T]]) -> tuple[list[T], str | None]:
        """Runs `read` on the current tab, then on each other one selected in turn, then selects the current again.

        Also returns why a selection failed, which ends the visit.
        """
        current = current_index(tabs)
        ordered = sorted(tabs, key=lambda tab: tab.index != current)
        found: list[T] = []
        selected = current
        for tab in ordered:
            if tab.index != selected:
                moved = await select_tab(self._client, tab.index)
                if moved["status"] != "success":
                    problems = [f"cannot select tab {tab.index}: {moved['message']}", await self._back(current, selected)]
                    return found, "; ".join(problem for problem in problems if problem)
                selected = tab.index
            found = [*found, await read(tab)]
        return found, await self._back(current, selected)

    async def _back(self, current: int, selected: int) -> str | None:
        """Selects the current tab again if another one is selected; says why that failed, if it did."""
        if selected == current:
            return None
        back = await select_tab(self._client, current)
        return None if back["status"] == "success" else f"cannot select tab {current} again: {back['message']}"

    def _forget(self, closed: int | str) -> None:
        if closed == EVERY_TAB:
            self._closed_recorded += sum(self._recorded.values())
            self._seen, self._recorded, self._tab_count = frozenset(), {}, None
            return

        def moved(index: int) -> int:
            return index - 1 if index > closed else index

        self._tab_count = None if self._tab_count is None else self._tab_count - 1
        self._closed_recorded += self._recorded.get(closed, 0)
        self._seen = frozenset((moved(index), number) for index, number in self._seen if index != closed)
        self._recorded = {moved(index): count for index, count in self._recorded.items() if index != closed}

    def _warn(self, message: str) -> None:
        self.warnings = [*self.warnings, message]

    async def _read_tab(self, tab: Tab) -> None:
        listed = await call_tool(self._client, "browser_network_requests", LIST_PARAMS)
        if _is_navigating(listed):
            self._warn(f"could not list requests of tab {tab.index} while it was navigating; the next read tries again")
            return
        if listed["status"] != "success":
            self.error = f"cannot list requests: {json.dumps(listed, ensure_ascii=False)}"
            return
        entries = parse_requests(listed["data"].get(RESULT, ""))
        self._recorded = {**self._recorded, tab.index: len(entries)}
        for number, method, url in entries:
            await self._add_if_new(tab.index, number, method, url)

    async def _add_if_new(self, index: int, number: int, method: str, url: str) -> None:
        identity = (index, number)
        if identity in self._seen or not self._wanted(url):
            return
        self._seen = self._seen | {identity}
        body = await self._read_body(number, url) if method == "POST" else None
        self.requests = [*self.requests, CapturedRequest(url=url, body=body)]

    async def _read_body(self, number: int, url: str) -> str | None:
        """The request's body as the selected tab recorded it; a request without one has an empty result."""
        response = await call_tool(self._client, "browser_network_request", {"index": number, "part": "request-body"})
        if response["status"] != "success":
            self._warn(f"could not read the POST body of {url}")
            return None
        return response["data"].get(RESULT) or None
