import re

SPLIT_KEY = re.compile(r"^pr\d+$")
SEPARATOR = "~"
CUSTOM_TOKEN = re.compile(r"^([kv])(\d+)(.*)$")
TOKEN_NAME_LENGTH = 2


def _split_value(key: str, raw: str) -> list[tuple[str, str]]:
    """Splits `id1~nmx~k0flag~v0yes` into `pr1.id`, `pr1.nm` and `pr1.flag` pairs."""
    fields: list[tuple[str, str]] = []
    custom_names: dict[str, str] = {}
    custom_values: dict[str, str] = {}

    for token in raw.split(SEPARATOR):
        custom = CUSTOM_TOKEN.match(token)
        if custom:
            kind, index, text = custom.groups()
            (custom_names if kind == "k" else custom_values)[index] = text
        elif len(token) > TOKEN_NAME_LENGTH:
            fields.append((f"{key}.{token[:TOKEN_NAME_LENGTH]}", token[TOKEN_NAME_LENGTH:]))

    named = [
        (f"{key}.{name}", custom_values[index])
        for index, name in custom_names.items()
        if name and index in custom_values
    ]
    return [*fields, *named]


def split_fields(event: dict[str, list[str]]) -> list[tuple[str, str]]:
    """Returns the dot-notation fields of every compound parameter (`pr1`, `pr2`, ...) in an event."""
    return [
        field
        for key, values in event.items()
        if SPLIT_KEY.match(key)
        for raw in values
        for field in _split_value(key, raw)
    ]
