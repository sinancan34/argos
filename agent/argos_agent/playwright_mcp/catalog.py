"""The tools the agent layer may call: the pinned server's tools, cut down to what playwright.dev/mcp documents.

A tool keeps the server's own name and input schema, minus every param the docs do not name, and accepts no other.
"""

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError

from argos_agent.playwright_mcp.docs import DocumentedParam
from argos_agent.playwright_mcp.server import SERVER_PACKAGE

CATALOG_PATH = Path(__file__).with_name("tool_catalog.json")
REFRESH_COMMAND = "python -m argos_agent.playwright_mcp.refresh"

Schema = dict[str, Any]


class CatalogError(Exception):
    """The tool catalog file could not be used; REFRESH_COMMAND writes it."""


class InvalidToolCall(ValueError):
    """A call to a tool or with a param that playwright.dev/mcp does not document, or with an invalid value."""

    def __init__(self, name: str, problems: list[str]) -> None:
        super().__init__(f"{name}: {'; '.join(problems)}")
        self.name = name
        self.problems = tuple(problems)


@dataclass(frozen=True)
class CatalogBuild:
    tools: dict[str, Schema]
    # What the server has and the docs do not name, or the other way round, one line each.
    excluded: tuple[str, ...]


def _undocumented(where: str, name: str, prop: Schema, required: list[str]) -> str:
    if name in required and "default" not in prop:
        return f"{where}.{name}: required by the server but not documented, so every call fails"
    return f"{where}.{name}: not documented"


def _required(kept: Mapping[str, Schema], documented: Mapping[str, bool | None], server: list[str]) -> list[str]:
    """Documented as required, or required by the server with no default; the server fills in a default itself."""
    by_docs = {name for name, required in documented.items() if required and name in kept}
    by_server = {name for name in server if name in kept and "default" not in kept[name]}
    return sorted(by_docs | by_server)


def _closed(schema: Schema, properties: dict[str, Schema], required: list[str]) -> Schema:
    return {**schema, "properties": properties, "required": required, "additionalProperties": False}


def _property(where: str, prop: Schema, param: DocumentedParam) -> tuple[Schema, list[str]]:
    """The param's schema; for an object[] param whose item keys are documented, only those keys."""
    items = prop.get("items")
    if not param.fields or not isinstance(items, dict) or "properties" not in items:
        return prop, []
    server_keys: dict[str, Schema] = items["properties"]
    server_required: list[str] = items.get("required", [])
    kept = {key: schema for key, schema in server_keys.items() if key in param.fields}
    notes = [
        *(
            _undocumented(f"{where}[]", key, server_keys[key], server_required)
            for key in server_keys
            if key not in kept
        ),
        *(
            f"{where}[].{key}: documented, but the server has no such key"
            for key in param.fields
            if key not in server_keys
        ),
    ]
    return {**prop, "items": _closed(items, kept, _required(kept, param.fields, server_required))}, notes


def _tool(tool: str, schema: Schema, params: Mapping[str, DocumentedParam]) -> tuple[Schema, list[str]]:
    server_props: dict[str, Schema] = schema.get("properties", {})
    server_required: list[str] = schema.get("required", [])
    built = {
        name: _property(f"{tool}.{name}", prop, params[name]) for name, prop in server_props.items() if name in params
    }
    kept = {name: prop for name, (prop, _) in built.items()}
    notes = [
        *(
            _undocumented(tool, name, prop, server_required)
            for name, prop in server_props.items()
            if name not in params
        ),
        *(
            f"{tool}.{name}: documented, but the server has no such param"
            for name in params
            if name not in server_props
        ),
        *(note for _, item_notes in built.values() for note in item_notes),
    ]
    documented_required = {name: param.required for name, param in params.items()}
    return _closed(schema, kept, _required(kept, documented_required, server_required)), notes


def build_catalog(
    server_tools: Mapping[str, Schema], documented: Mapping[str, Mapping[str, DocumentedParam]]
) -> CatalogBuild:
    """The documented tools the server has, each with only its documented params, and a note for all left out."""
    built = {
        tool: _tool(tool, server_tools[tool], params)
        for tool, params in sorted(documented.items())
        if tool in server_tools
    }
    excluded = [
        *(
            note
            for tool in sorted(documented)
            for note in (built[tool][1] if tool in built else [f"{tool}: documented, but the server has no such tool"])
        ),
        *(f"{tool}: not documented" for tool in sorted(set(server_tools) - set(documented))),
    ]
    return CatalogBuild(tools={tool: schema for tool, (schema, _) in built.items()}, excluded=tuple(excluded))


def _describe(error: ValidationError) -> str:
    """`fields[0]: 'x' is not of type 'string'`; a problem with the arguments as a whole has no path."""
    path = "".join(f"[{part}]" if isinstance(part, int) else f".{part}" for part in error.absolute_path).lstrip(".")
    return f"{path}: {error.message}" if path else error.message


@dataclass(frozen=True)
class ToolCatalog:
    server: str
    tools: Mapping[str, Schema]

    def problems(self, name: str, arguments: Mapping[str, Any]) -> list[str]:
        """Every way the call differs from the documented tool: its name, params, types and values."""
        schema = self.tools.get(name)
        if schema is None:
            return [f"unknown tool '{name}': playwright.dev/mcp documents no such tool"]
        errors = Draft202012Validator(schema).iter_errors(arguments)
        return [_describe(error) for error in sorted(errors, key=lambda error: error.json_path)]

    def check(self, name: str, arguments: Mapping[str, Any]) -> None:
        problems = self.problems(name, arguments)
        if problems:
            raise InvalidToolCall(name, problems)


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
    return ToolCatalog(server=SERVER_PACKAGE, tools=MappingProxyType(content["tools"]))
