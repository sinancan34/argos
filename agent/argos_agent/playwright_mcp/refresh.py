"""Regenerates tool_catalog.json from the pinned server and playwright.dev/mcp.

    python -m argos_agent.playwright_mcp.refresh

Run it again after changing the pinned server version; review what it lists as excluded.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any

from fastmcp import Client, FastMCP
from fastmcp.client.transports import ClientTransport

from argos_agent.playwright_mcp.catalog import CATALOG_PATH, build_catalog
from argos_agent.playwright_mcp.client import ServerError
from argos_agent.playwright_mcp.docs import DOCS_BASE, DocsError, read_documentation
from argos_agent.playwright_mcp.server import LAUNCH_FLAGS, SERVER_PACKAGE, server_transport

logger = logging.getLogger(__name__)


async def server_tools(transport: ClientTransport | FastMCP | None = None) -> dict[str, dict[str, Any]]:
    """Every tool of the server with its input schema; listing tools does not start the browser."""
    async with Client(transport or server_transport()) as client:
        return {tool.name: tool.inputSchema for tool in await client.list_tools()}


def refresh(path: Path = CATALOG_PATH) -> tuple[str, ...]:
    """Writes the catalog to `path` and returns what it left out; fails if a launch flag is not documented."""
    documentation = read_documentation()
    undocumented = [flag for flag in LAUNCH_FLAGS if flag not in documentation.flags]
    if undocumented:
        raise DocsError(f"launch flags not documented at {DOCS_BASE}: {', '.join(undocumented)}")
    try:
        listed = asyncio.run(server_tools())
    except Exception as exc:  # fastmcp raises several types for a server that cannot start or answer
        raise ServerError(f"cannot list the tools of {SERVER_PACKAGE}: {exc}") from exc
    build = build_catalog(listed, documentation.tools)
    catalog = {"server": SERVER_PACKAGE, "docs": DOCS_BASE, "tools": build.tools, "excluded": list(build.excluded)}
    _write_atomically(path, json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    logger.info("wrote %d tools of %s to %s", len(build.tools), SERVER_PACKAGE, path)
    return build.excluded


def _write_atomically(path: Path, text: str) -> None:
    """A write that fails halfway leaves the committed catalog as it was."""
    partial = path.with_name(f".{path.name}.partial")
    try:
        partial.write_text(text, encoding="utf-8")
        partial.replace(path)
    finally:
        partial.unlink(missing_ok=True)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
    try:
        excluded = refresh()
    except (DocsError, ServerError, OSError) as exc:
        logger.error("%s", exc)
        return 1
    for line in excluded:
        logger.info("excluded: %s", line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
