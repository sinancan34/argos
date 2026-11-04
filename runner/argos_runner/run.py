import argparse
import asyncio
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

from fastmcp import Client, FastMCP
from fastmcp.client.transports import ClientTransport, StdioTransport

from argos_runner.criteria.evaluator import Providers, is_wanted
from argos_runner.criteria.network_capture import NetworkCapture
from argos_runner.criteria.providers import ProvidersError, load_providers
from argos_runner.criteria.step_criteria import StepCriteria
from argos_runner.devtools.tool_catalog import CatalogError, load_catalog
from argos_runner.scenario.model import ScenarioError, Step
from argos_runner.step_runner import run_steps
from argos_runner.validate import check

SERVER_COMMAND = "npx"
# Pinned: the runner reads this version's text results, and scenarios are validated against its
# tool catalog; refresh_tool_schemas.py rewrites the catalog after a change.
SERVER_PACKAGE = "@playwright/mcp@0.0.84"
# Scenarios may call any tool; the tools of these capabilities are off unless asked for.
CAPABILITIES = ("network", "storage", "testing", "vision", "pdf", "devtools", "config")
# The server writes a snapshot file per action; past this size it evicts the oldest, so scheduled runs
# do not fill the temp dir. Files a scenario names itself are not counted.
OUTPUT_MAX_BYTES = 50 * 1024 * 1024
SERVER_ARGS = [
    "-y",
    SERVER_PACKAGE,
    # The profile lives in memory and is gone when the browser closes; it also keeps clear of
    # the profile an editor's Playwright MCP may be holding.
    "--isolated",
    f"--caps={','.join(CAPABILITIES)}",
    # Results carry no generated Playwright code, which the runner does not read.
    "--codegen",
    "none",
    f"--output-max-size={OUTPUT_MAX_BYTES}",
]
# Far above a navigation or a script; a call this slow means the server is stuck.
CLIENT_TIMEOUT_SECONDS = 180


def server_transport() -> StdioTransport:
    """The pinned server, started in the OS temp dir.

    The server writes its snapshots and any file a tool names by a relative path into the folder it starts in,
    so they land in the temp dir, not in the runner's folder; a file a scenario saves stays there after the run.
    """
    # Closing the client ends the server, which closes the browser and discards its profile.
    return StdioTransport(SERVER_COMMAND, SERVER_ARGS, cwd=tempfile.gettempdir(), keep_alive=False)


async def _ignore_server_log(message: Any) -> None:
    """Keeps server log messages off the console; stdout carries only the result."""


def _with_step_criteria(result: dict[str, Any], capture: NetworkCapture, step_criteria: StepCriteria) -> dict[str, Any]:
    if result["status"] == "error":
        return {**result, "step_success_criteria": step_criteria.results} if step_criteria.results else result
    warnings = {"warnings": capture.warnings} if capture.warnings else {}
    report = {
        "recorded_requests": capture.recorded_requests,
        "step_success_criteria": step_criteria.results,
        **warnings,
    }
    if result["status"] == "fail":
        return {**result, **report}
    passed = all(entry["status"] == "pass" for entry in step_criteria.results)
    return {**result, "status": "success" if passed else "fail", **report}


async def _run(client: Client, steps: list[Step], providers: Providers) -> dict[str, Any]:
    criteria = [criterion for step in steps for criterion in step.success_criteria or []]
    if not criteria:
        return await run_steps(client, steps)

    capture = NetworkCapture(client, lambda url: is_wanted(criteria, url, providers))
    step_criteria = StepCriteria(client, capture, providers)
    result = await run_steps(client, steps, step_criteria)
    return _with_step_criteria(result, capture, step_criteria)


async def execute(scenario_path: Path, transport: ClientTransport | FastMCP) -> dict[str, Any]:
    try:
        providers = load_providers()
        # Checked against the pinned tool catalog before the server starts.
        steps = check(scenario_path, providers, load_catalog())
        async with Client(transport, timeout=CLIENT_TIMEOUT_SECONDS, log_handler=_ignore_server_log) as client:
            return await _run(client, steps, providers)
    except (ScenarioError, ProvidersError, CatalogError) as exc:
        return {"status": "error", "message": str(exc)}
    except Exception as exc:
        return {"status": "error", "message": f"cannot reach MCP server: {exc}"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Runs a scenario JSON file through Playwright MCP.")
    parser.add_argument("scenario", type=Path, help="path to the scenario JSON file, criteria included")
    args = parser.parse_args(argv)

    result = asyncio.run(execute(args.scenario, server_transport()))
    sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
