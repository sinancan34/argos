import asyncio
import json
from pathlib import Path
from typing import Any

import pytest
from fastmcp.client.transports import ClientTransport, StdioTransport

from argos_agent.cli.run import main
from argos_agent.playwright_mcp.catalog import CatalogError
from argos_agent.runner.run import DELAY_RANGE_SECONDS, POLL_SECONDS, Pacing, random_delay, run
from tests.conftest import Calls, Heard, network_server

pytestmark = pytest.mark.unit

ACTION_DELAY = 3.0
GA4 = "https://region1.google-analytics.com/g/collect?v=2&tid=G-RQY35QJEY7"
GTM = "https://www.googletagmanager.com/gtm.js?id=GTM-MRDH2NZ"
NAVIGATE = {"action": "browser_navigate", "params": {"url": "https://www.emlakjet.com/"}}
WHEEL = {"action": "browser_mouse_wheel", "params": {"deltaX": 0, "deltaY": 300}}
CLICK = {"action": "browser_click", "params": {"target": 'text="En Yeni"'}}


def criterion(provider: str, key: str, value: str) -> dict[str, Any]:
    return {
        "provider": {"name": provider, "params": []},
        "conditions": [{"key": key, "match": "exact", "value": value}],
    }


HOME: Heard = [("https://www.emlakjet.com/", None), (GTM, None), (GA4, "en=page_view&ep.content_group=ana-sayfa")]
AFTER_CLICK: Heard = [*HOME, (GA4, "en=view_item_list")]
SCENARIO = [
    {
        "scenario": [NAVIGATE],
        "success_criteria": [criterion("gtm", "id", "GTM-MRDH2NZ"), criterion("ga4", "en", "page_view")],
    },
    {"scenario": [WHEEL, CLICK], "success_criteria": [criterion("ga4", "en", "view_item_list")]},
]


class Clock:
    """Stands in for asyncio.sleep and time.monotonic: a pause moves the time on and is kept."""

    def __init__(self) -> None:
        self.now = 0.0
        self.pauses: list[float] = []

    def time(self) -> float:
        return self.now

    async def sleep(self, seconds: float) -> None:
        self.now += seconds
        self.pauses.append(seconds)


def run_with(
    tmp_path: Path, scenario: Any, transport: ClientTransport | Any, wait_seconds: float = POLL_SECONDS
) -> tuple[dict[str, Any], Clock]:
    path = tmp_path / "scenario.json"
    path.write_text(json.dumps(scenario), encoding="utf-8")
    clock = Clock()
    pacing = Pacing(sleep=clock.sleep, clock=clock.time, delay=lambda: ACTION_DELAY, wait_seconds=wait_seconds)
    return asyncio.run(run(path, options={}, pacing=pacing, transport=transport)), clock


def test_a_scenario_whose_criteria_all_pass_is_a_success(tmp_path: Path) -> None:
    calls: Calls = []
    # step 1: baseline, then its hits; step 2: baseline, a poll before the hit arrives, then the hit.
    server = network_server([[], HOME, HOME, HOME, AFTER_CLICK], calls)

    report, clock = run_with(tmp_path, SCENARIO, server)

    assert report["status"] == "success", report
    assert [step["status"] for step in report["steps"]] == ["pass", "pass"]
    assert report["steps"][1]["criteria"][0]["url"] == GA4
    # No pause before the first action, one before every other action, one between two polls.
    assert clock.pauses == [ACTION_DELAY, ACTION_DELAY, POLL_SECONDS]
    # The listener starts before the first action.
    assert [name for name, _ in calls if name != "heard"] == [
        "listen",
        "browser_navigate",
        "browser_mouse_wheel",
        "browser_click",
    ]
    # Step 2 reads only the requests after step 1's three, so step 1's hits are never its own.
    assert [arguments["start"] for name, arguments in calls if name == "heard"] == [0, 0, 0, 3, 3]


def test_a_criterion_that_never_passes_fails_its_step_and_the_run_goes_on(tmp_path: Path) -> None:
    scenario = [
        {"scenario": [NAVIGATE], "success_criteria": [criterion("gtm", "id", "GTM-OTHER")]},
        {"scenario": [CLICK]},
    ]
    server = network_server([[], HOME], [])

    report, clock = run_with(tmp_path, scenario, server, wait_seconds=2 * POLL_SECONDS)

    assert report["status"] == "fail"
    assert [step["status"] for step in report["steps"]] == ["fail", "pass"]
    failed = report["steps"][0]["criteria"][0]
    assert failed["closest"][0]["actual"] == "GTM-MRDH2NZ"
    assert clock.pauses == [POLL_SECONDS, POLL_SECONDS, ACTION_DELAY]


def test_a_failing_action_ends_the_run(tmp_path: Path) -> None:
    scenario = [{"scenario": [CLICK, WHEEL]}, {"scenario": [NAVIGATE]}]
    calls: Calls = []
    server = network_server([[]], calls, failing_targets=frozenset({'text="En Yeni"'}))

    report, _ = run_with(tmp_path, scenario, server)

    assert report["status"] == "fail"
    (step,) = report["steps"]
    assert step["failed_action"]["action"] == 1
    assert step["failed_action"]["params"] == {"target": 'text="En Yeni"'}
    assert "TimeoutError" in step["failed_action"]["error"]
    assert [name for name, _ in calls if name.startswith("browser_")] == ["browser_click"]


def test_the_last_poll_is_made_as_the_wait_runs_out(tmp_path: Path) -> None:
    scenario = [{"scenario": [NAVIGATE], "success_criteria": [criterion("gtm", "id", "GTM-OTHER")]}]
    server = network_server([[], HOME], [])

    report, clock = run_with(tmp_path, scenario, server, wait_seconds=2.5 * POLL_SECONDS)

    assert report["status"] == "fail"
    assert clock.pauses == [POLL_SECONDS, POLL_SECONDS, 0.5 * POLL_SECONDS]


def test_the_criteria_wait_up_to_a_minute() -> None:
    assert Pacing().wait_seconds == 60


def test_a_stale_tool_catalog_is_an_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def stale() -> None:
        raise CatalogError("tool catalog was generated for @playwright/mcp@0.0.1")

    monkeypatch.setattr("argos_agent.scenario.model.load_catalog", stale)

    report, _ = run_with(tmp_path, [{"scenario": [NAVIGATE]}], None)

    assert report == {
        "scenario": str(tmp_path / "scenario.json"),
        "status": "error",
        "problems": [str(CatalogError("tool catalog was generated for @playwright/mcp@0.0.1"))],
    }


def test_an_invalid_scenario_is_an_error_before_the_server_starts(tmp_path: Path) -> None:
    report, _ = run_with(tmp_path, [{"scenario": [{"action": "browser_scroll", "params": {}}]}], None)

    assert report["status"] == "error"
    assert report["problems"][0].startswith("step 1 action 1 browser_scroll: unknown tool")


def test_a_server_that_cannot_start_is_an_error(tmp_path: Path) -> None:
    report, _ = run_with(tmp_path, [{"scenario": [NAVIGATE]}], StdioTransport("/nonexistent/argos-no-such-command", []))

    assert report["status"] == "error"
    assert "cannot start" in report["problems"][0]


def test_main_prints_the_report_and_exits_by_status(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "scenario.json"
    path.write_text("[]", encoding="utf-8")

    code = main([str(path), "--headless"])

    assert code == 2
    assert json.loads(capsys.readouterr().out)["status"] == "error"


def launch_options(argv: list[str], monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """The launch options main hands to run for these arguments."""
    seen: dict[str, Any] = {}

    async def fake_run(path: Path, *, options: dict[str, Any], pacing: Pacing) -> dict[str, Any]:
        seen.update(options)
        return {"scenario": str(path), "status": "success", "steps": []}

    monkeypatch.setattr("argos_agent.cli.run.run", fake_run)
    assert main(argv) == 0
    return seen


def test_main_passes_no_launch_options_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    assert launch_options(["scenario.json"], monkeypatch) == {}


def test_main_passes_the_device_to_emulate(monkeypatch: pytest.MonkeyPatch) -> None:
    options = launch_options(["scenario.json", "--headless", "--device", "iPhone 15"], monkeypatch)

    assert options == {"--headless": True, "--device": "iPhone 15"}


@pytest.mark.parametrize("name", ["iphone 15", "No Such Phone"])
def test_main_refuses_a_device_the_server_does_not_know(
    name: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit):
        launch_options(["scenario.json", "--device", name], monkeypatch)

    assert f"unknown device {name!r}" in capsys.readouterr().err


def test_main_suggests_the_closest_device_for_a_typo(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit):
        launch_options(["scenario.json", "--device", "iphone 15"], monkeypatch)

    assert "'iPhone 15'" in capsys.readouterr().err


def test_main_runs_on_the_given_profile_instead_of_an_in_memory_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "profile").mkdir()

    options = launch_options(["scenario.json", "--user-data-dir", "profile"], monkeypatch)

    assert options == {"--isolated": False, "--user-data-dir": str(tmp_path / "profile")}


def test_main_refuses_a_profile_dir_that_does_not_exist(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit):
        launch_options(["scenario.json", "--user-data-dir", str(tmp_path / "missing")], monkeypatch)

    assert "not an existing directory" in capsys.readouterr().err


def test_main_refuses_the_removed_wait_option() -> None:
    with pytest.raises(SystemExit):
        main(["scenario.json", "--wait", "1"])


def test_the_random_delay_is_between_one_and_five_seconds() -> None:
    low, high = DELAY_RANGE_SECONDS

    assert (low, high) == (1.0, 5.0)
    assert all(low <= random_delay() <= high for _ in range(200))
