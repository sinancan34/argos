from pathlib import Path
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError

from providers import CUSTOM_PROVIDER, ProviderDefinition
from success_criterion import SuccessCriterion


class ScenarioError(Exception):
    """The scenario file could not be read or does not match the step format."""


class Action(BaseModel):
    """A chrome-devtools-mcp tool call, named and with params as in MCP; validate.py checks them against the server."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    action: str = Field(min_length=1)
    params: dict[str, Any]


class Step(BaseModel):
    """Actions run in order; the success criteria judge the requests sent while any of them ran."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario: list[Action] = Field(min_length=1)
    success_criteria: list[SuccessCriterion] | None = Field(default=None, min_length=1)


_STEPS = TypeAdapter(Annotated[list[Step], Field(min_length=1)])


def _where(loc: tuple[int | str, ...]) -> str:
    """Numbers steps and criteria from 1: (1, 'success_criteria', 0, 'x') reads `step 2 success criterion 1 x`."""
    match loc:
        case (int() as step, "success_criteria", int() as criterion, *rest):
            head = f"step {step + 1} success criterion {criterion + 1}"
        case (int() as step, *rest):
            head = f"step {step + 1}"
        case _:
            head, rest = "", list(loc)
    return " ".join(part for part in (head, ".".join(map(str, rest))) if part)


def _describe(exc: ValidationError) -> str:
    return "; ".join(
        f"{where}: {error['msg']}" if (where := _where(error["loc"])) else error["msg"] for error in exc.errors()
    )


def _unknown_provider(steps: list[Step], providers: dict[str, ProviderDefinition]) -> str | None:
    return next(
        (
            f"step {number} success criterion {criterion_number} uses unknown provider '{criterion.provider.name}'"
            for number, step in enumerate(steps, start=1)
            for criterion_number, criterion in enumerate(step.success_criteria or [], start=1)
            if criterion.provider.name != CUSTOM_PROVIDER and criterion.provider.name not in providers
        ),
        None,
    )


def load_steps(path: Path, providers: dict[str, ProviderDefinition]) -> list[Step]:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ScenarioError(f"cannot read {path}: {exc}") from exc

    try:
        steps = _STEPS.validate_json(content)
    except ValidationError as exc:
        raise ScenarioError(f"invalid scenario {path}: {_describe(exc)}") from exc

    unknown = _unknown_provider(steps, providers)
    if unknown:
        raise ScenarioError(f"invalid scenario {path}: {unknown}")
    return steps
