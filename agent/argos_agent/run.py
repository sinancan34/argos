"""argos-run: runs a scenario JSON through the pinned Playwright MCP server and checks its success criteria.

    argos-run scenario.json [--headless] [--wait SECONDS]

Each step's actions run in order, with a random 1-5 s pause before every action but the first, as a user would
pause. The step's success criteria are then checked against the requests sent since the step began, until they
pass or the wait runs out. The JSON report goes to stdout; the exit code is 0 (success), 1 (fail) or 2 (error).
"""

import argparse
import asyncio
import json
import logging
import math
import random
import sys
from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from fastmcp.client.transports import ClientTransport

from argos_agent.playwright_mcp.catalog import CatalogError, InvalidLaunchOptions, InvalidToolCall
from argos_agent.playwright_mcp.client import PlaywrightMCP, ServerError
from argos_agent.playwright_mcp.server import LaunchValue
from argos_agent.runner.criteria import Captured, Outcome, evaluate, wanted
from argos_agent.runner.network import Listed, NetworkError, list_requests, request_body
from argos_agent.runner.scenario import Providers, ScenarioError, Step, load_providers, load_scenario

DELAY_RANGE_SECONDS = (1.0, 5.0)
DEFAULT_WAIT_SECONDS = 10.0
POLL_SECONDS = 2.0
BODY_METHOD = "POST"
EXIT_CODES = {"success": 0, "fail": 1, "error": 2}

Sleep = Callable[[float], Awaitable[None]]
Report = dict[str, Any]
Bodies = Mapping[int, str | None]


def random_delay() -> float:
    # A user's pause between actions, not a secret.
    return random.uniform(*DELAY_RANGE_SECONDS)  # noqa: S311  # nosec B311


@dataclass(frozen=True)
class Pacing:
    sleep: Sleep = asyncio.sleep
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


async def _body(mcp: PlaywrightMCP, request: Listed) -> tuple[str | None, list[str]]:
    if request.method != BODY_METHOD:
        return None, []
    try:
        return await request_body(mcp, request.index), []
    except NetworkError as exc:
        return None, [str(exc)]


async def _capture(
    mcp: PlaywrightMCP, baseline: int, step: Step, providers: Providers, bodies: Bodies
) -> tuple[list[Captured], Bodies, list[str]]:
    """The step's requests of a criterion's provider; a body read once is kept, one that failed is read again."""
    listed = [
        request
        for request in await list_requests(mcp)
        if request.index > baseline and wanted(request.url, step.criteria, providers)
    ]
    read = {request.index: await _body(mcp, request) for request in listed if request.index not in bodies}
    known = {**bodies, **{index: body for index, (body, failed) in read.items() if not failed}}
    warnings = [warning for _, found in read.values() for warning in found]
    return [Captured(request.url, known.get(request.index)) for request in listed], known, warnings


async def _outcomes(
    mcp: PlaywrightMCP, baseline: int, step: Step, providers: Providers, pacing: Pacing
) -> tuple[list[Outcome], list[str]]:
    """Checks the criteria until all pass or the wait runs out, reading the requests anew each time."""
    polls = math.ceil(pacing.wait_seconds / POLL_SECONDS) + 1
    bodies: Bodies = {}
    warnings: list[str] = []
    attempt = 1
    while True:
        captured, bodies, found = await _capture(mcp, baseline, step, providers, bodies)
        # A body that fails on every poll is warned about once.
        warnings = list(dict.fromkeys([*warnings, *found]))
        outcomes = [evaluate(index, criterion, captured, providers) for index, criterion in enumerate(step.criteria, 1)]
        if attempt >= polls or all(outcome["status"] == "pass" for outcome in outcomes):
            return outcomes, warnings
        attempt += 1
        await pacing.sleep(POLL_SECONDS)


async def run_steps(mcp: PlaywrightMCP, steps: Sequence[Step], providers: Providers, pacing: Pacing) -> Report:
    """Runs every step; a failed action ends the run, a failed criterion does not."""
    reports: list[Report] = []
    warnings: list[str] = []
    for number, step in enumerate(steps, start=1):
        baseline = max((request.index for request in await list_requests(mcp)), default=0)
        failed = await _failed_action(mcp, number, step, pacing)
        if failed:
            return {
                "status": "fail",
                "steps": [*reports, {"step": number, "status": "fail", "failed_action": failed}],
                "warnings": warnings,
            }
        outcomes, found = await _outcomes(mcp, baseline, step, providers, pacing) if step.criteria else ([], [])
        status = "pass" if all(outcome["status"] == "pass" for outcome in outcomes) else "fail"
        reports = [*reports, {"step": number, "status": status, "criteria": outcomes}]
        warnings = [*warnings, *found]
    status = "success" if all(report["status"] == "pass" for report in reports) else "fail"
    return {"status": status, "steps": reports, "warnings": warnings}


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
    except (ServerError, NetworkError, CatalogError, InvalidLaunchOptions, InvalidToolCall) as exc:
        return {**head, "status": "error", "problems": [str(exc)]}


def _seconds(text: str) -> float:
    try:
        seconds = float(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"not a number: {text!r}") from exc
    if not math.isfinite(seconds) or seconds < 0:
        raise argparse.ArgumentTypeError(f"must be 0 or more seconds: {text!r}")
    return seconds


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="argos-run", description="Run a scenario JSON and check its success criteria."
    )
    parser.add_argument("scenario", type=Path, help="the scenario JSON file")
    parser.add_argument("--headless", action="store_true", help="run the browser without a window")
    parser.add_argument(
        "--wait", type=_seconds, default=DEFAULT_WAIT_SECONDS, help="seconds a step's criteria may take to pass"
    )
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.WARNING)
    options: dict[str, LaunchValue] = {"--headless": True} if args.headless else {}
    report = asyncio.run(run(args.scenario, options=options, pacing=Pacing(wait_seconds=args.wait)))
    sys.stdout.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return EXIT_CODES[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
