import asyncio
import functools
import re
import threading
from collections.abc import Iterator
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

import pytest

from argos_agent.playwright_mcp.catalog import callable_schema, load_catalog
from argos_agent.playwright_mcp.client import PlaywrightMCP, ToolResult
from argos_agent.playwright_mcp.refresh import parse_help, server_help, server_tools
from tests.conftest import FIXTURES

pytestmark = pytest.mark.integration

# `- button "Buy" [ref=e2]`: a node of browser_snapshot.
BUY_REF = re.compile(r'button "Buy" \[ref=([^\]]+)\]')


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - the stdlib signature
        """Keeps request lines off the test output."""


@pytest.fixture(scope="module")
def site() -> Iterator[str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(FIXTURES)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}/page.html"
    server.shutdown()


def run(site: str, *calls: tuple[str, dict[str, Any]]) -> list[ToolResult]:
    """Opens the fixture page in the pinned server, then makes each call in order."""

    async def go() -> list[ToolResult]:
        async with PlaywrightMCP({"--headless": True}) as mcp:
            opened = await mcp.call("browser_navigate", {"url": site})
            return [opened, *[await mcp.call(name, arguments) for name, arguments in calls]]

    return asyncio.run(go())


def test_calls_run_on_the_pinned_server(site: str) -> None:
    opened, clicked, ambiguous, scrolled, requests, title = run(
        site,
        ("browser_click", {"target": 'text="Buy"'}),
        ("browser_click", {"target": "button.dup"}),
        ("browser_mouse_wheel", {"deltaX": 0, "deltaY": 300}),
        ("browser_network_requests", {"static": True}),
        ("browser_evaluate", {"function": "() => document.title"}),
    )

    assert not opened.is_error and "Page" in opened.sections
    assert not clicked.is_error
    assert ambiguous.is_error and ambiguous.error and "strict mode violation" in ambiguous.error
    assert not scrolled.is_error
    assert "/collect?en=page_view" in requests.sections["Result"]
    assert title.sections["Result"] == '"clicked:Buy"'


def test_a_generated_locator_works_as_a_target(site: str) -> None:
    async def go() -> tuple[ToolResult, ToolResult]:
        async with PlaywrightMCP({"--headless": True}) as mcp:
            await mcp.call("browser_navigate", {"url": site})
            snapshot = await mcp.call("browser_snapshot", {})
            match = BUY_REF.search(snapshot.sections["Snapshot"])
            assert match, snapshot.text
            locator = await mcp.call("browser_generate_locator", {"target": match.group(1)})
            return locator, await mcp.call("browser_click", {"target": locator.sections["Result"]})

    locator, clicked = asyncio.run(go())

    assert locator.sections["Result"] == "getByRole('button', { name: 'Buy' })"
    assert not clicked.is_error


def test_the_catalog_is_every_tool_and_option_of_the_pinned_server() -> None:
    committed = load_catalog()

    assert committed.tools == {name: callable_schema(schema) for name, schema in asyncio.run(server_tools()).items()}
    assert committed.options == parse_help(server_help())
