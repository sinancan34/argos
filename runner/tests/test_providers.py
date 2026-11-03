import json
from pathlib import Path

import pytest

from goal import Goal, Provider
from goal_evaluator import evaluate_goals, is_wanted
from network_capture import CapturedRequest
from providers import ProvidersError, load_providers
from scenario import ScenarioError, load_steps

pytestmark = pytest.mark.unit


def _write(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "providers.json"
    path.write_text(content, encoding="utf-8")
    return path


def _scenario_with_goal(tmp_path: Path, provider: str) -> Path:
    path = tmp_path / "scenario.json"
    goal = {"provider": {"name": provider, "params": []}, "conditions": []}
    path.write_text(
        json.dumps([{"action": "navigate", "params": {"url": "https://a.com"}, "goals": [goal]}]),
        encoding="utf-8",
    )
    return path


def _providers_with(tmp_path: Path, definitions: dict) -> dict:
    return load_providers(_write(tmp_path, json.dumps(definitions)))


def test_default_file_defines_ga4_gtm_and_meta() -> None:
    assert set(load_providers()) == {"ga4", "gtm", "meta"}


def test_provider_can_have_multiple_urls(tmp_path: Path) -> None:
    providers = _providers_with(
        tmp_path,
        {
            "ga4": {
                "urls": [
                    {"match": "contains", "value": "/g/collect"},
                    {"match": "startsWith", "value": "https://sgtm.example.com/events"},
                ]
            }
        },
    )
    goal = Goal(provider=Provider(name="ga4", params=[]), conditions=[])

    assert is_wanted([goal], "https://analytics.google.com/g/collect?v=2", providers) is True
    assert is_wanted([goal], "https://sgtm.example.com/events?v=2", providers) is True
    assert is_wanted([goal], "https://other.example.com/x", providers) is False


def test_new_provider_needs_only_a_json_entry(tmp_path: Path) -> None:
    providers = _providers_with(
        tmp_path, {"tiktok": {"urls": [{"match": "contains", "value": "analytics.tiktok.com"}]}}
    )
    goals = load_steps(_scenario_with_goal(tmp_path, "tiktok"), providers)[0].goals
    request = CapturedRequest(url="https://analytics.tiktok.com/api", body=None)

    assert evaluate_goals(goals, [request], providers)[0]["status"] == "pass"


def test_goal_rejects_provider_missing_from_file(tmp_path: Path) -> None:
    providers = _providers_with(tmp_path, {"meta": {"urls": [{"match": "contains", "value": "x"}]}})
    with pytest.raises(ScenarioError, match="unknown provider 'ga4'"):
        load_steps(_scenario_with_goal(tmp_path, "ga4"), providers)


def test_load_providers_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ProvidersError, match="cannot read"):
        load_providers(tmp_path / "missing.json")


def test_load_providers_rejects_non_utf8_file(tmp_path: Path) -> None:
    path = tmp_path / "providers.json"
    path.write_bytes(b"\xff\xfe")

    with pytest.raises(ProvidersError, match="cannot read"):
        load_providers(path)


@pytest.mark.parametrize(
    "definitions",
    [
        {"ga4": {"urls": []}},
        {"ga4": {}},
        {"ga4": {"urls": [{"match": "exists"}]}},
        {"ga4": {"urls": [{"match": "regex", "value": "("}]}},
        {"ga4": {"urls": [{"match": "contains"}]}},
        {"ga4": {"urls": [{"match": "contains", "value": "x"}], "name": "extra"}},
        {"custom": {"urls": [{"match": "contains", "value": "x"}]}},
    ],
)
def test_load_providers_rejects_invalid_definition(tmp_path: Path, definitions: dict) -> None:
    with pytest.raises(ProvidersError, match="invalid providers"):
        _providers_with(tmp_path, definitions)


def test_load_providers_rejects_invalid_json(tmp_path: Path) -> None:
    with pytest.raises(ProvidersError, match="invalid providers"):
        load_providers(_write(tmp_path, "not json"))
