import asyncio
from typing import Any, Awaitable, Callable

import pytest
from fastmcp import Client

from argos_runner import step_runner
from argos_runner.scenario.model import Action, Step
from argos_runner.step_runner import run_steps
from tests.conftest import FIRST_VISIBLE, FakePlaywrightServer, tab

pytestmark = pytest.mark.integration

NAVIGATE_ACTION = Action(action="browser_navigate", params={"url": "https://example.com"})
NAVIGATE = Step(scenario=[NAVIGATE_ACTION])


def _step(action: str, params: dict[str, Any]) -> Step:
    return Step(scenario=[Action(action=action, params=params)])


def _click_action(selector: str | list[str] = "a") -> Action:
    return Action(action="browser_click", params={"target": {"selector": selector}})


def _click(selector: str | list[str] = "a") -> Step:
    return Step(scenario=[_click_action(selector)])


class RecordingHooks:
    """Records each hook call with the tools called so far; returns `problem` from the named hook."""

    def __init__(self, server: FakePlaywrightServer, problem: tuple[str, int, str] | None = None) -> None:
        self._server = server
        self._problem = problem
        self.seen: list[tuple[str, int, list[str]]] = []
        self.actions: list[str] = []

    async def _record(self, hook: str, number: int) -> str | None:
        self.seen.append((hook, number, list(self._server.called_tools)))
        if self._problem and self._problem[:2] == (hook, number):
            return self._problem[2]
        return None

    async def before_step(self, number: int, step: Step) -> str | None:
        return await self._record("before", number)

    async def after_step(self, number: int, step: Step) -> str | None:
        return await self._record("after", number)

    async def around_action(self, action: Action, run: Callable[[], Awaitable[dict[str, Any]]]) -> dict[str, Any]:
        self.actions.append(action.action)
        return await run()


def _run(server: FakePlaywrightServer, steps: list[Step], hooks: RecordingHooks | None = None) -> dict[str, Any]:
    async def go() -> dict[str, Any]:
        async with Client(server.mcp) as client:
            return await run_steps(client, steps, hooks)

    return asyncio.run(go())


def _args(server: FakePlaywrightServer, tool: str) -> dict[str, Any]:
    return [args for name, args in server.calls if name == tool][-1]


def test_all_steps_succeed(server: FakePlaywrightServer) -> None:
    result = _run(server, [NAVIGATE, _click()])

    assert result == {"status": "success", "steps": 2}
    assert server.called_tools == ["browser_tabs", "browser_navigate", "browser_evaluate", "browser_click"]


def test_actions_of_a_step_run_in_order(server: FakePlaywrightServer) -> None:
    step = Step(scenario=[NAVIGATE_ACTION, _click_action("a"), _click_action("b")])

    result = _run(server, [step])

    assert result == {"status": "success", "steps": 1}
    actions = [name for name in server.called_tools if name in ("browser_navigate", "browser_click")]
    assert actions == ["browser_navigate", "browser_click", "browser_click"]


def test_failed_action_names_its_step_and_number(server: FakePlaywrightServer) -> None:
    server.missing = {"b"}

    result = _run(server, [NAVIGATE, Step(scenario=[_click_action("a"), _click_action("b"), NAVIGATE_ACTION])])

    assert (result["step"], result["action_number"], result["params"]) == (2, 2, {"target": {"selector": "b"}})
    assert server.called_tools.count("browser_navigate") == 1


def test_hooks_wrap_all_actions_of_a_step(server: FakePlaywrightServer) -> None:
    hooks = RecordingHooks(server)

    _run(server, [Step(scenario=[NAVIGATE_ACTION, NAVIGATE_ACTION])], hooks)

    assert hooks.seen == [
        ("before", 1, ["browser_tabs"]),
        ("after", 1, ["browser_tabs", "browser_navigate", "browser_navigate"]),
    ]


def test_every_action_runs_through_the_hooks(server: FakePlaywrightServer) -> None:
    hooks = RecordingHooks(server)

    _run(server, [Step(scenario=[NAVIGATE_ACTION, _click_action()]), NAVIGATE], hooks)

    assert hooks.actions == ["browser_navigate", "browser_click", "browser_navigate"]


def test_actions_run_on_the_current_tab_without_a_tab_param(server: FakePlaywrightServer) -> None:
    _run(server, [NAVIGATE])

    assert _args(server, "browser_navigate") == {"url": "https://example.com"}


def test_params_pass_through_to_the_tool(server: FakePlaywrightServer) -> None:
    _run(server, [_step("browser_wait_for", {"text": "Ara", "time": 2})])

    assert _args(server, "browser_wait_for") == {"text": "Ara", "time": 2}


def test_mouse_wheel_scrolls_with_its_own_params(server: FakePlaywrightServer) -> None:
    result = _run(server, [_step("browser_mouse_wheel", {"deltaX": 0, "deltaY": 500})])

    assert result == {"status": "success", "steps": 1}
    assert _args(server, "browser_mouse_wheel") == {"deltaX": 0, "deltaY": 500}


def test_later_steps_run_on_the_tab_a_step_selects(server: FakePlaywrightServer) -> None:
    steps = [_step("browser_tabs", {"action": "new", "url": "https://b.com"}), NAVIGATE]

    _run(server, steps)

    assert [entry["url"] for entry in server.tabs] == ["about:blank", "https://example.com"]


def test_css_selector_becomes_its_first_visible_element(server: FakePlaywrightServer) -> None:
    _run(server, [_click("button.buy")])

    assert _args(server, "browser_click") == {"target": f"button.buy{FIRST_VISIBLE}"}
    assert '["button.buy"]' in _args(server, "browser_evaluate")["function"]


def test_drag_selectors_become_start_and_end_targets(server: FakePlaywrightServer) -> None:
    _run(server, [_step("browser_drag", {"startTarget": {"selector": "#card"}, "endTarget": {"selector": "#bin"}})])

    assert _args(server, "browser_drag") == {"startTarget": f"#card{FIRST_VISIBLE}", "endTarget": f"#bin{FIRST_VISIBLE}"}


def test_form_field_selectors_become_targets(server: FakePlaywrightServer) -> None:
    fields = [
        {"target": {"selector": "#name"}, "name": "Name", "type": "textbox", "value": "Ada"},
        {"target": {"selector": "text=Buy"}, "name": "Buy", "type": "checkbox", "value": "true"},
    ]

    _run(server, [_step("browser_fill_form", {"fields": fields})])

    assert [field["target"] for field in _args(server, "browser_fill_form")["fields"]] == [f"#name{FIRST_VISIBLE}", "e2"]
    assert _args(server, "browser_fill_form")["fields"][0]["value"] == "Ada"


def test_script_target_selector_becomes_its_element(server: FakePlaywrightServer) -> None:
    function = "(el) => el.id"

    _run(server, [_step("browser_evaluate", {"function": function, "target": {"selector": "#buy"}})])

    assert _args(server, "browser_evaluate") == {"function": function, "target": f"#buy{FIRST_VISIBLE}"}


def test_step_without_selectors_reads_neither_snapshot_nor_page(server: FakePlaywrightServer) -> None:
    _run(server, [NAVIGATE])

    assert "browser_snapshot" not in server.called_tools
    assert "browser_evaluate" not in server.called_tools


def test_unmatched_selector_fails_the_step_without_calling_the_tool(server: FakePlaywrightServer) -> None:
    server.missing = {"h1"}
    server.tabs = [tab("https://a.com/job", "Access denied")]

    result = _run(server, [_click("h1"), NAVIGATE])

    assert result == {
        "status": "fail",
        "step": 1,
        "action_number": 1,
        "action": "browser_click",
        "params": {"target": {"selector": "h1"}},
        "response": {"status": "fail", "data": {"selector": "no element on the page matches h1"}},
        "pages": [{"url": "https://a.com/job", "title": "Access denied"}],
    }
    assert "browser_click" not in server.called_tools
    assert "browser_navigate" not in server.called_tools


def test_first_matching_candidate_is_used_without_a_fallback_record(server: FakePlaywrightServer) -> None:
    result = _run(server, [_click(["#buy", "text=Buy"])])

    assert _args(server, "browser_click") == {"target": f"#buy{FIRST_VISIBLE}"}
    assert "selector_fallbacks" not in result


def test_later_candidate_stands_in_for_an_unmatched_one_and_is_reported(server: FakePlaywrightServer) -> None:
    server.missing = {"#buy"}

    result = _run(server, [NAVIGATE, _click(["#buy", ".buy"])])

    assert _args(server, "browser_click") == {"target": f".buy{FIRST_VISIBLE}"}
    assert result["selector_fallbacks"] == [
        {"step": 2, "action_number": 1, "param": "target", "used": ".buy", "skipped": ["#buy"]}
    ]


def test_text_candidate_matches_the_accessible_name_in_the_snapshot(server: FakePlaywrightServer) -> None:
    server.missing = {"#share"}

    result = _run(server, [_click(["#share", "text=Share"])])

    assert _args(server, "browser_click") == {"target": "e3"}
    assert result["selector_fallbacks"][0]["used"] == "text=Share"


def test_text_only_selector_needs_no_script(server: FakePlaywrightServer) -> None:
    _run(server, [_click("text=Buy")])

    assert _args(server, "browser_click") == {"target": "e2"}
    assert "browser_evaluate" not in server.called_tools


def test_css_only_selector_needs_no_snapshot(server: FakePlaywrightServer) -> None:
    _run(server, [_click("#buy")])

    assert "browser_snapshot" not in server.called_tools


def test_no_matching_candidate_fails_naming_every_candidate(server: FakePlaywrightServer) -> None:
    server.missing = {"#buy"}

    result = _run(server, [_click(["#buy", "text=Nope"])])

    assert result["response"]["data"] == {"selector": "no element on the page matches #buy, text=Nope"}
    assert "browser_click" not in server.called_tools


def test_drag_and_form_candidates_are_reported_by_param(server: FakePlaywrightServer) -> None:
    server.missing = {"#gone"}
    drag = _step(
        "browser_drag", {"startTarget": {"selector": ["#gone", "#card"]}, "endTarget": {"selector": "#bin"}}
    )
    form = _step(
        "browser_fill_form",
        {"fields": [{"target": {"selector": ["#gone", "text=Buy"]}, "name": "N", "type": "textbox", "value": "A"}]},
    )

    result = _run(server, [drag, form])

    assert _args(server, "browser_drag") == {"startTarget": f"#card{FIRST_VISIBLE}", "endTarget": f"#bin{FIRST_VISIBLE}"}
    assert _args(server, "browser_fill_form")["fields"][0]["target"] == "e2"
    assert [(entry["step"], entry["param"]) for entry in result["selector_fallbacks"]] == [
        (1, "startTarget"),
        (2, "fields[0].target"),
    ]


def test_failed_run_keeps_the_fallbacks_used_before_it(server: FakePlaywrightServer) -> None:
    server.missing = {"#buy", "h1"}

    result = _run(server, [_click(["#buy", ".buy"]), _click("h1")])

    assert result["status"] == "fail"
    assert result["selector_fallbacks"][0]["used"] == ".buy"


def test_snapshot_error_fails_the_step(server: FakePlaywrightServer) -> None:
    server.errors = {"browser_snapshot": "page closed"}

    result = _run(server, [_click("text=Buy")])

    assert result["response"]["status"] == "error"
    assert "page closed" in result["response"]["message"]


def test_invalid_selector_error_is_reported(server: FakePlaywrightServer) -> None:
    server.errors = {"browser_evaluate": "SyntaxError: 'h1[' is not a valid selector."}

    result = _run(server, [_click("h1[")])

    assert "not a valid selector" in result["response"]["message"]


def test_tool_error_is_reported_as_failed_step(server: FakePlaywrightServer) -> None:
    server.errors = {"browser_navigate": "net::ERR_NAME_NOT_RESOLVED"}

    result = _run(server, [NAVIGATE])

    assert result["status"] == "fail"
    assert result["response"] == {"status": "error", "message": "net::ERR_NAME_NOT_RESOLVED"}


def test_browser_that_cannot_open_returns_error(server: FakePlaywrightServer) -> None:
    server.errors = {"browser_tabs": "Could not find Google Chrome"}

    result = _run(server, [NAVIGATE])

    assert result["status"] == "error"
    assert "Could not find Google Chrome" in result["message"]
    assert server.called_tools == ["browser_tabs"]


def test_hooks_run_around_every_step(server: FakePlaywrightServer) -> None:
    hooks = RecordingHooks(server)

    result = _run(server, [NAVIGATE, NAVIGATE], hooks)

    assert result == {"status": "success", "steps": 2}
    assert hooks.seen == [
        ("before", 1, ["browser_tabs"]),
        ("after", 1, ["browser_tabs", "browser_navigate"]),
        ("before", 2, ["browser_tabs", "browser_navigate"]),
        ("after", 2, ["browser_tabs", "browser_navigate", "browser_navigate"]),
    ]


def test_after_step_does_not_run_after_failed_step(server: FakePlaywrightServer) -> None:
    server.missing = {"a"}
    hooks = RecordingHooks(server)

    result = _run(server, [_click()], hooks)

    assert result["status"] == "fail"
    assert [hook for hook, _, _ in hooks.seen] == ["before"]


def test_problem_before_a_step_ends_the_run_without_running_it(server: FakePlaywrightServer) -> None:
    hooks = RecordingHooks(server, ("before", 1, "cannot list requests"))

    result = _run(server, [NAVIGATE], hooks)

    assert result == {"status": "error", "message": "cannot list requests"}
    assert "browser_navigate" not in server.called_tools


def test_problem_after_a_step_ends_the_run(server: FakePlaywrightServer) -> None:
    hooks = RecordingHooks(server, ("after", 1, "cannot list pages"))

    result = _run(server, [NAVIGATE, NAVIGATE], hooks)

    assert result == {"status": "error", "message": "cannot list pages"}
    assert server.called_tools.count("browser_navigate") == 1


@pytest.fixture
def recorded_delays(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    delays: list[float] = []

    async def record(seconds: float) -> None:
        delays.append(seconds)

    monkeypatch.setattr(step_runner, "ACTION_DELAY_RANGE_SECONDS", (1.0, 5.0))
    monkeypatch.setattr(step_runner, "_sleep", record)
    return delays


def test_random_delay_runs_between_steps(server: FakePlaywrightServer, recorded_delays: list[float]) -> None:
    _run(server, [NAVIGATE, NAVIGATE, NAVIGATE])

    assert len(recorded_delays) == 2
    assert all(1.0 <= delay <= 5.0 for delay in recorded_delays)


def test_delay_runs_before_the_next_step_opens(
    server: FakePlaywrightServer, monkeypatch: pytest.MonkeyPatch
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
    server: FakePlaywrightServer, recorded_delays: list[float]
) -> None:
    _run(server, [Step(scenario=[NAVIGATE_ACTION, NAVIGATE_ACTION, NAVIGATE_ACTION])])

    assert len(recorded_delays) == 2


def test_single_step_has_no_delay(server: FakePlaywrightServer, recorded_delays: list[float]) -> None:
    _run(server, [NAVIGATE])

    assert recorded_delays == []


def test_no_delay_after_failed_step(server: FakePlaywrightServer, recorded_delays: list[float]) -> None:
    server.missing = {"a"}

    _run(server, [_click(), NAVIGATE])

    assert recorded_delays == []


def test_open_pages_lists_url_and_title_of_every_tab(server: FakePlaywrightServer) -> None:
    server.tabs = [tab("https://a.com", "A"), tab("https://b.com", "B")]

    async def go() -> dict[str, Any]:
        async with Client(server.mcp) as client:
            return await step_runner.open_pages(client)

    assert asyncio.run(go()) == {
        "pages": [{"url": "https://a.com", "title": "A"}, {"url": "https://b.com", "title": "B"}]
    }


def test_open_pages_is_empty_when_tabs_cannot_be_listed(server: FakePlaywrightServer) -> None:
    server.errors = {"browser_tabs": "browser closed"}

    async def go() -> dict[str, Any]:
        async with Client(server.mcp) as client:
            return await step_runner.open_pages(client)

    assert asyncio.run(go()) == {}


def test_connection_failure_is_reported() -> None:
    class BrokenClient:
        async def call_tool(self, *args: Any, **kwargs: Any) -> None:
            raise ConnectionError("connection lost")

    result = asyncio.run(run_steps(BrokenClient(), [NAVIGATE]))

    assert result == {"status": "error", "message": "cannot open the browser: connection lost"}
