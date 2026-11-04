"""Judges a step's success criteria against the requests captured while the step ran."""

from collections.abc import Sequence
from typing import Any

from argos_agent.runner.event_fields import Event, request_events
from argos_agent.runner.matching import matches
from argos_agent.runner.network import Captured
from argos_agent.runner.scenario import Condition, Criterion, Providers

Outcome = dict[str, Any]


def _selects(provider: str, url: str, providers: Providers) -> bool:
    return any(matches(rule, url) for rule in providers[provider])


def wanted(url: str, criteria: Sequence[Criterion], providers: Providers) -> bool:
    """Whether a request belongs to a provider of any criterion, so its body is worth reading."""
    return any(_selects(criterion.provider, url, providers) for criterion in criteria)


def _check(condition: Condition, event: Event) -> dict[str, Any]:
    actual = event.get(condition.key)
    expected = {} if condition.rule.value is None else {"expected": condition.rule.value}
    return {
        "key": condition.key,
        "match": condition.rule.match,
        **expected,
        "actual": actual,
        "passed": actual is not None and matches(condition.rule, actual),
    }


def evaluate(number: int, criterion: Criterion, requests: Sequence[Captured], providers: Providers) -> Outcome:
    """`pass` when a single event of the provider's requests meets every condition; otherwise the closest event."""
    selected = [request for request in requests if _selects(criterion.provider, request.url, providers)]
    results = [
        (request, [_check(condition, event) for condition in criterion.conditions])
        for request in selected
        for event in request_events(request.url, request.body)
    ]
    summary: Outcome = {"criterion": number, "provider": criterion.provider}
    matched = [(request, checks) for request, checks in results if all(check["passed"] for check in checks)]
    if matched:
        # The values the conditions saw and the body they came from, so a body-only hit can be checked by eye.
        request, checks = matched[0]
        return {**summary, "status": "pass", "url": request.url, "body": request.body, "checks": checks}
    failed: Outcome = {**summary, "status": "fail", "requests": len(selected), "events": len(results)}
    if not results:
        return failed
    closest_request, closest = max(results, key=lambda result: sum(check["passed"] for check in result[1]))
    return {**failed, "closest_url": closest_request.url, "closest_body": closest_request.body, "closest": closest}
