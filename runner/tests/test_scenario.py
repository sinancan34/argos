import json
from pathlib import Path

import pytest

import scenario
from providers import load_providers
from scenario import Action, ScenarioError, Step
from success_criterion import SuccessCriterion

pytestmark = pytest.mark.unit

NAVIGATE = {"action": "navigate_page", "params": {"url": "https://example.com"}}
CLICK = {"action": "click", "params": {"selector": "h1"}}
GA4_PAGE_VIEW = {
    "provider": {"name": "ga4", "params": []},
    "conditions": [{"key": "en", "match": "exact", "value": "page_view"}],
}


def load_steps(path: Path) -> list[Step]:
    return scenario.load_steps(path, load_providers())


def _write(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "scenario.json"
    path.write_text(content, encoding="utf-8")
    return path


def _steps(tmp_path: Path, *steps: dict) -> Path:
    return _write(tmp_path, json.dumps(list(steps)))


def test_load_steps_returns_steps_and_their_actions_in_order(tmp_path: Path) -> None:
    path = _steps(tmp_path, {"scenario": [NAVIGATE, CLICK]}, {"scenario": [CLICK]})

    assert load_steps(path) == [
        Step(scenario=[Action(**NAVIGATE), Action(**CLICK)]),
        Step(scenario=[Action(**CLICK)]),
    ]


def test_load_steps_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ScenarioError, match="cannot read"):
        load_steps(tmp_path / "missing.json")


@pytest.mark.parametrize(
    "content",
    [
        "not json",
        "[]",
        '{"scenario": [{"action": "click", "params": {}}]}',
        '[{"scenario": []}]',
        '[{"success_criteria": []}]',
        '[{"action": "click", "params": {}}]',
        '[{"scenario": [{"params": {}}]}]',
        '[{"scenario": [{"action": "click"}]}]',
        '[{"scenario": [{"action": "", "params": {}}]}]',
        '[{"scenario": [{"action": "click", "params": "url"}]}]',
        '[{"scenario": [{"action": "click", "params": {}, "intent": "extra field"}]}]',
        '[{"scenario": [{"action": "click", "params": {}}], "goals": []}]',
    ],
)
def test_load_steps_rejects_invalid_content(tmp_path: Path, content: str) -> None:
    with pytest.raises(ScenarioError, match="invalid scenario"):
        load_steps(_write(tmp_path, content))


@pytest.mark.parametrize("action", ["take_screenshot", "lighthouse_audit", "not_a_tool_yet"])
def test_load_steps_leaves_action_names_to_the_server(tmp_path: Path, action: str) -> None:
    params = {"anything": [1, {"nested": True}]}

    steps = load_steps(_steps(tmp_path, {"scenario": [{"action": action, "params": params}]}))

    assert steps == [Step(scenario=[Action(action=action, params=params)])]


def test_load_steps_rejects_non_utf8_file(tmp_path: Path) -> None:
    path = tmp_path / "scenario.json"
    path.write_bytes(b"\xff\xfe")

    with pytest.raises(ScenarioError, match="cannot read"):
        load_steps(path)


def test_steps_have_no_success_criteria_unless_given(tmp_path: Path) -> None:
    assert load_steps(_steps(tmp_path, {"scenario": [NAVIGATE]}))[0].success_criteria is None


def test_load_steps_reads_success_criteria_after_several_actions(tmp_path: Path) -> None:
    path = _steps(tmp_path, {"scenario": [NAVIGATE, CLICK, CLICK, CLICK], "success_criteria": [GA4_PAGE_VIEW]})

    step = load_steps(path)[0]

    assert len(step.scenario) == 4
    assert step.success_criteria == [SuccessCriterion.model_validate(GA4_PAGE_VIEW)]


def test_load_steps_rejects_empty_success_criteria(tmp_path: Path) -> None:
    path = _steps(tmp_path, {"scenario": [NAVIGATE], "success_criteria": []})

    with pytest.raises(ScenarioError, match="invalid scenario"):
        load_steps(path)


def test_load_steps_reports_step_and_number_of_invalid_success_criterion(tmp_path: Path) -> None:
    broken = {**GA4_PAGE_VIEW, "conditions": [{"key": "en", "match": "exact"}]}
    steps = [{"scenario": [NAVIGATE]}, {"scenario": [NAVIGATE], "success_criteria": [GA4_PAGE_VIEW, broken]}]

    with pytest.raises(ScenarioError, match=r"step 2 success criterion 2 .*'exact' requires a value"):
        load_steps(_steps(tmp_path, *steps))


def test_load_steps_rejects_unknown_provider(tmp_path: Path) -> None:
    unknown = {"provider": {"name": "tiktok", "params": []}, "conditions": []}
    path = _steps(tmp_path, {"scenario": [NAVIGATE], "success_criteria": [unknown]})

    with pytest.raises(ScenarioError, match="step 1 success criterion 1 uses unknown provider 'tiktok'"):
        load_steps(path)
