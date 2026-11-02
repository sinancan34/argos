import re

ITEM_KEY = re.compile(r"^pr\d+$")
CUSTOM_TOKEN = re.compile(r"^([kv])(\d+)(.*)$")
TOKEN_NAME_LENGTH = 2


def _split_item(item_key: str, raw: str) -> list[tuple[str, str]]:
    """Splits `id1~nmx~k0flag~v0yes` into `pr1.id`, `pr1.nm` and `pr1.flag` pairs."""
    fields: list[tuple[str, str]] = []
    custom_names: dict[str, str] = {}
    custom_values: dict[str, str] = {}

    for token in raw.split("~"):
        custom = CUSTOM_TOKEN.match(token)
        if custom:
            kind, index, text = custom.groups()
            (custom_names if kind == "k" else custom_values)[index] = text
        elif len(token) > TOKEN_NAME_LENGTH:
            fields.append((f"{item_key}.{token[:TOKEN_NAME_LENGTH]}", token[TOKEN_NAME_LENGTH:]))

    named = [
        (f"{item_key}.{name}", custom_values[index])
        for index, name in custom_names.items()
        if name and index in custom_values
    ]
    return [*fields, *named]


def item_fields(event: dict[str, list[str]]) -> list[tuple[str, str]]:
    """Returns the named fields of every GA4 item parameter (`pr1`, `pr2`, ...) in an event."""
    return [
        field
        for key, values in event.items()
        if ITEM_KEY.match(key)
        for raw in values
        for field in _split_item(key, raw)
    ]
