"""Regenerates tool_catalog.json from the pinned Playwright MCP server itself.

    python -m argos_agent.playwright_mcp.refresh

The tools come from the server's tools/list with every capability on, the launch options from its --help.
Run it again after changing the pinned server version.
"""

import asyncio
import json
import logging
import re
import subprocess  # nosec B404
import sys
from pathlib import Path
from typing import Any

from fastmcp import Client, FastMCP
from fastmcp.client.transports import ClientTransport

from argos_agent.playwright_mcp.catalog import CATALOG_PATH, CatalogError, callable_schema
from argos_agent.playwright_mcp.client import ServerError
from argos_agent.playwright_mcp.server import FIXED_OPTIONS, SERVER_COMMAND, SERVER_PACKAGE, server_transport

logger = logging.getLogger(__name__)

HELP_TIMEOUT_SECONDS = 120
# `  --viewport-size <size>   specify ...` or `  --headless   run ...`: an option line of --help.
HELP_OPTION = re.compile(r"^  (?:-\w, )?(--[a-z][a-z0-9-]*)(?: <([^>]+)>)?", re.MULTILINE)
# Not launch options: they print and exit.
HELP_ONLY = frozenset({"--help", "--version"})


async def server_tools(transport: ClientTransport | FastMCP | None = None) -> dict[str, dict[str, Any]]:
    """Every tool of the server with its input schema; listing tools does not start the browser."""
    async with Client(transport or server_transport()) as client:
        return {tool.name: tool.inputSchema for tool in await client.list_tools()}


def server_help() -> str:
    """The pinned server's --help text: a fixed argv, no shell."""
    try:
        return subprocess.run(  # noqa: S603  # nosec B603
            [SERVER_COMMAND, "-y", SERVER_PACKAGE, "--help"],
            capture_output=True,
            text=True,
            timeout=HELP_TIMEOUT_SECONDS,
            check=True,
        ).stdout
    except (OSError, subprocess.SubprocessError) as exc:
        raise ServerError(f"cannot read the options of {SERVER_PACKAGE}: {exc}") from exc


def parse_help(text: str) -> dict[str, dict[str, str | None]]:
    """Each launch option by flag name, with the `<argument>` it takes, or None for a flag that takes none."""
    return {
        flag: {"argument": argument or None} for flag, argument in HELP_OPTION.findall(text) if flag not in HELP_ONLY
    }


def _write_atomically(path: Path, text: str) -> None:
    """A write that fails halfway leaves the committed catalog as it was."""
    partial = path.with_name(f".{path.name}.partial")
    try:
        partial.write_text(text, encoding="utf-8")
        partial.replace(path)
    finally:
        partial.unlink(missing_ok=True)


def refresh(path: Path = CATALOG_PATH) -> None:
    """Writes every tool and launch option of the pinned server to `path`."""
    try:
        listed = asyncio.run(server_tools())
    except Exception as exc:  # fastmcp raises several types for a server that cannot start or answer
        raise ServerError(f"cannot list the tools of {SERVER_PACKAGE}: {exc}") from exc
    options = parse_help(server_help())
    missing = [flag for flag in FIXED_OPTIONS if flag not in options]
    if missing:
        raise CatalogError(f"{SERVER_PACKAGE} does not take the fixed options {', '.join(missing)}")
    tools = {name: callable_schema(schema) for name, schema in sorted(listed.items())}
    catalog = {"server": SERVER_PACKAGE, "tools": tools, "options": dict(sorted(options.items()))}
    _write_atomically(path, json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    logger.info("wrote %d tools and %d launch options of %s to %s", len(tools), len(options), SERVER_PACKAGE, path)


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
