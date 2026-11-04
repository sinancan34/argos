import json
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

FIXTURES = Path(__file__).parent / "fixtures"
# Raw @playwright/mcp@0.0.84 results recorded on a local page; the client is tested against them.
RECORDED: dict[str, dict[str, Any]] = json.loads((FIXTURES / "playwright_mcp_0.0.84.json").read_text(encoding="utf-8"))

Calls = list[tuple[str, dict[str, Any]]]


def fake_server(answers: dict[str, str], calls: Calls, errors: frozenset[str] = frozenset()) -> FastMCP:
    """An in-memory server with three Playwright MCP tools; each answers with `answers[tool]`.

    A tool named in `errors` reports its answer as an error, as the real server does. Every call is appended to `calls`.
    """
    mcp = FastMCP("fake-playwright-mcp")

    def reply(tool: str, arguments: dict[str, Any]) -> str:
        calls.append((tool, arguments))
        if tool in errors:
            raise ToolError(answers[tool])
        return answers[tool]

    @mcp.tool(name="browser_navigate")
    def navigate(url: str) -> str:
        return reply("browser_navigate", {"url": url})

    @mcp.tool(name="browser_click")
    def click(target: str) -> str:
        return reply("browser_click", {"target": target})

    @mcp.tool(name="browser_mouse_wheel")
    def mouse_wheel(deltaX: float = 0, deltaY: float = 0) -> str:  # noqa: N803 - the MCP param names
        return reply("browser_mouse_wheel", {"deltaX": deltaX, "deltaY": deltaY})

    return mcp


def network_server(
    listings: list[str], bodies: dict[int, str], calls: Calls, failing_targets: frozenset[str] = frozenset()
) -> FastMCP:
    """An in-memory server whose page sends requests over time.

    Each browser_network_requests call answers the next of `listings` and repeats the last one once they run out;
    browser_network_request answers `bodies[index]`. A click on a target in `failing_targets` fails as a missing
    element does. Every call is appended to `calls`.
    """
    mcp = FastMCP("fake-playwright-mcp")
    pending = list(listings)

    @mcp.tool(name="browser_navigate")
    def navigate(url: str) -> str:
        calls.append(("browser_navigate", {"url": url}))
        return RECORDED["navigate"]["text"]

    @mcp.tool(name="browser_click")
    def click(target: str) -> str:
        calls.append(("browser_click", {"target": target}))
        if target in failing_targets:
            raise ToolError(f"### Error\nTimeoutError: waiting for locator('{target}')")
        return RECORDED["click"]["text"]

    @mcp.tool(name="browser_mouse_wheel")
    def mouse_wheel(deltaX: float = 0, deltaY: float = 0) -> str:  # noqa: N803 - the MCP param names
        calls.append(("browser_mouse_wheel", {"deltaX": deltaX, "deltaY": deltaY}))
        return ""

    @mcp.tool(name="browser_network_requests")
    def network_requests(static: bool = False, all: bool = False) -> str:  # noqa: A002 - the MCP param name
        calls.append(("browser_network_requests", {"static": static, "all": all}))
        return pending.pop(0) if len(pending) > 1 else pending[0]

    @mcp.tool(name="browser_network_request")
    def network_request(index: int, part: str | None = None) -> str:
        calls.append(("browser_network_request", {"index": index, "part": part}))
        if index not in bodies:
            raise ToolError(RECORDED["request_body_out_of_range"]["text"])
        return bodies[index]

    return mcp
