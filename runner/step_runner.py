import asyncio
import random
from typing import Any, Awaitable, Callable, Protocol

from fastmcp import Client

from mcp_call import call_tool
from page_actions import click_element, wait_for
from scenario import NEW_TAB_PLACEHOLDER, Step

NO_NEW_TAB_RESPONSE = {
    "status": "fail",
    "data": {"target_id": f"{NEW_TAB_PLACEHOLDER}: no earlier click_element opened a tab"},
}
STEP_DELAY_RANGE_SECONDS = (1.0, 5.0)



class StepHooks(Protocol):
    """Runs around each step; a returned message ends the run as an error."""

    async def before_step(self, number: int, step: Step) -> str | None: ...

    async def after_step(self, number: int, step: Step) -> str | None: ...


Action = Callable[[Client, int, dict[str, Any]], Awaitable[dict[str, Any]]]
_sleep = asyncio.sleep


async def _navigate(client: Client, page_id: int, params: dict[str, Any]) -> dict[str, Any]:
    return await call_tool(client, "navigate_page", {"pageId": page_id, "type": "url", "url": params["url"]})


async def _wait_for(client: Client, page_id: int, params: dict[str, Any]) -> dict[str, Any]:
    return await wait_for(client, page_id, params["selector"], params["timeout"])


async def _click_element(client: Client, page_id: int, params: dict[str, Any]) -> dict[str, Any]:
    return await click_element(client, page_id, params["selector"], params["timeout"])


ACTIONS: dict[str, Action] = {"navigate": _navigate, "wait_for": _wait_for, "click_element": _click_element}


async def run_steps(client: Client, steps: list[Step], hooks: StepHooks | None = None) -> dict[str, Any]:
    """Runs steps in order with a random pause between them; the first failing step ends the run.

    Steps without `target_id` run on the browser's first page. `hooks` run right before and
    after each step, after the pause, while the browser is still open.
    """
    # Listing pages is what launches the browser.
    listed = await call_tool(client, "list_pages", {})
    pages = listed["data"].get("pages") if listed["status"] == "success" else None
    if not pages:
        return {"status": "error", "message": f"cannot open the browser: {listed.get('message', 'no open page')}"}

    main_page = pages[0]["id"]
    new_tab: int | None = None
    for number, step in enumerate(steps, start=1):
        if number > 1:
            await _sleep(random.uniform(*STEP_DELAY_RANGE_SECONDS))
        problem = await hooks.before_step(number, step) if hooks else None
        if problem:
            return {"status": "error", "message": problem}
        response = await _run_step(client, step, main_page, new_tab)
        if response["status"] != "success":
            return await _failure(client, number, step, response)
        new_tab = _opened_tab(response) or new_tab
        problem = await hooks.after_step(number, step) if hooks else None
        if problem:
            return {"status": "error", "message": problem}

    return {"status": "success", "steps": len(steps)}


async def _run_step(client: Client, step: Step, main_page: int, new_tab: int | None) -> dict[str, Any]:
    on_new_tab = step.params.get("target_id") == NEW_TAB_PLACEHOLDER
    if on_new_tab and new_tab is None:
        return NO_NEW_TAB_RESPONSE
    return await ACTIONS[step.action](client, new_tab if on_new_tab else main_page, step.params)


def _opened_tab(response: dict[str, Any]) -> int | None:
    opened = response["data"].get("opened_pages")
    return opened[0]["id"] if opened else None


async def open_tabs(client: Client) -> dict[str, Any]:
    """Tells a blocked page from a broken selector: both fail a step with the same timeout."""
    response = await call_tool(client, "list_pages", {})
    if response["status"] != "success" or not response["data"].get("pages"):
        return {}
    return {"tabs": [{"url": page.get("url"), "title": page.get("title")} for page in response["data"]["pages"]]}


async def _failure(client: Client, number: int, step: Step, response: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "fail",
        "step": number,
        "action": step.action,
        "params": step.params,
        "response": response,
        **await open_tabs(client),
    }
