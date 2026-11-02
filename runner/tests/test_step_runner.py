import asyncio
from typing import Any

import pytest
from fastmcp import Client

import step_runner
from scenario import Step
from step_runner import run_steps
from tests.conftest import FakeNodriverServer

pytestmark = pytest.mark.integration


def _run(server: FakeNodriverServer, steps: list[Step]) -> dict[str, Any]:
    async def go() -> dict[str, Any]:
        async with Client(server.mcp) as client:
            return await run_steps(client, steps)

    return asyncio.run(go())


def test_all_steps_succeed(server: FakeNodriverServer) -> None:
    result = _run(
        server,
        [
            Step(action="start_browser", params={}),
            Step(action="navigate", params={"url": "https://example.com"}),
            Step(action="stop_browser", params={}),
        ],
    )

    assert result == {"status": "success", "steps": 3}
    assert server.called_tools == ["start_browser", "navigate", "stop_browser"]


def test_failing_step_returns_mcp_response_and_stops_browser(server: FakeNodriverServer) -> None:
    server.wait_for_response = {"status": "fail", "data": {"selector": "time ran out"}}

    result = _run(
        server,
        [
            Step(action="start_browser", params={}),
            Step(action="wait_for", params={"selector": "h1"}),
            Step(action="navigate", params={"url": "https://never.example"}),
        ],
    )

    assert result == {
        "status": "fail",
        "step": 2,
        "action": "wait_for",
        "params": {"selector": "h1"},
        "response": {"status": "fail", "data": {"selector": "time ran out"}},
    }
    assert server.called_tools == ["start_browser", "wait_for", "list_tabs", "stop_browser"]


def test_new_tab_placeholder_uses_target_opened_by_last_click(server: FakeNodriverServer) -> None:
    server.new_targets = [[{"targetId": "TAB-2"}]]

    result = _run(
        server,
        [
            Step(action="click_element", params={"selector": "a"}),
            Step(action="wait_for", params={"selector": "h1", "target_id": "$new_tab"}),
        ],
    )

    assert result == {"status": "success", "steps": 2}
    assert server.calls[-1] == ("wait_for", {"selector": "h1", "target_id": "TAB-2"})


def test_click_without_new_tab_keeps_previous_new_tab(server: FakeNodriverServer) -> None:
    server.new_targets = [[{"targetId": "TAB-2"}], []]

    result = _run(
        server,
        [
            Step(action="click_element", params={"selector": "a"}),
            Step(action="click_element", params={"selector": "b"}),
            Step(action="wait_for", params={"selector": "h1", "target_id": "$new_tab"}),
        ],
    )

    assert result == {"status": "success", "steps": 3}
    assert server.calls[-1] == ("wait_for", {"selector": "h1", "target_id": "TAB-2"})


def test_later_new_tab_replaces_earlier_one(server: FakeNodriverServer) -> None:
    server.new_targets = [[{"targetId": "TAB-2"}], [{"targetId": "TAB-3"}]]

    _run(
        server,
        [
            Step(action="click_element", params={"selector": "a"}),
            Step(action="click_element", params={"selector": "b"}),
            Step(action="wait_for", params={"selector": "h1", "target_id": "$new_tab"}),
        ],
    )

    assert server.calls[-1] == ("wait_for", {"selector": "h1", "target_id": "TAB-3"})


def test_new_tab_placeholder_without_new_tab_fails_without_calling_tool(
    server: FakeNodriverServer,
) -> None:
    params = {"selector": "h1", "target_id": "$new_tab"}

    result = _run(server, [Step(action="wait_for", params=params)])

    assert result["status"] == "fail"
    assert result["step"] == 1
    assert result["params"] == params
    assert result["response"]["status"] == "fail"
    assert "target_id" in result["response"]["data"]
    assert server.called_tools == ["list_tabs", "stop_browser"]


def test_unknown_action_is_reported_as_failed_step(server: FakeNodriverServer) -> None:
    result = _run(server, [Step(action="hover", params={})])

    assert result["status"] == "fail"
    assert result["action"] == "hover"
    assert result["response"]["status"] == "error"
    assert "hover" in result["response"]["message"]


def test_invalid_params_are_reported_as_failed_step(server: FakeNodriverServer) -> None:
    result = _run(server, [Step(action="navigate", params={"wrong": 1})])

    assert result["status"] == "fail"
    assert result["response"]["status"] == "error"


def test_cleanup_error_is_reported(server: FakeNodriverServer) -> None:
    server.wait_for_response = {"status": "fail", "data": {"selector": "time ran out"}}
    server.stop_response = {"status": "error", "message": "could not stop"}

    result = _run(server, [Step(action="wait_for", params={"selector": "h1"})])

    assert result["cleanup"] == {"status": "error", "message": "could not stop"}


def test_cleanup_fail_when_browser_not_running_is_not_reported(server: FakeNodriverServer) -> None:
    server.wait_for_response = {"status": "fail", "data": {"browser": "not running"}}
    server.stop_response = {"status": "fail", "data": {"browser": "not running"}}

    result = _run(server, [Step(action="wait_for", params={"selector": "h1"})])

    assert "cleanup" not in result


def test_failure_reports_open_tabs_before_browser_closes(server: FakeNodriverServer) -> None:
    server.wait_for_response = {"status": "fail", "data": {"selector": "time ran out"}}
    server.tabs_response = {
        "status": "success",
        "data": {
            "tabs": [
                {"targetId": "TAB-1", "url": "https://a.com/list", "title": "List"},
                {"targetId": "TAB-2", "url": "https://a.com/job", "title": "Access denied"},
            ]
        },
    }

    result = _run(server, [Step(action="wait_for", params={"selector": "h1"})])

    assert result["tabs"] == [
        {"url": "https://a.com/list", "title": "List"},
        {"url": "https://a.com/job", "title": "Access denied"},
    ]
    assert server.called_tools.index("list_tabs") < server.called_tools.index("stop_browser")


def test_failure_omits_tabs_when_browser_is_not_running(server: FakeNodriverServer) -> None:
    server.wait_for_response = {"status": "fail", "data": {"browser": "not running"}}
    server.tabs_response = {"status": "fail", "data": {"browser": "not running"}}

    result = _run(server, [Step(action="wait_for", params={"selector": "h1"})])

    assert "tabs" not in result


def _run_with_hook(server: FakeNodriverServer, steps: list[Step]) -> tuple[dict[str, Any], list[list[str]]]:
    seen: list[list[str]] = []

    async def before_stop() -> None:
        seen.append(list(server.called_tools))

    async def go() -> dict[str, Any]:
        async with Client(server.mcp) as client:
            return await run_steps(client, steps, before_stop)

    return asyncio.run(go()), seen


def test_before_stop_runs_right_before_stop_browser(server: FakeNodriverServer) -> None:
    result, seen = _run_with_hook(
        server,
        [
            Step(action="start_browser", params={}),
            Step(action="stop_browser", params={}),
        ],
    )

    assert result == {"status": "success", "steps": 2}
    assert seen == [["start_browser"]]
    assert server.called_tools == ["start_browser", "stop_browser"]


def test_before_stop_runs_after_last_step_when_scenario_has_no_stop(
    server: FakeNodriverServer,
) -> None:
    _, seen = _run_with_hook(server, [Step(action="start_browser", params={})])

    assert seen == [["start_browser"]]


def test_before_stop_does_not_run_after_failed_step(server: FakeNodriverServer) -> None:
    server.wait_for_response = {"status": "fail", "data": {"selector": "time ran out"}}

    result, seen = _run_with_hook(server, [Step(action="wait_for", params={"selector": "h1"})])

    assert result["status"] == "fail"
    assert seen == []


@pytest.fixture
def recorded_delays(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    delays: list[float] = []

    async def record(seconds: float) -> None:
        delays.append(seconds)

    monkeypatch.setattr(step_runner, "STEP_DELAY_RANGE_SECONDS", (1.0, 5.0))
    monkeypatch.setattr(step_runner, "_sleep", record)
    return delays


def test_random_delay_runs_between_steps(
    server: FakeNodriverServer, recorded_delays: list[float]
) -> None:
    _run(
        server,
        [
            Step(action="start_browser", params={}),
            Step(action="navigate", params={"url": "https://example.com"}),
            Step(action="stop_browser", params={}),
        ],
    )

    assert len(recorded_delays) == 2
    assert all(1.0 <= delay <= 5.0 for delay in recorded_delays)


def test_single_step_has_no_delay(server: FakeNodriverServer, recorded_delays: list[float]) -> None:
    _run(server, [Step(action="start_browser", params={})])

    assert recorded_delays == []


def test_no_delay_after_failed_step(server: FakeNodriverServer, recorded_delays: list[float]) -> None:
    server.wait_for_response = {"status": "fail", "data": {"selector": "time ran out"}}

    _run(
        server,
        [
            Step(action="wait_for", params={"selector": "h1"}),
            Step(action="navigate", params={"url": "https://never.example"}),
        ],
    )

    assert recorded_delays == []


def test_delay_runs_before_before_stop(server: FakeNodriverServer, recorded_delays: list[float]) -> None:
    delays_seen: list[int] = []

    async def before_stop() -> None:
        delays_seen.append(len(recorded_delays))

    async def go() -> None:
        async with Client(server.mcp) as client:
            steps = [Step(action="start_browser", params={}), Step(action="stop_browser", params={})]
            await run_steps(client, steps, before_stop)

    asyncio.run(go())

    assert delays_seen == [1]


def test_connection_failure_during_step_is_reported() -> None:
    class BrokenClient:
        async def call_tool(self, *args: Any, **kwargs: Any) -> None:
            raise ConnectionError("connection lost")

    result = asyncio.run(run_steps(BrokenClient(), [Step(action="navigate", params={})]))

    assert result["status"] == "fail"
    assert result["response"] == {"status": "error", "message": "connection lost"}
    assert result["cleanup"] == {"status": "error", "message": "connection lost"}
