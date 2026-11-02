import json
from pathlib import Path

import pytest

import goal as goal_module
from goal import Goal, GoalError
from providers import load_providers

pytestmark = pytest.mark.unit


def load_goals(path: Path) -> list[Goal]:
    return goal_module.load_goals(path, load_providers())


GA4_PAGE_VIEW = {
    "provider": {"name": "ga4", "params": []},
    "conditions": [{"key": "en", "match": "exact", "value": "page_view"}],
}
CUSTOM = {
    "provider": {
        "name": "custom",
        "params": [{"key": "url", "match": "contains", "value": "tiktok.com"}],
    },
    "conditions": [],
}


def _write(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "goal.json"
    path.write_text(content, encoding="utf-8")
    return path


def test_load_goals_accepts_preset_and_custom_providers(tmp_path: Path) -> None:
    goals = load_goals(_write(tmp_path, json.dumps([GA4_PAGE_VIEW, CUSTOM])))

    assert [goal.provider.name for goal in goals] == ["ga4", "custom"]
    assert isinstance(goals[0], Goal)


def test_load_goals_accepts_every_match_type(tmp_path: Path) -> None:
    conditions = [
        {"key": "a", "match": "exact", "value": "x"},
        {"key": "a", "match": "contains", "value": "x"},
        {"key": "a", "match": "startsWith", "value": "x"},
        {"key": "a", "match": "endsWith", "value": "x"},
        {"key": "a", "match": "regex", "value": "^x$"},
        {"key": "a", "match": "exists"},
    ]
    goal = {"provider": {"name": "meta", "params": []}, "conditions": conditions}

    assert len(load_goals(_write(tmp_path, json.dumps([goal])))[0].conditions) == 6


def test_load_goals_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(GoalError, match="cannot read"):
        load_goals(tmp_path / "missing.json")


def test_load_goals_rejects_non_utf8_file(tmp_path: Path) -> None:
    path = tmp_path / "goal.json"
    path.write_bytes(b"\xff\xfe")

    with pytest.raises(GoalError, match="cannot read"):
        load_goals(path)


@pytest.mark.parametrize(
    "goal",
    [
        {"provider": {"name": "tiktok", "params": []}, "conditions": []},
        {"provider": {"name": "ga4"}, "conditions": []},
        {"provider": "ga4", "conditions": []},
        {"provider": {"name": "ga4", "params": []}},
        {"provider": {"name": "ga4", "params": []}, "conditions": [], "name": "extra"},
        {
            "provider": {"name": "ga4", "params": [{"key": "url", "match": "exists"}]},
            "conditions": [],
        },
        {"provider": {"name": "custom", "params": []}, "conditions": []},
        {
            "provider": {"name": "custom", "params": [{"key": "url", "match": "exists"}]},
            "conditions": [],
        },
        {
            "provider": {
                "name": "custom",
                "params": [{"key": "host", "match": "exact", "value": "x"}],
            },
            "conditions": [],
        },
        {
            "provider": {
                "name": "custom",
                "params": [
                    {"key": "url", "match": "contains", "value": "x"},
                    {"key": "url", "match": "contains", "value": "y"},
                ],
            },
            "conditions": [],
        },
        {
            "provider": {"name": "ga4", "params": []},
            "conditions": [{"key": "en", "match": "exact"}],
        },
        {
            "provider": {"name": "ga4", "params": []},
            "conditions": [{"key": "en", "match": "exact", "value": ""}],
        },
        {
            "provider": {"name": "ga4", "params": []},
            "conditions": [{"key": "en", "match": "exists", "value": "x"}],
        },
        {
            "provider": {"name": "ga4", "params": []},
            "conditions": [{"key": "en", "match": "regex", "value": "("}],
        },
        {
            "provider": {"name": "ga4", "params": []},
            "conditions": [{"key": "en", "match": "equals", "value": "x"}],
        },
        {
            "provider": {"name": "ga4", "params": []},
            "conditions": [{"key": "", "match": "exact", "value": "x"}],
        },
    ],
)
def test_load_goals_rejects_invalid_goal(tmp_path: Path, goal: dict) -> None:
    with pytest.raises(GoalError, match="invalid goal"):
        load_goals(_write(tmp_path, json.dumps([goal])))


@pytest.mark.parametrize("content", ["not json", "[]", "{}"])
def test_load_goals_rejects_invalid_content(tmp_path: Path, content: str) -> None:
    with pytest.raises(GoalError, match="invalid goal"):
        load_goals(_write(tmp_path, content))
