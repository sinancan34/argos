import pytest

import goal_evaluator
from goal import Condition, Goal, Provider
from goal_evaluator import request_events
from network_capture import CapturedRequest
from providers import load_providers

pytestmark = pytest.mark.unit

PROVIDERS = load_providers()


def evaluate_goals(goals: list[Goal], requests: list[CapturedRequest]) -> list[dict]:
    return goal_evaluator.evaluate_goals(goals, requests, PROVIDERS)


def is_wanted(goals: list[Goal], url: str) -> bool:
    return goal_evaluator.is_wanted(goals, url, PROVIDERS)


GA4_URL = "https://analytics.google.com/g/collect?v=2&tid=G-1"
META_URL = "https://www.facebook.com/tr/"
GTM_URL = "https://www.googletagmanager.com/gtm.js?id=GTM-1"


def _condition(key: str, match: str, value: str | None = None) -> Condition:
    return Condition(key=key, match=match, value=value)


def _goal(name: str, *conditions: Condition) -> Goal:
    return Goal(provider=Provider(name=name, params=[]), conditions=list(conditions))


def _custom(url_match: str, url_value: str, *conditions: Condition) -> Goal:
    provider = Provider(name="custom", params=[_condition("url", url_match, url_value)])
    return Goal(provider=provider, conditions=list(conditions))


def test_request_events_uses_query_when_there_is_no_body() -> None:
    events = request_events(CapturedRequest(url=f"{GA4_URL}&en=page_view", body=None))

    assert events == [{"v": ["2"], "tid": ["G-1"], "en": ["page_view"]}]


def test_request_events_makes_one_event_per_body_line_merged_with_query() -> None:
    events = request_events(CapturedRequest(url=GA4_URL, body="en=a&x=1\nen=b&x=2\n"))

    assert events == [
        {"v": ["2"], "tid": ["G-1"], "en": ["a"], "x": ["1"]},
        {"v": ["2"], "tid": ["G-1"], "en": ["b"], "x": ["2"]},
    ]


def test_request_events_decodes_form_encoding() -> None:
    body = "ev=Click&cd%5BbuttonText%5D=ios_share&dl=https%3A%2F%2Fa.com%2F&t=a+b"

    event = request_events(CapturedRequest(url=META_URL, body=body))[0]

    assert event["cd[buttonText]"] == ["ios_share"]
    assert event["dl"] == ["https://a.com/"]
    assert event["t"] == ["a b"]


def test_request_events_keeps_repeated_keys() -> None:
    event = request_events(CapturedRequest(url="https://a.com/?x=1&x=2", body=None))[0]

    assert event["x"] == ["1", "2"]


REAL_ITEM = (
    "id4586649~nmgraphic-design-specialist~ln0~cano~c2score_null~c4is-yerinde"
    "~c5tam-zamanli~k0sort_score_flag~v0no~loistanbul"
)


def test_ga4_item_parameter_is_split_into_named_keys() -> None:
    request = CapturedRequest(url=f"{GA4_URL}&en=view_item&pr1={REAL_ITEM}", body=None)

    event = request_events(request)[0]

    assert event["pr1.id"] == ["4586649"]
    assert event["pr1.nm"] == ["graphic-design-specialist"]
    assert event["pr1.ln"] == ["0"]
    assert event["pr1.ca"] == ["no"]
    assert event["pr1.c2"] == ["score_null"]
    assert event["pr1.c4"] == ["is-yerinde"]
    assert event["pr1.lo"] == ["istanbul"]


def test_ga4_item_custom_parameter_uses_its_own_name() -> None:
    request = CapturedRequest(url=f"{GA4_URL}&pr1={REAL_ITEM}", body=None)

    event = request_events(request)[0]

    assert event["pr1.sort_score_flag"] == ["no"]
    assert "pr1.k0" not in event
    assert "pr1.v0" not in event


def test_ga4_item_keeps_raw_parameter() -> None:
    request = CapturedRequest(url=f"{GA4_URL}&pr1=id1~nmx", body=None)

    assert request_events(request)[0]["pr1"] == ["id1~nmx"]


def test_ga4_items_are_split_per_item_and_per_body_line() -> None:
    request = CapturedRequest(url=GA4_URL, body="en=a&pr1=id1&pr2=id2\nen=b&pr1=id3")

    first, second = request_events(request)

    assert (first["pr1.id"], first["pr2.id"]) == (["1"], ["2"])
    assert second["pr1.id"] == ["3"]
    assert "pr2.id" not in second


def test_ga4_item_custom_key_without_value_is_ignored() -> None:
    event = request_events(CapturedRequest(url=f"{GA4_URL}&pr1=id1~k0flag", body=None))[0]

    assert "pr1.flag" not in event
    assert event["pr1.id"] == ["1"]


def test_parameter_that_only_looks_like_an_item_prefix_is_not_split() -> None:
    event = request_events(CapturedRequest(url="https://a.com/?promo=id1&pr=id2", body=None))[0]

    assert set(event) == {"promo", "pr"}


def test_goal_can_check_ga4_item_keys() -> None:
    goal = _goal(
        "ga4",
        _condition("en", "exact", "view_item"),
        _condition("pr1.id", "exact", "4586649"),
        _condition("pr1.sort_score_flag", "exact", "no"),
    )
    request = CapturedRequest(url=f"{GA4_URL}&en=view_item&pr1={REAL_ITEM}", body=None)

    assert evaluate_goals([goal], [request])[0]["status"] == "pass"


@pytest.mark.parametrize(
    ("match", "value", "actual", "passed"),
    [
        ("exact", "abc", "abc", True),
        ("exact", "abc", "abcd", False),
        ("exact", "ABC", "abc", False),
        ("contains", "bc", "abcd", True),
        ("contains", "x", "abcd", False),
        ("startsWith", "ab", "abcd", True),
        ("startsWith", "cd", "abcd", False),
        ("endsWith", "cd", "abcd", True),
        ("endsWith", "ab", "abcd", False),
        ("regex", r"^\d+$", "123", True),
        ("regex", r"^\d+$", "12a", False),
        ("exists", None, "anything", True),
    ],
)
def test_match_types(match: str, value: str | None, actual: str, passed: bool) -> None:
    goal = _goal("ga4", _condition("p", match, value))
    request = CapturedRequest(url=f"{GA4_URL}&p={actual}", body=None)

    assert evaluate_goals([goal], [request])[0]["status"] == ("pass" if passed else "fail")


def test_exists_fails_when_parameter_is_missing() -> None:
    goal = _goal("ga4", _condition("missing", "exists"))

    assert evaluate_goals([goal], [CapturedRequest(url=GA4_URL, body=None)])[0]["status"] == "fail"


def test_any_value_of_a_repeated_parameter_can_match() -> None:
    goal = _goal("ga4", _condition("x", "exact", "2"))
    request = CapturedRequest(url=f"{GA4_URL}&x=1&x=2", body=None)

    assert evaluate_goals([goal], [request])[0]["status"] == "pass"


def test_conditions_must_hold_on_the_same_event() -> None:
    goal = _goal("ga4", _condition("en", "exact", "a"), _condition("x", "exact", "2"))
    request = CapturedRequest(url=GA4_URL, body="en=a&x=1\nen=b&x=2")

    result = evaluate_goals([goal], [request])[0]

    assert result["status"] == "fail"
    assert result["requests"] == 1
    assert result["events"] == 2


def test_event_inside_a_batch_is_found() -> None:
    goal = _goal("ga4", _condition("en", "exact", "b"), _condition("x", "exact", "2"))
    request = CapturedRequest(url=GA4_URL, body="en=a&x=1\nen=b&x=2\nen=c&x=3")

    result = evaluate_goals([goal], [request])[0]

    assert result["status"] == "pass"
    assert result["matched_events"] == 1
    assert result["url"] == GA4_URL


def test_each_goal_is_reported_separately() -> None:
    goals = [
        _goal("ga4", _condition("en", "exact", "page_view")),
        _goal("meta", _condition("ev", "exact", "Share")),
    ]
    requests = [
        CapturedRequest(url=f"{GA4_URL}&en=page_view", body=None),
        CapturedRequest(url=META_URL, body="ev=PageView"),
    ]

    results = evaluate_goals(goals, requests)

    assert [(r["goal"], r["status"]) for r in results] == [(1, "pass"), (2, "fail")]
    assert results[0]["provider"] == {"name": "ga4", "params": []}
    assert results[0]["conditions"] == [{"key": "en", "match": "exact", "value": "page_view"}]


def test_failure_without_matching_request_reports_zero_requests() -> None:
    goal = _goal("meta", _condition("ev", "exact", "PageView"))

    result = evaluate_goals([goal], [CapturedRequest(url=GA4_URL, body=None)])[0]

    assert result == {
        "goal": 1,
        "status": "fail",
        "provider": {"name": "meta", "params": []},
        "conditions": [{"key": "ev", "match": "exact", "value": "PageView"}],
        "requests": 0,
        "events": 0,
    }


def test_failure_reports_closest_event() -> None:
    goal = _goal("ga4", _condition("en", "exact", "b"), _condition("x", "exact", "9"))
    request = CapturedRequest(url=GA4_URL, body="en=a&x=1\nen=b&x=2")

    result = evaluate_goals([goal], [request])[0]

    assert result["closest_url"] == GA4_URL
    assert result["closest"] == [
        {"key": "en", "match": "exact", "expected": "b", "actual": "b", "passed": True},
        {"key": "x", "match": "exact", "expected": "9", "actual": "2", "passed": False},
    ]


def test_closest_reports_missing_parameter_as_none() -> None:
    goal = _goal("ga4", _condition("missing", "exists"))

    result = evaluate_goals([goal], [CapturedRequest(url=GA4_URL, body=None)])[0]

    assert result["closest"] == [
        {"key": "missing", "match": "exists", "actual": None, "passed": False}
    ]


def test_empty_conditions_pass_when_a_request_is_selected() -> None:
    goal = _custom("contains", "tiktok.com")

    request = CapturedRequest(url="https://analytics.tiktok.com/api/v2/pixel", body=None)

    assert evaluate_goals([goal], [request])[0]["status"] == "pass"
    assert evaluate_goals([goal], [CapturedRequest(url=GA4_URL, body=None)])[0]["status"] == "fail"


@pytest.mark.parametrize(
    ("name", "url", "expected"),
    [
        ("ga4", GA4_URL, True),
        ("ga4", "https://sgtm.example.com/g/collect?v=2", True),
        ("ga4", "https://www.google-analytics.com/collect?v=1", False),
        ("meta", META_URL, True),
        ("meta", "https://www.facebook.com/tr?id=1&ev=PageView", True),
        ("meta", "https://www.facebook.com/tracking/", False),
        ("gtm", GTM_URL, True),
        ("gtm", "https://www.googletagmanager.com/gtag/js?id=G-1", False),
    ],
)
def test_preset_provider_url_rules(name: str, url: str, expected: bool) -> None:
    assert is_wanted([_goal(name)], url) is expected


def test_custom_url_is_tried_with_and_without_query() -> None:
    goal = _custom("endsWith", "/pixel")

    assert is_wanted([goal], "https://a.com/pixel?x=1") is True
    assert is_wanted([goal], "https://a.com/other?x=/pixel") is True
    assert is_wanted([goal], "https://a.com/other?x=1") is False
