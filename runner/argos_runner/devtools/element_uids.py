import json
from collections.abc import Callable
from typing import Any

from fastmcp import Client

from argos_runner.devtools.mcp_call import call_tool, evaluate

# chrome-devtools-mcp names elements by snapshot uids, which change every run, so a scenario gives each
# element param, under its MCP name, a {"selector": ...} value that the runner swaps for the element's uid.
# A selector may also list candidates in order; the first that names an element is used.
UID_PARAMS = ("uid", "from_uid", "to_uid")
# fill_form names each element under elements[].uid; evaluate_script passes elements as args[].
FORM_PARAM = "elements"
FORM_UID_PARAM = "uid"
SCRIPT_ARGS_PARAM = "args"
SELECTOR_KEY = "selector"
# A candidate with this prefix names an element by its accessible name in the snapshot, not by CSS.
TEXT_PREFIX = "text="
SELECTOR_PROBLEM = 'must be {"selector": <selector or non-empty list of selectors>}; snapshot uids change every run'


def _items(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def element_values(params: dict[str, Any]) -> dict[str, Any]:
    """Each element param's value, keyed by where it sits in `params`."""
    top = {key: params[key] for key in UID_PARAMS if key in params}
    form = {
        f"{FORM_PARAM}[{index}].{FORM_UID_PARAM}": element[FORM_UID_PARAM]
        for index, element in enumerate(_items(params.get(FORM_PARAM)))
        if isinstance(element, dict) and FORM_UID_PARAM in element
    }
    script = {f"{SCRIPT_ARGS_PARAM}[{index}]": arg for index, arg in enumerate(_items(params.get(SCRIPT_ARGS_PARAM)))}
    return {**top, **form, **script}


def _candidates(value: dict[str, Any]) -> list[Any]:
    selector = value[SELECTOR_KEY]
    return [selector] if isinstance(selector, str) else selector


def _is_candidate(value: Any) -> bool:
    return isinstance(value, str) and value.removeprefix(TEXT_PREFIX) != ""


def _is_selector(value: Any) -> bool:
    if not isinstance(value, dict) or set(value) != {SELECTOR_KEY}:
        return False
    candidates = _candidates(value)
    return isinstance(candidates, list) and bool(candidates) and all(map(_is_candidate, candidates))


def malformed_elements(params: dict[str, Any]) -> list[str]:
    """Where each element param sits whose value is not a selector."""
    return [path for path, value in element_values(params).items() if not _is_selector(value)]


def with_uids(params: dict[str, Any], uid_for: Callable[[Any], str]) -> dict[str, Any]:
    """`params` with each element param's value replaced by `uid_for(value)`."""
    swapped = {key: uid_for(value) if key in UID_PARAMS else value for key, value in params.items()}
    if isinstance(params.get(FORM_PARAM), list):
        elements = [
            {**element, FORM_UID_PARAM: uid_for(element[FORM_UID_PARAM])}
            if isinstance(element, dict) and FORM_UID_PARAM in element
            else element
            for element in params[FORM_PARAM]
        ]
        swapped = {**swapped, FORM_PARAM: elements}
    if isinstance(params.get(SCRIPT_ARGS_PARAM), list):
        swapped = {**swapped, SCRIPT_ARGS_PARAM: [uid_for(arg) for arg in params[SCRIPT_ARGS_PARAM]]}
    return swapped


def _nodes(node: dict[str, Any]) -> list[dict[str, Any]]:
    """Every node of the snapshot, in document order; some text nodes have no uid."""
    return [node, *(nested for child in node.get("children", []) for nested in _nodes(child))]


def _matcher(selectors: list[str]) -> str:
    """For each selector, the index of the first snapshot element it matches, or -1; text nodes match nothing."""
    return f"(...els) => {json.dumps(selectors)}.map(s => els.findIndex(el => el?.nodeType === 1 && el.matches(s)))"


def _pick(candidates: list[str], uid_of: dict[str, str]) -> str | None:
    return next((candidate for candidate in candidates if candidate in uid_of), None)


async def _candidate_uids(client: Client, page_id: int, root: dict[str, Any], candidates: list[str]) -> dict[str, Any]:
    """Maps each candidate that names an element of the snapshot to that element's uid."""
    # Reversed, so the first element with a name wins.
    by_name = dict(reversed([(node["name"], node["id"]) for node in _nodes(root) if "id" in node and "name" in node]))
    texts = {
        candidate: by_name[candidate.removeprefix(TEXT_PREFIX)]
        for candidate in candidates
        if candidate.startswith(TEXT_PREFIX) and candidate.removeprefix(TEXT_PREFIX) in by_name
    }
    css = [candidate for candidate in candidates if not candidate.startswith(TEXT_PREFIX)]
    if not css:
        return {"status": "success", "data": texts}

    uids = [node["id"] for node in _nodes(root) if "id" in node]
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
    """Swaps each element param's selector for the uid of the element its first matching candidate names.

    Elements outside the accessibility snapshot have no uid, so candidates must name ones inside it.
    A success envelope lists under `fallbacks` the params whose first candidate named no element.
    """
    named = {path: _candidates(value) for path, value in element_values(params).items()}
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
        "data": with_uids(params, lambda value: uid_of[_pick(_candidates(value), uid_of)]),
        "fallbacks": _fallbacks(named, uid_of),
    }
