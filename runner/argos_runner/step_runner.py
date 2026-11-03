import asyncio
import random
from typing import Any, Protocol

from fastmcp import Client

from argos_runner.devtools.custom_tools import expand
from argos_runner.devtools.element_uids import resolve_selectors
from argos_runner.devtools.mcp_call import call_tool
from argos_runner.devtools.tool_catalog import PAGE_PARAM, page_tools
from argos_runner.scenario.model import Action, Step

ACTION_DELAY_RANGE_SECONDS = (1.0, 5.0)


class StepHooks(Protocol):
    """Runs around each step, before its first action and after its last; a returned message ends the run."""

    async def before_step(self, number: int, step: Step) -> str | None: ...

    async def after_step(self, number: int, step: Step) -> str | None: ...


_sleep = asyncio.sleep


async def _pause() -> None:
    await _sleep(random.uniform(*ACTION_DELAY_RANGE_SECONDS))


def _reported(result: dict[str, Any], fallbacks: list[dict[str, Any]]) -> dict[str, Any]:
    """Lists the selector candidates that stood in for unmatched ones, if any did."""
    return {**result, "selector_fallbacks": fallbacks} if fallbacks else result


def _selected(pages: list[dict[str, Any]], current: int) -> int:
    return next((page["id"] for page in pages if page.get("selected")), current)


async def run_steps(client: Client, steps: list[Step], hooks: StepHooks | None = None) -> dict[str, Any]:
    """Runs every action as the chrome-devtools-mcp tool it names, in order, with a random pause between.

    The steps must already be checked against the tool catalog; validate.check does that.
    A tool that takes `pageId` runs on the selected page unless the action names one; an action whose
    result lists the pages, such as new_page or select_page, moves later actions to the one it selects.
    `hooks` run around each step, after the pause before its first action, while the browser is still open.
    The result lists under `selector_fallbacks` each selector candidate that stood in for an unmatched one.
    """
    on_page = page_tools()
    # Listing pages is what launches the browser.
    listed = await call_tool(client, "list_pages", {})
    pages = listed["data"].get("pages") if listed["status"] == "success" else None
    if not pages:
        return {"status": "error", "message": f"cannot open the browser: {listed.get('message', 'no open page')}"}

    page_id = _selected(pages, pages[0]["id"])
    fallbacks: list[dict[str, Any]] = []
    for number, step in enumerate(steps, start=1):
        if number > 1:
            await _pause()
        problem = await hooks.before_step(number, step) if hooks else None
        if problem:
            return _reported({"status": "error", "message": problem}, fallbacks)
        outcome, used = await _run_scenario(client, number, step, on_page, page_id)
        fallbacks = [*fallbacks, *used]
        if outcome["status"] != "success":
            return _reported(outcome, fallbacks)
        page_id = outcome["page_id"]
        problem = await hooks.after_step(number, step) if hooks else None
        if problem:
            return _reported({"status": "error", "message": problem}, fallbacks)

    return _reported({"status": "success", "steps": len(steps)}, fallbacks)


async def _run_scenario(
    client: Client, number: int, step: Step, on_page: set[str], page_id: int
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Runs a step's actions in order; the first failing one fails the step and ends the run.

    Also returns the selector fallbacks its actions used.
    """
    fallbacks: list[dict[str, Any]] = []
    for action_number, action in enumerate(step.scenario, start=1):
        if action_number > 1:
            await _pause()
        response, used = await _run_action(client, action, on_page, page_id)
        fallbacks = [*fallbacks, *({"step": number, "action_number": action_number, **entry} for entry in used)]
        if response["status"] != "success":
            return await _failure(client, number, action_number, action, response), fallbacks
        page_id = _selected(response["data"].get("pages") or [], page_id)
    return {"status": "success", "page_id": page_id}, fallbacks


async def _run_action(
    client: Client, action: Action, on_page: set[str], page_id: int
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Resolves selectors as the action names them, so fallbacks report its params, then expands a runner tool."""
    resolved = await resolve_selectors(client, action.params.get(PAGE_PARAM, page_id), action.params)
    if resolved["status"] != "success":
        return resolved, []
    sent = expand(action.model_copy(update={"params": resolved["data"]}))
    params = {PAGE_PARAM: page_id, **sent.params} if sent.action in on_page else sent.params
    return await call_tool(client, sent.action, params), resolved["fallbacks"]


async def open_pages(client: Client) -> dict[str, Any]:
    """Tells a blocked page from a broken selector: both fail an action the same way."""
    response = await call_tool(client, "list_pages", {})
    if response["status"] != "success" or not response["data"].get("pages"):
        return {}
    return {"pages": [{"url": page.get("url"), "title": page.get("title")} for page in response["data"]["pages"]]}


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
