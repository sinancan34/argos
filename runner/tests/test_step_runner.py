import asyncio
from typing import Any

import pytest
from fastmcp import Client

import step_runner
from scenario import ACTION_PARAMS, Step
from step_runner import run_steps
from tests.conftest import FakeDevtoolsServer, page

pytestmark = pytest.mark.integration

NAVIGATE = Step(action="navigate", params={"url": "https://example.com"})


def _wait(selector: str = "h1", **extra: Any) -> Step:
    return Step(action="wait_for", params={"selector": selector, "timeout": 0.01, **extra})


def _click(selector: str = "a", **extra: Any) -> Step:
    return Step(action="click_element", params={"selector": selector, "timeout": 0.01, **extra})


class RecordingHooks:
    """Records each hook call with the tools called so far; returns `problem` from the named hook."""

    def __init__(self, server: FakeDevtoolsServer, problem: tuple[str, int, str] | None = None) -> None:
        self._server = server
        self._problem = problem
        self.seen: list[tuple[str, int, list[str]]] = []

    async def _record(self, hook: str, number: int) -> str | None:
        self.seen.append((hook, number, list(self._server.called_tools)))
        if self._problem and self._problem[:2] == (hook, number):
            return self._problem[2]
        return None

    async def before_step(self, number: int, step: Step) -> str | None:
        return await self._record("before", number)

    async def after_step(self, number: int, step: Step) -> str | None:
        return await self._record("after", number)


def _run(server: FakeDevtoolsServer, steps: list[Step], hooks: RecordingHooks | None = None) -> dict[str, Any]:
    async def go() -> dict[str, Any]:
        async with Client(server.mcp) as client:
            return await run_steps(client, steps, hooks)

    return asyncio.run(go())


def _page_ids(server: FakeDevtoolsServer, tool: str) -> list[int]:
    return [args["pageId"] for name, args in server.calls if name == tool]


def test_every_scenario_action_has_a_runner() -> None:
    assert set(step_runner.ACTIONS) == set(ACTION_PARAMS)


def test_all_steps_succeed(server: FakeDevtoolsServer) -> None:
    result = _run(server, [NAVIGATE, _wait(), _click()])

    assert result == {"status": "success", "steps": 3}
    assert server.called_tools == ["list_pages", "navigate_page", *["evaluate_script"] * 3]


def test_navigate_opens_the_url_on_the_first_page(server: FakeDevtoolsServer) -> None:
    server.pages = [page(7)]

    _run(server, [NAVIGATE])

    assert server.calls[-1] == ("navigate_page", {"pageId": 7, "url": "https://example.com", "type": "url"})


def test_wait_for_checks_until_element_appears(server: FakeDevtoolsServer) -> None:
    server.absent_checks = 2

    result = _run(server, [Step(action="wait_for", params={"selector": "h1", "timeout": 5})])

    assert result["status"] == "success"
    assert server.called_tools.count("evaluate_script") == 3


def test_wait_for_does_not_wait_for_a_stable_dom(server: FakeDevtoolsServer) -> None:
    _run(server, [_wait()])

    assert server.calls[-1][1]["waitForStableDom"] is False


def test_missing_element_fails_step_and_reports_open_tabs(server: FakeDevtoolsServer) -> None:
    server.missing = {"h1"}
    server.pages = [page(1, "https://a.com/job", "Access denied")]

    result = _run(server, [_wait(), NAVIGATE])

    assert result == {
        "status": "fail",
        "step": 1,
        "action": "wait_for",
        "params": {"selector": "h1", "timeout": 0.01},
        "response": {"status": "fail", "data": {"selector": "no element matched within 0.01s"}},
        "tabs": [{"url": "https://a.com/job", "title": "Access denied"}],
    }
    assert "navigate_page" not in server.called_tools


def test_page_error_is_reported_instead_of_timeout(server: FakeDevtoolsServer) -> None:
    server.errors = {"evaluate_script": "'h1[' is not a valid selector"}

    result = _run(server, [_wait()])

    assert result["response"]["status"] == "error"
    assert "not a valid selector" in result["response"]["message"]


def test_click_calls_element_click_and_waits_for_a_stable_dom(server: FakeDevtoolsServer) -> None:
    _run(server, [_click("button")])

    args = server.calls[-1][1]
    assert ".click()" in args["function"]
    assert args["waitForStableDom"] is True


def test_click_on_missing_element_does_not_click(server: FakeDevtoolsServer) -> None:
    server.missing = {"a"}

    result = _run(server, [_click()])

    assert result["response"]["data"] == {"selector": "no element matched within 0.01s"}
    assert all(".click()" not in args.get("function", "") for _, args in server.calls)


def test_click_fails_when_element_disappears_before_the_click(server: FakeDevtoolsServer) -> None:
    server.vanishing = {"a"}

    result = _run(server, [_click()])

    assert result["response"] == {"status": "fail", "data": {"selector": "element disappeared before the click"}}


def test_navigation_error_is_reported_as_failed_step(server: FakeDevtoolsServer) -> None:
    server.errors = {"navigate_page": "net::ERR_NAME_NOT_RESOLVED"}

    result = _run(server, [NAVIGATE])

    assert result["status"] == "fail"
    assert result["response"]["status"] == "error"
    assert "ERR_NAME_NOT_RESOLVED" in result["response"]["message"]


def test_new_tab_placeholder_uses_page_opened_by_last_click(server: FakeDevtoolsServer) -> None:
    server.opened_by_click = [[page(2)]]

    result = _run(server, [_click(), _wait(target_id="$new_tab")])

    assert result == {"status": "success", "steps": 2}
    assert _page_ids(server, "evaluate_script")[-1] == 2


def test_click_without_new_tab_keeps_previous_new_tab(server: FakeDevtoolsServer) -> None:
    server.opened_by_click = [[page(2)], []]

    _run(server, [_click(), _click("b"), _wait(target_id="$new_tab")])

    assert _page_ids(server, "evaluate_script")[-1] == 2


def test_later_new_tab_replaces_earlier_one(server: FakeDevtoolsServer) -> None:
    server.opened_by_click = [[page(2)], [page(3)]]

    _run(server, [_click(), _click("b"), _wait(target_id="$new_tab")])

    assert _page_ids(server, "evaluate_script")[-1] == 3


def test_new_tab_placeholder_without_new_tab_fails_without_calling_tool(server: FakeDevtoolsServer) -> None:
    params = {"url": "https://a.com", "target_id": "$new_tab"}

    result = _run(server, [Step(action="navigate", params=params)])

    assert result["status"] == "fail"
    assert result["step"] == 1
    assert result["params"] == params
    assert result["response"]["status"] == "fail"
    assert "target_id" in result["response"]["data"]
    assert server.called_tools == ["list_pages", "list_pages"]


def test_browser_that_cannot_open_returns_error(server: FakeDevtoolsServer) -> None:
    server.errors = {"list_pages": "Could not find Google Chrome"}

    result = _run(server, [NAVIGATE])

    assert result["status"] == "error"
    assert "Could not find Google Chrome" in result["message"]
    assert server.called_tools == ["list_pages"]


def test_hooks_run_around_every_step(server: FakeDevtoolsServer) -> None:
    hooks = RecordingHooks(server)

    result = _run(server, [NAVIGATE, NAVIGATE], hooks)

    assert result == {"status": "success", "steps": 2}
    assert hooks.seen == [
        ("before", 1, ["list_pages"]),
        ("after", 1, ["list_pages", "navigate_page"]),
        ("before", 2, ["list_pages", "navigate_page"]),
        ("after", 2, ["list_pages", "navigate_page", "navigate_page"]),
    ]


def test_after_step_does_not_run_after_failed_step(server: FakeDevtoolsServer) -> None:
    server.missing = {"h1"}
    hooks = RecordingHooks(server)

    result = _run(server, [_wait()], hooks)

    assert result["status"] == "fail"
    assert [hook for hook, _, _ in hooks.seen] == ["before"]


def test_problem_before_a_step_ends_the_run_without_running_it(server: FakeDevtoolsServer) -> None:
    hooks = RecordingHooks(server, ("before", 1, "cannot list requests"))

    result = _run(server, [NAVIGATE], hooks)

    assert result == {"status": "error", "message": "cannot list requests"}
    assert "navigate_page" not in server.called_tools


def test_problem_after_a_step_ends_the_run(server: FakeDevtoolsServer) -> None:
    hooks = RecordingHooks(server, ("after", 1, "cannot list pages"))

    result = _run(server, [NAVIGATE, NAVIGATE], hooks)

    assert result == {"status": "error", "message": "cannot list pages"}
    assert server.called_tools.count("navigate_page") == 1


@pytest.fixture
def recorded_delays(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    delays: list[float] = []

    async def record(seconds: float) -> None:
        delays.append(seconds)

    monkeypatch.setattr(step_runner, "STEP_DELAY_RANGE_SECONDS", (1.0, 5.0))
    monkeypatch.setattr(step_runner, "_sleep", record)
    return delays


def test_random_delay_runs_between_steps(server: FakeDevtoolsServer, recorded_delays: list[float]) -> None:
    _run(server, [NAVIGATE, NAVIGATE, NAVIGATE])

    assert len(recorded_delays) == 2
    assert all(1.0 <= delay <= 5.0 for delay in recorded_delays)


def test_delay_runs_before_the_next_step_opens(
    server: FakeDevtoolsServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    order: list[str] = []
    hooks = RecordingHooks(server)

    async def record(seconds: float) -> None:
        order.append("sleep")

    async def before_step(number: int, step: Step) -> None:
        order.append(f"before {number}")

    monkeypatch.setattr(step_runner, "_sleep", record)
    monkeypatch.setattr(hooks, "before_step", before_step)

    _run(server, [NAVIGATE, NAVIGATE], hooks)

    assert order == ["before 1", "sleep", "before 2"]


def test_single_step_has_no_delay(server: FakeDevtoolsServer, recorded_delays: list[float]) -> None:
    _run(server, [NAVIGATE])

    assert recorded_delays == []


def test_no_delay_after_failed_step(server: FakeDevtoolsServer, recorded_delays: list[float]) -> None:
    server.missing = {"h1"}

    _run(server, [_wait(), NAVIGATE])

    assert recorded_delays == []


def test_open_tabs_lists_url_and_title(server: FakeDevtoolsServer) -> None:
    server.pages = [page(1, "https://a.com", "A"), page(2, "https://b.com", "B")]

    async def go() -> dict[str, Any]:
        async with Client(server.mcp) as client:
            return await step_runner.open_tabs(client)

    assert asyncio.run(go()) == {
        "tabs": [{"url": "https://a.com", "title": "A"}, {"url": "https://b.com", "title": "B"}]
    }


def test_connection_failure_is_reported() -> None:
    class BrokenClient:
        async def call_tool(self, *args: Any, **kwargs: Any) -> None:
            raise ConnectionError("connection lost")

    result = asyncio.run(run_steps(BrokenClient(), [NAVIGATE]))

    assert result == {"status": "error", "message": "cannot open the browser: connection lost"}
