import json
import re
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from argos_agent.runner.network import LISTEN

FIXTURES = Path(__file__).parent / "fixtures"
# Raw @playwright/mcp@0.0.84 results recorded on a local page; the client is tested against them.
RECORDED: dict[str, dict[str, Any]] = json.loads((FIXTURES / "playwright_mcp_0.0.84.json").read_text(encoding="utf-8"))

Calls = list[tuple[str, dict[str, Any]]]
Heard = list[tuple[str, str | None]]
# `return heard.slice(3);`: where a read of the heard requests starts.
SLICE = re.compile(r"slice\((\d+)\)")


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


def network_server(heard: list[Heard], calls: Calls, failing_targets: frozenset[str] = frozenset()) -> FastMCP:
    """An in-memory server whose browser sends requests over time.

    Each read of the heard requests answers the next of `heard`, from where the read starts, and repeats the last
    one once they run out; a read before the listener started fails as the pinned server's does. A click on a target
    in `failing_targets` fails as a missing element does. Every call is appended to `calls`.
    """
    mcp = FastMCP("fake-playwright-mcp")
    pending = list(heard)
    listening: list[bool] = []

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

    @mcp.tool(name="browser_run_code_unsafe")
    def run_code(code: str) -> str:
        if code == LISTEN:
            calls.append(("listen", {}))
            listening.append(True)
            return RECORDED["run_code_listen"]["text"]
        if not listening:
            raise ToolError(RECORDED["run_code_not_listening"]["text"])
        found = SLICE.search(code)
        assert found, code
        start = int(found.group(1))
        calls.append(("heard", {"start": start}))
        requests = pending.pop(0) if len(pending) > 1 else pending[0]
        return "### Result\n" + json.dumps([{"url": url, "body": body} for url, body in requests[start:]])

    return mcp
