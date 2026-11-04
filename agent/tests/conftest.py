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
    def mouse_wheel(deltaX: float, deltaY: float) -> str:  # noqa: N803 - the MCP param names
        return reply("browser_mouse_wheel", {"deltaX": deltaX, "deltaY": deltaY})

    return mcp
