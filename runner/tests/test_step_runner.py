import asyncio
from typing import Any

import pytest
from fastmcp import Client

from argos_runner import step_runner
from argos_runner.scenario.model import Action, Step
from argos_runner.step_runner import run_steps
from tests.conftest import FakeDevtoolsServer, page

pytestmark = pytest.mark.integration

NAVIGATE_ACTION = Action(action="navigate_page", params={"type": "url", "url": "https://example.com"})
NAVIGATE = Step(scenario=[NAVIGATE_ACTION])


def _step(action: str, params: dict[str, Any]) -> Step:
    return Step(scenario=[Action(action=action, params=params)])


def _click_action(selector: str | list[str] = "a") -> Action:
    return Action(action="click", params={"uid": {"selector": selector}})


def _click(selector: str | list[str] = "a") -> Step:
    return Step(scenario=[_click_action(selector)])


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


def _args(server: FakeDevtoolsServer, tool: str) -> dict[str, Any]:
    return [args for name, args in server.calls if name == tool][-1]


def test_all_steps_succeed(server: FakeDevtoolsServer) -> None:
    result = _run(server, [NAVIGATE, _click()])

    assert result == {"status": "success", "steps": 2}
    assert server.called_tools == ["list_pages", "navigate_page", "take_snapshot", "evaluate_script", "click"]


def test_actions_of_a_step_run_in_order_on_one_page(server: FakeDevtoolsServer) -> None:
    step = Step(scenario=[NAVIGATE_ACTION, _click_action("a"), _click_action("b")])

    result = _run(server, [step])

    assert result == {"status": "success", "steps": 1}
    actions = [name for name in server.called_tools if name in ("navigate_page", "click")]
    assert actions == ["navigate_page", "click", "click"]


def test_failed_action_names_its_step_and_number(server: FakeDevtoolsServer) -> None:
    server.missing = {"b"}

    result = _run(server, [NAVIGATE, Step(scenario=[_click_action("a"), _click_action("b"), NAVIGATE_ACTION])])

    assert (result["step"], result["action_number"], result["params"]) == (2, 2, {"uid": {"selector": "b"}})
    assert server.called_tools.count("navigate_page") == 1


def test_hooks_wrap_all_actions_of_a_step(server: FakeDevtoolsServer) -> None:
    hooks = RecordingHooks(server)

    _run(server, [Step(scenario=[NAVIGATE_ACTION, NAVIGATE_ACTION])], hooks)

    assert hooks.seen == [
        ("before", 1, ["list_pages"]),
        ("after", 1, ["list_pages", "navigate_page", "navigate_page"]),
    ]


def test_step_runs_on_the_selected_page(server: FakeDevtoolsServer) -> None:
    server.pages = [page(3, selected=False), page(7, selected=True)]

    _run(server, [NAVIGATE])

    assert _args(server, "navigate_page")["pageId"] == 7


def test_step_runs_on_the_first_page_when_none_is_selected(server: FakeDevtoolsServer) -> None:
    server.pages = [page(3, selected=False), page(7, selected=False)]

    _run(server, [NAVIGATE])

    assert _args(server, "navigate_page")["pageId"] == 3


def test_page_named_by_the_step_wins(server: FakeDevtoolsServer) -> None:
    server.pages = [page(1), page(2, selected=False)]

    _run(server, [_step("navigate_page", {**NAVIGATE_ACTION.params, "pageId": 2})])

    assert _args(server, "navigate_page")["pageId"] == 2


def test_tool_without_page_gets_no_page(server: FakeDevtoolsServer) -> None:
    result = _run(server, [_step("list_extensions", {})])

    assert result["status"] == "success"
    assert _args(server, "list_extensions") == {}


def test_params_pass_through_to_the_tool(server: FakeDevtoolsServer) -> None:
    _run(server, [_step("wait_for", {"text": ["Ara"], "timeout": 5000})])

    assert _args(server, "wait_for") == {"pageId": 1, "text": ["Ara"], "timeout": 5000}


def test_later_steps_follow_the_page_a_step_selects(server: FakeDevtoolsServer) -> None:
    steps = [_step("new_page", {"url": "https://b.com"}), NAVIGATE, _step("select_page", {"pageId": 1}), _click()]

    _run(server, steps)

    assert _args(server, "navigate_page")["pageId"] == 2
    assert _args(server, "click")["pageId"] == 1


def test_selector_becomes_the_uid_of_the_matching_element(server: FakeDevtoolsServer) -> None:
    _run(server, [_click("button.buy")])

    assert _args(server, "click") == {"pageId": 1, "uid": "1_0"}
    assert _args(server, "evaluate_script")["args"] == ["1_0", "1_1", "1_2"]
    assert '["button.buy"]' in _args(server, "evaluate_script")["function"]


def test_drag_selectors_become_from_and_to_uids(server: FakeDevtoolsServer) -> None:
    _run(server, [_step("drag", {"from_uid": {"selector": "#card"}, "to_uid": {"selector": "#bin"}})])

    assert _args(server, "drag") == {"pageId": 1, "from_uid": "1_0", "to_uid": "1_1"}


def test_form_element_selectors_become_uids(server: FakeDevtoolsServer) -> None:
    elements = [{"uid": {"selector": "#name"}, "value": "Ada"}, {"uid": {"selector": "#mail"}, "value": "a@b.c"}]

    _run(server, [_step("fill_form", {"elements": elements})])

    assert _args(server, "fill_form")["elements"] == [{"uid": "1_0", "value": "Ada"}, {"uid": "1_1", "value": "a@b.c"}]


def test_script_arg_selectors_become_uids(server: FakeDevtoolsServer) -> None:
    function = "(el) => el.id"

    args = [{"selector": "#buy"}, {"selector": "#share"}]

    _run(server, [_step("evaluate_script", {"function": function, "args": args})])

    assert _args(server, "evaluate_script") == {
        "pageId": 1,
        "function": function,
        "waitForStableDom": True,
        "args": ["1_0", "1_1"],
    }


def test_custom_scroll_runs_as_a_script_on_the_element(server: FakeDevtoolsServer) -> None:
    result = _run(server, [_step("custom_scroll", {"uid": {"selector": "#featured"}})])

    assert result["status"] == "success"
    assert _args(server, "evaluate_script") == {
        "pageId": 1,
        "function": "(el) => { el.scrollIntoView(); return true; }",
        "waitForStableDom": True,
        "args": ["1_0"],
    }


def test_custom_scroll_fallback_is_reported_under_its_own_param(server: FakeDevtoolsServer) -> None:
    server.missing = {"#featured"}

    result = _run(server, [_step("custom_scroll", {"uid": {"selector": ["#featured", "text=Share"]}})])

    assert _args(server, "evaluate_script")["args"] == ["1_2"]
    assert result["selector_fallbacks"] == [
        {"step": 1, "action_number": 1, "param": "uid", "used": "text=Share", "skipped": ["#featured"]}
    ]


def test_failed_custom_tool_is_reported_as_written(server: FakeDevtoolsServer) -> None:
    server.missing = {"#featured"}

    result = _run(server, [_step("custom_scroll", {"uid": {"selector": "#featured"}})])

    assert (result["status"], result["action"], result["params"]) == (
        "fail",
        "custom_scroll",
        {"uid": {"selector": "#featured"}},
    )


def test_step_without_selectors_takes_no_snapshot(server: FakeDevtoolsServer) -> None:
    _run(server, [NAVIGATE])

    assert "take_snapshot" not in server.called_tools


def test_unmatched_selector_fails_the_step_without_calling_the_tool(server: FakeDevtoolsServer) -> None:
    server.missing = {"h1"}
    server.pages = [page(1, "https://a.com/job", "Access denied")]

    result = _run(server, [_click("h1"), NAVIGATE])

    assert result == {
        "status": "fail",
        "step": 1,
        "action_number": 1,
        "action": "click",
        "params": {"uid": {"selector": "h1"}},
        "response": {"status": "fail", "data": {"selector": "no element in the page snapshot matches h1"}},
        "pages": [{"url": "https://a.com/job", "title": "Access denied"}],
    }
    assert "click" not in server.called_tools
    assert "navigate_page" not in server.called_tools


def test_first_matching_candidate_is_used_without_a_fallback_record(server: FakeDevtoolsServer) -> None:
    result = _run(server, [_click(["#buy", "text=Buy"])])

    assert _args(server, "click") == {"pageId": 1, "uid": "1_0"}
    assert "selector_fallbacks" not in result


def test_later_candidate_stands_in_for_an_unmatched_one_and_is_reported(server: FakeDevtoolsServer) -> None:
    server.missing = {"#buy"}

    result = _run(server, [NAVIGATE, _click(["#buy", ".buy"])])

    assert _args(server, "click") == {"pageId": 1, "uid": "1_1"}
    assert result["selector_fallbacks"] == [
        {"step": 2, "action_number": 1, "param": "uid", "used": ".buy", "skipped": ["#buy"]}
    ]


def test_text_candidate_matches_the_accessible_name_in_the_snapshot(server: FakeDevtoolsServer) -> None:
    server.missing = {"#share"}

    result = _run(server, [_click(["#share", "text=Share"])])

    assert _args(server, "click") == {"pageId": 1, "uid": "1_2"}
    assert result["selector_fallbacks"][0]["used"] == "text=Share"


def test_text_only_selector_needs_no_script(server: FakeDevtoolsServer) -> None:
    _run(server, [_click("text=Buy")])

    assert _args(server, "click") == {"pageId": 1, "uid": "1_1"}
    assert "evaluate_script" not in server.called_tools


def test_no_matching_candidate_fails_naming_every_candidate(server: FakeDevtoolsServer) -> None:
    server.missing = {"#buy"}

    result = _run(server, [_click(["#buy", "text=Nope"])])

    assert result["response"]["data"] == {"selector": "no element in the page snapshot matches #buy, text=Nope"}
    assert "click" not in server.called_tools


def test_drag_and_form_candidates_are_reported_by_param(server: FakeDevtoolsServer) -> None:
    server.missing = {"#gone"}
    drag = _step("drag", {"from_uid": {"selector": ["#gone", "#card"]}, "to_uid": {"selector": "#bin"}})
    form = _step("fill_form", {"elements": [{"uid": {"selector": ["#gone", "text=Buy"]}, "value": "Ada"}]})

    result = _run(server, [drag, form])

    assert _args(server, "drag") == {"pageId": 1, "from_uid": "1_1", "to_uid": "1_2"}
    assert _args(server, "fill_form")["elements"] == [{"uid": "1_1", "value": "Ada"}]
    assert [(entry["step"], entry["param"]) for entry in result["selector_fallbacks"]] == [
        (1, "from_uid"),
        (2, "elements[0].uid"),
    ]


def test_failed_run_keeps_the_fallbacks_used_before_it(server: FakeDevtoolsServer) -> None:
    server.missing = {"#buy", "h1"}

    result = _run(server, [_click(["#buy", ".buy"]), _click("h1")])

    assert result["status"] == "fail"
    assert result["selector_fallbacks"][0]["used"] == ".buy"


def test_snapshot_error_fails_the_step(server: FakeDevtoolsServer) -> None:
    server.errors = {"take_snapshot": "page closed"}

    result = _run(server, [_click()])

    assert result["response"]["status"] == "error"
    assert "page closed" in result["response"]["message"]


def test_invalid_selector_error_is_reported(server: FakeDevtoolsServer) -> None:
    server.errors = {"evaluate_script": "'h1[' is not a valid selector"}

    result = _run(server, [_click("h1[")])

    assert "not a valid selector" in result["response"]["message"]


def test_tool_error_is_reported_as_failed_step(server: FakeDevtoolsServer) -> None:
    server.errors = {"navigate_page": "net::ERR_NAME_NOT_RESOLVED"}

    result = _run(server, [NAVIGATE])

    assert result["status"] == "fail"
    assert result["response"]["status"] == "error"
    assert "ERR_NAME_NOT_RESOLVED" in result["response"]["message"]


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
    server.missing = {"a"}
    hooks = RecordingHooks(server)

    result = _run(server, [_click()], hooks)

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

    monkeypatch.setattr(step_runner, "ACTION_DELAY_RANGE_SECONDS", (1.0, 5.0))
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


def test_random_delay_runs_between_actions_of_a_step(
    server: FakeDevtoolsServer, recorded_delays: list[float]
) -> None:
    _run(server, [Step(scenario=[NAVIGATE_ACTION, NAVIGATE_ACTION, NAVIGATE_ACTION])])

    assert len(recorded_delays) == 2


def test_single_step_has_no_delay(server: FakeDevtoolsServer, recorded_delays: list[float]) -> None:
    _run(server, [NAVIGATE])

    assert recorded_delays == []


def test_no_delay_after_failed_step(server: FakeDevtoolsServer, recorded_delays: list[float]) -> None:
    server.missing = {"a"}

    _run(server, [_click(), NAVIGATE])

    assert recorded_delays == []


def test_open_pages_lists_url_and_title(server: FakeDevtoolsServer) -> None:
    server.pages = [page(1, "https://a.com", "A"), page(2, "https://b.com", "B")]

    async def go() -> dict[str, Any]:
        async with Client(server.mcp) as client:
            return await step_runner.open_pages(client)

    assert asyncio.run(go()) == {
        "pages": [{"url": "https://a.com", "title": "A"}, {"url": "https://b.com", "title": "B"}]
    }


def test_connection_failure_is_reported() -> None:
    class BrokenClient:
        async def call_tool(self, *args: Any, **kwargs: Any) -> None:
            raise ConnectionError("connection lost")

    result = asyncio.run(run_steps(BrokenClient(), [NAVIGATE]))

    assert result == {"status": "error", "message": "cannot open the browser: connection lost"}
