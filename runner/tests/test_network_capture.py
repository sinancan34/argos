import asyncio
from typing import Any

import pytest
from fastmcp import Client

from network_capture import CapturedRequest, NetworkCapture
from tests.conftest import FakeNodriverServer, request_entry

pytestmark = pytest.mark.integration

GA4_URL = "https://analytics.google.com/g/collect?en=a"


def _is_pixel(url: str) -> bool:
    return "/g/collect" in url


def _capture(server: FakeNodriverServer) -> NetworkCapture:
    async def go() -> NetworkCapture:
        async with Client(server.mcp) as client:
            capture = NetworkCapture(client, _is_pixel)
            await capture()
            return capture

    return asyncio.run(go())


def test_reads_wanted_requests_from_every_tab(server: FakeNodriverServer) -> None:
    server.network = {
        "TAB-1": [request_entry("1", GA4_URL), request_entry("2", "https://a.com/x.js")],
        "TAB-2": [request_entry("3", "https://b.com/g/collect?en=b")],
    }

    capture = _capture(server)

    assert capture.requests == [
        CapturedRequest(url=GA4_URL, body=None),
        CapturedRequest(url="https://b.com/g/collect?en=b", body=None),
    ]
    assert capture.warnings == []
    assert capture.error is None


def test_counts_all_recorded_requests_across_tabs(server: FakeNodriverServer) -> None:
    server.network = {
        "TAB-1": [request_entry("1", GA4_URL), request_entry("2", "https://a.com/x.js")],
        "TAB-2": [request_entry("3", "https://b.com/y.js")],
    }

    assert _capture(server).recorded_requests == 3


def test_requests_full_urls_without_the_default_limit(server: FakeNodriverServer) -> None:
    server.network = {"TAB-1": [request_entry("1", GA4_URL)]}

    _capture(server)

    call = next(args for name, args in server.calls if name == "list_network_requests")
    assert call["url_max_length"] is None
    assert call["limit"] >= 5000


def test_reads_post_body(server: FakeNodriverServer) -> None:
    server.network = {"TAB-1": [request_entry("1", GA4_URL, has_post=True)]}
    server.post_data = {"1": {"postData": "en=b", "base64Encoded": False}}

    assert _capture(server).requests == [CapturedRequest(url=GA4_URL, body="en=b")]


def test_does_not_fetch_body_of_unwanted_request(server: FakeNodriverServer) -> None:
    server.network = {"TAB-1": [request_entry("1", "https://a.com/x", has_post=True)]}

    capture = _capture(server)

    assert capture.requests == []
    assert "get_network_request" not in server.called_tools


def test_base64_body_is_not_used(server: FakeNodriverServer) -> None:
    server.network = {"TAB-1": [request_entry("1", GA4_URL, has_post=True)]}
    server.post_data = {"1": {"postData": "H4sI", "base64Encoded": True}}

    assert _capture(server).requests == [CapturedRequest(url=GA4_URL, body=None)]


def test_unreadable_body_keeps_request_and_warns(server: FakeNodriverServer) -> None:
    server.network = {"TAB-1": [request_entry("1", GA4_URL, has_post=True)]}

    capture = _capture(server)

    assert capture.requests == [CapturedRequest(url=GA4_URL, body=None)]
    assert len(capture.warnings) == 1
    assert GA4_URL in capture.warnings[0]


def test_dropped_records_produce_a_warning(server: FakeNodriverServer) -> None:
    server.network = {"TAB-1": []}
    server.dropped = 7

    capture = _capture(server)

    assert len(capture.warnings) == 1
    assert "7" in capture.warnings[0]


def test_entry_without_url_is_skipped(server: FakeNodriverServer) -> None:
    server.network = {"TAB-1": [request_entry("1", None)]}

    assert _capture(server).requests == []


def _capture_twice(server: FakeNodriverServer, between: Any = None) -> NetworkCapture:
    async def go() -> NetworkCapture:
        async with Client(server.mcp) as client:
            capture = NetworkCapture(client, _is_pixel)
            await capture()
            if between:
                between()
            await capture()
            return capture

    return asyncio.run(go())


def test_repeated_reads_do_not_duplicate_requests(server: FakeNodriverServer) -> None:
    server.network = {"TAB-1": [request_entry("1", GA4_URL, has_post=True)]}
    server.post_data = {"1": {"postData": "en=b", "base64Encoded": False}}

    capture = _capture_twice(server)

    assert capture.requests == [CapturedRequest(url=GA4_URL, body="en=b")]
    assert server.called_tools.count("get_network_request") == 1


def test_later_read_adds_new_requests(server: FakeNodriverServer) -> None:
    server.network = {"TAB-1": [request_entry("1", GA4_URL)]}
    later = "https://b.com/g/collect?en=later"

    def add_request() -> None:
        server.network["TAB-1"].append(request_entry("2", later))

    capture = _capture_twice(server, add_request)

    assert [request.url for request in capture.requests] == [GA4_URL, later]


def test_same_request_id_in_another_tab_is_a_different_request(server: FakeNodriverServer) -> None:
    server.network = {
        "TAB-1": [request_entry("1", GA4_URL)],
        "TAB-2": [request_entry("1", "https://b.com/g/collect?en=b")],
    }

    assert len(_capture(server).requests) == 2


def test_repeated_reads_do_not_repeat_warnings(server: FakeNodriverServer) -> None:
    server.network = {"TAB-1": [request_entry("1", GA4_URL, has_post=True)]}
    server.dropped = 3

    assert len(_capture_twice(server).warnings) == 2


def test_recorded_count_reflects_latest_read(server: FakeNodriverServer) -> None:
    server.network = {"TAB-1": [request_entry("1", GA4_URL)]}

    def add_request() -> None:
        server.network["TAB-1"].append(request_entry("2", "https://a.com/x.js"))

    assert _capture_twice(server, add_request).recorded_requests == 2


def _read_page(server: FakeNodriverServer) -> NetworkCapture:
    async def go() -> NetworkCapture:
        async with Client(server.mcp) as client:
            capture = NetworkCapture(client, _is_pixel)
            await capture()
            await capture.read_page_urls()
            return capture

    return asyncio.run(go())


def test_reads_page_resource_urls_from_every_tab(server: FakeNodriverServer) -> None:
    server.network = {"TAB-1": [], "TAB-2": []}
    server.page_resources = {"TAB-1": ["https://a.com/1"], "TAB-2": ["https://a.com/2"]}

    assert _read_page(server).page_urls == ["https://a.com/1", "https://a.com/2"]


def test_failed_page_read_only_warns(server: FakeNodriverServer) -> None:
    server.network = {"TAB-1": []}
    server.evaluate_response = {"status": "fail", "data": {"expression": "boom"}}

    capture = _read_page(server)

    assert capture.page_urls == []
    assert capture.error is None
    assert len(capture.warnings) == 1


def test_unexpected_page_read_result_only_warns(server: FakeNodriverServer) -> None:
    server.network = {"TAB-1": []}
    server.evaluate_response = {"status": "success", "data": {"result": {"type": "object"}}}

    capture = _read_page(server)

    assert capture.page_urls == []
    assert len(capture.warnings) == 1


def test_malformed_page_read_result_only_warns(server: FakeNodriverServer) -> None:
    server.network = {"TAB-1": []}
    server.evaluate_response = {"status": "success", "data": {"result": "not json"}}

    capture = _read_page(server)

    assert capture.page_urls == []
    assert len(capture.warnings) == 1


def test_page_read_tolerates_failed_tab_listing(server: FakeNodriverServer) -> None:
    server.network = {"TAB-1": []}

    async def go() -> NetworkCapture:
        async with Client(server.mcp) as client:
            capture = NetworkCapture(client, _is_pixel)
            server.tabs_response = {"status": "fail", "data": {"browser": "gone"}}
            await capture.read_page_urls()
            return capture

    capture = asyncio.run(go())

    assert capture.page_urls == []
    assert len(capture.warnings) == 1


def test_failed_listing_sets_error(server: FakeNodriverServer) -> None:
    server.network = {"TAB-1": []}
    server.list_response = {"status": "fail", "data": {"network": "capture is off"}}

    capture = _capture(server)

    assert capture.requests == []
    assert "capture is off" in capture.error


def test_failed_tab_listing_sets_error(server: FakeNodriverServer) -> None:
    server.tabs_response = {"status": "fail", "data": {"browser": "not running"}}

    assert "not running" in _capture(server).error


def test_connection_failure_sets_error() -> None:
    class BrokenClient:
        async def call_tool(self, *args: Any, **kwargs: Any) -> None:
            raise ConnectionError("connection lost")

    capture = NetworkCapture(BrokenClient(), _is_pixel)
    asyncio.run(capture())

    assert "connection lost" in capture.error
