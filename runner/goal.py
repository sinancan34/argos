from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError, model_validator

from matching import MatchRule
from providers import CUSTOM_PROVIDER, ProviderDefinition

CUSTOM_URL_KEY = "url"


class GoalError(Exception):
    """The goal file could not be read or does not match the goal format."""


class Condition(MatchRule):
    key: str = Field(min_length=1)


class Provider(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1)
    params: list[Condition]

    @model_validator(mode="after")
    def _params_fit_provider(self) -> "Provider":
        if self.name != CUSTOM_PROVIDER:
            if self.params:
                raise ValueError(f"provider '{self.name}' takes no params")
            return self
        if len(self.params) != 1 or self.params[0].key != CUSTOM_URL_KEY:
            raise ValueError(f"provider '{CUSTOM_PROVIDER}' requires exactly one '{CUSTOM_URL_KEY}' param")
        if self.params[0].match == "exists":
            raise ValueError(f"the '{CUSTOM_URL_KEY}' param cannot use 'exists'")
        return self


class Goal(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    provider: Provider
    conditions: list[Condition]


_GOALS = TypeAdapter(Annotated[list[Goal], Field(min_length=1)])


def load_goals(path: Path, providers: dict[str, ProviderDefinition]) -> list[Goal]:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise GoalError(f"cannot read {path}: {exc}") from exc

    try:
        goals = _GOALS.validate_json(content)
    except ValidationError as exc:
        raise GoalError(f"invalid goal {path}: {exc}") from exc

    for number, goal in enumerate(goals, start=1):
        name = goal.provider.name
        if name != CUSTOM_PROVIDER and name not in providers:
            raise GoalError(f"invalid goal {path}: goal {number} uses unknown provider '{name}'")
    return goals
