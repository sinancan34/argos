import json
from typing import Any

from fastmcp import Client

from mcp_call import call_tool, evaluate

# chrome-devtools-mcp names elements by snapshot uids, which change every run, so scenarios
# name them by CSS selector instead; each selector param stands in for the uid param beside it.
UID_PARAMS = {"selector": "uid", "from_selector": "from_uid", "to_selector": "to_uid"}
FORM_UID_PARAMS = {"selector": "uid"}


def _form_elements(params: dict[str, Any]) -> list[dict[str, Any]]:
    elements = params.get("elements")
    return [element for element in elements if isinstance(element, dict)] if isinstance(elements, list) else []


def _selectors(params: dict[str, Any]) -> list[str]:
    named = [params.get(key) for key in UID_PARAMS] + [element.get("selector") for element in _form_elements(params)]
    return list(dict.fromkeys(selector for selector in named if isinstance(selector, str)))


def _uids(node: dict[str, Any]) -> list[str]:
    """Every uid in the snapshot, in document order; some text nodes have none."""
    own = [node["id"]] if "id" in node else []
    return [*own, *(uid for child in node.get("children", []) for uid in _uids(child))]


def _matcher(selectors: list[str]) -> str:
    """For each selector, the index of the first snapshot element it matches, or -1; text nodes match nothing."""
    return f"(...els) => {json.dumps(selectors)}.map(s => els.findIndex(el => el?.nodeType === 1 && el.matches(s)))"


def _swap(params: dict[str, Any], keys: dict[str, str], uid_of: dict[str, str]) -> dict[str, Any]:
    return {
        keys[key] if key in keys and isinstance(value, str) else key: uid_of.get(value, value) if key in keys else value
        for key, value in params.items()
    }


def _with_uids(params: dict[str, Any], uid_of: dict[str, str]) -> dict[str, Any]:
    swapped = _swap(params, UID_PARAMS, uid_of)
    if not isinstance(params.get("elements"), list):
        return swapped
    elements = [
        _swap(element, FORM_UID_PARAMS, uid_of) if isinstance(element, dict) else element
        for element in params["elements"]
    ]
    return {**swapped, "elements": elements}


async def resolve_selectors(client: Client, page_id: int, params: dict[str, Any]) -> dict[str, Any]:
    """Swaps each CSS selector in `params` for the uid of the first snapshot element it matches.

    Elements outside the accessibility snapshot have no uid, so selectors must name ones inside it.
    """
    selectors = _selectors(params)
    if not selectors:
        return {"status": "success", "data": params}

    snapshot = await call_tool(client, "take_snapshot", {"pageId": page_id})
    if snapshot["status"] != "success":
        return snapshot
    root = snapshot["data"].get("snapshot")
    if not isinstance(root, dict):
        return {"status": "error", "message": "take_snapshot returned no snapshot"}

    uids = _uids(root)
    found = await evaluate(client, page_id, _matcher(selectors), args=uids)
    if found["status"] != "success":
        return found
    indexes = found["data"]["result"]
    missing = [selector for selector, index in zip(selectors, indexes) if index < 0]
    if missing:
        return {"status": "fail", "data": {"selector": f"no element in the page snapshot matches {', '.join(missing)}"}}
    return {"status": "success", "data": _with_uids(params, {s: uids[i] for s, i in zip(selectors, indexes)})}
