import json
import re
from typing import Any

from fastmcp import Client

# Playwright MCP answers in text: each part of a result under its own `### <name>` heading.
_HEADING = re.compile(r"^### (.+)$", re.MULTILINE)
RESULT = "Result"
ERROR = "Error"


def sections(text: str) -> dict[str, str]:
    """The parts of a tool result by heading; JSON results escape line breaks, so no value holds a heading."""
    parts = _HEADING.split(text)
    return {name.strip(): body.strip() for name, body in zip(parts[1::2], parts[2::2])}


async def call_tool(client: Client, tool: str, params: dict[str, Any]) -> dict[str, Any]:
    """Wraps a Playwright MCP result in a JSend envelope, its parts under `data`; any failure becomes an `error`."""
    try:
        result = await client.call_tool(tool, params, raise_on_error=False)
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

    text = "\n".join(block.text for block in result.content if hasattr(block, "text"))
    parts = sections(text)
    if result.is_error or ERROR in parts:
        return {"status": "error", "message": parts.get(ERROR) or text}
    return {"status": "success", "data": parts}


async def evaluate(client: Client, function: str, target: str | None = None) -> dict[str, Any]:
    """Runs `function` in the current tab, called with the element `target` names if one is given.

    A success envelope carries its return value as `data.result`.
    """
    params = {"function": function, **({"target": target} if target else {})}
    response = await call_tool(client, "browser_evaluate", params)
    if response["status"] != "success":
        return response

    printed = response["data"].get(RESULT, "")
    try:
        result = json.loads(printed)
    except ValueError:
        return {"status": "error", "message": f"unreadable script result: {printed}"}
    return {"status": "success", "data": {**response["data"], "result": result}}
