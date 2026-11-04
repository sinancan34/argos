"""Loads a scenario JSON and refuses it before a browser starts if it cannot run.

A scenario is a list of steps. Each step's actions are Playwright MCP tool calls, checked against the pinned
server's tool catalog; its success criteria name a provider of PROVIDERS (ga4 or gtm) and conditions.
"""

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from jsonschema import Draft202012Validator

from argos_agent.playwright_mcp.catalog import ToolCatalog, describe, load_catalog
from argos_agent.runner.matching import MatchRule, rule_problems

RULE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"match": {"type": "string"}, "value": {"type": ["string", "number"]}},
    "required": ["match"],
    "additionalProperties": False,
}


def scenario_schema(provider_names: list[str]) -> dict[str, Any]:
    condition = {**RULE_SCHEMA, "properties": {**RULE_SCHEMA["properties"], "key": {"type": "string", "minLength": 1}}}
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
            "conditions": {"type": "array", "minItems": 1, "items": {**condition, "required": ["key", "match"]}},
        },
        "required": ["provider", "conditions"],
        "additionalProperties": False,
    }
    action = {
        "type": "object",
        "properties": {"action": {"type": "string"}, "params": {"type": "object"}},
        "required": ["action", "params"],
        "additionalProperties": False,
    }
    step = {
        "type": "object",
        "properties": {
            "scenario": {"type": "array", "minItems": 1, "items": action},
            "success_criteria": {"type": "array", "items": criterion},
        },
        "required": ["scenario"],
        "additionalProperties": False,
    }
    return {"type": "array", "minItems": 1, "items": step}


class ScenarioError(ValueError):
    """A scenario that cannot be run; `problems` names every reason."""

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


# Each provider's URL rules; a request is the provider's when any of them matches its URL.
Providers = Mapping[str, tuple[MatchRule, ...]]
PROVIDERS: Providers = MappingProxyType(
    {
        "ga4": (MatchRule("regex", r"^https?://([^/]+\.)?(google-analytics\.com|analytics\.google\.com)/g/collect"),),
        "gtm": (MatchRule("startsWith", "https://www.googletagmanager.com/gtm.js"),),
    }
)


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise ScenarioError([f"cannot read {path}: {exc}"]) from exc


def _shape_problems(content: Any, schema: dict[str, Any]) -> list[str]:
    errors = Draft202012Validator(schema).iter_errors(content)
    return [describe(error) for error in sorted(errors, key=lambda error: error.json_path)]


def _rule(raw: Mapping[str, Any]) -> MatchRule:
    return MatchRule(raw["match"], raw.get("value"))


def _step(raw: Mapping[str, Any]) -> Step:
    actions = tuple(Action(action["action"], MappingProxyType(action["params"])) for action in raw["scenario"])
    criteria = tuple(
        Criterion(
            criterion["provider"]["name"],
            tuple(Condition(condition["key"], _rule(condition)) for condition in criterion["conditions"]),
        )
        for criterion in raw.get("success_criteria", [])
    )
    return Step(actions, criteria)


def _step_problems(number: int, step: Step, catalog: ToolCatalog) -> list[str]:
    actions = [
        f"step {number} action {index} {action.tool}: {problem}"
        for index, action in enumerate(step.actions, start=1)
        for problem in catalog.problems(action.tool, dict(action.params))
    ]
    conditions = [
        f"step {number} criterion {index} condition {position} {condition.key}: {problem}"
        for index, criterion in enumerate(step.criteria, start=1)
        for position, condition in enumerate(criterion.conditions, start=1)
        for problem in rule_problems(condition.rule)
    ]
    return [*actions, *conditions]


def load_scenario(path: Path, providers: Providers = PROVIDERS) -> tuple[Step, ...]:
    """The scenario's steps, or a ScenarioError naming every problem: shape first, then tools and conditions."""
    content = _read_json(path)
    shape = _shape_problems(content, scenario_schema(list(providers)))
    if shape:
        raise ScenarioError(shape)
    steps = tuple(_step(raw) for raw in content)
    tools = load_catalog()
    problems = [
        problem for number, step in enumerate(steps, start=1) for problem in _step_problems(number, step, tools)
    ]
    if problems:
        raise ScenarioError(problems)
    return steps
