"""PlaywrightMCP: calls the tools of the pinned Playwright MCP server by their exact names and params."""

import logging
import re
from collections.abc import Mapping
from contextlib import AsyncExitStack
from dataclasses import dataclass
from types import MappingProxyType, TracebackType
from typing import Any

from fastmcp import Client, FastMCP
from fastmcp.client.logging import LogMessage
from fastmcp.client.transports import ClientTransport
from mcp.types import TextContent

from argos_agent.playwright_mcp.catalog import load_catalog
from argos_agent.playwright_mcp.server import SERVER_PACKAGE, LaunchValue, server_transport

logger = logging.getLogger(__name__)

# Playwright MCP answers in text, each part of a result under its own `### <name>` heading.
HEADING = re.compile(r"^### (.+)$", re.MULTILINE)
ERROR_SECTION = "Error"
# Far above a navigation or a script; a call this slow means the server is stuck.
CLIENT_TIMEOUT_SECONDS = 180


def sections(text: str) -> dict[str, str]:
    """The parts of a result by heading; JSON results escape line breaks, so no value holds a heading."""
    parts = HEADING.split(text)
    return {name.strip(): body.strip() for name, body in zip(parts[1::2], parts[2::2], strict=True)}


@dataclass(frozen=True)
class ToolResult:
    """What a tool answered. A tool that failed, for example on a selector that matches no element, has is_error."""

    is_error: bool
    text: str
    sections: Mapping[str, str]

    @property
    def error(self) -> str | None:
        if not self.is_error:
            return None
        return self.sections.get(ERROR_SECTION) or self.text


class ServerError(RuntimeError):
    """The server could not be started, or it did not answer a call."""


async def _log_server_message(message: LogMessage) -> None:
    logger.debug("%s log: %s", SERVER_PACKAGE, message)


class PlaywrightMCP:
    """A session with the pinned server.

        async with PlaywrightMCP({"--headless": True, "--device": "iPhone 15"}) as mcp:
            result = await mcp.call("browser_navigate", {"url": "https://www.emlakjet.com/"})

    Launch options use the server's own flag names. Every option and call is checked against the tool catalog
    first: an option, tool, param or value the server would reject raises InvalidLaunchOptions or InvalidToolCall
    and never reaches the server.
    """

    def __init__(
        self,
        options: Mapping[str, LaunchValue] | None = None,
        *,
        transport: ClientTransport | FastMCP | None = None,
    ) -> None:
        self._catalog = load_catalog()
        self._catalog.check_options(options or {})
        self._client: Client[Any] = Client(
            transport or server_transport(options), timeout=CLIENT_TIMEOUT_SECONDS, log_handler=_log_server_message
        )
        # Enters the client through a typed API; fastmcp's own __aenter__/__aexit__ are untyped.
        self._session = AsyncExitStack()

    async def __aenter__(self) -> "PlaywrightMCP":
        try:
            await self._session.enter_async_context(self._client)
        except Exception as exc:
            raise ServerError(f"cannot start {SERVER_PACKAGE}: {exc}") from exc
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, traceback: TracebackType | None
    ) -> None:
        await self._session.__aexit__(exc_type, exc, traceback)

    async def call(self, name: str, arguments: Mapping[str, Any] | None = None) -> ToolResult:
        """Calls the tool `name` with `arguments` exactly as given."""
        sent = dict(arguments or {})
        self._catalog.check(name, sent)
        try:
            result = await self._client.call_tool(name, sent, raise_on_error=False)
        except Exception as exc:
            raise ServerError(f"{name}: {SERVER_PACKAGE} did not answer: {exc}") from exc
        text = "\n".join(block.text for block in result.content if isinstance(block, TextContent))
        parts = sections(text)
        return ToolResult(
            is_error=result.is_error or ERROR_SECTION in parts,
            text=text,
            sections=MappingProxyType(parts),
        )
