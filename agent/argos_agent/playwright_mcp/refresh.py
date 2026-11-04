"""Regenerates tool_catalog.json from the pinned Playwright MCP server itself.

    python -m argos_agent.playwright_mcp.refresh

The tools come from the server's tools/list with every capability on.
Run it again after changing the pinned server version.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any

from fastmcp import Client, FastMCP
from fastmcp.client.transports import ClientTransport

from argos_agent.playwright_mcp.catalog import CATALOG_PATH, CatalogError, callable_schema
from argos_agent.playwright_mcp.client import ServerError
from argos_agent.playwright_mcp.server import SERVER_PACKAGE, server_transport

logger = logging.getLogger(__name__)


async def server_tools(transport: ClientTransport | FastMCP | None = None) -> dict[str, dict[str, Any]]:
    """Every tool of the server with its input schema; listing tools does not start the browser."""
    async with Client(transport or server_transport()) as client:
        return {tool.name: tool.inputSchema for tool in await client.list_tools()}


def refresh(path: Path = CATALOG_PATH) -> None:
    """Writes every tool of the pinned server to `path`."""
    try:
        listed = asyncio.run(server_tools())
    except Exception as exc:  # fastmcp raises several types for a server that cannot start or answer
        raise ServerError(f"cannot list the tools of {SERVER_PACKAGE}: {exc}") from exc
    tools = {name: callable_schema(schema) for name, schema in sorted(listed.items())}
    catalog = {"server": SERVER_PACKAGE, "tools": tools}
    path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    logger.info("wrote %d tools of %s to %s", len(tools), SERVER_PACKAGE, path)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
    try:
        refresh()
    except (CatalogError, ServerError, OSError) as exc:
        logger.error("%s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
