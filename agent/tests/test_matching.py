import pytest

from argos_agent.scenario.matching import MatchRule, matches, rule_problems

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("match", "value", "actual", "expected"),
    [
        ("exact", "page_view", "page_view", True),
        ("exact", "page_view", "page_view2", False),
        ("exists", None, "", True),
        ("contains", "yeni", "anasayfa/en-yeni", True),
        ("contains", "eski", "anasayfa/en-yeni", False),
        ("startsWith", "https://www.emlakjet.com/ilan/", "https://www.emlakjet.com/ilan/1", True),
        ("startsWith", "https://www.emlakjet.com/ilan/", "https://www.emlakjet.com/", False),
        ("endsWith", "/en-yeni", "anasayfa/en-yeni", True),
        ("endsWith", "/en-yeni", "en-yeni/x", False),
        ("regex", r"^\d+$", "19760160", True),
        ("regex", r"^\d+$", "19760160a", False),
        ("gt", 10, "10.5", True),
        ("gt", "10", "10", False),
        ("gt", 10, "abc", False),
        ("lt", 10, "-1", True),
        ("lt", "10", "10", False),
        ("lt", 10, "", False),
        ("gt", 5, "1_0", False),
        ("gt", 5, " 10 ", False),
        ("lt", 5, "-inf", False),
        ("gt", "0.5", ".75", True),
    ],
)
def test_matches(match: str, value: str | float | None, actual: str, expected: bool) -> None:
    assert matches(MatchRule(match, value), actual) is expected


@pytest.mark.parametrize(
    ("rule", "problem"),
    [
        (MatchRule("equals", "x"), "unknown match 'equals'"),
        (MatchRule("exists", "x"), "'exists' takes no value"),
        (MatchRule("exact", None), "'exact' needs a string value"),
        (MatchRule("exact", ""), "'exact' needs a string value"),
        (MatchRule("exact", 1), "'exact' needs a string value"),
        (MatchRule("regex", "("), "invalid regex"),
        (MatchRule("gt", "ten"), "'gt' needs a number"),
        (MatchRule("lt", None), "'lt' needs a number"),
        (MatchRule("gt", True), "'gt' needs a number"),
        (MatchRule("gt", 10**400), "'gt' needs a number"),
        (MatchRule("lt", "1_000"), "'lt' needs a number"),
    ],
)
def test_rule_problems(rule: MatchRule, problem: str) -> None:
    problems = rule_problems(rule)

    assert len(problems) == 1 and problems[0].startswith(problem)


@pytest.mark.parametrize(
    "rule", [MatchRule("exists"), MatchRule("exact", "x"), MatchRule("regex", "^a"), MatchRule("gt", "1.5")]
)
def test_valid_rules_have_no_problems(rule: MatchRule) -> None:
    assert rule_problems(rule) == []
