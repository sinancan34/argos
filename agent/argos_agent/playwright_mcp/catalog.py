"""Every tool and launch option of the pinned Playwright MCP server, as the server itself publishes them.

Tools and their input schemas come from the server's tools/list, launch options from its --help; refresh.py writes
both into tool_catalog.json. A call or option the server would reject is refused before it is sent.
"""

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError

from argos_agent.playwright_mcp.server import SERVER_PACKAGE, LaunchValue

CATALOG_PATH = Path(__file__).with_name("tool_catalog.json")
REFRESH_COMMAND = "python -m argos_agent.playwright_mcp.refresh"
# `<path...>`: an option that takes one or more values.
VARIADIC = "..."

Schema = dict[str, Any]


class CatalogError(Exception):
    """The tool catalog could not be read or written; REFRESH_COMMAND writes it."""


class InvalidToolCall(ValueError):
    """A call to a tool the server does not have, or with params or values it would reject."""

    def __init__(self, name: str, problems: list[str]) -> None:
        super().__init__(f"{name}: {'; '.join(problems)}")
        self.name = name
        self.problems = tuple(problems)


class InvalidLaunchOptions(ValueError):
    """Launch options the server does not take, or values it would reject."""

    def __init__(self, problems: list[str]) -> None:
        super().__init__("; ".join(problems))
        self.problems = tuple(problems)


def callable_schema(schema: Schema) -> Schema:
    """The server's input schema as the server applies it: a param it fills in with a default may be left out."""
    properties: dict[str, Schema] = schema.get("properties", {})
    required = [name for name in schema.get("required", []) if "default" not in properties.get(name, {})]
    return {**schema, "required": required}


def describe(error: ValidationError) -> str:
    """`fields[0]: 'x' is not of type 'string'`; a problem with the arguments as a whole has no path."""
    path = "".join(f"[{part}]" if isinstance(part, int) else f".{part}" for part in error.absolute_path).lstrip(".")
    return f"{path}: {error.message}" if path else error.message


def _option_problem(flag: str, value: Any, argument: str | None) -> str | None:
    if argument is None:
        return None if isinstance(value, bool) else f"{flag}: takes true or false, got {value!r}"
    if argument.endswith(VARIADIC):
        values_ok = isinstance(value, list | tuple) and bool(value) and all(isinstance(v, str) and v for v in value)
        return None if values_ok else f"{flag}: takes a list of <{argument}> strings, got {value!r}"
    return None if isinstance(value, str) and value else f"{flag}: takes a <{argument}> string, got {value!r}"


@dataclass(frozen=True)
class ToolCatalog:
    server: str
    tools: Mapping[str, Schema]
    # Each launch option by flag name, with the `<argument>` it takes or None for a flag that takes none.
    options: Mapping[str, Mapping[str, str | None]]

    def problems(self, name: str, arguments: Mapping[str, Any]) -> list[str]:
        """Every way the call differs from what the server takes: the tool, its params, types and values."""
        schema = self.tools.get(name)
        if schema is None:
            return [f"unknown tool '{name}': {self.server} has no such tool"]
        errors = Draft202012Validator(schema).iter_errors(arguments)
        return [describe(error) for error in sorted(errors, key=lambda error: error.json_path)]

    def check(self, name: str, arguments: Mapping[str, Any]) -> None:
        problems = self.problems(name, arguments)
        if problems:
            raise InvalidToolCall(name, problems)

    def option_problems(self, options: Mapping[str, LaunchValue]) -> list[str]:
        """Every option the server does not take, or whose value does not fit what its flag takes."""
        problems = [
            (
                f"unknown option '{flag}': {self.server} has no such option"
                if flag not in self.options
                else _option_problem(flag, value, self.options[flag].get("argument"))
            )
            for flag, value in options.items()
        ]
        return [problem for problem in problems if problem]

    def check_options(self, options: Mapping[str, LaunchValue]) -> None:
        problems = self.option_problems(options)
        if problems:
            raise InvalidLaunchOptions(problems)


def load_catalog(path: Path = CATALOG_PATH) -> ToolCatalog:
    """The committed catalog; it must be generated for the pinned server and hold valid schemas."""
    try:
        content = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise CatalogError(f"cannot read tool catalog {path}: {exc}") from exc
    if not isinstance(content, dict) or not all(isinstance(content.get(key), dict) for key in ("tools", "options")):
        raise CatalogError(f"tool catalog {path} has no 'tools' and 'options' objects")
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
    return ToolCatalog(
        server=SERVER_PACKAGE, tools=MappingProxyType(content["tools"]), options=MappingProxyType(content["options"])
    )
