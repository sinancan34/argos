import json
from pathlib import Path

_SHARED_FILE = Path(__file__).resolve().parent.parent.parent / "shared" / "commands.json"

with open(_SHARED_FILE) as f:
    _defs = json.load(f)

VALID_COMMANDS: set[str] = {c["command"] for c in _defs["commands"]}
COMMAND_PARAMS: dict[str, list[dict]] = {
    c["command"]: c["params"] for c in _defs["commands"]
}
VALID_SELECTOR_STRATEGIES: set[str] = set(_defs["selectorStrategies"])
VALID_MATCH_TYPES: list[str] = _defs["matchTypes"]
