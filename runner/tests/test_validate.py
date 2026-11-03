import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

import run
import validate
from providers import load_providers
from tool_catalog import CatalogError, load_catalog

pytestmark = pytest.mark.unit

CATALOG = load_catalog()
TOOLS = CATALOG["tools"]
PROVIDERS = load_providers()


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


@pytest.mark.parametrize("tool", sorted(TOOLS))
def test_every_catalog_schema_is_a_valid_json_schema(tool: str) -> None:
    Draft202012Validator.check_schema(TOOLS[tool])


def test_valid_scenario_passes_with_its_step_count(tmp_path: Path) -> None:
    path = _file(tmp_path, _action("navigate_page", {"url": "https://a.com"}), _action("take_snapshot", {}))

    assert validate.validate_file(path, PROVIDERS, CATALOG) == {
        "status": "success",
        "data": {"scenario": str(path), "steps": 1},
    }


def test_page_id_may_be_left_to_the_runner(tmp_path: Path) -> None:
    assert _problems(tmp_path, _action("wait_for", {"text": ["Ara"]})) == []


def test_unknown_tool_is_named(tmp_path: Path) -> None:
    assert _problems(tmp_path, _action("scroll", {})) == [
        f"step 1 action 1: unknown action 'scroll'; {run.SERVER_PACKAGE} has no such tool"
    ]


def test_unknown_param_is_named(tmp_path: Path) -> None:
    problems = _problems(tmp_path, _action("take_screenshot", {"fullpage": True}))

    assert problems == [
        "step 1 action 1 take_screenshot: Additional properties are not allowed ('fullpage' was unexpected)"
    ]


def test_missing_required_param_is_named(tmp_path: Path) -> None:
    assert _problems(tmp_path, _action("new_page", {})) == [
        "step 1 action 1 new_page: 'url' is a required property"
    ]


def test_wrong_type_names_the_param(tmp_path: Path) -> None:
    problems = _problems(tmp_path, _action("resize_page", {"width": "800", "height": 600}))

    assert problems == ["step 1 action 1 resize_page param 'width': '800' is not of type 'integer'"]


def test_value_outside_the_enum_names_the_param(tmp_path: Path) -> None:
    problems = _problems(tmp_path, _action("navigate_page", {"type": "sideways"}))

    assert len(problems) == 1
    assert problems[0].startswith("step 1 action 1 navigate_page param 'type': 'sideways' is not one of")


def test_unknown_param_inside_a_list_item_is_named(tmp_path: Path) -> None:
    elements = [{"uid": {"selector": "#name"}, "value": "Ada", "label": "Name"}]

    problems = _problems(tmp_path, _action("fill_form", {"elements": elements}))

    assert problems == [
        "step 1 action 1 fill_form param 'elements[0]': Additional properties are not allowed ('label' was unexpected)"
    ]


def test_every_problem_of_every_action_is_listed(tmp_path: Path) -> None:
    problems = _problems(
        tmp_path,
        _action("new_page", {}),
        _action("navigate_page", {"url": "https://a.com"}),
        _action("click_element", {}),
        _action("press_key", {"key": "Enter", "repeat": 2}),
    )

    assert [problem.split(":")[0] for problem in problems] == [
        "step 1 action 1 new_page",
        "step 1 action 3",
        "step 1 action 4 press_key",
    ]


@pytest.mark.parametrize(
    ("action", "params"),
    [
        ("click", {"uid": {"selector": "#buy"}}),
        ("click", {"uid": {"selector": ["#buy", "text=Buy"]}, "dblClick": True}),
        ("hover", {"uid": {"selector": "text=Menu"}}),
        ("fill", {"uid": {"selector": "#q"}, "value": "ev"}),
        ("drag", {"from_uid": {"selector": "#card"}, "to_uid": {"selector": "#bin"}}),
        ("fill_form", {"elements": [{"uid": {"selector": "#name"}, "value": "Ada"}]}),
        ("upload_file", {"uid": {"selector": "input[type=file]"}, "filePaths": ["/tmp/a.png"]}),
        ("get_css_styles", {"uid": {"selector": "h1"}}),
        ("take_screenshot", {"uid": {"selector": "header"}, "format": "png"}),
        ("evaluate_script", {"function": "(el) => el.id", "args": [{"selector": "#buy"}]}),
    ],
)
def test_element_params_take_selectors_under_their_mcp_names(tmp_path: Path, action: str, params: dict) -> None:
    assert _problems(tmp_path, _action(action, params)) == []


@pytest.mark.parametrize(
    ("params", "path"),
    [
        ({"uid": "1_2"}, "uid"),
        ({"uid": {"selector": []}}, "uid"),
        ({"uid": {"selector": ""}}, "uid"),
        ({"uid": {"selector": ["text="]}}, "uid"),
        ({"uid": {"selector": ["#a", 3]}}, "uid"),
        ({"uid": {"selector": "#a", "nth": 2}}, "uid"),
        ({"uid": 5}, "uid"),
    ],
)
def test_element_param_without_a_selector_is_rejected(tmp_path: Path, params: dict, path: str) -> None:
    assert _problems(tmp_path, _action("click", params)) == [
        f"step 1 action 1 click param '{path}': must be {{\"selector\": <selector or non-empty list of selectors>}}; "
        "snapshot uids change every run"
    ]


def test_form_and_script_element_params_are_checked_by_position(tmp_path: Path) -> None:
    form = _action("fill_form", {"elements": [{"uid": {"selector": "#a"}, "value": "x"}, {"uid": "1_3", "value": "y"}]})
    script = _action("evaluate_script", {"function": "(a) => 1", "args": ["1_4"]})

    problems = _problems(tmp_path, form, script)

    assert [problem.split(":")[0] for problem in problems] == [
        "step 1 action 1 fill_form param 'elements[1].uid'",
        "step 1 action 2 evaluate_script param 'args[0]'",
    ]


def test_old_selector_param_names_are_not_mcp_params(tmp_path: Path) -> None:
    problems = _problems(tmp_path, _action("click", {"selector": "#buy"}))

    assert "step 1 action 1 click: 'uid' is a required property" in problems
    assert "step 1 action 1 click: Additional properties are not allowed ('selector' was unexpected)" in problems


def test_unreadable_json_fails_with_its_reason(tmp_path: Path) -> None:
    path = tmp_path / "broken.json"
    path.write_text('[{"scenario": [', encoding="utf-8")

    result = validate.validate_file(path, PROVIDERS, CATALOG)

    assert result["status"] == "fail"
    assert result["data"]["problems"][0].startswith(f"invalid scenario {path}")


def test_check_returns_steps_of_a_valid_scenario(tmp_path: Path) -> None:
    steps = validate.check(_file(tmp_path, _action("navigate_page", {"url": "https://a.com"})), PROVIDERS, CATALOG)

    assert steps[0].scenario[0].action == "navigate_page"


def test_check_raises_with_every_problem(tmp_path: Path) -> None:
    path = _file(tmp_path, _action("new_page", {}), _action("scroll", {}))

    expected = r"invalid scenario .*'url' is a required property; .*unknown action"
    with pytest.raises(validate.ScenarioError, match=expected):
        validate.check(path, PROVIDERS, CATALOG)


def test_main_validates_every_file_and_exits_1_if_any_is_invalid(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    good = _file(tmp_path, _action("navigate_page", {"url": "https://a.com"}), name="good.json")
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

    exit_code = validate.main([str(_file(tmp_path, _action("list_pages", {})))])

    assert exit_code == 1
    assert "cannot read tool catalog" in json.loads(capsys.readouterr().out)["message"]


def test_main_exits_0_when_every_file_is_valid(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = validate.main([str(_file(tmp_path, _action("list_pages", {})))])

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out)[0]["status"] == "success"


@pytest.mark.parametrize("path", sorted(Path(__file__).parents[2].joinpath("scenarios").glob("*/*.json")))
def test_checked_in_scenarios_are_valid(path: Path) -> None:
    assert validate.validate_file(path, PROVIDERS, CATALOG)["status"] == "success"
