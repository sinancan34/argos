"""What playwright.dev/mcp documents: its tools, their params, and the server's launch flags.

The agent layer allows no tool, param or flag that these pages do not name.
"""

import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field, replace
from html.parser import HTMLParser
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

DOCS_BASE = "https://playwright.dev/mcp/"
# The pages of the Playwright MCP docs, in the order of its sidebar.
DOC_PAGES = (
    "introduction",
    "installation",
    "clients/vscode",
    "clients/cursor",
    "clients/claude-code",
    "clients/claude-desktop",
    "clients/windsurf",
    "clients/other-clients",
    "snapshots",
    "capabilities",
    "vision-mode",
    "tools/navigation",
    "tools/interaction",
    "tools/forms",
    "tools/keyboard-mouse",
    "tools/tabs",
    "tools/dialogs",
    "tools/file-upload",
    "tools/waiting",
    "tools/network-mocking",
    "tools/storage",
    "tools/console",
    "tools/screenshots",
    "tools/code-execution",
    "tools/tracing",
    "tools/devtools",
    "tools/assertions",
    "tools/pdf",
    "tools/video",
    "configuration/user-profile",
    "configuration/browser-extension",
    "configuration/options",
)
TOOL_PAGE_PREFIX = "tools/"
FETCH_TIMEOUT_SECONDS = 30
USER_AGENT = "argos-agent"
TOOL = re.compile(r"browser_\w+")
FLAG = re.compile(r"--[a-z][a-z0-9-]+")
# `key (string), value (string)`: the params in a row of a "Tool | Parameters" table.
INLINE_PARAM = re.compile(r"(\w+) \([^)]+\)")
REQUIRED = {"yes": True, "no": False}
# The Type cell of a param whose items a "Field key" table documents.
OBJECT_LIST = "object[]"
HEADINGS = ("h1", "h2", "h3", "h4")
# Heading anchors end in a zero-width space.
ZERO_WIDTH_SPACE = "​"

Event = tuple[str, Any]


class DocsError(Exception):
    """A docs page could not be read, or two pages document the same param differently."""


@dataclass(frozen=True)
class DocumentedParam:
    """`required` is None where the page does not say.

    `fields` holds the documented keys of each item of an object[] param, each mapped to whether it is required.
    """

    required: bool | None
    fields: Mapping[str, bool | None] = field(default_factory=dict)


Tools = dict[str, dict[str, DocumentedParam]]


@dataclass(frozen=True)
class Documentation:
    tools: Mapping[str, Mapping[str, DocumentedParam]]
    flags: frozenset[str]


class _Article(HTMLParser):
    """Flattens a page's <article> into heading, code, table and row events; the sidebar stays out.

    The pages are minified and leave </th>, </td> and </tr> out, so a new cell or row closes the open one.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.events: list[Event] = []
        self._depth = 0
        self._text: list[str] | None = None
        self._code: list[str] | None = None
        self._row: list[str] | None = None
        self._in_table = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "article":
            self._depth += 1
        if not self._depth:
            return
        if tag in HEADINGS:
            self._text = []
        elif tag in ("th", "td"):
            self._end_cell()
            self._text = []
        elif tag in ("tr", "thead", "tbody"):
            self._end_row()
        if tag == "tr":
            self._row = []
        elif tag == "table":
            self._in_table = True
            self.events.append(("table", None))
        elif tag == "code" and not self._in_table:
            self._code = []

    def handle_endtag(self, tag: str) -> None:
        if not self._depth:
            return
        if tag == "article":
            self._depth -= 1
        elif tag in HEADINGS and self._text is not None and self._row is None:
            self.events.append(("heading", "".join(self._text).replace(ZERO_WIDTH_SPACE, "").strip()))
            self._text = None
        elif tag in ("th", "td"):
            self._end_cell()
        elif tag == "tr":
            self._end_row()
        elif tag == "table":
            self._end_row()
            self._in_table = False
            self.events.append(("/table", None))
        elif tag == "code" and self._code is not None:
            self.events.append(("code", "".join(self._code).strip()))
            self._code = None

    def handle_data(self, data: str) -> None:
        if self._text is not None:
            self._text.append(data)
        if self._code is not None:
            self._code.append(data)

    def _end_cell(self) -> None:
        if self._row is None:
            return
        if self._text is not None:
            self._row.append(" ".join("".join(self._text).split()))
        self._text = None

    def _end_row(self) -> None:
        self._end_cell()
        if self._row is not None:
            self.events.append(("row", self._row))
        self._row = None


def _events(html: str) -> list[Event]:
    article = _Article()
    article.feed(html)
    article.close()
    return article.events


class _Sections:
    """Gives each parameter table to the tools its section documents.

    A `browser_*` heading (or `browser_a / browser_b`) documents the tools it names; under any other heading,
    the section documents the first tool it names in code.
    """

    def __init__(self) -> None:
        self.tools: Tools = {}
        self._named: list[str] = []
        self._mentioned: str | None = None
        self._header: list[str] | None = None
        self._object_list: str | None = None

    def heading(self, text: str) -> None:
        names = [name.strip() for name in text.split("/")]
        self._named = names if all(TOOL.fullmatch(name) for name in names) else []
        self.tools = {**self.tools, **{name: self.tools.get(name, {}) for name in self._named}}
        self._mentioned, self._object_list = None, None

    def code(self, text: str) -> None:
        if self._mentioned is None and TOOL.fullmatch(text):
            self._mentioned = text

    def table(self) -> None:
        self._header = None

    def row(self, cells: list[str]) -> None:
        if self._header is None:
            self._header = cells
            return
        row = dict(zip(self._header, cells, strict=False))
        kind = self._header[0] if self._header else ""
        if kind == "Parameter":
            self._param(row)
        elif kind == "Field key":
            self._field(row)
        elif kind == "Tool":
            self._tool_row(row)

    def _owners(self) -> list[str]:
        return self._named or ([self._mentioned] if self._mentioned else [])

    def _set(self, tool: str, name: str, param: DocumentedParam) -> None:
        self.tools = {**self.tools, tool: {**self.tools.get(tool, {}), name: param}}

    def _param(self, row: dict[str, str]) -> None:
        owners = self._owners()
        for tool in owners:
            self._set(tool, row["Parameter"], DocumentedParam(required=REQUIRED.get(row.get("Required", ""))))
        if owners and row.get("Type") == OBJECT_LIST:
            self._object_list = row["Parameter"]

    def _field(self, row: dict[str, str]) -> None:
        """A "Field key" row documents an item key of the section's object[] param."""
        if self._object_list is None:
            return
        for tool in self._owners():
            param = self.tools.get(tool, {}).get(self._object_list)
            if param is None:
                continue
            fields = {**param.fields, row["Field key"]: REQUIRED.get(row.get("Required", ""))}
            self._set(tool, self._object_list, replace(param, fields=fields))

    def _tool_row(self, row: dict[str, str]) -> None:
        tool = row["Tool"]
        if not TOOL.fullmatch(tool):
            return
        params = {name: DocumentedParam(required=None) for name in INLINE_PARAM.findall(row.get("Parameters", ""))}
        self.tools = {**self.tools, tool: {**self.tools.get(tool, {}), **params}}


def parse_page(html: str) -> Tools:
    """The tools a page documents, each with its documented params."""
    sections = _Sections()
    for kind, value in _events(html):
        if kind == "heading":
            sections.heading(value)
        elif kind == "code":
            sections.code(value)
        elif kind == "table":
            sections.table()
        elif kind == "row":
            sections.row(value)
    return sections.tools


def parse_flags(html: str) -> frozenset[str]:
    """The `--flags` a page names in code or in a table."""
    texts = [value if kind == "code" else " ".join(value) for kind, value in _events(html) if kind in ("code", "row")]
    return frozenset(flag for text in texts for flag in FLAG.findall(text))


def _agree(where: str, known: bool | None, new: bool | None) -> bool | None:
    if known is None or known == new:
        return new
    if new is None:
        return known
    raise DocsError(f"{where}: one page says required={known}, another required={new}")


def _merge_param(where: str, known: DocumentedParam | None, new: DocumentedParam) -> DocumentedParam:
    if known is None or known == new:
        return new
    if known.fields and new.fields and known.fields != new.fields:
        raise DocsError(f"{where}: pages document different item keys")
    return DocumentedParam(required=_agree(where, known.required, new.required), fields=known.fields or new.fields)


def merge_pages(pages: Iterable[Mapping[str, Mapping[str, DocumentedParam]]]) -> Tools:
    """One entry per tool across all pages; a page that says whether a param is required wins over one that does not."""
    merged: Tools = {}
    for page in pages:
        for tool, params in page.items():
            known = merged.get(tool, {})
            update = {name: _merge_param(f"{tool}.{name}", known.get(name), param) for name, param in params.items()}
            merged = {**merged, tool: {**known, **update}}
    return merged


def fetch_page(page: str, timeout: float = FETCH_TIMEOUT_SECONDS) -> str:
    # Always https://playwright.dev: DOCS_BASE is fixed and `page` is one of DOC_PAGES.
    url = f"{DOCS_BASE}{page}"
    request = Request(url, headers={"User-Agent": USER_AGENT})  # noqa: S310
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310  # nosec B310
            body: bytes = response.read()
            return body.decode("utf-8")
    except (URLError, OSError, UnicodeDecodeError) as exc:
        raise DocsError(f"cannot read {url}: {exc}") from exc


def read_documentation(fetch: Callable[[str], str] = fetch_page) -> Documentation:
    """Reads every docs page and merges what they document.

    A tool reference page that documents no tool (an error page, a changed layout) fails the read, so a broken page
    cannot shrink the catalog.
    """
    pages = {page: fetch(page) for page in DOC_PAGES}
    tools = {page: parse_page(html) for page, html in pages.items()}
    empty = [page for page, found in tools.items() if page.startswith(TOOL_PAGE_PREFIX) and not found]
    if empty:
        raise DocsError(f"no tool documented on {', '.join(DOCS_BASE + page for page in empty)}")
    return Documentation(
        tools=merge_pages(tools.values()),
        flags=frozenset().union(*(parse_flags(html) for html in pages.values())),
    )
