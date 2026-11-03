import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from fastmcp import Client, FastMCP
from fastmcp.client.transports import ClientTransport, StdioTransport

from goal_evaluator import Providers, is_wanted
from network_capture import NetworkCapture
from providers import ProvidersError, load_providers
from scenario import ScenarioError, Step, load_steps
from step_goals import StepGoals
from step_runner import run_steps

SERVER_COMMAND = "npx"
SERVER_ARGS = [
    "-y",
    # Pinned: the runner reads its experimental structured results.
    "chrome-devtools-mcp@1.12.0",
    "--experimentalStructuredContent",
    # A temporary profile per run, removed when the browser closes; it also keeps clear of
    # the profile an editor's chrome-devtools-mcp may be holding.
    "--isolated",
    # Keeps request bodies of up to 25 navigations per page instead of 3.
    "--maxNavigationSaved=25",
    "--no-usage-statistics",
]
# Far above a navigation or a script; a call this slow means the server is stuck.
CLIENT_TIMEOUT_SECONDS = 180


async def _ignore_server_log(message: Any) -> None:
    """Keeps server log messages off the console; stdout carries only the result."""


def _new_client(transport: ClientTransport | FastMCP) -> Client:
    return Client(transport, timeout=CLIENT_TIMEOUT_SECONDS, log_handler=_ignore_server_log)


def _with_step_goals(result: dict[str, Any], capture: NetworkCapture, step_goals: StepGoals) -> dict[str, Any]:
    if result["status"] == "error":
        return {**result, "step_goals": step_goals.results} if step_goals.results else result
    warnings = {"warnings": capture.warnings} if capture.warnings else {}
    report = {"recorded_requests": capture.recorded_requests, "step_goals": step_goals.results, **warnings}
    if result["status"] == "fail":
        return {**result, **report}
    passed = all(entry["status"] == "pass" for entry in step_goals.results)
    return {**result, "status": "success" if passed else "fail", **report}


async def _run(client: Client, steps: list[Step], providers: Providers) -> dict[str, Any]:
    goals = [goal for step in steps for goal in step.goals or []]
    if not goals:
        return await run_steps(client, steps)

    capture = NetworkCapture(client, lambda url: is_wanted(goals, url, providers))
    step_goals = StepGoals(client, capture, providers)
    result = await run_steps(client, steps, step_goals)
    return _with_step_goals(result, capture, step_goals)


async def execute(scenario_path: Path, transport: ClientTransport | FastMCP) -> dict[str, Any]:
    try:
        providers = load_providers()
        steps = load_steps(scenario_path, providers)
        async with _new_client(transport) as client:
            return await _run(client, steps, providers)
    except (ScenarioError, ProvidersError) as exc:
        return {"status": "error", "message": str(exc)}
    except Exception as exc:
        return {"status": "error", "message": f"cannot reach MCP server: {exc}"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Runs a scenario JSON file through chrome-devtools-mcp.")
    parser.add_argument("scenario", type=Path, help="path to the scenario JSON file, goals included")
    args = parser.parse_args(argv)

    # Closing the client ends the server, which closes the browser and discards its profile.
    transport = StdioTransport(SERVER_COMMAND, SERVER_ARGS, keep_alive=False)
    result = asyncio.run(execute(args.scenario, transport))
    sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
