import json
from pathlib import Path
from typing import Any

CATALOG_PATH = Path(__file__).parents[1] / "data" / "tool_schemas.json"


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
