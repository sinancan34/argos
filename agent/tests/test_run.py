import asyncio
import json
from pathlib import Path
from typing import Any

import pytest
from fastmcp.client.transports import ClientTransport, StdioTransport

from argos_agent.playwright_mcp.catalog import CatalogError
from argos_agent.run import DELAY_RANGE_SECONDS, POLL_SECONDS, Pacing, main, random_delay, run
from tests.conftest import Calls, network_server

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


def listing(*requests: tuple[str, str]) -> str:
    lines = [f"{index}. [{method}] {url} => [200] OK" for index, (method, url) in enumerate(requests, start=1)]
    return "### Result\n" + "\n".join(lines) if lines else ""


HOME = [("GET", "https://www.emlakjet.com/"), ("GET", GTM), ("POST", GA4)]
AFTER_CLICK = [*HOME, ("POST", GA4)]
BODIES = {3: "### Result\nen=page_view&ep.content_group=ana-sayfa", 4: "### Result\nen=view_item_list"}
SCENARIO = [
    {
        "scenario": [NAVIGATE],
        "success_criteria": [criterion("gtm", "id", "GTM-MRDH2NZ"), criterion("ga4", "en", "page_view")],
    },
    {"scenario": [WHEEL, CLICK], "success_criteria": [criterion("ga4", "en", "view_item_list")]},
]


class Clock:
    """Stands in for asyncio.sleep and keeps every pause it was asked for."""

    def __init__(self) -> None:
        self.pauses: list[float] = []

    async def sleep(self, seconds: float) -> None:
        self.pauses.append(seconds)


def run_with(
    tmp_path: Path, scenario: Any, transport: ClientTransport | Any, wait_seconds: float = POLL_SECONDS
) -> tuple[dict[str, Any], Clock]:
    path = tmp_path / "scenario.json"
    path.write_text(json.dumps(scenario), encoding="utf-8")
    clock = Clock()
    pacing = Pacing(sleep=clock.sleep, delay=lambda: ACTION_DELAY, wait_seconds=wait_seconds)
    return asyncio.run(run(path, options={}, pacing=pacing, transport=transport)), clock


def test_a_scenario_whose_criteria_all_pass_is_a_success(tmp_path: Path) -> None:
    calls: Calls = []
    # step 1: baseline, then its hits; step 2: baseline, a poll before the hit arrives, then the hit.
    server = network_server(
        [listing(), listing(*HOME), listing(*HOME), listing(*HOME), listing(*AFTER_CLICK)], BODIES, calls
    )

    report, clock = run_with(tmp_path, SCENARIO, server)

    assert report["status"] == "success", report
    assert [step["status"] for step in report["steps"]] == ["pass", "pass"]
    assert report["steps"][1]["criteria"][0]["url"] == GA4
    assert report["warnings"] == []
    # No pause before the first action, one before every other action, one between two polls.
    assert clock.pauses == [ACTION_DELAY, ACTION_DELAY, POLL_SECONDS]
    actions = [name for name, _ in calls if not name.startswith("browser_network")]
    assert actions == ["browser_navigate", "browser_mouse_wheel", "browser_click"]
    # The step 1 hit (index 3) is not read again for step 2, whose requests start after its baseline.
    assert [arguments["index"] for name, arguments in calls if name == "browser_network_request"] == [3, 4]


def test_a_criterion_that_never_passes_fails_its_step_and_the_run_goes_on(tmp_path: Path) -> None:
    scenario = [
        {"scenario": [NAVIGATE], "success_criteria": [criterion("gtm", "id", "GTM-OTHER")]},
        {"scenario": [CLICK]},
    ]
    server = network_server([listing(), listing(*HOME)], BODIES, [])

    report, clock = run_with(tmp_path, scenario, server, wait_seconds=2 * POLL_SECONDS)

    assert report["status"] == "fail"
    assert [step["status"] for step in report["steps"]] == ["fail", "pass"]
    failed = report["steps"][0]["criteria"][0]
    assert failed["closest"][0]["actual"] == "GTM-MRDH2NZ"
    assert clock.pauses == [POLL_SECONDS, POLL_SECONDS, ACTION_DELAY]


def test_a_failing_action_ends_the_run(tmp_path: Path) -> None:
    scenario = [{"scenario": [CLICK, WHEEL]}, {"scenario": [NAVIGATE]}]
    calls: Calls = []
    server = network_server([listing()], {}, calls, failing_targets=frozenset({'text="En Yeni"'}))

    report, _ = run_with(tmp_path, scenario, server)

    assert report["status"] == "fail"
    (step,) = report["steps"]
    assert step["failed_action"]["action"] == 1
    assert step["failed_action"]["params"] == {"target": 'text="En Yeni"'}
    assert "TimeoutError" in step["failed_action"]["error"]
    assert [name for name, _ in calls if not name.startswith("browser_network")] == ["browser_click"]


def test_an_unreadable_body_is_read_again_on_every_poll_and_warned_about_once(tmp_path: Path) -> None:
    scenario = [{"scenario": [NAVIGATE], "success_criteria": [criterion("ga4", "en", "page_view")]}]
    calls: Calls = []
    server = network_server([listing(), listing(*HOME)], {}, calls)

    report, _ = run_with(tmp_path, scenario, server, wait_seconds=POLL_SECONDS)

    assert report["status"] == "fail"
    assert len(report["warnings"]) == 1 and "browser_network_request #3" in report["warnings"][0]
    assert [arguments["index"] for name, arguments in calls if name == "browser_network_request"] == [3, 3]


def test_launch_options_the_server_does_not_take_are_an_error(tmp_path: Path) -> None:
    path = tmp_path / "scenario.json"
    path.write_text(json.dumps([{"scenario": [NAVIGATE]}]), encoding="utf-8")

    report = asyncio.run(run(path, options={"--no-such-option": True}, pacing=Pacing()))

    assert report["status"] == "error"
    assert "--no-such-option" in report["problems"][0]


def test_a_stale_tool_catalog_is_an_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def stale() -> None:
        raise CatalogError("tool catalog was generated for @playwright/mcp@0.0.1")

    monkeypatch.setattr("argos_agent.runner.scenario.load_catalog", stale)

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

    code = main([str(path), "--headless", "--wait", "1"])

    assert code == 2
    assert json.loads(capsys.readouterr().out)["status"] == "error"


@pytest.mark.parametrize("wait", ["-1", "nan", "x"])
def test_main_refuses_a_bad_wait(wait: str) -> None:
    with pytest.raises(SystemExit):
        main(["scenario.json", "--wait", wait])


def test_the_random_delay_is_between_one_and_five_seconds() -> None:
    low, high = DELAY_RANGE_SECONDS

    assert (low, high) == (1.0, 5.0)
    assert all(low <= random_delay() <= high for _ in range(200))
