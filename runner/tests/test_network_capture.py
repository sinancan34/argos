import asyncio
from pathlib import Path
from typing import Any, Callable

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from network_capture import CapturedRequest, NetworkCapture
from tests.conftest import FakeDevtoolsServer, page, request_entry

pytestmark = pytest.mark.integration

GA4_URL = "https://analytics.google.com/g/collect?en=a"


def _is_pixel(url: str) -> bool:
    return "/g/collect" in url


def _with_pages(server: FakeDevtoolsServer, network: dict[int, list[dict[str, Any]]]) -> None:
    server.pages = [page(page_id) for page_id in network]
    server.network = network


def _capture(server: FakeDevtoolsServer, between: Callable[[], None] | None = None, reads: int = 1) -> NetworkCapture:
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


def test_reads_wanted_requests_from_every_page(server: FakeDevtoolsServer) -> None:
    _with_pages(
        server,
        {
            1: [request_entry(1, GA4_URL), request_entry(2, "https://a.com/x.js")],
            2: [request_entry(3, "https://b.com/g/collect?en=b")],
        },
    )

    capture = _capture(server)

    assert capture.requests == [
        CapturedRequest(url=GA4_URL, body=None),
        CapturedRequest(url="https://b.com/g/collect?en=b", body=None),
    ]
    assert capture.warnings == []
    assert capture.error is None


def test_counts_all_recorded_requests_across_pages(server: FakeDevtoolsServer) -> None:
    _with_pages(
        server,
        {
            1: [request_entry(1, GA4_URL), request_entry(2, "https://a.com/x.js")],
            2: [request_entry(3, "https://b.com/y.js")],
        },
    )

    assert _capture(server).recorded_requests == 3


def test_includes_requests_of_earlier_navigations(server: FakeDevtoolsServer) -> None:
    _with_pages(server, {1: []})

    _capture(server)

    call = next(args for name, args in server.calls if name == "list_network_requests")
    assert call == {"pageId": 1, "includePreservedRequests": True}


def test_reads_post_body(server: FakeDevtoolsServer) -> None:
    _with_pages(server, {1: [request_entry(1, GA4_URL, "POST")]})
    server.bodies = {1: "en=b"}

    assert _capture(server).requests == [CapturedRequest(url=GA4_URL, body="en=b")]


def test_post_without_body_needs_no_warning(server: FakeDevtoolsServer) -> None:
    _with_pages(server, {1: [request_entry(1, GA4_URL, "POST")]})

    capture = _capture(server)

    assert capture.requests == [CapturedRequest(url=GA4_URL, body=None)]
    assert capture.warnings == []


def test_does_not_fetch_body_of_get_request(server: FakeDevtoolsServer) -> None:
    _with_pages(server, {1: [request_entry(1, GA4_URL)]})

    _capture(server)

    assert "get_network_request" not in server.called_tools


def test_does_not_fetch_body_of_unwanted_request(server: FakeDevtoolsServer) -> None:
    _with_pages(server, {1: [request_entry(1, "https://a.com/x", "POST")]})

    capture = _capture(server)

    assert capture.requests == []
    assert "get_network_request" not in server.called_tools


@pytest.mark.parametrize(
    "body",
    ["<Request body not available anymore>", "en=a\nen=b&ep.x=... <truncated>"],
)
def test_incomplete_body_is_not_used_and_warns(server: FakeDevtoolsServer, body: str) -> None:
    _with_pages(server, {1: [request_entry(1, GA4_URL, "POST")]})
    server.bodies = {1: body}

    capture = _capture(server)

    assert capture.requests == [CapturedRequest(url=GA4_URL, body=None)]
    assert len(capture.warnings) == 1
    assert GA4_URL in capture.warnings[0]


def test_cut_off_body_is_read_whole_from_a_file(server: FakeDevtoolsServer) -> None:
    _with_pages(server, {1: [request_entry(1, GA4_URL, "POST")]})
    whole = "en=a\nen=b&ep.x=" + "y" * 20000
    server.bodies = {1: whole[:10000] + "... <truncated>"}
    server.full_bodies = {1: whole}

    capture = _capture(server)

    assert capture.requests == [CapturedRequest(url=GA4_URL, body=whole)]
    assert capture.warnings == []
    saved = Path(server.calls[-1][1]["requestFilePath"])
    assert saved.suffix == ".network-request"
    assert not saved.exists()


def test_unreadable_body_file_only_warns(server: FakeDevtoolsServer, monkeypatch: pytest.MonkeyPatch) -> None:
    _with_pages(server, {1: [request_entry(1, GA4_URL, "POST")]})
    server.bodies = {1: "en=a... <truncated>"}
    server.full_bodies = {1: "en=a"}

    def unreadable(self: Path, *args: Any, **kwargs: Any) -> str:
        raise OSError("permission denied")

    monkeypatch.setattr(Path, "read_text", unreadable)

    capture = _capture(server)

    assert capture.requests == [CapturedRequest(url=GA4_URL, body=None)]
    assert len(capture.warnings) == 1
    assert "body file: permission denied" in capture.warnings[0]


def test_cut_off_body_warning_says_why_it_was_not_read_whole(server: FakeDevtoolsServer) -> None:
    _with_pages(server, {1: [request_entry(1, GA4_URL, "POST")]})
    server.bodies = {1: "en=a... <truncated>"}

    capture = _capture(server)

    assert capture.requests == [CapturedRequest(url=GA4_URL, body=None)]
    assert "the server saved no body file" in capture.warnings[0]


def test_cut_off_body_warning_carries_the_server_error(
    server: FakeDevtoolsServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    _with_pages(server, {1: [request_entry(1, GA4_URL, "POST")]})
    server.bodies = {1: "en=a... <truncated>"}
    record = server._record

    def refuse_to_save(name: str, args: dict[str, Any]) -> None:
        record(name, args)
        if "requestFilePath" in args:
            raise ToolError("No post data available")

    monkeypatch.setattr(server, "_record", refuse_to_save)

    capture = _capture(server)

    assert "server: No post data available" in capture.warnings[0]


def test_unreadable_body_keeps_request_and_warns(server: FakeDevtoolsServer) -> None:
    _with_pages(server, {1: [request_entry(1, GA4_URL, "POST")]})
    server.errors = {"get_network_request": "Request not found"}

    capture = _capture(server)

    assert capture.requests == [CapturedRequest(url=GA4_URL, body=None)]
    assert len(capture.warnings) == 1
    assert GA4_URL in capture.warnings[0]


def test_entry_without_url_is_skipped(server: FakeDevtoolsServer) -> None:
    _with_pages(server, {1: [request_entry(1, "")]})

    assert _capture(server).requests == []


def test_repeated_reads_do_not_duplicate_requests(server: FakeDevtoolsServer) -> None:
    _with_pages(server, {1: [request_entry(1, GA4_URL, "POST")]})
    server.bodies = {1: "en=b"}

    capture = _capture(server, reads=2)

    assert capture.requests == [CapturedRequest(url=GA4_URL, body="en=b")]
    assert server.called_tools.count("get_network_request") == 1


def test_later_read_adds_new_requests(server: FakeDevtoolsServer) -> None:
    _with_pages(server, {1: [request_entry(1, GA4_URL)]})
    later = "https://b.com/g/collect?en=later"

    def add_request() -> None:
        server.network[1].append(request_entry(2, later))

    capture = _capture(server, add_request, reads=2)

    assert [request.url for request in capture.requests] == [GA4_URL, later]


def test_same_request_id_in_another_page_is_a_different_request(server: FakeDevtoolsServer) -> None:
    _with_pages(server, {1: [request_entry(1, GA4_URL)], 2: [request_entry(1, "https://b.com/g/collect?en=b")]})

    assert len(_capture(server).requests) == 2


def test_repeated_reads_do_not_repeat_warnings(server: FakeDevtoolsServer) -> None:
    _with_pages(server, {1: [request_entry(1, GA4_URL, "POST")]})
    server.bodies = {1: "<Request body not available anymore>"}

    assert len(_capture(server, reads=2).warnings) == 1


def test_recorded_count_reflects_latest_read(server: FakeDevtoolsServer) -> None:
    _with_pages(server, {1: [request_entry(1, GA4_URL)]})

    def add_request() -> None:
        server.network[1].append(request_entry(2, "https://a.com/x.js"))

    assert _capture(server, add_request, reads=2).recorded_requests == 2


def _read_page(server: FakeDevtoolsServer, since_ms: float = 0) -> tuple[NetworkCapture, list[str]]:
    async def go() -> tuple[NetworkCapture, list[str]]:
        async with Client(server.mcp) as client:
            capture = NetworkCapture(client, _is_pixel)
            return capture, await capture.read_page_urls(since_ms)

    return asyncio.run(go())


def test_reads_page_resource_urls_from_every_page(server: FakeDevtoolsServer) -> None:
    _with_pages(server, {1: [], 2: []})
    server.page_resources = {1: ["https://a.com/1"], 2: ["https://a.com/2"]}

    assert _read_page(server)[1] == ["https://a.com/1", "https://a.com/2"]


def test_page_resources_are_read_from_the_given_time_on(server: FakeDevtoolsServer) -> None:
    _read_page(server, since_ms=1700000000123.5)

    function = server.calls[-1][1]["function"]
    assert "performance.timeOrigin + e.startTime >= 1700000000123.5" in function


def test_failed_page_read_only_warns(server: FakeDevtoolsServer) -> None:
    server.errors = {"evaluate_script": "boom"}

    capture, urls = _read_page(server)

    assert urls == []
    assert capture.error is None
    assert len(capture.warnings) == 1


@pytest.mark.parametrize(
    "message",
    ['Script ran on page and returned:\n```json\n{"type": "object"}\n```', "Script ran on page."],
)
def test_unexpected_page_read_result_only_warns(server: FakeDevtoolsServer, message: str) -> None:
    server.script_result = {"message": message}

    capture, urls = _read_page(server)

    assert urls == []
    assert len(capture.warnings) == 1


def test_page_read_tolerates_failed_page_listing(server: FakeDevtoolsServer) -> None:
    server.errors = {"list_pages": "browser closed"}

    capture, urls = _read_page(server)

    assert urls == []
    assert len(capture.warnings) == 1


def test_failed_listing_sets_error(server: FakeDevtoolsServer) -> None:
    _with_pages(server, {1: []})
    server.errors = {"list_network_requests": "No page found"}

    capture = _capture(server)

    assert capture.requests == []
    assert "No page found" in capture.error


def test_failed_page_listing_sets_error(server: FakeDevtoolsServer) -> None:
    server.errors = {"list_pages": "browser closed"}

    assert "browser closed" in _capture(server).error


def test_connection_failure_sets_error() -> None:
    class BrokenClient:
        async def call_tool(self, *args: Any, **kwargs: Any) -> None:
            raise ConnectionError("connection lost")

    capture = NetworkCapture(BrokenClient(), _is_pixel)
    asyncio.run(capture())

    assert "connection lost" in capture.error
