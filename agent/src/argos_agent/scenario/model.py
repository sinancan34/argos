"""The scenario format: loads a scenario JSON and refuses it before a browser starts if it cannot run.

A scenario is a list of steps. Each step's actions are Playwright MCP tool calls, checked against the pinned
server's tool catalog; its success criteria name a provider (see providers.py) and conditions.
"""

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from jsonschema import Draft202012Validator

from argos_agent.playwright_mcp.catalog import ToolCatalog, load_catalog, schema_problems
from argos_agent.scenario.matching import MatchRule, rule_problems

RULE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"match": {"type": "string"}, "value": {"type": ["string", "number"]}},
    "required": ["match"],
    "additionalProperties": False,
}


CONDITION_SCHEMA: dict[str, Any] = {
    **RULE_SCHEMA,
    "properties": {**RULE_SCHEMA["properties"], "key": {"type": "string", "minLength": 1}},
    "required": ["key", "match"],
}
ACTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"action": {"type": "string"}, "params": {"type": "object"}},
    "required": ["action", "params"],
    "additionalProperties": False,
}
# A step, criterion or condition is numbered from 1 under the name of the list that holds it.
SECTIONS = {"scenario": "action", "success_criteria": "criterion", "conditions": "condition"}


def scenario_schema(provider_names: list[str]) -> dict[str, Any]:
    criterion = {
        "type": "object",
        "properties": {
            "provider": {
                "type": "object",
                # params is kept for the scenario format; no provider takes one yet.
                "properties": {"name": {"enum": provider_names}, "params": {"type": "array", "maxItems": 0}},
                "required": ["name", "params"],
                "additionalProperties": False,
            },
            "conditions": {"type": "array", "minItems": 1, "items": CONDITION_SCHEMA},
        },
        "required": ["provider", "conditions"],
        "additionalProperties": False,
    }
    step = {
        "type": "object",
        "properties": {
            "scenario": {"type": "array", "minItems": 1, "items": ACTION_SCHEMA},
            "success_criteria": {"type": "array", "items": criterion},
        },
        "required": ["scenario"],
        "additionalProperties": False,
    }
    return {"type": "array", "minItems": 1, "items": step}


class ScenarioError(ValueError):
    """A scenario or provider file that cannot be run; `problems` names every reason."""

    def __init__(self, problems: list[str]) -> None:
        super().__init__("; ".join(problems))
        self.problems = tuple(problems)


@dataclass(frozen=True)
class Action:
    tool: str
    params: Mapping[str, Any]


@dataclass(frozen=True)
class Condition:
    key: str
    rule: MatchRule


@dataclass(frozen=True)
class Criterion:
    provider: str
    conditions: tuple[Condition, ...]


@dataclass(frozen=True)
class Step:
    actions: tuple[Action, ...]
    criteria: tuple[Criterion, ...]


Providers = Mapping[str, tuple[MatchRule, ...]]


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise ScenarioError([f"cannot read {path}: {exc}"]) from exc


def rule(raw: Mapping[str, Any]) -> MatchRule:
    return MatchRule(raw["match"], raw.get("value"))


def _step(raw: Mapping[str, Any]) -> Step:
    actions = tuple(Action(action["action"], MappingProxyType(action["params"])) for action in raw["scenario"])
    criteria = tuple(
        Criterion(
            criterion["provider"]["name"],
            tuple(Condition(condition["key"], rule(condition)) for condition in criterion["conditions"]),
        )
        for criterion in raw.get("success_criteria", [])
    )
    return Step(actions, criteria)


def step_location(path: Sequence[str | int]) -> str:
    """`[0, 'success_criteria', 1, 'provider', 'name']` as `step 1 criterion 2 provider.name`."""
    numbered: list[str] = []
    keys: list[str] = []
    label = "step"
    for index, part in enumerate(path):
        if isinstance(part, int):
            numbered.append(f"{label} {part + 1}")
        elif index + 1 < len(path) and isinstance(path[index + 1], int):
            label = SECTIONS.get(part, part)
        else:
            keys.append(part)
    return " ".join([*numbered, ".".join(keys)]).strip()


def _matching(items: Any, schema: dict[str, Any]) -> list[tuple[int, Any]]:
    """Each item of a list that matches `schema`, numbered from 1; the shape check reports the others."""
    if not isinstance(items, list):
        return []
    validator = Draft202012Validator(schema)
    return [(number, item) for number, item in enumerate(items, start=1) if validator.is_valid(item)]


def _step_problems(number: int, step: Any, catalog: ToolCatalog) -> list[str]:
    """The problems of each well-formed action's params and condition's rule, even when the rest of the step is not."""
    if not isinstance(step, dict):
        return []
    actions = [
        f"step {number} action {index} {action['action']}: {problem}"
        for index, action in _matching(step.get("scenario"), ACTION_SCHEMA)
        for problem in catalog.problems(action["action"], action["params"])
    ]
    criteria = step.get("success_criteria")
    conditions = [
        f"step {number} criterion {index} condition {position} {condition['key']}: {problem}"
        for index, criterion in enumerate(criteria if isinstance(criteria, list) else [], start=1)
        if isinstance(criterion, dict)
        for position, condition in _matching(criterion.get("conditions"), CONDITION_SCHEMA)
        for problem in rule_problems(rule(condition))
    ]
    return [*actions, *conditions]


def load_scenario(path: Path, providers: Providers) -> tuple[Step, ...]:
    """The scenario's steps, or a ScenarioError naming every problem at once: the shape, then the params of each
    well-formed action and the rule of each well-formed condition."""
    content = read_json(path)
    catalog = load_catalog()
    steps = content if isinstance(content, list) else []
    problems = [
        *schema_problems(scenario_schema(list(providers)), content, step_location),
        *(problem for number, step in enumerate(steps, start=1) for problem in _step_problems(number, step, catalog)),
    ]
    if problems:
        raise ScenarioError(problems)
    return tuple(_step(raw) for raw in content)
