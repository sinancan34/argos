from typing import Any, Awaitable, Callable

from fastmcp import Client

from mcp_call import call_tool
from scenario import Step

NEW_TAB_PLACEHOLDER = "$new_tab"
NO_NEW_TAB_RESPONSE = {
    "status": "fail",
    "data": {"target_id": f"{NEW_TAB_PLACEHOLDER}: no earlier click_element opened a tab"},
}
STOP_ACTION = "stop_browser"

BeforeStop = Callable[[], Awaitable[None]]


async def run_steps(client: Client, steps: list[Step], before_stop: BeforeStop | None = None) -> dict[str, Any]:
    """Runs steps in order; the first step that does not succeed ends the run.

    `before_stop` runs while the browser is still open: right before each
    stop_browser step, or after the last step when the scenario has none.
    """
    new_tab: str | None = None

    for number, step in enumerate(steps, start=1):
        if before_stop and step.action == STOP_ACTION:
            await before_stop()
        response = await _run_step(client, step, new_tab)
        if response["status"] != "success":
            return await _failure(client, number, step, response)
        new_tab = _opened_tab(step, response) or new_tab

    if before_stop and steps[-1].action != STOP_ACTION:
        await before_stop()
    return {"status": "success", "steps": len(steps)}


async def _run_step(client: Client, step: Step, new_tab: str | None) -> dict[str, Any]:
    if step.params.get("target_id") != NEW_TAB_PLACEHOLDER:
        return await call_tool(client, step.action, step.params)
    if new_tab is None:
        return NO_NEW_TAB_RESPONSE
    return await call_tool(client, step.action, {**step.params, "target_id": new_tab})


def _opened_tab(step: Step, response: dict[str, Any]) -> str | None:
    if step.action != "click_element":
        return None
    opened = response["data"]["new_targets"]
    return opened[0]["targetId"] if opened else None


async def _failure(
    client: Client, number: int, step: Step, response: dict[str, Any]
) -> dict[str, Any]:
    failure = {
        "status": "fail",
        "step": number,
        "action": step.action,
        "params": step.params,
        "response": response,
    }
    cleanup = await call_tool(client, STOP_ACTION, {})
    # A "fail" here means no browser was running, so there was nothing to close.
    return {**failure, "cleanup": cleanup} if cleanup["status"] == "error" else failure
