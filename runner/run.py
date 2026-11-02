import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from fastmcp import Client, FastMCP

from goal import Goal, GoalError, load_goals
from goal_evaluator import Providers, evaluate_goals, is_wanted
from goal_waiter import wait_until_satisfied
from network_capture import NetworkCapture
from providers import ProvidersError, load_providers
from scenario import ScenarioError, Step, load_steps
from step_runner import run_steps

DEFAULT_MCP_URL = "http://127.0.0.1:8000/mcp"
# Above the longest tool timeout on the server (start_browser, 120 s).
CLIENT_TIMEOUT_SECONDS = 180
# How long pixels may take to appear before unmet goals count as failed.
GOAL_WAIT_SECONDS = 60


async def _ignore_server_log(message: Any) -> None:
    """Keeps server log messages off the console; stdout carries only the result."""


def _new_client(transport: str | FastMCP) -> Client:
    return Client(transport, timeout=CLIENT_TIMEOUT_SECONDS, log_handler=_ignore_server_log)


def _all_passed(outcomes: list[dict[str, Any]]) -> bool:
    return all(outcome["status"] == "pass" for outcome in outcomes)


async def _run_with_goals(
    transport: str | FastMCP, steps: list[Step], goals: list[Goal], providers: Providers
) -> dict[str, Any]:
    async with _new_client(transport) as client:
        capture = NetworkCapture(client, lambda url: is_wanted(goals, url, providers))

        def outcomes() -> list[dict[str, Any]]:
            return evaluate_goals(goals, capture.requests, providers)

        async def before_stop() -> None:
            await wait_until_satisfied(capture, lambda: _all_passed(outcomes()), GOAL_WAIT_SECONDS)

        result = await run_steps(client, steps, before_stop)

    if result["status"] != "success":
        return result
    if capture.error is not None:
        return {"status": "error", "message": capture.error}

    final = outcomes()
    warnings = {"warnings": capture.warnings} if capture.warnings else {}
    return {
        **result,
        "status": "success" if _all_passed(final) else "fail",
        "recorded_requests": capture.recorded_requests,
        "goals": final,
        **warnings,
    }


async def execute(
    scenario_path: Path, transport: str | FastMCP, goal_path: Path | None = None
) -> dict[str, Any]:
    try:
        steps = load_steps(scenario_path)
        if goal_path is not None:
            providers = load_providers()
            goals = load_goals(goal_path, providers)
            return await _run_with_goals(transport, steps, goals, providers)
        async with _new_client(transport) as client:
            return await run_steps(client, steps)
    except (ScenarioError, GoalError, ProvidersError) as exc:
        return {"status": "error", "message": str(exc)}
    except Exception as exc:
        return {"status": "error", "message": f"cannot reach MCP server: {exc}"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Runs a scenario JSON file through nodriver MCP.")
    parser.add_argument("scenario", type=Path, help="path to the scenario JSON file")
    parser.add_argument("--goal", type=Path, help="path to the goal JSON file to check after a successful run")
    parser.add_argument("--mcp-url", default=DEFAULT_MCP_URL, help="nodriver MCP server address")
    args = parser.parse_args(argv)

    result = asyncio.run(execute(args.scenario, args.mcp_url, args.goal))
    sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
