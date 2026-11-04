import argparse
import json
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, ValidationError

from argos_runner.criteria.providers import ProviderDefinition, ProvidersError, load_providers
from argos_runner.devtools.element_targets import SELECTOR_PROBLEM, malformed_elements, with_targets
from argos_runner.devtools.tool_catalog import CatalogError, load_catalog
from argos_runner.scenario.model import Action, ScenarioError, Step, load_steps

# Stands in for the element target the runner fills in only while it runs.
TARGET_PLACEHOLDER = "e1"


def _strict(schema: Any) -> Any:
    """`schema` with every object that lists its properties closed to others, nested ones too."""
    if isinstance(schema, list):
        return [_strict(item) for item in schema]
    if not isinstance(schema, dict):
        return schema
    strict = {key: _strict(value) for key, value in schema.items()}
    return {"additionalProperties": False, **strict} if "properties" in schema else strict


def _param_path(path: Iterable[str | int]) -> str:
    """('fields', 0, 'target') reads `fields[0].target`."""
    return "".join(f"[{part}]" if isinstance(part, int) else f".{part}" for part in path).lstrip(".")


def _schema_problem(where: str, error: ValidationError) -> str:
    path = _param_path(error.absolute_path)
    return f"{where} param '{path}': {error.message}" if path else f"{where}: {error.message}"


def _as_sent(action: Action) -> dict[str, Any]:
    """The params the runner would send, with a placeholder for each element target it fills in while running."""
    return with_targets(action.params, lambda _: TARGET_PLACEHOLDER)


def _action_problems(where: str, action: Action, validators: dict[str, Draft202012Validator], server: str) -> list[str]:
    validator = validators.get(action.action)
    if validator is None:
        return [f"{where}: unknown action '{action.action}'; {server} has no such tool"]
    named = f"{where} {action.action}"
    elements = [f"{named} param '{path}': {SELECTOR_PROBLEM}" for path in malformed_elements(action.params)]
    errors = sorted(validator.iter_errors(_as_sent(action)), key=lambda error: error.json_path)
    return [*elements, *(_schema_problem(named, error) for error in errors)]


def action_problems(steps: list[Step], catalog: dict[str, Any]) -> list[str]:
    """Every way the actions differ from the tools of the catalog: names, params, types and values."""
    validators = {name: Draft202012Validator(_strict(schema)) for name, schema in catalog["tools"].items()}
    return [
        problem
        for number, step in enumerate(steps, start=1)
        for action_number, action in enumerate(step.scenario, start=1)
        for problem in _action_problems(f"step {number} action {action_number}", action, validators, catalog["server"])
    ]


def check(path: Path, providers: dict[str, ProviderDefinition], catalog: dict[str, Any]) -> list[Step]:
    """The steps of a scenario that matches the catalog; a ScenarioError names every problem otherwise."""
    steps = load_steps(path, providers)
    problems = action_problems(steps, catalog)
    if problems:
        raise ScenarioError(f"invalid scenario {path}: {'; '.join(problems)}")
    return steps


def validate_file(path: Path, providers: dict[str, ProviderDefinition], catalog: dict[str, Any]) -> dict[str, Any]:
    """A JSend envelope: the step count of a valid scenario, or every problem of an invalid one."""
    try:
        steps = load_steps(path, providers)
    except ScenarioError as exc:
        return {"status": "fail", "data": {"scenario": str(path), "problems": [str(exc)]}}
    problems = action_problems(steps, catalog)
    if problems:
        return {"status": "fail", "data": {"scenario": str(path), "problems": problems}}
    return {"status": "success", "data": {"scenario": str(path), "steps": len(steps)}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Checks scenario JSON files against the pinned Playwright MCP tools, without running them."
    )
    parser.add_argument("scenarios", type=Path, nargs="+", help="paths to the scenario JSON files")
    args = parser.parse_args(argv)

    try:
        providers = load_providers()
        catalog = load_catalog()
    except (ProvidersError, CatalogError) as exc:
        sys.stdout.write(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False, indent=2) + "\n")
        return 1
    results = [validate_file(path, providers, catalog) for path in args.scenarios]
    sys.stdout.write(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    return 0 if all(result["status"] == "success" for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
