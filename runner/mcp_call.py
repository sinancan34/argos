import json
import re
from typing import Any

from fastmcp import Client

# evaluate_script prints the function's JSON return value inside a ```json fence.
_SCRIPT_RESULT = re.compile(r"```json\n(.*)\n```", re.DOTALL)


async def call_tool(client: Client, tool: str, params: dict[str, Any]) -> dict[str, Any]:
    """Wraps a chrome-devtools-mcp result in a JSend envelope; any failure becomes an `error` envelope."""
    try:
        result = await client.call_tool(tool, params, raise_on_error=False)
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

    structured = result.structured_content
    if not result.is_error and structured is not None:
        return {"status": "success", "data": structured}
    text = " ".join(block.text for block in result.content if hasattr(block, "text"))
    return {"status": "error", "message": (structured or {}).get("errorMessage") or text}


async def evaluate(
    client: Client, page_id: int, function: str, wait_for_stable_dom: bool = False, args: list[str] | None = None
) -> dict[str, Any]:
    """Runs `function` in the page, called with the elements of the snapshot uids in `args`.

    A success envelope carries its return value as `data.result`.
    """
    uids = {"args": args} if args is not None else {}
    params = {"pageId": page_id, "function": function, "waitForStableDom": wait_for_stable_dom, **uids}
    response = await call_tool(client, "evaluate_script", params)
    if response["status"] != "success":
        return response

    message = response["data"].get("message", "")
    match = _SCRIPT_RESULT.search(message)
    try:
        result = json.loads(match.group(1) if match else "")
    except ValueError:
        return {"status": "error", "message": f"unreadable script result: {message}"}
    return {"status": "success", "data": {**response["data"], "result": result}}
