from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError

from goal import Goal
from providers import CUSTOM_PROVIDER, ProviderDefinition

NEW_TAB_PLACEHOLDER = "$new_tab"
# A selector that has not shown up within a minute is broken, not slow.
MAX_TIMEOUT_SECONDS = 60


class ScenarioError(Exception):
    """The scenario file could not be read or does not match the step format."""


class Step(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    action: str = Field(min_length=1)
    params: dict[str, Any]
    goals: list[Goal] | None = Field(default=None, min_length=1)


class _StepShape(BaseModel):
    """A step whose goals are checked one by one, so errors name the goal by its number."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    action: str = Field(min_length=1)
    params: dict[str, Any]
    goals: list[dict[str, Any]] | None = Field(default=None, min_length=1)


class _Params(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    target_id: Literal["$new_tab"] | None = None


class _NavigateParams(_Params):
    url: str = Field(min_length=1)


class _ElementParams(_Params):
    selector: str = Field(min_length=1)
    timeout: float = Field(gt=0, lt=MAX_TIMEOUT_SECONDS, strict=True)


ACTION_PARAMS: dict[str, type[_Params]] = {
    "navigate": _NavigateParams,
    "wait_for": _ElementParams,
    "click_element": _ElementParams,
}

_STEPS = TypeAdapter(Annotated[list[_StepShape], Field(min_length=1)])


def _describe(exc: ValidationError) -> str:
    return "; ".join(
        f"{'.'.join(map(str, error['loc']))}: {error['msg']}" if error["loc"] else error["msg"]
        for error in exc.errors()
    )


def _check_params(path: Path, number: int, step: _StepShape) -> None:
    params = ACTION_PARAMS.get(step.action)
    if params is None:
        raise ScenarioError(f"invalid scenario {path}: step {number} uses unsupported action '{step.action}'")
    try:
        params.model_validate(step.params)
    except ValidationError as exc:
        raise ScenarioError(f"invalid scenario {path}: step {number} ({step.action}) {_describe(exc)}") from exc


def _parse_goal(
    path: Path, number: int, goal_number: int, raw: dict[str, Any], providers: dict[str, ProviderDefinition]
) -> Goal:
    where = f"invalid scenario {path}: step {number} goal {goal_number}"
    try:
        goal = Goal.model_validate(raw)
    except ValidationError as exc:
        raise ScenarioError(f"{where} {_describe(exc)}") from exc

    name = goal.provider.name
    if name != CUSTOM_PROVIDER and name not in providers:
        raise ScenarioError(f"{where} uses unknown provider '{name}'")
    return goal


def _to_step(path: Path, number: int, shape: _StepShape, providers: dict[str, ProviderDefinition]) -> Step:
    _check_params(path, number, shape)
    goals = (
        None
        if shape.goals is None
        else [_parse_goal(path, number, goal_number, raw, providers) for goal_number, raw in enumerate(shape.goals, 1)]
    )
    return Step(action=shape.action, params=shape.params, goals=goals)


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
