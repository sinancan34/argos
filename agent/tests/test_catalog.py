import json
from pathlib import Path
from typing import Any

import pytest

from argos_agent.playwright_mcp.catalog import (
    CatalogError,
    InvalidToolCall,
    ToolCatalog,
    callable_schema,
    load_catalog,
)
from argos_agent.playwright_mcp.server import SERVER_PACKAGE

pytestmark = pytest.mark.unit

TOOLS: dict[str, dict[str, Any]] = {
    "browser_click": {
        "type": "object",
        "properties": {"target": {"type": "string"}, "button": {"type": "string", "enum": ["left", "right", "middle"]}},
        "required": ["target"],
        "additionalProperties": False,
    },
    "browser_fill_form": {
        "type": "object",
        "properties": {
            "fields": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"target": {"type": "string"}, "name": {"type": "string"}},
                    "required": ["target", "name"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["fields"],
        "additionalProperties": False,
    },
}


@pytest.fixture
def catalog() -> ToolCatalog:
    return ToolCatalog(server=SERVER_PACKAGE, tools=TOOLS)


def test_a_param_the_server_fills_in_itself_is_not_required() -> None:
    wheel = {
        "type": "object",
        "properties": {"deltaX": {"type": "number", "default": 0}, "deltaY": {"type": "number", "default": 0}},
        "required": ["deltaX", "deltaY"],
        "additionalProperties": False,
    }

    assert callable_schema(wheel) == {**wheel, "required": []}
    assert callable_schema(TOOLS["browser_click"]) == TOOLS["browser_click"]


def test_a_call_the_server_accepts_has_no_problems(catalog: ToolCatalog) -> None:
    assert catalog.problems("browser_click", {"target": 'text="En Yeni"', "button": "left"}) == []
    assert catalog.problems("browser_fill_form", {"fields": [{"target": "#q", "name": "Search"}]}) == []


@pytest.mark.parametrize(
    ("name", "arguments", "problem"),
    [
        ("browser_no_such_tool", {}, "unknown tool 'browser_no_such_tool'"),
        ("browser_click", {"target": "#a", "no_such_param": 1}, "'no_such_param' was unexpected"),
        ("browser_click", {"target": {"selector": "#a"}}, "target: {'selector': '#a'} is not of type 'string'"),
        ("browser_click", {"target": "#a", "button": "primary"}, "button: 'primary' is not one of"),
        ("browser_click", {}, "'target' is a required property"),
        ("browser_fill_form", {"fields": [{"target": "#q", "name": "Q", "no_such_key": "Q"}]}, "fields[0]:"),
    ],
)
def test_a_call_the_server_would_reject_names_its_problem(
    catalog: ToolCatalog, name: str, arguments: dict[str, Any], problem: str
) -> None:
    problems = catalog.problems(name, arguments)

    assert len(problems) == 1
    assert problem in problems[0]


def test_check_raises_with_every_problem(catalog: ToolCatalog) -> None:
    with pytest.raises(InvalidToolCall) as raised:
        catalog.check("browser_click", {"no_such_param": 1})

    assert str(raised.value).startswith("browser_click: ")
    assert str(raised.value).count("; ") == 1


def write(tmp_path: Path, content: Any) -> Path:
    path = tmp_path / "tool_catalog.json"
    path.write_text(content if isinstance(content, str) else json.dumps(content), encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("content", "problem"),
    [
        ("{not json", "cannot read"),
        ([], "has no 'tools' object"),
        ({"server": SERVER_PACKAGE, "tools": []}, "has no 'tools' object"),
        ({"server": "@playwright/mcp@0.0.1", "tools": {}}, "generated for @playwright/mcp@0.0.1"),
        ({"server": SERVER_PACKAGE, "tools": {"x": {"type": 5}}}, "x has an invalid schema"),
    ],
)
def test_an_unusable_catalog_file_fails(tmp_path: Path, content: Any, problem: str) -> None:
    with pytest.raises(CatalogError, match=problem):
        load_catalog(write(tmp_path, content))


def test_a_missing_catalog_file_fails(tmp_path: Path) -> None:
    with pytest.raises(CatalogError, match="cannot read"):
        load_catalog(tmp_path / "missing.json")


def test_the_committed_catalog_holds_every_tool_of_the_pinned_server() -> None:
    committed = load_catalog()

    assert committed.server == SERVER_PACKAGE
    assert len(committed.tools) == 72
    assert committed.problems("browser_mouse_wheel", {}) == []
