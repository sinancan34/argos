import json
from pathlib import Path

import pytest

import scenario
from goal import Goal
from providers import load_providers
from scenario import ScenarioError, Step

pytestmark = pytest.mark.unit

NAVIGATE = {"action": "navigate", "params": {"url": "https://example.com"}}
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


def _one_step(tmp_path: Path, action: str, params: dict) -> Path:
    return _write(tmp_path, json.dumps([{"action": action, "params": params}]))


def test_load_steps_returns_steps_in_order(tmp_path: Path) -> None:
    wait = {"action": "wait_for", "params": {"selector": "h1", "timeout": 30}}
    path = _write(tmp_path, json.dumps([NAVIGATE, wait]))

    assert load_steps(path) == [
        Step(action="navigate", params={"url": "https://example.com"}),
        Step(action="wait_for", params={"selector": "h1", "timeout": 30}),
    ]


def test_load_steps_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ScenarioError, match="cannot read"):
        load_steps(tmp_path / "missing.json")


@pytest.mark.parametrize(
    "content",
    [
        "not json",
        "[]",
        '{"action": "navigate", "params": {}}',
        '[{"params": {}}]',
        '[{"action": "navigate"}]',
        '[{"action": "", "params": {}}]',
        '[{"action": "navigate", "params": "url"}]',
        '[{"action": "navigate", "params": {}, "intent": "extra field"}]',
    ],
)
def test_load_steps_rejects_invalid_content(tmp_path: Path, content: str) -> None:
    with pytest.raises(ScenarioError, match="invalid scenario"):
        load_steps(_write(tmp_path, content))


@pytest.mark.parametrize("action", ["start_browser", "stop_browser", "send_keys", "hover"])
def test_load_steps_rejects_unsupported_action(tmp_path: Path, action: str) -> None:
    path = _write(tmp_path, json.dumps([NAVIGATE, {"action": action, "params": {}}]))

    with pytest.raises(ScenarioError, match=f"step 2 uses unsupported action '{action}'"):
        load_steps(path)


@pytest.mark.parametrize("params", [{}, {"url": ""}, {"url": "https://a.com", "new_tab": True}])
def test_load_steps_rejects_invalid_navigate_params(tmp_path: Path, params: dict) -> None:
    with pytest.raises(ScenarioError, match=r"step 1 \(navigate\)"):
        load_steps(_one_step(tmp_path, "navigate", params))


@pytest.mark.parametrize("action", ["click_element", "wait_for"])
def test_load_steps_requires_timeout_on_element_actions(tmp_path: Path, action: str) -> None:
    with pytest.raises(ScenarioError, match="step 1.*timeout"):
        load_steps(_one_step(tmp_path, action, {"selector": "a"}))


@pytest.mark.parametrize("timeout", [0, -1, 60, 61, "30", True, None])
def test_load_steps_rejects_invalid_timeout(tmp_path: Path, timeout: object) -> None:
    with pytest.raises(ScenarioError, match="step 1.*timeout"):
        load_steps(_one_step(tmp_path, "wait_for", {"selector": "a", "timeout": timeout}))


@pytest.mark.parametrize("timeout", [1, 30, 59.5])
def test_load_steps_accepts_valid_timeout(tmp_path: Path, timeout: float) -> None:
    path = _one_step(tmp_path, "wait_for", {"selector": "a", "timeout": timeout})

    assert load_steps(path)[0].params["timeout"] == timeout


@pytest.mark.parametrize(
    "params",
    [
        {"timeout": 1},
        {"selector": "", "timeout": 1},
        {"text": "Ara", "timeout": 1},
        {"selector": "a", "timeout": 1, "include_children": False},
    ],
)
def test_load_steps_rejects_invalid_element_params(tmp_path: Path, params: dict) -> None:
    with pytest.raises(ScenarioError, match=r"step 1 \(click_element\)"):
        load_steps(_one_step(tmp_path, "click_element", params))


def test_load_steps_accepts_new_tab_placeholder(tmp_path: Path) -> None:
    params = {"selector": "a", "timeout": 1, "target_id": "$new_tab"}

    assert load_steps(_one_step(tmp_path, "wait_for", params))[0].params == params


@pytest.mark.parametrize("target_id", ["TAB-1", "", 2])
def test_load_steps_rejects_other_target_ids(tmp_path: Path, target_id: object) -> None:
    params = {"url": "https://a.com", "target_id": target_id}

    with pytest.raises(ScenarioError, match="target_id"):
        load_steps(_one_step(tmp_path, "navigate", params))


def test_load_steps_reports_number_of_invalid_step(tmp_path: Path) -> None:
    steps = [NAVIGATE, {"action": "click_element", "params": {"selector": "a"}}]

    with pytest.raises(ScenarioError, match="step 2"):
        load_steps(_write(tmp_path, json.dumps(steps)))


def test_load_steps_rejects_non_utf8_file(tmp_path: Path) -> None:
    path = tmp_path / "scenario.json"
    path.write_bytes(b"\xff\xfe")

    with pytest.raises(ScenarioError, match="cannot read"):
        load_steps(path)


def test_steps_have_no_goals_unless_given(tmp_path: Path) -> None:
    assert load_steps(_write(tmp_path, json.dumps([NAVIGATE])))[0].goals is None


def test_load_steps_reads_goals_of_a_step(tmp_path: Path) -> None:
    path = _write(tmp_path, json.dumps([{**NAVIGATE, "goals": [GA4_PAGE_VIEW]}]))

    goals = load_steps(path)[0].goals

    assert goals == [Goal.model_validate(GA4_PAGE_VIEW)]


def test_load_steps_rejects_empty_goals(tmp_path: Path) -> None:
    path = _write(tmp_path, json.dumps([{**NAVIGATE, "goals": []}]))

    with pytest.raises(ScenarioError, match="invalid scenario"):
        load_steps(path)


def test_load_steps_reports_step_and_goal_of_invalid_goal(tmp_path: Path) -> None:
    broken = {**GA4_PAGE_VIEW, "conditions": [{"key": "en", "match": "exact"}]}
    steps = [NAVIGATE, {**NAVIGATE, "goals": [GA4_PAGE_VIEW, broken]}]

    with pytest.raises(ScenarioError, match=r"step 2 goal 2 .*'exact' requires a value"):
        load_steps(_write(tmp_path, json.dumps(steps)))


def test_load_steps_rejects_unknown_provider(tmp_path: Path) -> None:
    unknown = {"provider": {"name": "tiktok", "params": []}, "conditions": []}
    path = _write(tmp_path, json.dumps([{**NAVIGATE, "goals": [unknown]}]))

    with pytest.raises(ScenarioError, match="step 1 goal 1 uses unknown provider 'tiktok'"):
        load_steps(path)
