"""tool-catalog-updater: creates playwright_mcp/tool_catalog.json from the pinned Playwright MCP server.

    tool-catalog-updater

The tools come from the server's tools/list with every capability on. Run it again after changing the pinned
server version: an existing catalog is updated in place.
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
