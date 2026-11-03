from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, RootModel, ValidationError, model_validator

from argos_runner.criteria.matching import MatchRule

CUSTOM_PROVIDER = "custom"
DEFAULT_PROVIDERS_PATH = Path(__file__).parents[1] / "data" / "providers.json"


class ProvidersError(Exception):
    """The provider definitions could not be read or do not match the format."""


class UrlRule(MatchRule):
    @model_validator(mode="after")
    def _must_narrow_requests(self) -> "UrlRule":
        if self.match == "exists":
            raise ValueError("a url rule cannot use 'exists'")
        return self


class ProviderDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    urls: list[UrlRule] = Field(min_length=1)


class _Providers(RootModel[dict[str, ProviderDefinition]]):
    @model_validator(mode="after")
    def _custom_is_reserved(self) -> "_Providers":
        if CUSTOM_PROVIDER in self.root:
            raise ValueError(f"'{CUSTOM_PROVIDER}' is a reserved provider name")
        return self


def load_providers(path: Path = DEFAULT_PROVIDERS_PATH) -> dict[str, ProviderDefinition]:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ProvidersError(f"cannot read {path}: {exc}") from exc

    try:
        return _Providers.model_validate_json(content).root
    except ValidationError as exc:
        raise ProvidersError(f"invalid providers {path}: {exc}") from exc
