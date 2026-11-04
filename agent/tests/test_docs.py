from urllib.error import URLError

import pytest

from argos_agent.playwright_mcp import docs
from argos_agent.playwright_mcp.docs import (
    DOC_PAGES,
    DocsError,
    DocumentedParam,
    merge_pages,
    parse_flags,
    parse_page,
    read_documentation,
)

pytestmark = pytest.mark.unit

PARAMS_HEADER = "<table><thead><tr><th>Parameter<th>Type<th>Required<th>Description<tbody>"


def page(article: str) -> str:
    """A minified docs page: unclosed cells and rows, and a sidebar table outside the <article> that must be ignored."""
    sidebar = (
        f"<aside><h2>browser_sidebar</h2>{PARAMS_HEADER}<tr><td><code>leak</code><td>string<td>yes</table></aside>"
    )
    return f"<html><body>{sidebar}<article>{article}</article></body></html>"


def params_table(*rows: tuple[str, str] | tuple[str, str, str]) -> str:
    """Rows of (name, required) or (name, required, type); the type defaults to string."""
    cells = "".join(f"<tr><td><code>{row[0]}</code><td>{(*row, 'string')[2]}<td>{row[1]}<td>text" for row in rows)
    return f"{PARAMS_HEADER}{cells}</table>"


FIELD_KEYS = (
    "<table><thead><tr><th>Field key<th>Type<th>Required<th>Description<tbody>"
    "<tr><td><code>name</code><td>string<td>yes<td>Name<tr><td><code>value</code><td>string<td>no<td>Value</table>"
)


def test_a_tool_heading_owns_the_parameter_table_after_it() -> None:
    html = page(
        "<h2 id=browser_navigate>browser_navigate<a href=#browser_navigate>​</a></h2><p>Navigate.</p>"
        + params_table(("url", "yes"), ("timeout", "no"))
    )

    assert parse_page(html) == {
        "browser_navigate": {"url": DocumentedParam(required=True), "timeout": DocumentedParam(required=False)}
    }


def test_a_shared_heading_gives_its_table_to_every_tool_it_names() -> None:
    html = page("<h2>browser_mouse_down / browser_mouse_up</h2>" + params_table(("button", "no")))

    assert parse_page(html) == {
        "browser_mouse_down": {"button": DocumentedParam(required=False)},
        "browser_mouse_up": {"button": DocumentedParam(required=False)},
    }


def test_a_tool_parameters_table_lists_each_tool_with_its_params() -> None:
    html = page(
        "<h2>localStorage</h2><table><thead><tr><th>Tool<th>Parameters<tbody>"
        "<tr><td><code>browser_localstorage_set</code><td><code>key</code> (string), <code>value</code> (string)"
        "<tr><td><code>browser_localstorage_clear</code><td>(none)</table>"
    )

    assert parse_page(html) == {
        "browser_localstorage_set": {"key": DocumentedParam(required=None), "value": DocumentedParam(required=None)},
        "browser_localstorage_clear": {},
    }


def test_a_field_key_table_documents_the_items_of_the_param_before_it() -> None:
    html = page(
        "<h2>browser_fill_form</h2>"
        + params_table(("fields", "yes", "object[]"))
        + "<p>Each field is an object:</p><table><thead><tr><th>Field key<th>Type<th>Required<th>Description<tbody>"
        "<tr><td><code>name</code><td>string<td>yes<td>Name<tr><td><code>value</code><td>string<td>no<td>Value</table>"
    )

    assert parse_page(html) == {
        "browser_fill_form": {"fields": DocumentedParam(required=True, fields={"name": True, "value": False})}
    }


def test_a_table_under_another_heading_belongs_to_the_first_tool_its_section_names() -> None:
    html = page(
        "<h2>Searching a snapshot</h2><p><code>browser_find</code> searches what <code>browser_snapshot</code> returns."
        "</p>" + params_table(("text", "no"))
    )

    assert parse_page(html) == {"browser_find": {"text": DocumentedParam(required=False)}}


def test_a_table_in_a_section_that_names_no_tool_is_ignored() -> None:
    html = page(
        "<h2>browser_click</h2>" + params_table(("target", "yes")) + "<h2>Workflow</h2>" + params_table(("x", "no"))
    )

    assert parse_page(html) == {"browser_click": {"target": DocumentedParam(required=True)}}


def test_an_overview_table_names_tools_without_params() -> None:
    html = page(
        "<h2>Core</h2><table><thead><tr><th>Tool<th>Description<tbody>"
        "<tr><td><code>browser_close</code><td>Close the page"
        "<tr><td><code>browser_cookie_list/get</code><td>Cookies</table>"
    )

    assert parse_page(html) == {"browser_close": {}}


def test_flags_are_read_from_code_and_table_cells() -> None:
    html = page(
        "<table><thead><tr><th>Option<th>Description<tbody>"
        "<tr><td><code>--device &lt;device&gt;</code><td>Device</table>"
        '<pre><code>"@playwright/mcp@latest", "--headless"</code></pre><p>not a flag: --prose</p>'
    )

    assert parse_flags(html) == frozenset({"--device", "--headless"})


def test_pages_merge_and_a_page_that_states_required_wins_over_one_that_does_not() -> None:
    merged = merge_pages(
        [
            {"browser_close": {}, "browser_tabs": {"action": DocumentedParam(required=None)}},
            {"browser_tabs": {"action": DocumentedParam(required=True), "index": DocumentedParam(required=False)}},
        ]
    )

    assert merged == {
        "browser_close": {},
        "browser_tabs": {"action": DocumentedParam(required=True), "index": DocumentedParam(required=False)},
    }


def test_pages_that_contradict_each_other_fail() -> None:
    with pytest.raises(DocsError, match="browser_tabs.action"):
        merge_pages(
            [
                {"browser_tabs": {"action": DocumentedParam(required=True)}},
                {"browser_tabs": {"action": DocumentedParam(required=False)}},
            ]
        )


def test_the_sources_are_the_playwright_mcp_docs_pages() -> None:
    assert len(DOC_PAGES) == len(set(DOC_PAGES)) == 32
    assert {"introduction", "snapshots", "tools/navigation", "configuration/options"} <= set(DOC_PAGES)


def test_field_keys_belong_to_the_object_list_param_even_when_it_is_not_the_last_row() -> None:
    html = page(
        "<h2>browser_fill_form</h2>" + params_table(("fields", "yes", "object[]"), ("timeout", "no")) + FIELD_KEYS
    )

    assert parse_page(html)["browser_fill_form"] == {
        "fields": DocumentedParam(required=True, fields={"name": True, "value": False}),
        "timeout": DocumentedParam(required=False),
    }


def test_field_keys_without_an_object_list_param_are_ignored() -> None:
    html = page("<h2>browser_type</h2>" + params_table(("text", "yes")) + FIELD_KEYS)

    assert parse_page(html) == {"browser_type": {"text": DocumentedParam(required=True)}}


def test_a_tool_page_that_documents_no_tool_fails_instead_of_shrinking_the_catalog() -> None:
    pages = {name: page("<h2>browser_close</h2>") for name in DOC_PAGES}
    pages["tools/tabs"] = "<html><body>Service unavailable</body></html>"

    with pytest.raises(DocsError, match="tools/tabs"):
        read_documentation(pages.__getitem__)


def test_documentation_reads_every_page_and_merges_tools_and_flags() -> None:
    pages = {name: page("<h2>browser_close</h2>" if name.startswith("tools/") else "") for name in DOC_PAGES}
    pages["tools/navigation"] = page("<h2>browser_navigate</h2>" + params_table(("url", "yes")))
    pages["configuration/options"] = page("<pre><code>--headless</code></pre>")
    read: list[str] = []

    def fetch(name: str) -> str:
        read.append(name)
        return pages[name]

    documentation = read_documentation(fetch)

    assert read == list(DOC_PAGES)
    assert documentation.tools == {"browser_close": {}, "browser_navigate": {"url": DocumentedParam(required=True)}}
    assert documentation.flags == frozenset({"--headless"})


def test_a_page_that_cannot_be_fetched_fails_with_its_url(monkeypatch: pytest.MonkeyPatch) -> None:
    def unreachable(*_: object, **__: object) -> None:
        raise URLError("offline")

    monkeypatch.setattr(docs, "urlopen", unreachable)

    with pytest.raises(DocsError, match="https://playwright.dev/mcp/snapshots"):
        docs.fetch_page("snapshots")
