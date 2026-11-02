from typing import Any
from urllib.parse import parse_qsl, urlsplit

from ga4_items import item_fields
from goal import Condition, Goal, Provider
from matching import matches, url_matches
from network_capture import CapturedRequest
from providers import CUSTOM_PROVIDER, ProviderDefinition

Event = dict[str, list[str]]
Providers = dict[str, ProviderDefinition]


def _group(pairs: list[tuple[str, str]]) -> Event:
    event: Event = {}
    for key, value in pairs:
        event[key] = [*event.get(key, []), value]
    return event


def _to_event(pairs: list[tuple[str, str]]) -> Event:
    return _group([*pairs, *item_fields(_group(pairs))])


def request_events(request: CapturedRequest) -> list[Event]:
    """Splits a request into events: query params alone, or merged with each POST body line."""
    query = parse_qsl(urlsplit(request.url).query, keep_blank_values=True)
    lines = [line for line in (request.body or "").splitlines() if line]
    if not lines:
        return [_to_event(query)]
    return [_to_event(query + parse_qsl(line, keep_blank_values=True)) for line in lines]


def _selects(provider: Provider, url: str, providers: Providers) -> bool:
    rules = provider.params if provider.name == CUSTOM_PROVIDER else providers[provider.name].urls
    return any(url_matches(rule, url) for rule in rules)


def is_wanted(goals: list[Goal], url: str, providers: Providers) -> bool:
    return any(_selects(goal.provider, url, providers) for goal in goals)


def _check(condition: Condition, event: Event) -> dict[str, Any]:
    values = event.get(condition.key, [])
    matched = [value for value in values if matches(condition, value)]
    actual = (matched or values or [None])[0]
    expected = {} if condition.value is None else {"expected": condition.value}
    return {
        "key": condition.key,
        "match": condition.match,
        **expected,
        "actual": actual,
        "passed": bool(matched),
    }


def _passed_count(checks: list[dict[str, Any]]) -> int:
    return sum(check["passed"] for check in checks)


def _evaluate(number: int, goal: Goal, requests: list[CapturedRequest], providers: Providers) -> dict[str, Any]:
    selected = [request for request in requests if _selects(goal.provider, request.url, providers)]
    results = [
        (request.url, [_check(condition, event) for condition in goal.conditions])
        for request in selected
        for event in request_events(request)
    ]
    matched = [url for url, checks in results if all(check["passed"] for check in checks)]
    summary = {
        "goal": number,
        "status": "pass" if matched else "fail",
        "provider": goal.provider.model_dump(exclude_none=True),
        "conditions": [condition.model_dump(exclude_none=True) for condition in goal.conditions],
    }
    if matched:
        return {**summary, "matched_events": len(matched), "url": matched[0]}

    report = {**summary, "requests": len(selected), "events": len(results)}
    if not results:
        return report
    closest_url, closest = max(results, key=lambda result: _passed_count(result[1]))
    return {**report, "closest_url": closest_url, "closest": closest}


def with_page_requests(
    outcomes: list[dict[str, Any]], goals: list[Goal], page_urls: list[str], providers: Providers
) -> list[dict[str, Any]]:
    """Adds to each failed goal how many matching requests the page itself reports."""
    return [
        outcome
        if outcome["status"] == "pass"
        else {**outcome, "page_requests": sum(_selects(goal.provider, url, providers) for url in page_urls)}
        for outcome, goal in zip(outcomes, goals)
    ]


def evaluate_goals(goals: list[Goal], requests: list[CapturedRequest], providers: Providers) -> list[dict[str, Any]]:
    """Evaluates each goal on its own, so one failing goal never hides another's result."""
    return [_evaluate(number, goal, requests, providers) for number, goal in enumerate(goals, start=1)]
