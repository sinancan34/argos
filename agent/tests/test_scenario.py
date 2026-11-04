import json
from pathlib import Path
from typing import Any

import pytest

from argos_agent.runner.matching import MatchRule, rule_problems
from argos_agent.runner.scenario import PROVIDERS, ScenarioError, load_scenario

pytestmark = pytest.mark.unit

EXAMPLE = Path(__file__).parents[1] / "docs" / "scenario-example.json"
NAVIGATE = {"action": "browser_navigate", "params": {"url": "https://www.emlakjet.com/"}}
GTM_CRITERION = {
    "provider": {"name": "gtm", "params": []},
    "conditions": [{"key": "id", "match": "exact", "value": "GTM-MRDH2NZ"}],
}


def write(tmp_path: Path, content: Any) -> Path:
    path = tmp_path / "scenario.json"
    path.write_text(content if isinstance(content, str) else json.dumps(content), encoding="utf-8")
    return path


def problems(tmp_path: Path, content: Any) -> tuple[str, ...]:
    with pytest.raises(ScenarioError) as raised:
        load_scenario(write(tmp_path, content))
    return raised.value.problems


def test_the_providers_are_ga4_and_gtm_with_usable_url_rules() -> None:
    assert set(PROVIDERS) == {"ga4", "gtm"}
    assert [problem for rules in PROVIDERS.values() for rule in rules for problem in rule_problems(rule)] == []


def test_the_example_scenario_loads() -> None:
    steps = load_scenario(EXAMPLE)

    assert len(steps) == 4
    assert steps[0].actions[0].tool == "browser_navigate"
    assert steps[0].actions[0].params == {"url": "https://www.emlakjet.com/"}
    assert [criterion.provider for criterion in steps[0].criteria] == ["ga4", "gtm"]
    assert steps[0].criteria[0].conditions[-1].key == "ep.search_id"
    assert steps[0].criteria[0].conditions[-1].rule == MatchRule("exists")


def test_success_criteria_may_be_left_out(tmp_path: Path) -> None:
    (step,) = load_scenario(write(tmp_path, [{"scenario": [NAVIGATE]}]))

    assert step.criteria == ()


def test_every_problem_is_reported_at_once(tmp_path: Path) -> None:
    scenario = [
        {
            "scenario": [
                {"action": "browser_click", "params": {"target": {"selector": "text=En Yeni"}}},
                {"action": "browser_scroll", "params": {}},
            ],
            "success_criteria": [
                {
                    "provider": {"name": "ga4", "params": []},
                    "conditions": [
                        {"key": "en", "match": "exists", "value": "x"},
                        {"key": "pr1.id", "match": "regex", "value": "("},
                    ],
                }
            ],
        },
        {"scenario": [NAVIGATE], "success_criteria": [GTM_CRITERION]},
    ]

    found = problems(tmp_path, scenario)

    assert len(found) == 4
    assert found[0].startswith("step 1 action 1 browser_click: target: ")
    assert found[1].startswith("step 1 action 2 browser_scroll: unknown tool")
    assert found[2] == "step 1 criterion 1 condition 1 en: 'exists' takes no value"
    assert found[3].startswith("step 1 criterion 1 condition 2 pr1.id: invalid regex")


@pytest.mark.parametrize(
    ("provider", "expected"),
    [
        ({"name": "meta", "params": []}, "'meta' is not one of ['ga4', 'gtm']"),
        ({"name": "ga4", "params": [{"key": "url"}]}, "[{'key': 'url'}] is expected to be empty"),
        ({"name": "ga4"}, "'params' is a required property"),
    ],
)
def test_only_ga4_and_gtm_without_params_are_providers(tmp_path: Path, provider: Any, expected: str) -> None:
    scenario = [{"scenario": [NAVIGATE], "success_criteria": [{**GTM_CRITERION, "provider": provider}]}]

    (found,) = problems(tmp_path, scenario)

    assert expected in found


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ([], "should be non-empty"),
        ([{"scenario": []}], "[0].scenario: [] should be non-empty"),
        ([{"scenario": [{"action": "browser_navigate"}]}], "'params' is a required property"),
        ([{"scenario": [NAVIGATE], "extra": 1}], "Additional properties are not allowed"),
        ([{"scenario": [NAVIGATE], "success_criteria": [{**GTM_CRITERION, "conditions": []}]}], "non-empty"),
    ],
)
def test_the_scenario_shape_is_checked_first(tmp_path: Path, content: Any, expected: str) -> None:
    (found,) = problems(tmp_path, content)

    assert expected in found


@pytest.mark.parametrize("content", ["{not json", "\udcff"])
def test_an_unreadable_file_is_a_scenario_error(tmp_path: Path, content: str) -> None:
    path = tmp_path / "scenario.json"
    path.write_bytes(content.encode("utf-8", "surrogateescape"))

    with pytest.raises(ScenarioError, match="cannot read"):
        load_scenario(path)


def test_a_missing_file_is_a_scenario_error(tmp_path: Path) -> None:
    with pytest.raises(ScenarioError, match="cannot read"):
        load_scenario(tmp_path / "missing.json")
