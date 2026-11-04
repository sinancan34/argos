from collections.abc import Callable
from pathlib import Path
from typing import Any

from argos_runner.scenario.model import Action

# An action named with this prefix is a runner tool, for what chrome-devtools-mcp has no tool for;
# the runner sends it as the MCP action it expands to.
CUSTOM_PREFIX = "custom_"

# Moves the page to the element as a person would, in eased bursts with pauses; see the script.
HUMAN_SCROLL_PATH = Path(__file__).parents[1] / "data" / "human_scroll.js"
_HUMAN_SCROLL = HUMAN_SCROLL_PATH.read_text(encoding="utf-8")


def _scroll(params: dict[str, Any]) -> Action:
    return Action(action="evaluate_script", params={"function": _HUMAN_SCROLL, "args": [params["uid"]]})


_ELEMENT = {"type": "string", "description": "The uid of an element on the page from the page content snapshot"}

# Each tool's params as an MCP input schema, so validate.py checks them as it checks MCP tools;
# an element param takes a selector under `uid`, as click and hover do.
SCHEMAS: dict[str, dict[str, Any]] = {
    "custom_scroll": {"type": "object", "properties": {"uid": _ELEMENT}, "required": ["uid"]},
}
_EXPANSIONS: dict[str, Callable[[dict[str, Any]], Action]] = {"custom_scroll": _scroll}


def expand(action: Action) -> Action:
    """The MCP action a runner tool stands for, its element params already uids; any other action as it is."""
    to_mcp = _EXPANSIONS.get(action.action)
    return to_mcp(action.params) if to_mcp else action
