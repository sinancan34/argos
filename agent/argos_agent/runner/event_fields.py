"""Turns a captured request into events: flat {key: value} maps with the keys the request itself sends.

Whichever provider selected the request, an event is built the same way:
- the URL query gives the fields of the request;
- each non-empty body line is one event of a batch, merged with the query; a body value wins over a query value;
- an item (`pr1=id123~nmName~k0flag~v0yes`) is split on `~` into `pr1.id`, `pr1.nm` and `pr1.flag`, and the raw
  `pr1` key is dropped.
"""

import re
from urllib.parse import parse_qsl, urlsplit

Event = dict[str, str]

ITEM_KEY = re.compile(r"^pr\d+$")
ITEM_SEPARATOR = "~"
# `k1item_price` names custom param 1; GA4 sends its value right after it, `v15350000`. The value may start with
# digits, so its index is the one of the name before it, never read from the value token itself.
CUSTOM_NAME = re.compile(r"^k(\d+)(.*)$")
CUSTOM_VALUE = re.compile(r"^v\d")
FIELD_NAME_LENGTH = 2


def _item_fields(key: str, raw: str) -> Event:
    fields: Event = {}
    named: tuple[str, str] | None = None
    for token in raw.split(ITEM_SEPARATOR):
        name = CUSTOM_NAME.match(token)
        if name:
            named = (name.group(1), name.group(2))
        elif CUSTOM_VALUE.match(token):
            if named and named[1] and token.startswith(f"v{named[0]}"):
                fields[f"{key}.{named[1]}"] = token[len(named[0]) + 1 :]
            named = None
        elif len(token) >= FIELD_NAME_LENGTH:
            fields[f"{key}.{token[:FIELD_NAME_LENGTH]}"] = token[FIELD_NAME_LENGTH:]
    return fields


def _event(pairs: list[tuple[str, str]]) -> Event:
    """A later pair replaces an earlier one with the same key, so a body line wins over the query."""
    flat = dict(pairs)
    plain = {key: value for key, value in flat.items() if not ITEM_KEY.match(key)}
    items = [_item_fields(key, raw) for key, raw in flat.items() if ITEM_KEY.match(key)]
    return {**plain, **{field: value for item in items for field, value in item.items()}}


def request_events(url: str, body: str | None) -> list[Event]:
    """The events of one request: its query alone, or its query merged with each body line."""
    query = parse_qsl(urlsplit(url).query, keep_blank_values=True)
    lines = [line for line in (body or "").splitlines() if line.strip()]
    if not lines:
        return [_event(query)]
    return [_event([*query, *parse_qsl(line, keep_blank_values=True)]) for line in lines]
