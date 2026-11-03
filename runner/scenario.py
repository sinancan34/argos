from pathlib import Path
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError

from providers import CUSTOM_PROVIDER, ProviderDefinition
from success_criterion import SuccessCriterion


class ScenarioError(Exception):
    """The scenario file could not be read or does not match the step format."""


class Action(BaseModel):
    """A chrome-devtools-mcp tool call; the server, not the file, says which actions and params exist."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    action: str = Field(min_length=1)
    params: dict[str, Any]


class Step(BaseModel):
    """Actions run in order; the success criteria judge the requests sent while any of them ran."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario: list[Action] = Field(min_length=1)
    success_criteria: list[SuccessCriterion] | None = Field(default=None, min_length=1)


class _StepShape(BaseModel):
    """A step whose success criteria are checked one by one, so errors name each by its number."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario: list[Action] = Field(min_length=1)
    success_criteria: list[dict[str, Any]] | None = Field(default=None, min_length=1)


_STEPS = TypeAdapter(Annotated[list[_StepShape], Field(min_length=1)])


def _describe(exc: ValidationError) -> str:
    return "; ".join(
        f"{'.'.join(map(str, error['loc']))}: {error['msg']}" if error["loc"] else error["msg"]
        for error in exc.errors()
    )


def _parse_criterion(
    path: Path, number: int, criterion_number: int, raw: dict[str, Any], providers: dict[str, ProviderDefinition]
) -> SuccessCriterion:
    where = f"invalid scenario {path}: step {number} success criterion {criterion_number}"
    try:
        criterion = SuccessCriterion.model_validate(raw)
    except ValidationError as exc:
        raise ScenarioError(f"{where} {_describe(exc)}") from exc

    name = criterion.provider.name
    if name != CUSTOM_PROVIDER and name not in providers:
        raise ScenarioError(f"{where} uses unknown provider '{name}'")
    return criterion


def _to_step(path: Path, number: int, shape: _StepShape, providers: dict[str, ProviderDefinition]) -> Step:
    raw_criteria = shape.success_criteria
    criteria = (
        None
        if raw_criteria is None
        else [_parse_criterion(path, number, index, raw, providers) for index, raw in enumerate(raw_criteria, 1)]
    )
    return Step(scenario=shape.scenario, success_criteria=criteria)


def load_steps(path: Path, providers: dict[str, ProviderDefinition]) -> list[Step]:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ScenarioError(f"cannot read {path}: {exc}") from exc

    try:
        shapes = _STEPS.validate_json(content)
    except ValidationError as exc:
        raise ScenarioError(f"invalid scenario {path}: {exc}") from exc

    return [_to_step(path, number, shape, providers) for number, shape in enumerate(shapes, start=1)]
