"""The tracking providers a success criterion can name (ga4, gtm), read from providers.json next to this file.

Each provider has URL rules; a request is the provider's when any of them matches its URL.
"""

from pathlib import Path
from types import MappingProxyType
from typing import Any

from argos_agent.playwright_mcp.catalog import schema_problems
from argos_agent.scenario.matching import rule_problems
from argos_agent.scenario.model import RULE_SCHEMA, Providers, ScenarioError, read_json, rule

PROVIDERS_PATH = Path(__file__).with_name("providers.json")

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


def load_providers(path: Path = PROVIDERS_PATH) -> Providers:
    """Each provider's URL rules, or a ScenarioError naming every problem with the file."""
    content = read_json(path)
    problems = schema_problems(PROVIDERS_SCHEMA, content)
    if problems:
        raise ScenarioError([f"{path}: {problem}" for problem in problems])
    providers = {name: tuple(rule(raw) for raw in provider["urls"]) for name, provider in content.items()}
    problems = [
        f"{name} url {number}: {problem}"
        for name, rules in providers.items()
        for number, url_rule in enumerate(rules, start=1)
        for problem in rule_problems(url_rule)
    ]
    if problems:
        raise ScenarioError(problems)
    return MappingProxyType(providers)
