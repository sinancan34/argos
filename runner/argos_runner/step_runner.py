import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import Any, Protocol

from fastmcp import Client

from argos_runner.devtools.element_targets import resolve_selectors
from argos_runner.devtools.mcp_call import call_tool
from argos_runner.devtools.tabs import list_tabs
from argos_runner.scenario.model import Action, Step

ACTION_DELAY_RANGE_SECONDS = (1.0, 5.0)


class StepHooks(Protocol):
    """Runs around each step, before its first action and after its last; a returned message ends the run.

    `around_action` runs each action, given as `run`, and returns its response.
    """

    async def before_step(self, number: int, step: Step) -> str | None: ...

    async def after_step(self, number: int, step: Step) -> str | None: ...

    async def around_action(self, action: Action, run: Callable[[], Awaitable[dict[str, Any]]]) -> dict[str, Any]: ...


_sleep = asyncio.sleep


async def _pause() -> None:
    await _sleep(random.uniform(*ACTION_DELAY_RANGE_SECONDS))


def _reported(result: dict[str, Any], fallbacks: list[dict[str, Any]]) -> dict[str, Any]:
    """Lists the selector candidates that stood in for unmatched ones, if any did."""
    return {**result, "selector_fallbacks": fallbacks} if fallbacks else result


async def run_steps(client: Client, steps: list[Step], hooks: StepHooks | None = None) -> dict[str, Any]:
    """Runs every action as the Playwright MCP tool it names, in order, with a random pause between.

    The steps must already be checked against the tool catalog; validate.check does that.
    Tools act on the server's current tab, which an action such as browser_tabs may change for later ones.
    `hooks` run around each step, after the pause before its first action, while the browser is still open.
    The result lists under `selector_fallbacks` each selector candidate that stood in for an unmatched one.
    """
    # Listing tabs is what launches the browser.
    listed = await list_tabs(client)
    if listed["status"] != "success" or not listed["data"]["tabs"]:
        return {"status": "error", "message": f"cannot open the browser: {listed.get('message', 'no open tab')}"}

    fallbacks: list[dict[str, Any]] = []
    for number, step in enumerate(steps, start=1):
        if number > 1:
            await _pause()
        problem = await hooks.before_step(number, step) if hooks else None
        if problem:
            return _reported({"status": "error", "message": problem}, fallbacks)
        outcome, used = await _run_scenario(client, number, step, hooks)
        fallbacks = [*fallbacks, *used]
        if outcome["status"] != "success":
            return _reported(outcome, fallbacks)
        problem = await hooks.after_step(number, step) if hooks else None
        if problem:
            return _reported({"status": "error", "message": problem}, fallbacks)

    return _reported({"status": "success", "steps": len(steps)}, fallbacks)


async def _run_scenario(
    client: Client, number: int, step: Step, hooks: StepHooks | None
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Runs a step's actions in order; the first failing one fails the step and ends the run.

    Also returns the selector fallbacks its actions used.
    """
    fallbacks: list[dict[str, Any]] = []
    for action_number, action in enumerate(step.scenario, start=1):
        if action_number > 1:
            await _pause()
        response, used = await _run_action(client, action, hooks)
        fallbacks = [*fallbacks, *({"step": number, "action_number": action_number, **entry} for entry in used)]
        if response["status"] != "success":
            return await _failure(client, number, action_number, action, response), fallbacks
    return {"status": "success"}, fallbacks


async def _run_action(
    client: Client, action: Action, hooks: StepHooks | None
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Resolves selectors as the action names them, so fallbacks report its params, then calls the tool."""
    resolved = await resolve_selectors(client, action.params)
    if resolved["status"] != "success":
        return resolved, []

    async def run() -> dict[str, Any]:
        return await call_tool(client, action.action, resolved["data"])

    response = await hooks.around_action(action, run) if hooks else await run()
    return response, resolved["fallbacks"]


async def open_pages(client: Client) -> dict[str, Any]:
    """Tells a blocked page from a broken selector: both fail an action the same way."""
    listed = await list_tabs(client)
    if listed["status"] != "success" or not listed["data"]["tabs"]:
        return {}
    return {"pages": [{"url": tab.url, "title": tab.title} for tab in listed["data"]["tabs"]]}


async def _failure(
    client: Client, number: int, action_number: int, action: Action, response: dict[str, Any]
) -> dict[str, Any]:
    return {
        "status": "fail",
        "step": number,
        "action_number": action_number,
        "action": action.action,
        "params": action.params,
        "response": response,
        **await open_pages(client),
    }
