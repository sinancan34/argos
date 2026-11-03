import asyncio
import json
from typing import Any

from fastmcp import Client

from mcp_call import evaluate

# chrome-devtools-mcp finds elements only through its accessibility snapshot,
# so CSS selectors are checked by page scripts, about twice a second.
POLL_SECONDS = 0.5


def _on_element(selector: str, body: str) -> str:
    return f"() => {{ const el = document.querySelector({json.dumps(selector)}); return {body}; }}"


def _timed_out(timeout: float) -> dict[str, Any]:
    return {"status": "fail", "data": {"selector": f"no element matched within {timeout}s"}}


async def wait_for(client: Client, page_id: int, selector: str, timeout: float) -> dict[str, Any]:
    """Checks for the element until it exists or `timeout` seconds pass.

    A check that throws, as it does while a navigation replaces the page, is retried.
    """
    loop = asyncio.get_running_loop()
    deadline = loop.time() + timeout
    while True:
        response = await evaluate(client, page_id, _on_element(selector, "el !== null"))
        if response["status"] == "success" and response["data"]["result"] is True:
            return {"status": "success", "data": {}}
        remaining = deadline - loop.time()
        if remaining <= 0:
            # A page that keeps throwing, such as for an invalid selector, says more than a timeout.
            return response if response["status"] == "error" else _timed_out(timeout)
        await asyncio.sleep(min(POLL_SECONDS, remaining))


async def click_element(client: Client, page_id: int, selector: str, timeout: float) -> dict[str, Any]:
    """Waits for the element, then calls `el.click()` in the page; no real mouse event is sent."""
    found = await wait_for(client, page_id, selector, timeout)
    if found["status"] != "success":
        return found

    click = _on_element(selector, "el !== null && (el.click(), true)")
    # The server then waits for the page to settle and reports the tabs the click opened.
    clicked = await evaluate(client, page_id, click, wait_for_stable_dom=True)
    if clicked["status"] != "success":
        return clicked
    if clicked["data"]["result"] is not True:
        return {"status": "fail", "data": {"selector": "element disappeared before the click"}}
    return {"status": "success", "data": {"opened_pages": clicked["data"].get("openedPages", [])}}
