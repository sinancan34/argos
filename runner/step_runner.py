import asyncio
import random
from typing import Any, Protocol

from fastmcp import Client

from element_uids import resolve_selectors, selector_problem
from mcp_call import call_tool
from scenario import Action, Step

ACTION_DELAY_RANGE_SECONDS = (1.0, 5.0)
PAGE_PARAM = "pageId"


class StepHooks(Protocol):
    """Runs around each step, before its first action and after its last; a returned message ends the run."""

    async def before_step(self, number: int, step: Step) -> str | None: ...

    async def after_step(self, number: int, step: Step) -> str | None: ...


_sleep = asyncio.sleep


async def _pause() -> None:
    await _sleep(random.uniform(*ACTION_DELAY_RANGE_SECONDS))


async def _tool_params(client: Client) -> dict[str, set[str]]:
    """Maps each chrome-devtools-mcp tool to the names of the params it takes."""
    tools = await client.list_tools()
    return {tool.name: set(tool.inputSchema.get("properties", {})) for tool in tools}


def _unknown_action(steps: list[Step], tools: dict[str, set[str]]) -> str | None:
    unknown = next(
        (
            (number, action_number, action)
            for number, step in enumerate(steps, 1)
            for action_number, action in enumerate(step.scenario, 1)
            if action.action not in tools
        ),
        None,
    )
    if unknown is None:
        return None
    number, action_number, action = unknown
    return (
        f"step {number} action {action_number} uses unknown action '{action.action}'; "
        "chrome-devtools-mcp has no such tool"
    )


def _malformed_selector(steps: list[Step]) -> str | None:
    found = next(
        (
            (number, action_number, problem)
            for number, step in enumerate(steps, 1)
            for action_number, action in enumerate(step.scenario, 1)
            if (problem := selector_problem(action.params))
        ),
        None,
    )
    if found is None:
        return None
    number, action_number, problem = found
    return f"step {number} action {action_number} {problem}"


def _reported(result: dict[str, Any], fallbacks: list[dict[str, Any]]) -> dict[str, Any]:
    """Lists the selector candidates that stood in for unmatched ones, if any did."""
    return {**result, "selector_fallbacks": fallbacks} if fallbacks else result


def _selected(pages: list[dict[str, Any]], current: int) -> int:
    return next((page["id"] for page in pages if page.get("selected")), current)


async def run_steps(client: Client, steps: list[Step], hooks: StepHooks | None = None) -> dict[str, Any]:
    """Runs every action as the chrome-devtools-mcp tool it names, in order, with a random pause between.

    A tool that takes `pageId` runs on the selected page unless the action names one; an action whose
    result lists the pages, such as new_page or select_page, moves later actions to the one it selects.
    `hooks` run around each step, after the pause before its first action, while the browser is still open.
    The result lists under `selector_fallbacks` each selector candidate that stood in for an unmatched one.
    """
    try:
        tools = await _tool_params(client)
    except Exception as exc:
        return {"status": "error", "message": f"cannot list chrome-devtools-mcp tools: {exc}"}
    problem = _unknown_action(steps, tools) or _malformed_selector(steps)
    if problem:
        return {"status": "error", "message": problem}

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
        outcome, used = await _run_scenario(client, number, step, tools, page_id)
        fallbacks = [*fallbacks, *used]
        if outcome["status"] != "success":
            return _reported(outcome, fallbacks)
        page_id = outcome["page_id"]
        problem = await hooks.after_step(number, step) if hooks else None
        if problem:
            return _reported({"status": "error", "message": problem}, fallbacks)

    return _reported({"status": "success", "steps": len(steps)}, fallbacks)


async def _run_scenario(
    client: Client, number: int, step: Step, tools: dict[str, set[str]], page_id: int
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Runs a step's actions in order; the first failing one fails the step and ends the run.

    Also returns the selector fallbacks its actions used.
    """
    fallbacks: list[dict[str, Any]] = []
    for action_number, action in enumerate(step.scenario, start=1):
        if action_number > 1:
            await _pause()
        response, used = await _run_action(client, action, tools[action.action], page_id)
        fallbacks = [*fallbacks, *({"step": number, "action_number": action_number, **entry} for entry in used)]
        if response["status"] != "success":
            return await _failure(client, number, action_number, action, response), fallbacks
        page_id = _selected(response["data"].get("pages") or [], page_id)
    return {"status": "success", "page_id": page_id}, fallbacks


async def _run_action(
    client: Client, action: Action, tool_params: set[str], page_id: int
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    params = {PAGE_PARAM: page_id, **action.params} if PAGE_PARAM in tool_params else action.params
    resolved = await resolve_selectors(client, params.get(PAGE_PARAM, page_id), params)
    if resolved["status"] != "success":
        return resolved, []
    return await call_tool(client, action.action, resolved["data"]), resolved["fallbacks"]


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
