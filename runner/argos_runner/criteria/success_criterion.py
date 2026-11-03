from pydantic import BaseModel, ConfigDict, Field, model_validator

from argos_runner.criteria.matching import MatchRule
from argos_runner.criteria.providers import CUSTOM_PROVIDER

CUSTOM_URL_KEY = "url"


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


class SuccessCriterion(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    provider: Provider
    conditions: list[Condition]

