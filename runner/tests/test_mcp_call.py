import asyncio
from typing import Any

import pytest
from fastmcp import Client, FastMCP
from fastmcp.exceptions import ToolError

from argos_runner.criteria.network_capture import parse_requests
from argos_runner.devtools.element_targets import snapshot_refs
from argos_runner.devtools.mcp_call import call_tool, evaluate, sections
from argos_runner.devtools.tabs import Tab, parse_tabs
from tests.conftest import RECORDED

pytestmark = pytest.mark.unit

PAGE = "http://127.0.0.1:8000/"


def _replay(key: str) -> FastMCP:
    """A server whose tool answers as Playwright MCP answered the recorded call `key`."""
    recorded = RECORDED[key]
    mcp = FastMCP("replay")

    @mcp.tool(name=recorded["tool"])
    def answer(function: str = "") -> str:
        if recorded["is_error"]:
            raise ToolError(recorded["text"])
        return recorded["text"]

    return mcp


def _call(key: str) -> dict[str, Any]:
    async def go() -> dict[str, Any]:
        async with Client(_replay(key)) as client:
            return await call_tool(client, RECORDED[key]["tool"], {})

    return asyncio.run(go())


def _evaluate(key: str) -> dict[str, Any]:
    async def go() -> dict[str, Any]:
        async with Client(_replay(key)) as client:
            return await evaluate(client, "() => 1")

    return asyncio.run(go())


def test_sections_are_keyed_by_heading() -> None:
    parts = sections(RECORDED["click"]["text"])

    assert list(parts) == ["Open tabs", "Page", "Snapshot"]
    assert parts["Page"] == f'- Page URL: {PAGE}\n- Page Title: Fixture "page"'


def test_success_carries_the_sections() -> None:
    response = _call("tabs_list_with_popup")

    assert response["status"] == "success"
    assert response["data"]["Result"].startswith("- 0: (current) [")


def test_empty_success_has_no_sections() -> None:
    assert _call("mouse_wheel") == {"status": "success", "data": {}}


@pytest.mark.parametrize(
    ("key", "expected"),
    [
        ("click_strict_mode_error", "strict mode violation: locator('button.dup') resolved to 2 elements"),
        ("invalid_params", 'Invalid arguments for tool "browser_click"'),
        ("request_body_out_of_range", "Request #999 not found"),
    ],
)
def test_error_carries_the_error_section(key: str, expected: str) -> None:
    response = _call(key)

    assert response["status"] == "error"
    assert expected in response["message"]
    assert not response["message"].startswith("###")


def test_connection_failure_is_an_error() -> None:
    class BrokenClient:
        async def call_tool(self, *args: Any, **kwargs: Any) -> None:
            raise ConnectionError("connection lost")

    assert asyncio.run(call_tool(BrokenClient(), "browser_tabs", {})) == {"status": "error", "message": "connection lost"}


@pytest.mark.parametrize(
    ("key", "result"),
    [
        ("evaluate_object", {"a": [1, "İ"], "b": None}),
        ("evaluate_string", "x\n### y"),
        ("evaluate_target", "H2"),
    ],
)
def test_script_result_is_the_printed_json(key: str, result: Any) -> None:
    assert _evaluate(key)["data"]["result"] == result


def test_script_without_a_json_result_is_an_error() -> None:
    assert _evaluate("evaluate_undefined") == {"status": "error", "message": "unreadable script result: undefined"}


@pytest.mark.parametrize("key", ["evaluate_throws", "evaluate_bad_selector"])
def test_failed_script_is_an_error(key: str) -> None:
    assert _evaluate(key)["status"] == "error"


def test_evaluate_sends_the_target_only_when_given() -> None:
    calls: list[dict[str, Any]] = []
    mcp = FastMCP("record")

    @mcp.tool
    def browser_evaluate(function: str, target: str | None = None) -> str:
        calls.append({"function": function, "target": target})
        return "### Result\n1"

    async def go() -> None:
        async with Client(mcp) as client:
            await evaluate(client, "() => 1")
            await evaluate(client, "(el) => 1", target="e2")

    asyncio.run(go())
    assert calls == [{"function": "() => 1", "target": None}, {"function": "(el) => 1", "target": "e2"}]


def test_tabs_are_read_with_the_current_one_marked() -> None:
    assert parse_tabs(sections(RECORDED["tabs_list_with_popup"]["text"])["Result"]) == [
        Tab(index=0, url=PAGE, title='Fixture "page"', current=True),
        Tab(index=1, url=f"{PAGE}popup", title='Fixture "page"', current=False),
    ]


def test_blank_tab_at_start_is_read() -> None:
    assert parse_tabs(sections(RECORDED["tabs_list_at_start"]["text"])["Result"]) == [
        Tab(index=0, url="about:blank", title="", current=True)
    ]


def test_requests_are_read_with_number_method_and_url() -> None:
    assert parse_requests(sections(RECORDED["network_requests"]["text"])["Result"]) == [
        (1, "GET", PAGE),
        (2, "POST", f"{PAGE}collect?v=2&en=page_view"),
        (3, "POST", f"{PAGE}collect?v=2&en=empty"),
        (4, "GET", f"{PAGE}pixel.gif?id=GTM-X"),
    ]


def test_failed_and_pending_requests_are_read() -> None:
    listed = "1. [POST] https://a.com/g/collect?en=a => [FAILED] net::ERR_ABORTED\n2. [POST] https://a.com/g/collect?en=b"

    assert [number for number, _, _ in parse_requests(listed)] == [1, 2]


def test_snapshot_names_map_to_refs_with_escapes_and_turkish() -> None:
    refs = snapshot_refs(sections(RECORDED["snapshot"]["text"])["Snapshot"])

    assert refs["Öne Çıkan İlanlar"] == "e2"
    assert refs['Say "hi"'] == "e3"
    assert refs["open popup"] == "e4"


def test_first_node_with_a_name_wins() -> None:
    assert snapshot_refs(sections(RECORDED["snapshot"]["text"])["Snapshot"])["Dup"] == "e5"
