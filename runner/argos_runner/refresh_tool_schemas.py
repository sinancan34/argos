import asyncio
import json
import sys
from typing import Any

from fastmcp import Client

from argos_runner.devtools.tool_catalog import CATALOG_PATH
from argos_runner.run import SERVER_PACKAGE, server_transport


async def _tools() -> dict[str, dict[str, Any]]:
    # Listing tools does not launch the browser.
    async with Client(server_transport()) as client:
        return {tool.name: tool.inputSchema for tool in await client.list_tools()}


def main() -> int:
    """Writes the catalog of the pinned Playwright MCP tools, every capability on, that scenarios are validated against.

    Run it again after changing the pinned server version.
    """
    catalog = {"server": SERVER_PACKAGE, "tools": dict(sorted(asyncio.run(_tools()).items()))}
    CATALOG_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sys.stdout.write(f"wrote {len(catalog['tools'])} tools of {SERVER_PACKAGE} to {CATALOG_PATH}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
