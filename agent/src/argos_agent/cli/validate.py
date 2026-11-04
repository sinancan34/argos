"""validate: checks a scenario JSON statically, without starting the browser or the MCP server.

    validate scenario.json

The JSON report goes to stdout; the exit code is 0 (valid), 1 (invalid) or 2 (error: the tool catalog cannot be used).
"""

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from argos_agent.playwright_mcp.catalog import CatalogError
from argos_agent.scenario.model import ScenarioError, load_scenario
from argos_agent.scenario.providers import load_providers

EXIT_CODES = {"valid": 0, "invalid": 1, "error": 2}


def validate(path: Path) -> dict[str, Any]:
    """The validation report of a scenario file: the same static check the runner makes before it starts."""
    head = {"scenario": str(path)}
    try:
        load_scenario(path, load_providers())
    except ScenarioError as exc:
        return {**head, "status": "invalid", "problems": list(exc.problems)}
    except CatalogError as exc:
        return {**head, "status": "error", "problems": [str(exc)]}
    return {**head, "status": "valid", "problems": []}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="validate", description="Check a scenario JSON without running it.")
    parser.add_argument("scenario", type=Path, help="the scenario JSON file")
    args = parser.parse_args(argv)
    report = validate(args.scenario)
    sys.stdout.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return EXIT_CODES[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
