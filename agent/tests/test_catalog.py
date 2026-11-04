import json
from pathlib import Path
from typing import Any

import pytest

from argos_agent.playwright_mcp.catalog import (
    CatalogError,
    InvalidToolCall,
    ToolCatalog,
    build_catalog,
    load_catalog,
)
from argos_agent.playwright_mcp.docs import DocumentedParam
from argos_agent.playwright_mcp.server import SERVER_PACKAGE

pytestmark = pytest.mark.unit

SERVER_TOOLS: dict[str, dict[str, Any]] = {
    "browser_click": {
        "type": "object",
        "properties": {
            "element": {"type": "string"},
            "target": {"type": "string"},
            "button": {"type": "string", "enum": ["left", "right", "middle"]},
        },
        "required": ["target"],
        "additionalProperties": False,
    },
    "browser_mouse_wheel": {
        "type": "object",
        "properties": {"deltaX": {"type": "number", "default": 0}, "deltaY": {"type": "number", "default": 0}},
        "required": ["deltaX", "deltaY"],
        "additionalProperties": False,
    },
    "browser_cookie_delete": {
        "type": "object",
        "properties": {"name": {"type": "string"}},
        "required": ["name"],
        "additionalProperties": False,
    },
    "browser_fill_form": {
        "type": "object",
        "properties": {
            "fields": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "element": {"type": "string"},
                        "target": {"type": "string"},
                        "name": {"type": "string"},
                    },
                    "required": ["target", "name"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["fields"],
        "additionalProperties": False,
    },
    "browser_emulate_media": {"type": "object", "properties": {}, "additionalProperties": False},
}
DOCUMENTED = {
    "browser_click": {"target": DocumentedParam(required=True), "button": DocumentedParam(required=False)},
    "browser_mouse_wheel": {"deltaX": DocumentedParam(required=False), "deltaY": DocumentedParam(required=False)},
    "browser_cookie_delete": {},
    "browser_fill_form": {"fields": DocumentedParam(required=True, fields={"target": True, "name": True})},
    "browser_ghost": {"x": DocumentedParam(required=True)},
}


@pytest.fixture
def catalog() -> ToolCatalog:
    return ToolCatalog(server=SERVER_PACKAGE, tools=build_catalog(SERVER_TOOLS, DOCUMENTED).tools)


def test_only_documented_tools_that_the_server_has_are_kept() -> None:
    assert set(build_catalog(SERVER_TOOLS, DOCUMENTED).tools) == {
        "browser_click",
        "browser_mouse_wheel",
        "browser_cookie_delete",
        "browser_fill_form",
    }


def test_only_documented_params_are_kept_and_no_other_is_accepted() -> None:
    click = build_catalog(SERVER_TOOLS, DOCUMENTED).tools["browser_click"]

    assert click["properties"] == {
        "target": {"type": "string"},
        "button": {"type": "string", "enum": ["left", "right", "middle"]},
    }
    assert click["required"] == ["target"]
    assert click["additionalProperties"] is False


def test_a_param_the_server_defaults_is_not_required() -> None:
    assert build_catalog(SERVER_TOOLS, DOCUMENTED).tools["browser_mouse_wheel"]["required"] == []


def test_only_documented_item_keys_are_kept() -> None:
    items = build_catalog(SERVER_TOOLS, DOCUMENTED).tools["browser_fill_form"]["properties"]["fields"]["items"]

    assert set(items["properties"]) == {"target", "name"}
    assert items["required"] == ["name", "target"]


def test_everything_left_out_is_reported() -> None:
    assert build_catalog(SERVER_TOOLS, DOCUMENTED).excluded == (
        "browser_click.element: not documented",
        "browser_cookie_delete.name: required by the server but not documented, so every call fails",
        "browser_fill_form.fields[].element: not documented",
        "browser_ghost: documented, but the server has no such tool",
        "browser_emulate_media: not documented",
    )


def test_a_documented_call_has_no_problems(catalog: ToolCatalog) -> None:
    assert catalog.problems("browser_click", {"target": 'text="En Yeni"', "button": "left"}) == []
    assert catalog.problems("browser_fill_form", {"fields": [{"target": "#q", "name": "Search"}]}) == []


@pytest.mark.parametrize(
    ("name", "arguments", "problem"),
    [
        ("browser_emulate_media", {}, "unknown tool 'browser_emulate_media'"),
        ("browser_click", {"target": "#a", "element": "Buy"}, "'element' was unexpected"),
        ("browser_click", {"target": {"selector": "#a"}}, "target: {'selector': '#a'} is not of type 'string'"),
        ("browser_click", {"target": "#a", "button": "primary"}, "button: 'primary' is not one of"),
        ("browser_click", {}, "'target' is a required property"),
        ("browser_fill_form", {"fields": [{"target": "#q", "name": "Q", "element": "Q"}]}, "fields[0]:"),
    ],
)
def test_an_undocumented_or_invalid_call_names_its_problem(
    catalog: ToolCatalog, name: str, arguments: dict[str, Any], problem: str
) -> None:
    problems = catalog.problems(name, arguments)

    assert len(problems) == 1
    assert problem in problems[0]


def test_check_raises_with_every_problem(catalog: ToolCatalog) -> None:
    with pytest.raises(InvalidToolCall) as raised:
        catalog.check("browser_click", {"element": "Buy"})

    assert raised.value.name == "browser_click"
    assert len(raised.value.problems) == 2
    assert str(raised.value).startswith("browser_click: ")


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
    ],
)
def test_an_unusable_catalog_file_fails(tmp_path: Path, content: Any, problem: str) -> None:
    with pytest.raises(CatalogError, match=problem):
        load_catalog(write(tmp_path, content))


def test_a_missing_catalog_file_fails(tmp_path: Path) -> None:
    with pytest.raises(CatalogError, match="cannot read"):
        load_catalog(tmp_path / "missing.json")


def test_the_committed_catalog_is_the_documented_pinned_server() -> None:
    committed = load_catalog()

    assert committed.server == SERVER_PACKAGE
    assert len(committed.tools) == 71
    assert "browser_emulate_media" not in committed.tools
    assert "element" not in committed.tools["browser_click"]["properties"]
    assert "all" not in committed.tools["browser_network_requests"]["properties"]
    assert set(committed.tools["browser_snapshot"]["properties"]) == {"target", "depth", "boxes", "filename"}
