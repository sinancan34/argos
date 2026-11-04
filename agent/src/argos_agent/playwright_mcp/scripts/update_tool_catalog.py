"""Creates src/argos_agent/playwright_mcp/tool_catalog.json from the pinned Playwright MCP server.

    python -m argos_agent.playwright_mcp.scripts.update_tool_catalog

The tools come from the server's tools/list with every capability on. Run it again after changing the pinned
server version: an existing catalog is updated in place. A maintainer script, not an installed command:
the catalog is committed and shipped, and it changes only with the pin in code.
"""

import logging
import sys

from argos_agent.playwright_mcp.catalog import CatalogError, write_catalog

logger = logging.getLogger(__name__)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
    try:
        write_catalog()
    except (CatalogError, OSError) as exc:
        logger.error("%s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
