import asyncio
from typing import Any

import pytest
from fastmcp import FastMCP
from fastmcp.client.transports import StdioTransport

from argos_agent.playwright_mcp.catalog import InvalidToolCall
from argos_agent.playwright_mcp.client import PlaywrightMCP, ServerError, ToolResult, sections
from tests.conftest import RECORDED, Calls, fake_server

pytestmark = pytest.mark.unit

ANSWERS = {
    "browser_navigate": RECORDED["navigate"]["text"],
    "browser_click": RECORDED["click"]["text"],
    "browser_mouse_wheel": RECORDED["mouse_wheel"]["text"],
}


def call(server: FastMCP, name: str, arguments: dict[str, Any] | None = None) -> ToolResult:
    async def go() -> ToolResult:
        async with PlaywrightMCP(transport=server) as mcp:
            return await mcp.call(name, arguments)

    return asyncio.run(go())


def test_sections_key_each_part_of_a_result_by_its_heading() -> None:
    parts = sections(RECORDED["click"]["text"])

    assert list(parts) == ["Open tabs", "Page", "Snapshot"]
    assert parts["Page"] == '- Page URL: http://127.0.0.1:8000/\n- Page Title: Fixture "page"'
    assert sections("") == {}


def test_a_call_sends_the_tool_name_and_arguments_unchanged() -> None:
    calls: Calls = []

    result = call(fake_server(ANSWERS, calls), "browser_navigate", {"url": "https://www.emlakjet.com/"})

    assert calls == [("browser_navigate", {"url": "https://www.emlakjet.com/"})]
    assert not result.is_error
    assert result.error is None
    assert result.sections["Page"].startswith("- Page URL: ")
    assert result.text == RECORDED["navigate"]["text"]


def test_a_result_without_text_is_a_success_without_sections() -> None:
    result = call(fake_server(ANSWERS, []), "browser_mouse_wheel", {"deltaX": 0, "deltaY": 300})

    assert not result.is_error
    assert result.sections == {}


def test_an_error_the_server_reports_is_returned_with_its_message() -> None:
    answers = {**ANSWERS, "browser_click": RECORDED["click_strict_mode_error"]["text"]}

    result = call(
        fake_server(answers, [], errors=frozenset({"browser_click"})), "browser_click", {"target": "button.dup"}
    )

    assert result.is_error
    assert result.error is not None
    assert "strict mode violation: locator('button.dup') resolved to 2 elements" in result.error


def test_an_error_section_marks_the_result_as_an_error() -> None:
    server = fake_server({**ANSWERS, "browser_click": RECORDED["invalid_params"]["text"]}, [])

    result = call(server, "browser_click", {"target": "#a"})

    assert result.is_error
    assert result.error is not None
    assert result.error.startswith('Invalid arguments for tool "browser_click"')


@pytest.mark.parametrize(
    ("name", "arguments"),
    [
        ("browser_click", {"target": "#a", "no_such_param": 1}),
        ("browser_click", {"target": {"selector": "#a"}}),
        ("browser_no_such_tool", {}),
    ],
)
def test_a_call_the_server_would_reject_is_refused_before_it_is_sent(name: str, arguments: dict[str, Any]) -> None:
    calls: Calls = []

    with pytest.raises(InvalidToolCall):
        call(fake_server(ANSWERS, calls), name, arguments)

    assert calls == []


def test_a_server_that_cannot_start_fails_with_server_error() -> None:
    async def go() -> None:
        async with PlaywrightMCP(transport=StdioTransport("/nonexistent/argos-no-such-command", [])):
            pass

    with pytest.raises(ServerError, match="cannot start"):
        asyncio.run(go())


def test_a_call_outside_the_session_fails_with_server_error() -> None:
    async def go() -> None:
        await PlaywrightMCP(transport=fake_server(ANSWERS, [])).call("browser_navigate", {"url": "about:blank"})

    with pytest.raises(ServerError, match="browser_navigate"):
        asyncio.run(go())
