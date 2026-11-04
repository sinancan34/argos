"""Every tool of the pinned Playwright MCP server, as the server itself publishes them.

Tools and their input schemas come from the server's tools/list; argos-tool-catalog-updater writes them into
data/tool_catalog.json.
A call the server would reject is refused before it is sent.
"""

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError

from argos_agent.playwright_mcp.server import SERVER_PACKAGE

CATALOG_PATH = Path(__file__).parents[1] / "data" / "tool_catalog.json"
REFRESH_COMMAND = "argos-tool-catalog-updater"

Schema = dict[str, Any]


class CatalogError(Exception):
    """The tool catalog could not be read or written; REFRESH_COMMAND writes it."""


class InvalidToolCall(ValueError):
    """A call to a tool the server does not have, or with params or values it would reject."""


def callable_schema(schema: Schema) -> Schema:
    """The server's input schema as the server applies it: a param it fills in with a default may be left out."""
    properties: dict[str, Schema] = schema.get("properties", {})
    required = [name for name in schema.get("required", []) if "default" not in properties.get(name, {})]
    return {**schema, "required": required}


def describe(error: ValidationError) -> str:
    """`fields[0]: 'x' is not of type 'string'`; a problem with the arguments as a whole has no path."""
    path = "".join(f"[{part}]" if isinstance(part, int) else f".{part}" for part in error.absolute_path).lstrip(".")
    return f"{path}: {error.message}" if path else error.message


def schema_problems(schema: Schema, content: Any) -> list[str]:
    """Every way `content` differs from `schema`, in path order."""
    errors = Draft202012Validator(schema).iter_errors(content)
    return [describe(error) for error in sorted(errors, key=lambda error: error.json_path)]


@dataclass(frozen=True)
class ToolCatalog:
    tools: Mapping[str, Schema]

    def problems(self, name: str, arguments: Mapping[str, Any]) -> list[str]:
        """Every way the call differs from what the server takes: the tool, its params, types and values."""
        schema = self.tools.get(name)
        if schema is None:
            return [f"unknown tool '{name}': {SERVER_PACKAGE} has no such tool"]
        return schema_problems(schema, arguments)

    def check(self, name: str, arguments: Mapping[str, Any]) -> None:
        problems = self.problems(name, arguments)
        if problems:
            raise InvalidToolCall(f"{name}: {'; '.join(problems)}")


def load_catalog(path: Path = CATALOG_PATH) -> ToolCatalog:
    """The committed catalog; it must be generated for the pinned server and hold valid schemas."""
    try:
        content = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise CatalogError(f"cannot read tool catalog {path}: {exc}") from exc
    if not isinstance(content, dict) or not isinstance(content.get("tools"), dict):
        raise CatalogError(f"tool catalog {path} has no 'tools' object")
    if content.get("server") != SERVER_PACKAGE:
        raise CatalogError(
            f"tool catalog {path} was generated for {content.get('server')}, but {SERVER_PACKAGE} is pinned; "
            f"run {REFRESH_COMMAND}"
        )
    for name, schema in content["tools"].items():
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as exc:
            raise CatalogError(f"tool catalog {path}: {name} has an invalid schema: {exc.message}") from exc
    return ToolCatalog(tools=MappingProxyType(content["tools"]))
