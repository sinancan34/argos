"""Loads a scenario JSON and the provider file, and refuses either before a browser starts if it cannot run.

A scenario is a list of steps. Each step's actions are Playwright MCP tool calls, checked against the pinned
server's tool catalog; its success criteria name a provider from data/providers.json (ga4 or gtm) and conditions.
"""

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

from argos_agent.playwright_mcp.catalog import ToolCatalog, load_catalog, schema_problems
from argos_agent.runner.matching import MatchRule, rule_problems

PROVIDERS_PATH = Path(__file__).parents[1] / "data" / "providers.json"

RULE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"match": {"type": "string"}, "value": {"type": ["string", "number"]}},
    "required": ["match"],
    "additionalProperties": False,
}
PROVIDERS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "minProperties": 1,
    "additionalProperties": {
        "type": "object",
        "properties": {"urls": {"type": "array", "minItems": 1, "items": RULE_SCHEMA}},
        "required": ["urls"],
        "additionalProperties": False,
    },
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


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise ScenarioError([f"cannot read {path}: {exc}"]) from exc


def _rule(raw: Mapping[str, Any]) -> MatchRule:
    return MatchRule(raw["match"], raw.get("value"))


def load_providers(path: Path = PROVIDERS_PATH) -> Providers:
    """Each provider's URL rules; a request is the provider's when any of them matches its URL."""
    content = _read_json(path)
    problems = schema_problems(PROVIDERS_SCHEMA, content)
    if problems:
        raise ScenarioError([f"{path}: {problem}" for problem in problems])
    providers = {name: tuple(_rule(raw) for raw in provider["urls"]) for name, provider in content.items()}
    problems = [
        f"{name} url {number}: {problem}"
        for name, rules in providers.items()
        for number, rule in enumerate(rules, start=1)
        for problem in rule_problems(rule)
    ]
    if problems:
        raise ScenarioError(problems)
    return MappingProxyType(providers)


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


def load_scenario(path: Path, providers: Providers | None = None) -> tuple[Step, ...]:
    """The scenario's steps, or a ScenarioError naming every problem: shape first, then tools and conditions."""
    content = _read_json(path)
    names = list(load_providers() if providers is None else providers)
    shape = schema_problems(scenario_schema(names), content)
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
