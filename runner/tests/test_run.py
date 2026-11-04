import asyncio
import json
import tempfile
from functools import partial
from pathlib import Path
from typing import Any

import pytest

from argos_runner import run
from argos_runner.criteria.waiter import wait_until_satisfied
from tests.conftest import FakePlaywrightServer, request_entry, tab

pytestmark = pytest.mark.integration

URL = "https://example.com"
OTHER_URL = "https://example.com/other"
NAVIGATE = {"scenario": [{"action": "browser_navigate", "params": {"url": URL}}]}
NAVIGATE_OTHER = {"scenario": [{"action": "browser_navigate", "params": {"url": OTHER_URL}}]}
CLICK = {"scenario": [{"action": "browser_click", "params": {"target": {"selector": "a"}}}]}
GA4_CRITERION = {
    "provider": {"name": "ga4", "params": []},
    "conditions": [{"key": "en", "match": "exact", "value": "page_view"}],
}
GTM_CRITERION = {
    "provider": {"name": "gtm", "params": []},
    "conditions": [{"key": "id", "match": "exact", "value": "GTM-1"}],
}
GA4_HIT = "https://analytics.google.com/g/collect?en=page_view"


def _with_criteria(step: dict[str, Any], *criteria: dict[str, Any]) -> dict[str, Any]:
    return {**step, "success_criteria": list(criteria)}


def _scenario(tmp_path: Path, steps: list[dict[str, Any]]) -> Path:
    path = tmp_path / "scenario.json"
    path.write_text(json.dumps(steps), encoding="utf-8")
    return path


def _sends_ga4_hit(server: FakePlaywrightServer, trigger: str, tab_index: int = 0) -> None:
    server.sent_on = {**server.sent_on, trigger: {tab_index: [request_entry(GA4_HIT)]}}


def _execute(tmp_path: Path, server: FakePlaywrightServer, steps: list[dict[str, Any]]) -> dict[str, Any]:
    return asyncio.run(run.execute(_scenario(tmp_path, steps), server.mcp))


def test_server_runs_with_a_fresh_profile_and_no_generated_code() -> None:
    assert "--isolated" in run.SERVER_ARGS
    codegen = run.SERVER_ARGS.index("--codegen")
    assert run.SERVER_ARGS[codegen + 1] == "none"


def test_server_offers_every_capability() -> None:
    assert "--caps=network,storage,testing,vision,pdf,devtools,config" in run.SERVER_ARGS


def test_server_bounds_the_files_it_names_itself() -> None:
    assert f"--output-max-size={run.OUTPUT_MAX_BYTES}" in run.SERVER_ARGS


def test_server_keeps_its_files_in_the_temp_dir() -> None:
    transport = run.server_transport()

    assert transport.cwd == tempfile.gettempdir()
    assert transport.args == run.SERVER_ARGS


def test_scenario_without_criteria_does_not_read_requests(tmp_path: Path, server: FakePlaywrightServer) -> None:
    result = _execute(tmp_path, server, [NAVIGATE])

    assert result == {"status": "success", "steps": 1}
    assert "browser_network_requests" not in server.called_tools


def test_criterion_passes_with_a_request_its_step_sent(tmp_path: Path, server: FakePlaywrightServer) -> None:
    _sends_ga4_hit(server, URL)

    result = _execute(tmp_path, server, [_with_criteria(NAVIGATE, GA4_CRITERION)])

    assert result["status"] == "success"
    assert result["steps"] == 1
    assert result["recorded_requests"] == 1
    assert result["step_success_criteria"] == [
        {
            "step": 1,
            "status": "pass",
            "success_criteria": [
                {
                    "criterion": 1,
                    "status": "pass",
                    "provider": {"name": "ga4", "params": []},
                    "conditions": [{"key": "en", "match": "exact", "value": "page_view"}],
                    "matched_events": 1,
                    "url": GA4_HIT,
                }
            ],
        }
    ]


def test_criterion_after_several_actions_sees_requests_of_every_action(
    tmp_path: Path, server: FakePlaywrightServer
) -> None:
    _sends_ga4_hit(server, URL)
    actions = [*NAVIGATE["scenario"], *CLICK["scenario"], *CLICK["scenario"], *NAVIGATE_OTHER["scenario"]]

    result = _execute(tmp_path, server, [{"scenario": actions, "success_criteria": [GA4_CRITERION]}])

    assert result["status"] == "success"
    assert result["steps"] == 1
    assert result["step_success_criteria"][0]["success_criteria"][0]["matched_events"] == 1


def test_request_sent_by_an_earlier_step_does_not_count(tmp_path: Path, server: FakePlaywrightServer) -> None:
    _sends_ga4_hit(server, URL)

    result = _execute(tmp_path, server, [NAVIGATE, _with_criteria(NAVIGATE_OTHER, GA4_CRITERION)])

    assert result["status"] == "fail"
    assert result["step_success_criteria"][0]["step"] == 2
    assert result["step_success_criteria"][0]["success_criteria"][0]["requests"] == 0


def test_request_sent_after_the_window_closes_does_not_count(tmp_path: Path, server: FakePlaywrightServer) -> None:
    _sends_ga4_hit(server, OTHER_URL)

    result = _execute(tmp_path, server, [_with_criteria(NAVIGATE, GA4_CRITERION), NAVIGATE_OTHER])

    assert result["status"] == "fail"
    assert result["step_success_criteria"][0]["status"] == "fail"


def test_each_step_counts_only_its_own_requests(tmp_path: Path, server: FakePlaywrightServer) -> None:
    _sends_ga4_hit(server, URL)
    _sends_ga4_hit(server, OTHER_URL)
    steps = [_with_criteria(NAVIGATE, GA4_CRITERION), _with_criteria(NAVIGATE_OTHER, GA4_CRITERION)]

    result = _execute(tmp_path, server, steps)

    assert result["status"] == "success"
    assert [entry["success_criteria"][0]["matched_events"] for entry in result["step_success_criteria"]] == [1, 1]


def test_request_from_another_open_page_counts(tmp_path: Path, server: FakePlaywrightServer) -> None:
    server.tabs = [tab(), tab()]
    _sends_ga4_hit(server, "a", tab_index=1)

    result = _execute(tmp_path, server, [NAVIGATE, _with_criteria(CLICK, GA4_CRITERION)])

    assert result["status"] == "success"
    assert result["step_success_criteria"][0]["step"] == 2


def test_failed_criterion_does_not_stop_later_steps(tmp_path: Path, server: FakePlaywrightServer) -> None:
    _sends_ga4_hit(server, OTHER_URL)
    steps = [_with_criteria(NAVIGATE, GTM_CRITERION), _with_criteria(NAVIGATE_OTHER, GA4_CRITERION)]

    result = _execute(tmp_path, server, steps)

    assert result["status"] == "fail"
    assert result["steps"] == 2
    assert [entry["status"] for entry in result["step_success_criteria"]] == ["fail", "pass"]


def test_one_failed_criterion_fails_its_step_but_others_are_reported(
    tmp_path: Path, server: FakePlaywrightServer
) -> None:
    _sends_ga4_hit(server, URL)

    result = _execute(tmp_path, server, [_with_criteria(NAVIGATE, GA4_CRITERION, GTM_CRITERION)])

    entry = result["step_success_criteria"][0]
    assert entry["status"] == "fail"
    assert [criterion["status"] for criterion in entry["success_criteria"]] == ["pass", "fail"]


def test_failed_step_criteria_report_open_pages_and_page_requests(tmp_path: Path, server: FakePlaywrightServer) -> None:
    server.tabs = [tab(URL, "Access denied")]
    server.page_resources = {0: [GA4_HIT]}

    result = _execute(tmp_path, server, [_with_criteria(NAVIGATE, GA4_CRITERION)])

    entry = result["step_success_criteria"][0]
    assert entry["pages"] == [{"url": URL, "title": "Access denied"}]
    assert entry["success_criteria"][0]["requests"] == 0
    assert entry["success_criteria"][0]["page_requests"] == 1


def test_passed_step_criteria_do_not_read_the_page(tmp_path: Path, server: FakePlaywrightServer) -> None:
    _sends_ga4_hit(server, URL)

    result = _execute(tmp_path, server, [_with_criteria(NAVIGATE, GA4_CRITERION)])

    assert "pages" not in result["step_success_criteria"][0]
    assert "page_requests" not in result["step_success_criteria"][0]["success_criteria"][0]
    assert "browser_evaluate" not in server.called_tools


def test_failed_step_stops_the_run_and_keeps_earlier_criteria(tmp_path: Path, server: FakePlaywrightServer) -> None:
    _sends_ga4_hit(server, URL)
    server.missing = {"a"}
    steps = [_with_criteria(NAVIGATE, GA4_CRITERION), _with_criteria(CLICK, GA4_CRITERION), NAVIGATE_OTHER]

    result = _execute(tmp_path, server, steps)

    assert result["status"] == "fail"
    assert result["step"] == 2
    assert [entry["step"] for entry in result["step_success_criteria"]] == [1]
    assert OTHER_URL not in [args.get("url") for _, args in server.calls]


def test_capture_failure_returns_error(tmp_path: Path, server: FakePlaywrightServer) -> None:
    server.errors = {"browser_network_requests": "No page found"}

    result = _execute(tmp_path, server, [_with_criteria(NAVIGATE, GA4_CRITERION)])

    assert result["status"] == "error"
    assert "No page found" in result["message"]
    assert "browser_navigate" not in server.called_tools


def test_capture_failure_while_waiting_returns_error_and_earlier_criteria(
    tmp_path: Path, server: FakePlaywrightServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    def send_then_close_browser(trigger: str) -> None:
        if trigger == URL:
            server.network = {0: [request_entry(GA4_HIT)]}
        else:
            server.errors = {"browser_network_requests": "browser closed"}

    monkeypatch.setattr(server, "_send", send_then_close_browser)
    steps = [_with_criteria(NAVIGATE, GA4_CRITERION), _with_criteria(NAVIGATE_OTHER, GA4_CRITERION), NAVIGATE]

    result = _execute(tmp_path, server, steps)

    assert result["status"] == "error"
    assert "browser closed" in result["message"]
    assert [entry["status"] for entry in result["step_success_criteria"]] == ["pass"]
    assert server.called_tools.count("browser_navigate") == 2


def test_request_read_on_a_later_poll_of_the_window_counts(
    tmp_path: Path, server: FakePlaywrightServer, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("argos_runner.criteria.step_criteria.CRITERIA_WAIT_SECONDS", 5)
    monkeypatch.setattr(
        "argos_runner.criteria.step_criteria.wait_until_satisfied", partial(wait_until_satisfied, poll_seconds=0)
    )
    record = server._record

    def send_on_third_read(name: str, args: dict[str, Any]) -> None:
        record(name, args)
        if server.called_tools.count("browser_network_requests") == 3:
            server.network = {0: [request_entry(GA4_HIT)]}

    monkeypatch.setattr(server, "_record", send_on_third_read)

    result = _execute(tmp_path, server, [_with_criteria(NAVIGATE, GA4_CRITERION)])

    assert result["status"] == "success"
    assert server.called_tools.count("browser_network_requests") == 3


def test_capture_warnings_are_reported(tmp_path: Path, server: FakePlaywrightServer) -> None:
    server.sent_on = {URL: {0: [request_entry(GA4_HIT, "POST", "en=page_view")]}}
    server.errors = {"browser_network_request": "Request #1 not found."}

    result = _execute(tmp_path, server, [_with_criteria(NAVIGATE, GA4_CRITERION)])

    assert len(result["warnings"]) == 1


def test_invalid_scenario_is_rejected_before_browser_starts(tmp_path: Path, server: FakePlaywrightServer) -> None:
    result = _execute(tmp_path, server, [{"scenario": [{"action": "start_browser", "params": {}}]}])

    assert result["status"] == "error"
    assert "unknown action 'start_browser'" in result["message"]
    assert server.calls == []


def test_invalid_criterion_is_rejected_before_browser_starts(tmp_path: Path, server: FakePlaywrightServer) -> None:
    unknown = {"provider": {"name": "tiktok", "params": []}, "conditions": []}

    result = _execute(tmp_path, server, [_with_criteria(NAVIGATE, unknown)])

    assert result["status"] == "error"
    assert "step 1 success criterion 1 uses unknown provider" in result["message"]
    assert server.calls == []


@pytest.fixture
def fake_server_main(monkeypatch: pytest.MonkeyPatch, server: FakePlaywrightServer) -> FakePlaywrightServer:
    original_execute = run.execute

    async def fake_execute(scenario: Path, transport: object) -> dict:
        return await original_execute(scenario, server.mcp)

    monkeypatch.setattr(run, "execute", fake_execute)
    return server


def test_main_exit_code_follows_result_status(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], fake_server_main: FakePlaywrightServer
) -> None:
    exit_code = run.main([str(_scenario(tmp_path, [NAVIGATE]))])

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out) == {"status": "success", "steps": 1}


def test_main_exit_code_is_1_when_a_criterion_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], fake_server_main: FakePlaywrightServer
) -> None:
    exit_code = run.main([str(_scenario(tmp_path, [_with_criteria(NAVIGATE, GTM_CRITERION)]))])

    assert exit_code == 1
    assert json.loads(capsys.readouterr().out)["step_success_criteria"][0]["status"] == "fail"


def test_main_exit_code_is_1_when_step_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], fake_server_main: FakePlaywrightServer
) -> None:
    fake_server_main.missing = {"a"}
    steps = [CLICK]

    exit_code = run.main([str(_scenario(tmp_path, steps))])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert output["status"] == "fail"
    assert output["step"] == 1


def test_main_no_longer_takes_a_criterion_file(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        run.main([str(_scenario(tmp_path, [NAVIGATE])), "--criterion", "criterion.json"])


def test_main_prints_error_and_exits_1_for_missing_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = run.main([str(tmp_path / "missing.json")])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert output["status"] == "error"
    assert "cannot read" in output["message"]


def test_main_prints_error_and_exits_1_when_server_cannot_start(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(run, "SERVER_COMMAND", str(tmp_path / "no-such-npx"))

    exit_code = run.main([str(_scenario(tmp_path, [NAVIGATE]))])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert output["status"] == "error"
    assert output["message"]
