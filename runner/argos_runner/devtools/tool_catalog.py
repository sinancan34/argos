import json
from pathlib import Path
from typing import Any

CATALOG_PATH = Path(__file__).parents[1] / "data" / "tool_schemas.json"
# The runner fills this param with the selected page when a tool takes it and the action leaves it out.
PAGE_PARAM = "pageId"


class CatalogError(Exception):
    """The tool catalog could not be read; refresh_tool_schemas.py writes it."""


def load_catalog(path: Path = CATALOG_PATH) -> dict[str, Any]:
    """The pinned server name under `server` and each tool's MCP input schema under `tools`."""
    try:
        catalog = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise CatalogError(f"cannot read tool catalog {path}: {exc}") from exc
    if not isinstance(catalog, dict) or not isinstance(catalog.get("tools"), dict):
        raise CatalogError(f"tool catalog {path} has no 'tools' object")
    return catalog


def takes_page(schema: dict[str, Any]) -> bool:
    return PAGE_PARAM in schema.get("properties", {})


def page_tools() -> set[str]:
    """The tools that run on a page."""
    return {name for name, schema in load_catalog()["tools"].items() if takes_page(schema)}
