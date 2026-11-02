from pathlib import Path
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError


class ScenarioError(Exception):
    """The scenario file could not be read or does not match the step format."""


class Step(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    action: str = Field(min_length=1)
    params: dict[str, Any]


_STEPS = TypeAdapter(Annotated[list[Step], Field(min_length=1)])


def load_steps(path: Path) -> list[Step]:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ScenarioError(f"cannot read {path}: {exc}") from exc

    try:
        return _STEPS.validate_json(content)
    except ValidationError as exc:
        raise ScenarioError(f"invalid scenario {path}: {exc}") from exc
