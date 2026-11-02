from typing import Any

from fastmcp import Client


async def call_tool(client: Client, action: str, params: dict[str, Any]) -> dict[str, Any]:
    """Returns the tool's JSend envelope; a transport failure becomes an `error` envelope."""
    try:
        result = await client.call_tool(action, params, raise_on_error=False)
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

    if result.structured_content is not None:
        return result.structured_content
    text = " ".join(block.text for block in result.content if hasattr(block, "text"))
    return {"status": "error", "message": text}
