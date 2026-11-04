import asyncio
from typing import Any, Callable

import pytest
from fastmcp import Client

from argos_runner.criteria.network_capture import CapturedRequest, NetworkCapture
from argos_runner.devtools.mcp_call import call_tool
from argos_runner.scenario.model import Action
from tests.conftest import FakePlaywrightServer, request_entry, tab

pytestmark = pytest.mark.integration

GA4_URL = "https://analytics.google.com/g/collect?en=a"


def _hit(name: str) -> dict[str, Any]:
    return request_entry(f"https://analytics.google.com/g/collect?en={name}")


def _names(capture: NetworkCapture) -> list[str]:
    return [request.url.split("en=")[1] for request in capture.requests]


def _is_pixel(url: str) -> bool:
    return "/g/collect" in url


def _with_tabs(server: FakePlaywrightServer, network: dict[int, list[dict[str, Any]]]) -> None:
    server.tabs = [tab(f"https://a.com/{index}") for index in network]
    server.network = network


def _capture(server: FakePlaywrightServer, between: Callable[[], None] | None = None, reads: int = 1) -> NetworkCapture:
    async def go() -> NetworkCapture:
        async with Client(server.mcp) as client:
            capture = NetworkCapture(client, _is_pixel)
            await capture()
            for _ in range(reads - 1):
                if between:
                    between()
                await capture()
            return capture

    return asyncio.run(go())


def _args(server: FakePlaywrightServer, tool: str) -> list[dict[str, Any]]:
    return [args for name, args in server.calls if name == tool]


def test_reads_wanted_requests_from_every_tab(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [request_entry(GA4_URL), request_entry("https://a.com/x.js")], 1: [_hit("b")]})

    capture = _capture(server)

    assert capture.requests == [CapturedRequest(url=GA4_URL, body=None), CapturedRequest(url=_hit("b")["url"], body=None)]
    assert capture.warnings == []
    assert capture.error is None


def test_returns_to_the_current_tab_after_reading_the_others(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [], 1: [], 2: []})
    server.current = 1

    _capture(server)

    assert server.current == 1
    assert [args.get("index") for args in _args(server, "browser_tabs") if args["action"] == "select"] == [0, 2, 1]


def test_single_tab_is_read_without_selecting_it(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [request_entry(GA4_URL)]})

    _capture(server)

    assert [args["action"] for args in _args(server, "browser_tabs")] == ["list"]


def test_counts_all_recorded_requests_across_tabs(server: FakePlaywrightServer) -> None:
    _with_tabs(
        server, {0: [request_entry(GA4_URL), request_entry("https://a.com/x.js")], 1: [request_entry("https://b.com/y.js")]}
    )

    assert _capture(server).recorded_requests == 3


def test_lists_successful_and_earlier_navigation_requests(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [request_entry(GA4_URL, "POST")]})

    capture = _capture(server)

    assert _args(server, "browser_network_requests") == [{"static": True, "all": True}]
    assert len(capture.requests) == 1


def test_reads_requests_sent_before_the_last_navigation(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [_hit("before"), _hit("after")]})
    server.navigated_at = {0: 1}

    assert _names(_capture(server)) == ["before", "after"]


def test_reads_post_body(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [request_entry(GA4_URL, "POST", "en=b\nen=c")]})

    assert _capture(server).requests == [CapturedRequest(url=GA4_URL, body="en=b\nen=c")]
    assert _args(server, "browser_network_request") == [{"index": 1, "part": "request-body"}]


def test_long_post_body_is_read_whole(server: FakePlaywrightServer) -> None:
    body = "en=a\nen=b&ep.x=" + "y" * 20000
    _with_tabs(server, {0: [request_entry(GA4_URL, "POST", body)]})

    assert _capture(server).requests == [CapturedRequest(url=GA4_URL, body=body)]


def test_post_without_body_needs_no_warning(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [request_entry(GA4_URL, "POST")]})

    capture = _capture(server)

    assert capture.requests == [CapturedRequest(url=GA4_URL, body=None)]
    assert capture.warnings == []


def test_does_not_fetch_body_of_get_request(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [request_entry(GA4_URL)]})

    _capture(server)

    assert "browser_network_request" not in server.called_tools


def test_does_not_fetch_body_of_unwanted_request(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [request_entry("https://a.com/x", "POST", "x=1")]})

    capture = _capture(server)

    assert capture.requests == []
    assert "browser_network_request" not in server.called_tools


def test_unreadable_body_keeps_request_and_warns(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [request_entry(GA4_URL, "POST", "en=b")]})
    server.errors = {"browser_network_request": "Request #1 not found."}

    capture = _capture(server)

    assert capture.requests == [CapturedRequest(url=GA4_URL, body=None)]
    assert len(capture.warnings) == 1
    assert GA4_URL in capture.warnings[0]


def test_body_is_read_from_the_tab_that_sent_it(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [], 1: [request_entry(GA4_URL, "POST", "en=popup")]})

    assert _capture(server).requests == [CapturedRequest(url=GA4_URL, body="en=popup")]


def test_repeated_reads_do_not_duplicate_requests(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [request_entry(GA4_URL, "POST", "en=b")]})

    capture = _capture(server, reads=2)

    assert capture.requests == [CapturedRequest(url=GA4_URL, body="en=b")]
    assert server.called_tools.count("browser_network_request") == 1


def test_later_read_adds_new_requests(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [request_entry(GA4_URL)]})

    def add_request() -> None:
        server.network[0].append(_hit("later"))

    capture = _capture(server, add_request, reads=2)

    assert [request.url for request in capture.requests] == [GA4_URL, _hit("later")["url"]]


def test_same_number_in_another_tab_is_a_different_request(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [request_entry(GA4_URL)], 1: [_hit("b")]})

    assert len(_capture(server).requests) == 2


def test_repeated_reads_do_not_repeat_warnings(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [request_entry(GA4_URL, "POST", "en=b")]})
    server.errors = {"browser_network_request": "Request #1 not found."}

    assert len(_capture(server, reads=2).warnings) == 1


def test_recorded_count_reflects_latest_read(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [request_entry(GA4_URL)]})

    def add_request() -> None:
        server.network[0].append(request_entry("https://a.com/x.js"))

    assert _capture(server, add_request, reads=2).recorded_requests == 2


def _around(
    server: FakePlaywrightServer,
    action: Action,
    after: Callable[[], None] = lambda: None,
    run: Callable[[Client], Any] | None = None,
) -> tuple[NetworkCapture, dict[str, Any]]:
    """Reads, runs `action` through the capture, lets the tabs change with `after`, then reads again."""

    async def go() -> tuple[NetworkCapture, dict[str, Any]]:
        async with Client(server.mcp) as client:
            capture = NetworkCapture(client, _is_pixel)
            await capture()
            running = run(client) if run else lambda: call_tool(client, action.action, action.params)
            response = await capture.around_action(action, running)
            after()
            await capture()
            return capture, response

    return asyncio.run(go())


def _close(index: int | None = None) -> Action:
    return Action(action="browser_tabs", params={"action": "close", **({} if index is None else {"index": index})})


def test_closing_a_tab_keeps_the_later_tabs_new_requests(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [_hit("a")], 1: [_hit("b1"), _hit("b2")], 2: [_hit("c")]})

    capture, _ = _around(server, _close(1), after=lambda: server.network[1].append(_hit("d")))

    assert _names(capture) == ["a", "b1", "b2", "c", "d"]


def test_closing_a_tab_does_not_read_the_later_tabs_requests_twice(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [_hit("a")], 1: [_hit("b")], 2: [_hit("c1"), _hit("c2")]})

    capture, _ = _around(server, _close(1))

    assert _names(capture) == ["a", "b", "c1", "c2"]


def test_requests_sent_right_before_a_close_are_read(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [_hit("a")], 1: []})

    async def go() -> NetworkCapture:
        async with Client(server.mcp) as client:
            capture = NetworkCapture(client, _is_pixel)
            await capture()
            server.network[1].append(_hit("last"))
            await capture.around_action(_close(1), lambda: call_tool(client, "browser_tabs", _close(1).params))
            return capture

    assert _names(asyncio.run(go())) == ["a", "last"]


def test_closing_the_current_tab_without_an_index_renumbers_from_it(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [_hit("a")], 1: [_hit("b")], 2: [_hit("c1"), _hit("c2")]})
    server.current = 1

    capture, _ = _around(server, _close())

    # The current tab is read first.
    assert _names(capture) == ["b", "a", "c1", "c2"]


def test_closing_a_tab_keeps_its_recorded_count(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [_hit("a")], 1: [_hit("b"), request_entry("https://a.com/x.js")]})

    capture, _ = _around(server, _close(1))

    assert capture.recorded_requests == 3


def test_closing_the_browser_reads_the_new_browser_from_its_first_request(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [_hit("a")], 1: [_hit("b")]})

    capture, _ = _around(
        server, Action(action="browser_close", params={}), after=lambda: setattr(server, "network", {0: [_hit("new")]})
    )

    assert _names(capture) == ["a", "b", "new"]
    assert capture.recorded_requests == 3


def test_failed_close_leaves_the_numbering_as_it_was(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [_hit("a")], 1: [_hit("b")], 2: [_hit("c")]})

    async def refuse() -> dict[str, Any]:
        return {"status": "error", "message": "no such tab"}

    capture, response = _around(server, _close(1), run=lambda client: refuse)

    assert response == {"status": "error", "message": "no such tab"}
    assert _names(capture) == ["a", "b", "c"]


def test_close_is_not_run_when_the_tabs_cannot_be_read_first(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [_hit("a")], 1: [_hit("b")], 2: [_hit("c")]})
    server.current = 2

    async def go() -> dict[str, Any]:
        async with Client(server.mcp) as client:
            capture = NetworkCapture(client, _is_pixel)
            await capture()
            server.errors = {"browser_tabs": "Execution context was destroyed, most likely because of a navigation."}
            return await capture.around_action(_close(), lambda: call_tool(client, "browser_tabs", _close().params))

    response = asyncio.run(go())

    assert response == {"status": "error", "message": "cannot read the tabs before browser_tabs closes one"}
    assert [args["action"] for args in _args(server, "browser_tabs")].count("close") == 0
    assert len(server.tabs) == 3


def test_tab_the_page_closes_itself_is_warned_about(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [_hit("a")], 1: [_hit("popup")]})

    capture = _capture(server, between=lambda: server._close(1), reads=2)

    assert capture.warnings == [
        "a tab closed without a scenario action closing it; requests of the tabs after it may be missed or read twice"
    ]


def test_tab_an_action_closes_is_not_warned_about(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [_hit("a")], 1: [_hit("b")], 2: [_hit("c")]})

    capture, _ = _around(server, _close(1))

    assert capture.warnings == []


def test_other_actions_just_run(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: []})
    navigate = Action(action="browser_navigate", params={"url": "https://a.com"})

    _, response = _around(server, navigate)

    assert response["status"] == "success"
    assert server.called_tools.count("browser_network_requests") == 2


def _read_page(server: FakePlaywrightServer, since_ms: float = 0) -> tuple[NetworkCapture, list[str]]:
    async def go() -> tuple[NetworkCapture, list[str]]:
        async with Client(server.mcp) as client:
            capture = NetworkCapture(client, _is_pixel)
            return capture, await capture.read_page_urls(since_ms)

    return asyncio.run(go())


def test_reads_page_resource_urls_from_every_tab(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [], 1: []})
    server.page_resources = {0: ["https://a.com/1"], 1: ["https://a.com/2"]}

    _, urls = _read_page(server)

    assert urls == ["https://a.com/1", "https://a.com/2"]
    assert server.current == 0


def test_page_resources_are_read_from_the_given_time_on(server: FakePlaywrightServer) -> None:
    _read_page(server, since_ms=1700000000123.5)

    function = _args(server, "browser_evaluate")[-1]["function"]
    assert "performance.timeOrigin + e.startTime >= 1700000000123.5" in function


def test_failed_page_read_only_warns(server: FakePlaywrightServer) -> None:
    server.errors = {"browser_evaluate": "boom"}

    capture, urls = _read_page(server)

    assert urls == []
    assert capture.error is None
    assert len(capture.warnings) == 1


@pytest.mark.parametrize("printed", ['### Result\n{"type": "object"}', "### Result\nundefined"])
def test_unexpected_page_read_result_only_warns(server: FakePlaywrightServer, printed: str) -> None:
    server.script_result = printed

    capture, urls = _read_page(server)

    assert urls == []
    assert len(capture.warnings) == 1


def test_page_read_tolerates_failed_tab_listing(server: FakePlaywrightServer) -> None:
    server.errors = {"browser_tabs": "browser closed"}

    capture, urls = _read_page(server)

    assert urls == []
    assert len(capture.warnings) == 1


def test_failed_request_listing_sets_error(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: []})
    server.errors = {"browser_network_requests": "No page found"}

    capture = _capture(server)

    assert capture.requests == []
    assert "No page found" in capture.error


def test_failed_tab_selection_sets_error(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [request_entry(GA4_URL)], 1: [_hit("b")]})
    server.errors = {"browser_tabs select 1": "Tab 1 not found"}

    capture = _capture(server)

    assert capture.error == "cannot select tab 1: Tab 1 not found"
    assert capture.requests == [CapturedRequest(url=GA4_URL, body=None)]


def test_failed_return_to_the_current_tab_sets_error(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [request_entry(GA4_URL)], 1: [_hit("b")]})
    server.current = 1
    server.errors = {"browser_tabs select 1": "Tab 1 not found"}

    capture = _capture(server)

    assert capture.error == "cannot select tab 1 again: Tab 1 not found"
    assert len(capture.requests) == 2


def test_failed_tab_selection_only_warns_while_reading_page_resources(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [], 1: []})
    server.page_resources = {0: ["https://a.com/1"], 1: ["https://a.com/2"]}
    server.errors = {"browser_tabs select 1": "Tab 1 not found"}

    capture, urls = _read_page(server)

    assert urls == ["https://a.com/1"]
    assert capture.error is None
    assert capture.warnings == ["cannot select tab 1: Tab 1 not found"]


def test_failed_selection_still_returns_to_the_current_tab(server: FakePlaywrightServer) -> None:
    _with_tabs(server, {0: [], 1: [], 2: []})
    server.current = 2
    server.errors = {"browser_tabs select 1": "Tab 1 not found"}

    _read_page(server)

    assert server.current == 2
    assert [args.get("index") for args in _args(server, "browser_tabs") if args["action"] == "select"] == [0, 1, 2]


def test_failed_tab_listing_sets_error(server: FakePlaywrightServer) -> None:
    server.errors = {"browser_tabs": "browser closed"}

    assert "browser closed" in _capture(server).error


@pytest.mark.parametrize("tool", ["browser_tabs", "browser_network_requests"])
def test_read_during_navigation_only_warns_and_next_read_retries(server: FakePlaywrightServer, tool: str) -> None:
    _with_tabs(server, {0: [request_entry(GA4_URL)]})
    server.errors = {tool: "Execution context was destroyed, most likely because of a navigation."}

    capture = _capture(server, between=lambda: setattr(server, "errors", {}), reads=2)

    assert capture.error is None
    assert len(capture.warnings) == 1
    assert capture.requests == [CapturedRequest(url=GA4_URL, body=None)]


def test_connection_failure_sets_error() -> None:
    class BrokenClient:
        async def call_tool(self, *args: Any, **kwargs: Any) -> None:
            raise ConnectionError("connection lost")

    capture = NetworkCapture(BrokenClient(), _is_pixel)
    asyncio.run(capture())

    assert "connection lost" in capture.error
