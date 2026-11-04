import pytest

from argos_agent.runner.criteria import Captured, evaluate, wanted
from argos_agent.runner.matching import MatchRule
from argos_agent.runner.scenario import PROVIDERS, Condition, Criterion

pytestmark = pytest.mark.unit

GA4 = "https://region1.google-analytics.com/g/collect?v=2&tid=G-RQY35QJEY7"
GTM = "https://www.googletagmanager.com/gtm.js?id=GTM-MRDH2NZ&l=dataLayer"


def criterion(provider: str, *conditions: tuple[str, str, str | float | None]) -> Criterion:
    return Criterion(provider, tuple(Condition(key, MatchRule(match, value)) for key, match, value in conditions))


def test_wanted_is_any_url_of_the_criteria_providers() -> None:
    criteria = (criterion("gtm", ("id", "exists", None)),)

    assert wanted(GTM, criteria, PROVIDERS)
    assert not wanted(GA4, criteria, PROVIDERS)


def test_a_criterion_passes_when_one_event_meets_every_condition() -> None:
    requests = [
        Captured(f"{GA4}&dl=https%3A%2F%2Fwww.emlakjet.com%2F", "en=scroll\nen=page_view&ep.content_group=ana-sayfa"),
        Captured(GTM, None),
    ]
    page_view = criterion("ga4", ("en", "exact", "page_view"), ("ep.content_group", "exact", "ana-sayfa"))

    outcome = evaluate(1, page_view, requests, PROVIDERS)

    assert outcome["status"] == "pass"
    assert outcome["url"] == requests[0].url
    assert outcome["provider"] == "ga4"
    # What matched is in the report, so a hit sent in the body can be checked without DevTools.
    assert outcome["body"] == requests[0].body
    assert outcome["checks"] == [
        {"key": "en", "match": "exact", "expected": "page_view", "actual": "page_view", "passed": True},
        {"key": "ep.content_group", "match": "exact", "expected": "ana-sayfa", "actual": "ana-sayfa", "passed": True},
    ]


def test_a_request_without_a_body_reports_none() -> None:
    outcome = evaluate(1, criterion("gtm", ("id", "exact", "GTM-MRDH2NZ")), [Captured(GTM, None)], PROVIDERS)

    assert outcome["body"] is None
    assert outcome["checks"][0]["actual"] == "GTM-MRDH2NZ"


def test_conditions_met_by_different_events_do_not_pass() -> None:
    requests = [Captured(GA4, "en=page_view\nep.content_group=ana-sayfa")]
    page_view = criterion("ga4", ("en", "exact", "page_view"), ("ep.content_group", "exact", "ana-sayfa"))

    outcome = evaluate(2, page_view, requests, PROVIDERS)

    assert outcome["status"] == "fail"
    assert (outcome["criterion"], outcome["requests"], outcome["events"]) == (2, 1, 2)
    assert outcome["closest_body"] == requests[0].body
    assert outcome["closest"] == [
        {"key": "en", "match": "exact", "expected": "page_view", "actual": "page_view", "passed": True},
        {"key": "ep.content_group", "match": "exact", "expected": "ana-sayfa", "actual": None, "passed": False},
    ]


def test_requests_of_another_provider_are_not_looked_at() -> None:
    outcome = evaluate(1, criterion("gtm", ("id", "exact", "GTM-MRDH2NZ")), [Captured(GA4, None)], PROVIDERS)

    assert (outcome["status"], outcome["requests"], outcome["events"]) == ("fail", 0, 0)
    assert "closest" not in outcome


def test_a_gtm_container_id_is_read_from_the_query_and_items_from_the_body() -> None:
    gtm = evaluate(1, criterion("gtm", ("id", "exact", "GTM-MRDH2NZ")), [Captured(GTM, None)], PROVIDERS)
    item = evaluate(
        1,
        criterion("ga4", ("pr1.li", "exact", "anasayfa/one-cikan/en-yeni"), ("pr1.id", "regex", r"^\d+$")),
        [Captured(GA4, "en=view_item_list&pr1=id19760160~lianasayfa%2Fone-cikan%2Fen-yeni~brilan")],
        PROVIDERS,
    )

    assert gtm["status"] == item["status"] == "pass"


def test_an_exists_condition_reports_no_expected_value() -> None:
    outcome = evaluate(1, criterion("ga4", ("ep.search_id", "exists", None)), [Captured(GA4, None)], PROVIDERS)

    assert outcome["closest"] == [{"key": "ep.search_id", "match": "exists", "actual": None, "passed": False}]
