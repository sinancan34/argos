import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

MatchType = Literal["exact", "contains", "startsWith", "endsWith", "regex", "exists"]


class MatchRule(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    match: MatchType
    value: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def _value_fits_match(self) -> "MatchRule":
        if self.match == "exists":
            if self.value is not None:
                raise ValueError("'exists' does not take a value")
            return self
        if self.value is None:
            raise ValueError(f"'{self.match}' requires a value")
        if self.match == "regex":
            try:
                re.compile(self.value)
            except re.error as exc:
                raise ValueError(f"invalid regex: {exc}") from exc
        return self


def matches(rule: MatchRule, actual: str) -> bool:
    if rule.match == "exists":
        return True
    if rule.match == "exact":
        return actual == rule.value
    if rule.match == "contains":
        return rule.value in actual
    if rule.match == "startsWith":
        return actual.startswith(rule.value)
    if rule.match == "endsWith":
        return actual.endswith(rule.value)
    return re.search(rule.value, actual) is not None


def url_matches(rule: MatchRule, url: str) -> bool:
    return matches(rule, url) or matches(rule, url.split("?", 1)[0])
