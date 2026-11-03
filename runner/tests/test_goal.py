import pytest
from pydantic import ValidationError

from goal import Goal

pytestmark = pytest.mark.unit

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


def test_goal_accepts_preset_and_custom_providers() -> None:
    goals = [Goal.model_validate(goal) for goal in [GA4_PAGE_VIEW, CUSTOM]]

    assert [goal.provider.name for goal in goals] == ["ga4", "custom"]


def test_goal_accepts_every_match_type() -> None:
    conditions = [
        {"key": "a", "match": "exact", "value": "x"},
        {"key": "a", "match": "contains", "value": "x"},
        {"key": "a", "match": "startsWith", "value": "x"},
        {"key": "a", "match": "endsWith", "value": "x"},
        {"key": "a", "match": "regex", "value": "^x$"},
        {"key": "a", "match": "exists"},
    ]
    goal = {"provider": {"name": "meta", "params": []}, "conditions": conditions}

    assert len(Goal.model_validate(goal).conditions) == 6


@pytest.mark.parametrize(
    "goal",
    [
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
def test_goal_rejects_invalid_goal(goal: dict) -> None:
    with pytest.raises(ValidationError):
        Goal.model_validate(goal)
