import asyncio
from collections.abc import Awaitable, Callable

import pytest
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from argos_agent.playwright_mcp.client import PlaywrightMCP
from argos_agent.runner.network import LISTEN, Captured, NetworkError, requests_since, start_listening
from tests.conftest import RECORDED

pytestmark = pytest.mark.unit

SHOP_BATCH = "en=page_view&ep.content_group=shop\nen=view_item_list&pr1=id42~lishop%2Flist~lp1"


def recorded_server(answer: str, codes: list[str], is_error: bool = False) -> FastMCP:
    """A server whose run-code tool answers `answer` as the pinned server did; every code sent goes to `codes`."""
    mcp = FastMCP("fake-playwright-mcp")

    @mcp.tool(name="browser_run_code_unsafe")
    def run_code(code: str) -> str:
        codes.append(code)
        if is_error:
            raise ToolError(answer)
        return answer

    return mcp


def against[T](answer: str, go: Callable[[PlaywrightMCP], Awaitable[T]], is_error: bool = False) -> tuple[T, list[str]]:
    codes: list[str] = []

    async def session() -> T:
        async with PlaywrightMCP(transport=recorded_server(answer, codes, is_error)) as mcp:
            return await go(mcp)

    return asyncio.run(session()), codes


def test_start_listening_sends_the_listener_code() -> None:
    _, codes = against(RECORDED["run_code_listen"]["text"], start_listening)

    assert codes == [LISTEN]


def test_a_listener_the_server_cannot_start_is_a_network_error() -> None:
    with pytest.raises(NetworkError, match="cannot start the request listener"):
        against("### Error\nError: boom", start_listening, is_error=True)


def test_requests_since_reads_the_recorded_requests_with_their_bodies() -> None:
    heard, codes = against(RECORDED["run_code_heard"]["text"], lambda mcp: requests_since(mcp, 0))

    assert heard == [
        Captured("http://127.0.0.1:8000/shop.html", None),
        Captured("http://127.0.0.1:8000/g/collect?v=2&tid=G-1", SHOP_BATCH),
    ]
    assert codes == [RECORDED["run_code_heard"]["params"]["code"]]


def test_requests_since_asks_only_for_the_requests_after_start() -> None:
    heard, codes = against(RECORDED["run_code_heard_since_1"]["text"], lambda mcp: requests_since(mcp, 1))

    assert heard == [Captured("http://127.0.0.1:8000/g/collect?v=2&tid=G-1", SHOP_BATCH)]
    assert codes == [RECORDED["run_code_heard_since_1"]["params"]["code"]]


def test_nothing_heard_is_an_empty_list() -> None:
    assert against(RECORDED["run_code_heard_nothing"]["text"], lambda mcp: requests_since(mcp, 0))[0] == []


def test_reading_before_the_listener_started_is_a_network_error() -> None:
    with pytest.raises(NetworkError, match="the request listener was not started"):
        against(RECORDED["run_code_not_listening"]["text"], lambda mcp: requests_since(mcp, 0), is_error=True)


@pytest.mark.parametrize(
    ("answer", "problem"),
    [
        ("### Result\nundefined", "not JSON"),
        ('### Result\n{"url": "x"}', "unexpected heard requests at \\$"),
        ('### Result\n[{"url": "x"}]', "unexpected heard requests at \\$\\[0\\]"),
        ('### Result\n[{"url": 1, "body": null}]', "unexpected heard requests at \\$\\[0\\].url"),
    ],
)
def test_heard_requests_of_an_unexpected_shape_are_a_network_error(answer: str, problem: str) -> None:
    with pytest.raises(NetworkError, match=problem):
        against(answer, lambda mcp: requests_since(mcp, 0))
