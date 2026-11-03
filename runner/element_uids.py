import json
from collections.abc import Callable
from typing import Any

from fastmcp import Client

from mcp_call import call_tool, evaluate

# chrome-devtools-mcp names elements by snapshot uids, which change every run, so scenarios
# name them by CSS selector instead; each selector param stands in for the uid param beside it.
# A param may also list candidates in order; the first that names an element is used.
UID_PARAMS = {"selector": "uid", "from_selector": "from_uid", "to_selector": "to_uid"}
FORM_UID_PARAMS = {"selector": "uid"}
# A candidate with this prefix names an element by its accessible name in the snapshot, not by CSS.
TEXT_PREFIX = "text="


def _named(params: dict[str, Any]) -> dict[str, Any]:
    """Each selector param's value, keyed by where it sits in `params`."""
    elements = params.get("elements")
    form = {
        f"elements[{index}].selector": element["selector"]
        for index, element in enumerate(elements if isinstance(elements, list) else [])
        if isinstance(element, dict) and "selector" in element
    }
    return {**{key: params[key] for key in UID_PARAMS if key in params}, **form}


def _candidates(value: Any) -> list[str]:
    return [value] if isinstance(value, str) else value


def _is_candidate(value: Any) -> bool:
    return isinstance(value, str) and value.removeprefix(TEXT_PREFIX) != ""


def selector_problem(params: dict[str, Any]) -> str | None:
    """Names the first selector param that is neither a selector nor a non-empty list of them."""
    return next(
        (
            f"param '{path}' must be a selector or a non-empty list of selectors"
            for path, value in _named(params).items()
            if not (candidates := value if isinstance(value, list) else [value])
            or not all(map(_is_candidate, candidates))
        ),
        None,
    )


def _uids(node: dict[str, Any]) -> list[str]:
    """Every uid in the snapshot, in document order; some text nodes have none."""
    own = [node["id"]] if "id" in node else []
    return [*own, *(uid for child in node.get("children", []) for uid in _uids(child))]


def _named_uids(node: dict[str, Any]) -> list[tuple[str, str]]:
    """Every (accessible name, uid) pair in the snapshot, in document order."""
    own = [(node["name"], node["id"])] if "id" in node and "name" in node else []
    return [*own, *(pair for child in node.get("children", []) for pair in _named_uids(child))]


def _matcher(selectors: list[str]) -> str:
    """For each selector, the index of the first snapshot element it matches, or -1; text nodes match nothing."""
    return f"(...els) => {json.dumps(selectors)}.map(s => els.findIndex(el => el?.nodeType === 1 && el.matches(s)))"


def _pick(candidates: list[str], uid_of: dict[str, str]) -> str | None:
    return next((candidate for candidate in candidates if candidate in uid_of), None)


def _swap(params: dict[str, Any], keys: dict[str, str], uid_for: Callable[[Any], str]) -> dict[str, Any]:
    return {keys.get(key, key): uid_for(value) if key in keys else value for key, value in params.items()}


def _with_uids(params: dict[str, Any], uid_for: Callable[[Any], str]) -> dict[str, Any]:
    swapped = _swap(params, UID_PARAMS, uid_for)
    if not isinstance(params.get("elements"), list):
        return swapped
    elements = [
        _swap(element, FORM_UID_PARAMS, uid_for) if isinstance(element, dict) else element
        for element in params["elements"]
    ]
    return {**swapped, "elements": elements}


async def _candidate_uids(client: Client, page_id: int, root: dict[str, Any], candidates: list[str]) -> dict[str, Any]:
    """Maps each candidate that names an element of the snapshot to that element's uid."""
    # Reversed, so the first element with a name wins.
    by_name = dict(reversed(_named_uids(root)))
    texts = {
        candidate: by_name[candidate.removeprefix(TEXT_PREFIX)]
        for candidate in candidates
        if candidate.startswith(TEXT_PREFIX) and candidate.removeprefix(TEXT_PREFIX) in by_name
    }
    css = [candidate for candidate in candidates if not candidate.startswith(TEXT_PREFIX)]
    if not css:
        return {"status": "success", "data": texts}

    uids = _uids(root)
    found = await evaluate(client, page_id, _matcher(css), args=uids)
    if found["status"] != "success":
        return found
    matched = {selector: uids[index] for selector, index in zip(css, found["data"]["result"]) if index >= 0}
    return {"status": "success", "data": {**texts, **matched}}


def _fallbacks(named: dict[str, list[str]], uid_of: dict[str, str]) -> list[dict[str, Any]]:
    """Each param whose first candidate named no element, with the candidate used in its place."""
    picked = {path: _pick(candidates, uid_of) for path, candidates in named.items()}
    return [
        {"param": path, "used": used, "skipped": named[path][: named[path].index(used)]}
        for path, used in picked.items()
        if used != named[path][0]
    ]


async def resolve_selectors(client: Client, page_id: int, params: dict[str, Any]) -> dict[str, Any]:
    """Swaps each selector param in `params` for the uid of the element its first matching candidate names.

    Elements outside the accessibility snapshot have no uid, so candidates must name ones inside it.
    A success envelope lists under `fallbacks` the params whose first candidate named no element.
    """
    named = {path: _candidates(value) for path, value in _named(params).items()}
    if not named:
        return {"status": "success", "data": params, "fallbacks": []}

    snapshot = await call_tool(client, "take_snapshot", {"pageId": page_id})
    if snapshot["status"] != "success":
        return snapshot
    root = snapshot["data"].get("snapshot")
    if not isinstance(root, dict):
        return {"status": "error", "message": "take_snapshot returned no snapshot"}

    candidates = list(dict.fromkeys(candidate for listed in named.values() for candidate in listed))
    found = await _candidate_uids(client, page_id, root, candidates)
    if found["status"] != "success":
        return found
    uid_of = found["data"]
    missing = [candidate for listed in named.values() if _pick(listed, uid_of) is None for candidate in listed]
    if missing:
        unmatched = ", ".join(dict.fromkeys(missing))
        return {"status": "fail", "data": {"selector": f"no element in the page snapshot matches {unmatched}"}}
    return {
        "status": "success",
        "data": _with_uids(params, lambda value: uid_of[_pick(_candidates(value), uid_of)]),
        "fallbacks": _fallbacks(named, uid_of),
    }
