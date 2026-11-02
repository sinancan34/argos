from pathlib import Path
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError

# Every MCP tool that looks for an element takes a `timeout`.
TIMEOUT_ACTIONS = frozenset(
    {"click_element", "wait_for", "send_keys", "clear_input", "set_value", "select_option", "send_file"}
)
# The MCP server cuts every tool off at 60 seconds, so a timeout must end before that.
MAX_TIMEOUT_SECONDS = 60


class ScenarioError(Exception):
    """The scenario file could not be read or does not match the step format."""


class Step(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    action: str = Field(min_length=1)
    params: dict[str, Any]


_STEPS = TypeAdapter(Annotated[list[Step], Field(min_length=1)])


def _has_valid_timeout(step: Step) -> bool:
    timeout = step.params.get("timeout")
    is_number = isinstance(timeout, (int, float)) and not isinstance(timeout, bool)
    return is_number and 0 < timeout < MAX_TIMEOUT_SECONDS


def load_steps(path: Path) -> list[Step]:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ScenarioError(f"cannot read {path}: {exc}") from exc

    try:
        steps = _STEPS.validate_json(content)
    except ValidationError as exc:
        raise ScenarioError(f"invalid scenario {path}: {exc}") from exc

    for number, step in enumerate(steps, start=1):
        if step.action in TIMEOUT_ACTIONS and not _has_valid_timeout(step):
            raise ScenarioError(
                f"invalid scenario {path}: step {number} ({step.action}) "
                f"requires a timeout between 0 and {MAX_TIMEOUT_SECONDS} seconds"
            )
    return steps
