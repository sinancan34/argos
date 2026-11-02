import json
from pathlib import Path

import pytest

from scenario import ScenarioError, Step, load_steps

pytestmark = pytest.mark.unit


def _write(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "scenario.json"
    path.write_text(content, encoding="utf-8")
    return path


def test_load_steps_returns_steps_in_order(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        json.dumps(
            [
                {"action": "start_browser", "params": {}},
                {"action": "navigate", "params": {"url": "https://example.com"}},
            ]
        ),
    )

    assert load_steps(path) == [
        Step(action="start_browser", params={}),
        Step(action="navigate", params={"url": "https://example.com"}),
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


@pytest.mark.parametrize(
    "action",
    ["click_element", "wait_for", "send_keys", "clear_input", "set_value", "select_option", "send_file"],
)
def test_load_steps_requires_timeout_on_actions_that_support_it(tmp_path: Path, action: str) -> None:
    path = _write(tmp_path, json.dumps([{"action": action, "params": {"selector": "a"}}]))

    with pytest.raises(ScenarioError, match="step 1.*timeout"):
        load_steps(path)


@pytest.mark.parametrize("timeout", [0, -1, 60, 61, "30", True, None])
def test_load_steps_rejects_invalid_timeout(tmp_path: Path, timeout: object) -> None:
    step = {"action": "wait_for", "params": {"selector": "a", "timeout": timeout}}

    with pytest.raises(ScenarioError, match="step 1.*timeout"):
        load_steps(_write(tmp_path, json.dumps([step])))


@pytest.mark.parametrize("timeout", [1, 30, 59.5])
def test_load_steps_accepts_valid_timeout(tmp_path: Path, timeout: float) -> None:
    step = {"action": "wait_for", "params": {"selector": "a", "timeout": timeout}}

    assert load_steps(_write(tmp_path, json.dumps([step])))[0].params["timeout"] == timeout


def test_load_steps_does_not_require_timeout_on_other_actions(tmp_path: Path) -> None:
    steps = [
        {"action": "start_browser", "params": {}},
        {"action": "navigate", "params": {"url": "https://example.com"}},
        {"action": "sleep", "params": {"t": 1}},
    ]

    assert len(load_steps(_write(tmp_path, json.dumps(steps)))) == 3


def test_load_steps_reports_number_of_step_without_timeout(tmp_path: Path) -> None:
    steps = [
        {"action": "start_browser", "params": {}},
        {"action": "click_element", "params": {"selector": "a"}},
    ]

    with pytest.raises(ScenarioError, match="step 2"):
        load_steps(_write(tmp_path, json.dumps(steps)))


def test_load_steps_rejects_non_utf8_file(tmp_path: Path) -> None:
    path = tmp_path / "scenario.json"
    path.write_bytes(b"\xff\xfe")

    with pytest.raises(ScenarioError, match="cannot read"):
        load_steps(path)
