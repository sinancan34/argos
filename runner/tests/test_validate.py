import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from argos_runner import run, validate
from argos_runner.criteria.providers import load_providers
from argos_runner.devtools.tool_catalog import CatalogError, load_catalog

pytestmark = pytest.mark.unit

CATALOG = load_catalog()
TOOLS = CATALOG["tools"]
PROVIDERS = load_providers()
SCENARIOS = sorted(Path(__file__).parents[2].joinpath("scenarios").glob("*/*.json"))


def _action(action: str, params: dict[str, Any]) -> dict[str, Any]:
    return {"action": action, "params": params}


def _file(tmp_path: Path, *actions: dict[str, Any], name: str = "scenario.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps([{"scenario": list(actions)}]), encoding="utf-8")
    return path


def _problems(tmp_path: Path, *actions: dict[str, Any]) -> list[str]:
    result = validate.validate_file(_file(tmp_path, *actions), PROVIDERS, CATALOG)
    return result["data"].get("problems", [])


def test_catalog_is_of_the_pinned_server() -> None:
    assert load_catalog()["server"] == run.SERVER_PACKAGE


def test_catalog_has_the_tools_of_every_capability() -> None:
    assert len(TOOLS) == 72
    for tool in ["browser_route", "browser_cookie_set", "browser_verify_value", "browser_start_tracing",
                 "browser_pdf_save", "browser_mouse_wheel", "browser_get_config"]:
        assert tool in TOOLS


@pytest.mark.parametrize("tool", sorted(TOOLS))
def test_every_catalog_schema_is_a_valid_json_schema(tool: str) -> None:
    Draft202012Validator.check_schema(TOOLS[tool])


def test_valid_scenario_passes_with_its_step_count(tmp_path: Path) -> None:
    path = _file(
        tmp_path,
        _action("browser_navigate", {"url": "https://a.com"}),
        _action("browser_mouse_wheel", {"deltaX": 0, "deltaY": 400}),
        _action("browser_snapshot", {}),
    )

    assert validate.validate_file(path, PROVIDERS, CATALOG) == {
        "status": "success",
        "data": {"scenario": str(path), "steps": 1},
    }


def test_tools_take_no_tab_param(tmp_path: Path) -> None:
    assert _problems(tmp_path, _action("browser_wait_for", {"text": "Ara"})) == []


def test_unknown_tool_is_named(tmp_path: Path) -> None:
    assert _problems(tmp_path, _action("scroll", {})) == [
        f"step 1 action 1: unknown action 'scroll'; {run.SERVER_PACKAGE} has no such tool"
    ]


@pytest.mark.parametrize("action", ["custom_scroll", "click", "navigate_page"])
def test_runner_and_chrome_devtools_tools_are_unknown(tmp_path: Path, action: str) -> None:
    assert _problems(tmp_path, _action(action, {})) == [
        f"step 1 action 1: unknown action '{action}'; {run.SERVER_PACKAGE} has no such tool"
    ]


def test_unknown_param_is_named(tmp_path: Path) -> None:
    problems = _problems(tmp_path, _action("browser_take_screenshot", {"fullpage": True, "scale": "css"}))

    assert problems == [
        "step 1 action 1 browser_take_screenshot: Additional properties are not allowed ('fullpage' was unexpected)"
    ]


def test_missing_required_param_is_named(tmp_path: Path) -> None:
    assert _problems(tmp_path, _action("browser_navigate", {})) == [
        "step 1 action 1 browser_navigate: 'url' is a required property"
    ]


def test_wrong_type_names_the_param(tmp_path: Path) -> None:
    problems = _problems(tmp_path, _action("browser_resize", {"width": "800", "height": 600}))

    assert problems == ["step 1 action 1 browser_resize param 'width': '800' is not of type 'number'"]


def test_value_outside_the_enum_names_the_param(tmp_path: Path) -> None:
    problems = _problems(tmp_path, _action("browser_tabs", {"action": "sideways"}))

    assert len(problems) == 1
    assert problems[0].startswith("step 1 action 1 browser_tabs param 'action': 'sideways' is not one of")


def test_unknown_param_inside_a_list_item_is_named(tmp_path: Path) -> None:
    fields = [{"target": {"selector": "#name"}, "name": "Name", "type": "textbox", "value": "Ada", "label": "Name"}]

    problems = _problems(tmp_path, _action("browser_fill_form", {"fields": fields}))

    assert problems == [
        "step 1 action 1 browser_fill_form param 'fields[0]': Additional properties are not allowed "
        "('label' was unexpected)"
    ]


def test_every_problem_of_every_action_is_listed(tmp_path: Path) -> None:
    problems = _problems(
        tmp_path,
        _action("browser_navigate", {}),
        _action("browser_navigate", {"url": "https://a.com"}),
        _action("click_element", {}),
        _action("browser_press_key", {"key": "Enter", "repeat": 2}),
    )

    assert [problem.split(":")[0] for problem in problems] == [
        "step 1 action 1 browser_navigate",
        "step 1 action 3",
        "step 1 action 4 browser_press_key",
    ]


@pytest.mark.parametrize(
    ("action", "params"),
    [
        ("browser_click", {"target": {"selector": "#buy"}}),
        ("browser_click", {"target": {"selector": ["#buy", "text=Buy"]}, "doubleClick": True, "element": "Buy"}),
        ("browser_hover", {"target": {"selector": "text=Menu"}}),
        ("browser_type", {"target": {"selector": "#q"}, "text": "ev"}),
        ("browser_drag", {"startTarget": {"selector": "#card"}, "endTarget": {"selector": "#bin"}}),
        (
            "browser_fill_form",
            {"fields": [{"target": {"selector": "#name"}, "name": "Name", "type": "textbox", "value": "Ada"}]},
        ),
        ("browser_select_option", {"target": {"selector": "select"}, "values": ["a"]}),
        ("browser_take_screenshot", {"target": {"selector": "header"}, "type": "png", "scale": "css"}),
        ("browser_evaluate", {"function": "(el) => el.id", "target": {"selector": "#buy"}}),
        ("browser_snapshot", {"target": {"selector": "main"}}),
    ],
)
def test_element_params_take_selectors_under_their_mcp_names(tmp_path: Path, action: str, params: dict) -> None:
    assert _problems(tmp_path, _action(action, params)) == []


@pytest.mark.parametrize(
    "target",
    ["e2", {"selector": []}, {"selector": ""}, {"selector": ["text="]}, {"selector": ["#a", 3]}, {"selector": "#a", "nth": 2}, 5],
)
def test_element_param_without_a_selector_is_rejected(tmp_path: Path, target: Any) -> None:
    assert _problems(tmp_path, _action("browser_click", {"target": target})) == [
        "step 1 action 1 browser_click param 'target': must be {\"selector\": <selector or non-empty list of selectors>}; "
        "snapshot refs change every run"
    ]


def test_form_and_script_element_params_are_checked_by_position(tmp_path: Path) -> None:
    fields = [
        {"target": {"selector": "#a"}, "name": "A", "type": "textbox", "value": "x"},
        {"target": "e3", "name": "B", "type": "textbox", "value": "y"},
    ]
    form = _action("browser_fill_form", {"fields": fields})
    script = _action("browser_evaluate", {"function": "(a) => 1", "target": "e4"})

    problems = _problems(tmp_path, form, script)

    assert [problem.split(":")[0] for problem in problems] == [
        "step 1 action 1 browser_fill_form param 'fields[1].target'",
        "step 1 action 2 browser_evaluate param 'target'",
    ]


@pytest.mark.parametrize("old", ["selector", "uid"])
def test_old_element_param_names_are_not_mcp_params(tmp_path: Path, old: str) -> None:
    problems = _problems(tmp_path, _action("browser_click", {old: {"selector": "#buy"}}))

    assert "step 1 action 1 browser_click: 'target' is a required property" in problems
    assert f"step 1 action 1 browser_click: Additional properties are not allowed ('{old}' was unexpected)" in problems


def test_unreadable_json_fails_with_its_reason(tmp_path: Path) -> None:
    path = tmp_path / "broken.json"
    path.write_text('[{"scenario": [', encoding="utf-8")

    result = validate.validate_file(path, PROVIDERS, CATALOG)

    assert result["status"] == "fail"
    assert result["data"]["problems"][0].startswith(f"invalid scenario {path}")


def test_check_returns_steps_of_a_valid_scenario(tmp_path: Path) -> None:
    steps = validate.check(_file(tmp_path, _action("browser_navigate", {"url": "https://a.com"})), PROVIDERS, CATALOG)

    assert steps[0].scenario[0].action == "browser_navigate"


def test_check_raises_with_every_problem(tmp_path: Path) -> None:
    path = _file(tmp_path, _action("browser_navigate", {}), _action("scroll", {}))

    expected = r"invalid scenario .*'url' is a required property; .*unknown action"
    with pytest.raises(validate.ScenarioError, match=expected):
        validate.check(path, PROVIDERS, CATALOG)


def test_main_validates_every_file_and_exits_1_if_any_is_invalid(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    good = _file(tmp_path, _action("browser_navigate", {"url": "https://a.com"}), name="good.json")
    bad = _file(tmp_path, _action("scroll", {}), name="bad.json")

    exit_code = validate.main([str(good), str(bad)])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert [entry["status"] for entry in output] == ["success", "fail"]


@pytest.mark.parametrize("content", ["", "[]", '{"server": "x"}'])
def test_unreadable_catalog_is_an_error(tmp_path: Path, content: str) -> None:
    path = tmp_path / "tool_schemas.json"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(CatalogError):
        load_catalog(path)


def test_main_reports_a_missing_catalog(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(validate, "load_catalog", lambda: load_catalog(tmp_path / "missing.json"))

    exit_code = validate.main([str(_file(tmp_path, _action("browser_tabs", {"action": "list"})))])

    assert exit_code == 1
    assert "cannot read tool catalog" in json.loads(capsys.readouterr().out)["message"]


def test_main_exits_0_when_every_file_is_valid(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = validate.main([str(_file(tmp_path, _action("browser_tabs", {"action": "list"})))])

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out)[0]["status"] == "success"


@pytest.mark.parametrize(
    "path",
    [
        pytest.param(path, marks=pytest.mark.skip(reason="mobile scenarios move to Playwright MCP in the mobile phase"))
        if path.stem.endswith("-mobile")
        else path
        for path in SCENARIOS
    ],
    ids=[path.name for path in SCENARIOS],
)
def test_checked_in_scenarios_are_valid(path: Path) -> None:
    assert validate.validate_file(path, PROVIDERS, CATALOG)["status"] == "success"
