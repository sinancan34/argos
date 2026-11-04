import asyncio
from collections.abc import Awaitable, Callable

import pytest

from argos_agent.playwright_mcp.client import PlaywrightMCP
from argos_agent.runner.network import Listed, NetworkError, list_requests, parse_requests, request_body
from tests.conftest import RECORDED, Calls, network_server

pytestmark = pytest.mark.unit

LISTING = RECORDED["network_requests"]["text"]


def against[T](listings: list[str], bodies: dict[int, str], go: Callable[[PlaywrightMCP], Awaitable[T]]) -> T:
    calls: Calls = []

    async def session() -> T:
        async with PlaywrightMCP(transport=network_server(listings, bodies, calls)) as mcp:
            return await go(mcp)

    return asyncio.run(session())


def test_parse_requests_reads_each_line_of_the_recorded_listing() -> None:
    assert parse_requests(LISTING) == [
        Listed(1, "GET", "http://127.0.0.1:8000/"),
        Listed(2, "POST", "http://127.0.0.1:8000/collect?v=2&en=page_view"),
        Listed(3, "POST", "http://127.0.0.1:8000/collect?v=2&en=empty"),
        Listed(4, "GET", "http://127.0.0.1:8000/pixel.gif?id=GTM-X"),
    ]


def test_parse_requests_of_a_page_that_sent_nothing() -> None:
    assert parse_requests("") == []


def test_list_requests_asks_for_static_resources_of_the_whole_session() -> None:
    calls: Calls = []

    async def go() -> list[Listed]:
        async with PlaywrightMCP(transport=network_server([LISTING], {}, calls)) as mcp:
            return await list_requests(mcp)

    assert len(asyncio.run(go())) == 4
    assert calls == [("browser_network_requests", {"static": True, "all": True})]


def test_request_body_is_the_result_text() -> None:
    body = against([LISTING], {2: RECORDED["request_body_beacon"]["text"]}, lambda mcp: request_body(mcp, 2))

    assert body == "en=scroll&epn.percent_scrolled=90\nen=user_engagement"


def test_an_empty_body_is_an_empty_string() -> None:
    assert against([LISTING], {1: ""}, lambda mcp: request_body(mcp, 1)) == ""


def test_a_body_the_server_cannot_find_is_a_network_error() -> None:
    with pytest.raises(NetworkError, match=r"^browser_network_request #9: Request #\d+ not found"):
        against([LISTING], {}, lambda mcp: request_body(mcp, 9))
