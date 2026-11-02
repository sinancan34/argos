import asyncio
import json
import socket
from pathlib import Path

import pytest

import run
from tests.conftest import FakeNodriverServer, request_entry

pytestmark = pytest.mark.integration


def _scenario(tmp_path: Path, steps: list[dict]) -> Path:
    path = tmp_path / "scenario.json"
    path.write_text(json.dumps(steps), encoding="utf-8")
    return path


def _unused_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_execute_runs_scenario_file(tmp_path: Path, server: FakeNodriverServer) -> None:
    path = _scenario(tmp_path, [{"action": "start_browser", "params": {}}])

    result = asyncio.run(run.execute(path, server.mcp))

    assert result == {"status": "success", "steps": 1}


GA4_GOAL = {
    "provider": {"name": "ga4", "params": []},
    "conditions": [{"key": "en", "match": "exact", "value": "page_view"}],
}
META_GOAL = {
    "provider": {"name": "meta", "params": []},
    "conditions": [{"key": "ev", "match": "exact", "value": "Share"}],
}
START_AND_STOP = [
    {"action": "start_browser", "params": {}},
    {"action": "stop_browser", "params": {}},
]


def _goal_file(tmp_path: Path, goals: list[dict]) -> Path:
    path = tmp_path / "goal.json"
    path.write_text(json.dumps(goals), encoding="utf-8")
    return path


def _with_ga4_hit(server: FakeNodriverServer) -> None:
    url = "https://analytics.google.com/g/collect?en=page_view"
    server.network = {"TAB-1": [request_entry("1", url)]}


def test_goals_are_evaluated_from_requests_read_before_stop(
    tmp_path: Path, server: FakeNodriverServer
) -> None:
    _with_ga4_hit(server)

    result = asyncio.run(
        run.execute(_scenario(tmp_path, START_AND_STOP), server.mcp, _goal_file(tmp_path, [GA4_GOAL]))
    )

    assert result["status"] == "success"
    assert result["steps"] == 2
    assert result["goals"][0]["status"] == "pass"
    assert server.called_tools[-1] == "stop_browser"


def test_one_failed_goal_fails_the_run_but_others_are_reported(
    tmp_path: Path, server: FakeNodriverServer
) -> None:
    _with_ga4_hit(server)
    goal_path = _goal_file(tmp_path, [GA4_GOAL, META_GOAL])

    result = asyncio.run(run.execute(_scenario(tmp_path, START_AND_STOP), server.mcp, goal_path))

    assert result["status"] == "fail"
    assert [goal["status"] for goal in result["goals"]] == ["pass", "fail"]


def test_goals_are_not_evaluated_when_a_step_fails(
    tmp_path: Path, server: FakeNodriverServer
) -> None:
    _with_ga4_hit(server)
    server.wait_for_response = {"status": "fail", "data": {"selector": "time ran out"}}
    steps = [{"action": "wait_for", "params": {"selector": "h1", "timeout": 1}}]

    result = asyncio.run(
        run.execute(_scenario(tmp_path, steps), server.mcp, _goal_file(tmp_path, [GA4_GOAL]))
    )

    assert result["status"] == "fail"
    assert result["step"] == 1
    assert "goals" not in result
    assert "list_network_requests" not in server.called_tools


def test_invalid_goal_file_is_rejected_before_browser_starts(
    tmp_path: Path, server: FakeNodriverServer
) -> None:
    goal_path = tmp_path / "goal.json"
    goal_path.write_text("not json", encoding="utf-8")

    result = asyncio.run(run.execute(_scenario(tmp_path, START_AND_STOP), server.mcp, goal_path))

    assert result["status"] == "error"
    assert "invalid goal" in result["message"]
    assert server.calls == []


def test_capture_failure_returns_error_and_still_closes_browser(
    tmp_path: Path, server: FakeNodriverServer
) -> None:
    server.tabs_response = {"status": "fail", "data": {"browser": "gone"}}

    result = asyncio.run(
        run.execute(_scenario(tmp_path, START_AND_STOP), server.mcp, _goal_file(tmp_path, [GA4_GOAL]))
    )

    assert result["status"] == "error"
    assert "gone" in result["message"]
    assert server.called_tools[-1] == "stop_browser"


def test_failed_goal_reports_what_the_page_itself_requested(
    tmp_path: Path, server: FakeNodriverServer
) -> None:
    server.network = {"TAB-1": []}
    server.page_resources = {"TAB-1": ["https://analytics.google.com/g/collect?en=page_view"]}

    result = asyncio.run(
        run.execute(_scenario(tmp_path, START_AND_STOP), server.mcp, _goal_file(tmp_path, [GA4_GOAL]))
    )

    assert result["goals"][0]["status"] == "fail"
    assert result["goals"][0]["requests"] == 0
    assert result["goals"][0]["page_requests"] == 1
    assert server.called_tools.index("evaluate_javascript") < server.called_tools.index("stop_browser")


def test_page_is_not_read_when_all_goals_pass(tmp_path: Path, server: FakeNodriverServer) -> None:
    _with_ga4_hit(server)

    result = asyncio.run(
        run.execute(_scenario(tmp_path, START_AND_STOP), server.mcp, _goal_file(tmp_path, [GA4_GOAL]))
    )

    assert "page_requests" not in result["goals"][0]
    assert "evaluate_javascript" not in server.called_tools


def test_capture_warnings_are_reported(tmp_path: Path, server: FakeNodriverServer) -> None:
    _with_ga4_hit(server)
    server.dropped = 3

    result = asyncio.run(
        run.execute(_scenario(tmp_path, START_AND_STOP), server.mcp, _goal_file(tmp_path, [GA4_GOAL]))
    )

    assert len(result["warnings"]) == 1


def test_main_passes_goal_argument(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], server: FakeNodriverServer
) -> None:
    _with_ga4_hit(server)
    scenario_path = _scenario(tmp_path, START_AND_STOP)
    goal_path = _goal_file(tmp_path, [META_GOAL])
    original_execute = run.execute

    async def fake_execute(scenario: Path, transport: str, goal: Path | None) -> dict:
        return await original_execute(scenario, server.mcp, goal)

    monkeypatch.setattr(run, "execute", fake_execute)

    exit_code = run.main([str(scenario_path), "--goal", str(goal_path)])

    assert exit_code == 1
    assert json.loads(capsys.readouterr().out)["goals"][0]["status"] == "fail"


def test_main_prints_error_and_exits_1_for_missing_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = run.main([str(tmp_path / "missing.json")])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert output["status"] == "error"
    assert "cannot read" in output["message"]


def test_main_prints_error_and_exits_1_when_server_is_unreachable(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _scenario(tmp_path, [{"action": "start_browser", "params": {}}])
    url = f"http://127.0.0.1:{_unused_port()}/mcp"

    exit_code = run.main([str(path), "--mcp-url", url])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert output["status"] == "error"
    assert output["message"]


def test_main_exit_code_follows_result_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    server: FakeNodriverServer,
) -> None:
    path = _scenario(tmp_path, [{"action": "start_browser", "params": {}}])

    async def fake_execute(scenario_path: Path, transport: str, goal: Path | None) -> dict:
        return await original_execute(scenario_path, server.mcp, goal)

    original_execute = run.execute
    monkeypatch.setattr(run, "execute", fake_execute)

    exit_code = run.main([str(path)])

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out) == {"status": "success", "steps": 1}


def test_main_exit_code_is_1_when_step_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    server: FakeNodriverServer,
) -> None:
    server.wait_for_response = {"status": "fail", "data": {"selector": "time ran out"}}
    path = _scenario(tmp_path, [{"action": "wait_for", "params": {"selector": "h1", "timeout": 1}}])

    async def fake_execute(scenario_path: Path, transport: str, goal: Path | None) -> dict:
        return await original_execute(scenario_path, server.mcp, goal)

    original_execute = run.execute
    monkeypatch.setattr(run, "execute", fake_execute)

    exit_code = run.main([str(path)])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert output["status"] == "fail"
    assert output["step"] == 1
