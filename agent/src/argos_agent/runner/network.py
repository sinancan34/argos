"""Hears every request the browser sends, in every tab, through a listener on the browser context.

The listener is Playwright code the server runs in its own process, not in the page, so the site cannot see it.
It hears a request as it is sent: a popup that closes itself or a page left by a navigation loses nothing.
"""

import json
from dataclasses import dataclass
from typing import Any

from jsonschema import Draft202012Validator

from argos_agent.playwright_mcp.client import PlaywrightMCP

RUN_CODE = "browser_run_code_unsafe"
RESULT_SECTION = "Result"
# The list lives on the context: it outlives each call, while the code's own globals do not.
LISTEN = """async (page) => {
  const context = page.context();
  if (!context.argosRequests) {
    context.argosRequests = [];
    context.on('request', (request) => context.argosRequests.push({url: request.url(), body: request.postData()}));
  }
}"""
HEARD_SCHEMA: dict[str, Any] = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {"url": {"type": "string"}, "body": {"type": ["string", "null"]}},
        "required": ["url", "body"],
    },
}


class NetworkError(RuntimeError):
    """The server could not start the listener or read what it heard."""


@dataclass(frozen=True)
class Captured:
    url: str
    body: str | None


def _since_code(start: int) -> str:
    # `start` is the only value put into the code, and it is an int.
    return f"""async (page) => {{
  const heard = page.context().argosRequests;
  if (!heard) throw new Error('the request listener was not started');
  return heard.slice({int(start)});
}}"""


async def start_listening(mcp: PlaywrightMCP) -> None:
    """Starts hearing the requests of every tab; a second start keeps the first listener."""
    result = await mcp.call(RUN_CODE, {"code": LISTEN})
    if result.is_error:
        raise NetworkError(f"{RUN_CODE}: cannot start the request listener: {result.error}")


async def requests_since(mcp: PlaywrightMCP, start: int) -> list[Captured]:
    """The requests heard after the first `start`, in the order they were sent."""
    result = await mcp.call(RUN_CODE, {"code": _since_code(start)})
    if result.is_error:
        raise NetworkError(f"{RUN_CODE}: cannot read the heard requests: {result.error}")
    text = result.sections.get(RESULT_SECTION, "")
    try:
        heard = json.loads(text)
    except ValueError as exc:
        raise NetworkError(f"{RUN_CODE}: the heard requests are not JSON: {text[:200]!r}") from exc
    error = next(Draft202012Validator(HEARD_SCHEMA).iter_errors(heard), None)
    if error is not None:
        raise NetworkError(f"{RUN_CODE}: unexpected heard requests at {error.json_path}: {error.message}")
    return [Captured(request["url"], request["body"]) for request in heard]
