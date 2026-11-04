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
# `k0flag` names custom param 0, `v0yes` gives its value.
CUSTOM_TOKEN = re.compile(r"^([kv])(\d+)(.*)$")
FIELD_NAME_LENGTH = 2


def _item_fields(key: str, raw: str) -> Event:
    fields: Event = {}
    names: dict[str, str] = {}
    values: dict[str, str] = {}
    for token in raw.split(ITEM_SEPARATOR):
        custom = CUSTOM_TOKEN.match(token)
        if custom:
            kind, index, text = custom.groups()
            (names if kind == "k" else values)[index] = text
        elif len(token) >= FIELD_NAME_LENGTH:
            fields[f"{key}.{token[:FIELD_NAME_LENGTH]}"] = token[FIELD_NAME_LENGTH:]
    custom_fields = {f"{key}.{name}": values[index] for index, name in names.items() if name and index in values}
    return {**fields, **custom_fields}


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
