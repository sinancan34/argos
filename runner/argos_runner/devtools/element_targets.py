import json
import re
from collections.abc import Callable
from typing import Any

from fastmcp import Client

from argos_runner.devtools.mcp_call import call_tool, evaluate

# Playwright MCP names elements by snapshot refs, which change every run, so a scenario gives each element
# param, under its MCP name, a {"selector": ...} value that the runner swaps for a target naming one element.
# A selector may also list candidates in order; the first that names an element is used.
TARGET_PARAMS = ("target", "startTarget", "endTarget")
# browser_fill_form names each element under fields[].target.
FORM_PARAM = "fields"
FORM_TARGET_PARAM = "target"
SELECTOR_KEY = "selector"
# A candidate with this prefix names an element by its accessible name in the snapshot, not by CSS.
TEXT_PREFIX = "text="
SELECTOR_PROBLEM = 'must be {"selector": <selector or non-empty list of selectors>}; snapshot refs change every run'
# Playwright's selector chain for the first element of a CSS selector that a person can see: a target must
# name one element, and a selector may match several.
FIRST_VISIBLE = " >> visible=true >> nth=0"
# `- button "Buy" [ref=e2]`: a named node of browser_snapshot; the name is a JSON string.
_NAMED_NODE = re.compile(r'^\s*- [\w-]+ "((?:[^"\\]|\\.)*)".*?\[ref=([^\]]+)\]', re.MULTILINE)


def _items(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def element_values(params: dict[str, Any]) -> dict[str, Any]:
    """Each element param's value, keyed by where it sits in `params`."""
    top = {key: params[key] for key in TARGET_PARAMS if key in params}
    form = {
        f"{FORM_PARAM}[{index}].{FORM_TARGET_PARAM}": field[FORM_TARGET_PARAM]
        for index, field in enumerate(_items(params.get(FORM_PARAM)))
        if isinstance(field, dict) and FORM_TARGET_PARAM in field
    }
    return {**top, **form}


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


def with_targets(params: dict[str, Any], target_for: Callable[[Any], str]) -> dict[str, Any]:
    """`params` with each element param's value replaced by `target_for(value)`."""
    swapped = {key: target_for(value) if key in TARGET_PARAMS else value for key, value in params.items()}
    if isinstance(params.get(FORM_PARAM), list):
        fields = [
            {**field, FORM_TARGET_PARAM: target_for(field[FORM_TARGET_PARAM])}
            if isinstance(field, dict) and FORM_TARGET_PARAM in field
            else field
            for field in params[FORM_PARAM]
        ]
        swapped = {**swapped, FORM_PARAM: fields}
    return swapped


def snapshot_refs(snapshot: str) -> dict[str, str]:
    """The ref of the first node in document order with each accessible name."""
    return dict(reversed([(json.loads(f'"{name}"'), ref) for name, ref in _NAMED_NODE.findall(snapshot)]))


def _visible_matcher(selectors: list[str]) -> str:
    """For each CSS selector, whether it names an element a person can see, as Playwright's `visible=` judges.

    Open shadow roots are searched too, as Playwright's CSS engine does.
    """
    roots = "const roots = r => [r, ...[...r.querySelectorAll('*')].filter(e => e.shadowRoot).flatMap(e => roots(e.shadowRoot))];"
    seen = (
        "const seen = el => { const box = el.getBoundingClientRect(); "
        "return box.width > 0 && box.height > 0 && getComputedStyle(el).visibility !== 'hidden'; };"
    )
    found = "s => roots(document).some(root => [...root.querySelectorAll(s)].some(seen))"
    return f"() => {{ {roots} {seen} return {json.dumps(selectors)}.map({found}); }}"


def _pick(candidates: list[str], target_of: dict[str, str]) -> str | None:
    return next((candidate for candidate in candidates if candidate in target_of), None)


async def _text_targets(client: Client, texts: list[str]) -> dict[str, Any]:
    if not texts:
        return {"status": "success", "data": {}}
    snapshot = await call_tool(client, "browser_snapshot", {})
    if snapshot["status"] != "success":
        return snapshot
    refs = snapshot_refs(snapshot["data"].get("Snapshot", ""))
    named = {text: refs[text.removeprefix(TEXT_PREFIX)] for text in texts if text.removeprefix(TEXT_PREFIX) in refs}
    return {"status": "success", "data": named}


async def _css_targets(client: Client, css: list[str]) -> dict[str, Any]:
    if not css:
        return {"status": "success", "data": {}}
    found = await evaluate(client, _visible_matcher(css))
    if found["status"] != "success":
        return found
    return {"status": "success", "data": {s: f"{s}{FIRST_VISIBLE}" for s, seen in zip(css, found["data"]["result"]) if seen}}


async def _candidate_targets(client: Client, candidates: list[str]) -> dict[str, Any]:
    """Maps each candidate that names an element of the current tab to a target naming that one element."""
    texts = await _text_targets(client, [candidate for candidate in candidates if candidate.startswith(TEXT_PREFIX)])
    if texts["status"] != "success":
        return texts
    css = await _css_targets(client, [candidate for candidate in candidates if not candidate.startswith(TEXT_PREFIX)])
    if css["status"] != "success":
        return css
    return {"status": "success", "data": {**texts["data"], **css["data"]}}


def _fallbacks(named: dict[str, list[str]], target_of: dict[str, str]) -> list[dict[str, Any]]:
    """Each param whose first candidate named no element, with the candidate used in its place."""
    picked = {path: _pick(candidates, target_of) for path, candidates in named.items()}
    return [
        {"param": path, "used": used, "skipped": named[path][: named[path].index(used)]}
        for path, used in picked.items()
        if used != named[path][0]
    ]


async def resolve_selectors(client: Client, params: dict[str, Any]) -> dict[str, Any]:
    """Swaps each element param's selector for a target naming the element its first matching candidate names.

    A text candidate becomes the snapshot ref of the element with that accessible name; a CSS one
    becomes Playwright's selector for its first visible element.
    A success envelope lists under `fallbacks` the params whose first candidate named no element.
    """
    named = {path: _candidates(value) for path, value in element_values(params).items()}
    if not named:
        return {"status": "success", "data": params, "fallbacks": []}

    candidates = list(dict.fromkeys(candidate for listed in named.values() for candidate in listed))
    found = await _candidate_targets(client, candidates)
    if found["status"] != "success":
        return found
    target_of = found["data"]
    missing = [candidate for listed in named.values() if _pick(listed, target_of) is None for candidate in listed]
    if missing:
        unmatched = ", ".join(dict.fromkeys(missing))
        return {"status": "fail", "data": {"selector": f"no element on the page matches {unmatched}"}}
    return {
        "status": "success",
        "data": with_targets(params, lambda value: target_of[_pick(_candidates(value), target_of)]),
        "fallbacks": _fallbacks(named, target_of),
    }
