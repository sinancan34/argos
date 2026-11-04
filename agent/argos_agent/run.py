"""argos-runner: runs a scenario JSON through the pinned Playwright MCP server and checks its success criteria.

    argos-runner scenario.json [--headless]

Each step's actions run in order, with a random 1-5 s pause before every action but the first, as a user would
pause. The step's success criteria are then checked against the requests sent since the step began, until they
pass or 60 s run out. The JSON report goes to stdout; the exit code is 0 (success), 1 (fail) or 2 (error).
"""

import argparse
import asyncio
import json
import logging
import random
import sys
import time
from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from fastmcp.client.transports import ClientTransport

from argos_agent.playwright_mcp.catalog import CatalogError, InvalidToolCall
from argos_agent.playwright_mcp.client import PlaywrightMCP, ServerError
from argos_agent.playwright_mcp.server import LaunchValue
from argos_agent.runner.criteria import Outcome, evaluate, wanted
from argos_agent.runner.network import Captured, NetworkError, requests_since, start_listening
from argos_agent.runner.scenario import Providers, ScenarioError, Step, load_providers, load_scenario

DELAY_RANGE_SECONDS = (1.0, 5.0)
DEFAULT_WAIT_SECONDS = 60.0
POLL_SECONDS = 2.0
EXIT_CODES = {"success": 0, "fail": 1, "error": 2}

Sleep = Callable[[float], Awaitable[None]]
Report = dict[str, Any]


def random_delay() -> float:
    # A user's pause between actions, not a secret.
    return random.uniform(*DELAY_RANGE_SECONDS)  # noqa: S311  # nosec B311


@dataclass(frozen=True)
class Pacing:
    sleep: Sleep = asyncio.sleep
    clock: Callable[[], float] = time.monotonic
    delay: Callable[[], float] = random_delay
    # How long a step's criteria may take to pass; pixels are sent after the action that triggers them.
    wait_seconds: float = DEFAULT_WAIT_SECONDS


async def _failed_action(mcp: PlaywrightMCP, number: int, step: Step, pacing: Pacing) -> Report | None:
    """Runs the step's actions in order; the first one the server fails ends the step."""
    for index, action in enumerate(step.actions, start=1):
        if number > 1 or index > 1:
            await pacing.sleep(pacing.delay())
        result = await mcp.call(action.tool, action.params)
        if result.is_error:
            return {"action": index, "tool": action.tool, "params": dict(action.params), "error": result.error}
    return None


async def _captured(mcp: PlaywrightMCP, baseline: int, step: Step, providers: Providers) -> list[Captured]:
    """The step's requests, from every tab, of a criterion's provider."""
    return [request for request in await requests_since(mcp, baseline) if wanted(request.url, step.criteria, providers)]


async def _outcomes(
    mcp: PlaywrightMCP, baseline: int, step: Step, providers: Providers, pacing: Pacing
) -> list[Outcome]:
    """Checks the criteria every poll until all pass or the wait runs out, reading the requests anew each time."""
    deadline = pacing.clock() + pacing.wait_seconds
    while True:
        captured = await _captured(mcp, baseline, step, providers)
        outcomes = [evaluate(index, criterion, captured, providers) for index, criterion in enumerate(step.criteria, 1)]
        left = deadline - pacing.clock()
        if left <= 0 or all(outcome["status"] == "pass" for outcome in outcomes):
            return outcomes
        # The last pause ends at the deadline, so the last check is made right as the wait runs out.
        await pacing.sleep(min(POLL_SECONDS, left))


async def run_steps(mcp: PlaywrightMCP, steps: Sequence[Step], providers: Providers, pacing: Pacing) -> Report:
    """Runs every step; a failed action ends the run, a failed criterion does not."""
    # Before the first action, so every request the browser sends is heard.
    await start_listening(mcp)
    reports: list[Report] = []
    baseline = 0
    for number, step in enumerate(steps, start=1):
        # A step's requests are the ones sent after it began; a late hit of the step before is not one of them.
        baseline += len(await requests_since(mcp, baseline))
        failed = await _failed_action(mcp, number, step, pacing)
        if failed:
            return {
                "status": "fail",
                "steps": [*reports, {"step": number, "status": "fail", "failed_action": failed}],
            }
        outcomes = await _outcomes(mcp, baseline, step, providers, pacing) if step.criteria else []
        status = "pass" if all(outcome["status"] == "pass" for outcome in outcomes) else "fail"
        reports = [*reports, {"step": number, "status": status, "criteria": outcomes}]
    status = "success" if all(report["status"] == "pass" for report in reports) else "fail"
    return {"status": status, "steps": reports}


async def run(
    path: Path,
    *,
    options: Mapping[str, LaunchValue],
    pacing: Pacing,
    transport: ClientTransport | FastMCP | None = None,
) -> Report:
    """The run report of a scenario file; a scenario that cannot run or a server that fails is an `error`."""
    head = {"scenario": str(path)}
    try:
        providers = load_providers()
        steps = load_scenario(path, providers=providers)
    except ScenarioError as exc:
        return {**head, "status": "error", "problems": list(exc.problems)}
    except CatalogError as exc:
        return {**head, "status": "error", "problems": [str(exc)]}
    # Anything that keeps the run from finishing is an error, never a fail: a fail means a pixel was not sent.
    try:
        async with PlaywrightMCP(options, transport=transport) as mcp:
            return {**head, **await run_steps(mcp, steps, providers, pacing)}
    except (ServerError, NetworkError, CatalogError, InvalidToolCall) as exc:
        return {**head, "status": "error", "problems": [str(exc)]}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="argos-runner", description="Run a scenario JSON and check its success criteria."
    )
    parser.add_argument("scenario", type=Path, help="the scenario JSON file")
    parser.add_argument("--headless", action="store_true", help="run the browser without a window")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.WARNING)
    options: dict[str, LaunchValue] = {"--headless": True} if args.headless else {}
    report = asyncio.run(run(args.scenario, options=options, pacing=Pacing()))
    sys.stdout.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return EXIT_CODES[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
