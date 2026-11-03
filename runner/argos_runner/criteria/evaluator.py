from typing import Any
from urllib.parse import parse_qsl, urlsplit

from argos_runner.criteria.param_splitter import split_fields
from argos_runner.criteria.matching import matches, url_matches
from argos_runner.criteria.network_capture import CapturedRequest
from argos_runner.criteria.providers import CUSTOM_PROVIDER, ProviderDefinition
from argos_runner.criteria.success_criterion import Condition, Provider, SuccessCriterion

Event = dict[str, list[str]]
Providers = dict[str, ProviderDefinition]


def _group(pairs: list[tuple[str, str]]) -> Event:
    event: Event = {}
    for key, value in pairs:
        event[key] = [*event.get(key, []), value]
    return event


def _to_event(pairs: list[tuple[str, str]]) -> Event:
    return _group([*pairs, *split_fields(_group(pairs))])


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


def is_wanted(criteria: list[SuccessCriterion], url: str, providers: Providers) -> bool:
    return any(_selects(criterion.provider, url, providers) for criterion in criteria)


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


def _evaluate(
    number: int, criterion: SuccessCriterion, requests: list[CapturedRequest], providers: Providers
) -> dict[str, Any]:
    selected = [request for request in requests if _selects(criterion.provider, request.url, providers)]
    results = [
        (request.url, [_check(condition, event) for condition in criterion.conditions])
        for request in selected
        for event in request_events(request)
    ]
    matched = [url for url, checks in results if all(check["passed"] for check in checks)]
    summary = {
        "criterion": number,
        "status": "pass" if matched else "fail",
        "provider": criterion.provider.model_dump(exclude_none=True),
        "conditions": [condition.model_dump(exclude_none=True) for condition in criterion.conditions],
    }
    if matched:
        return {**summary, "matched_events": len(matched), "url": matched[0]}

    report = {**summary, "requests": len(selected), "events": len(results)}
    if not results:
        return report
    closest_url, closest = max(results, key=lambda result: sum(check["passed"] for check in result[1]))
    return {**report, "closest_url": closest_url, "closest": closest}


def with_page_requests(
    outcomes: list[dict[str, Any]], criteria: list[SuccessCriterion], page_urls: list[str], providers: Providers
) -> list[dict[str, Any]]:
    """Adds to each failed criterion how many matching requests the page itself reports."""
    return [
        outcome
        if outcome["status"] == "pass"
        else {**outcome, "page_requests": sum(_selects(criterion.provider, url, providers) for url in page_urls)}
        for outcome, criterion in zip(outcomes, criteria)
    ]


def evaluate_criteria(
    criteria: list[SuccessCriterion], requests: list[CapturedRequest], providers: Providers
) -> list[dict[str, Any]]:
    """Evaluates each criterion on its own, so one failing criterion never hides another's result."""
    return [_evaluate(number, criterion, requests, providers) for number, criterion in enumerate(criteria, start=1)]
