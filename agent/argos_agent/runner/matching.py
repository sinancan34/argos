"""How a success criterion compares a value it finds in a request with the value it expects."""

import math
import re
from collections.abc import Callable
from dataclasses import dataclass

Expected = str | float | None

TEXT_MATCHES: dict[str, Callable[[str, str], bool]] = {
    "exact": lambda actual, expected: actual == expected,
    "contains": lambda actual, expected: expected in actual,
    "startsWith": lambda actual, expected: actual.startswith(expected),
    "endsWith": lambda actual, expected: actual.endswith(expected),
    "regex": lambda actual, expected: re.search(expected, actual) is not None,
}
NUMBER_MATCHES: dict[str, Callable[[float, float], bool]] = {
    "gt": lambda actual, expected: actual > expected,
    "lt": lambda actual, expected: actual < expected,
}
# Not float()'s syntax: `1_000`, ` 5 `, `inf` and `1e3` are not values a pixel sends as a number.
DECIMAL = re.compile(r"^[+-]?(\d+(\.\d*)?|\.\d+)$")
EXISTS = "exists"
MATCH_TYPES = (EXISTS, *TEXT_MATCHES, *NUMBER_MATCHES)


@dataclass(frozen=True)
class MatchRule:
    match: str
    value: Expected = None


def _number(value: Expected) -> float | None:
    """A finite number from a JSON number or a plain decimal string (`-1.5`); anything else is None."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str) and not DECIMAL.match(value):
        return None
    try:
        number = float(value)
    except OverflowError:
        # A JSON integer past float's range.
        return None
    return number if math.isfinite(number) else None


def rule_problems(rule: MatchRule) -> list[str]:
    """Every way the rule cannot be applied; a rule without problems never raises in `matches`."""
    if rule.match not in MATCH_TYPES:
        return [f"unknown match '{rule.match}': use one of {', '.join(MATCH_TYPES)}"]
    if rule.match == EXISTS:
        return [] if rule.value is None else ["'exists' takes no value"]
    if rule.match in NUMBER_MATCHES:
        return [] if _number(rule.value) is not None else [f"'{rule.match}' needs a number, got {rule.value!r}"]
    if not isinstance(rule.value, str) or not rule.value:
        return [f"'{rule.match}' needs a string value, got {rule.value!r}"]
    if rule.match == "regex":
        try:
            re.compile(rule.value)
        except re.error as exc:
            return [f"invalid regex {rule.value!r}: {exc}"]
    return []


def matches(rule: MatchRule, actual: str) -> bool:
    """Whether `actual` satisfies a rule that has no problems; a non-numeric value fails `gt` and `lt`."""
    if rule.match == EXISTS:
        return True
    if rule.match in NUMBER_MATCHES:
        number, expected = _number(actual), _number(rule.value)
        return number is not None and expected is not None and NUMBER_MATCHES[rule.match](number, expected)
    return TEXT_MATCHES[rule.match](actual, str(rule.value))


def url_matches(rule: MatchRule, url: str) -> bool:
    """A URL rule matches the full URL or the URL without its query."""
    return matches(rule, url) or matches(rule, url.split("?", 1)[0])
