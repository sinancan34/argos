import json
from pathlib import Path

_SHARED_DIR = Path(__file__).resolve().parent.parent.parent / "shared"

with open(_SHARED_DIR / "validations.json") as f:
    _defs = json.load(f)

with open(_SHARED_DIR / "commands.json") as f:
    _commands = json.load(f)


def _resolve_source(source: str) -> list[str]:
    """Resolve 'commands.matchTypes' style references to actual values."""
    file_key, field_key = source.split(".")
    if file_key == "commands":
        return _commands[field_key]
    raise ValueError(f"Unknown source: {source}")


ENUMS: dict[str, list[str]] = _defs["enums"]
SCENARIO_FIELDS: dict[str, dict] = _defs["scenario"]
URL_CHECK_FIELDS: dict[str, dict] = _defs["urlCheck"]
PARAM_CHECK_FIELDS: dict[str, dict] = _defs["paramCheck"]
SELECTOR_FIELDS: dict[str, dict] = _defs["selector"]


def get_enum_values(field_def: dict) -> list[str]:
    """Return enum values for a field, resolving source references."""
    if "source" in field_def:
        return _resolve_source(field_def["source"])
    raise ValueError("Field has no 'source' key")


def pydantic_field_kwargs(field_def: dict) -> dict:
    """Convert a shared field definition to Pydantic Field() kwargs."""
    kwargs: dict = {}
    if "minLength" in field_def:
        kwargs["min_length"] = field_def["minLength"]
    if "maxLength" in field_def:
        kwargs["max_length"] = field_def["maxLength"]
    if "min" in field_def:
        kwargs["ge"] = field_def["min"]
    if "max" in field_def:
        kwargs["le"] = field_def["max"]
    if field_def.get("positive"):
        kwargs["gt"] = 0
    if "default" in field_def:
        kwargs["default"] = field_def["default"]
    if "minItems" in field_def:
        kwargs["min_length"] = field_def["minItems"]
    return kwargs
