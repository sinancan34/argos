import json
from pathlib import Path

import pytest

from argos_agent.cli.validate import main
from argos_agent.playwright_mcp.catalog import CatalogError

pytestmark = pytest.mark.unit

EXAMPLE = Path(__file__).parents[1] / "docs" / "scenario-example.json"


def validate(path: Path, capsys: pytest.CaptureFixture[str]) -> tuple[int, dict[str, object]]:
    code = main([str(path)])
    return code, json.loads(capsys.readouterr().out)


def test_a_valid_scenario_exits_0(capsys: pytest.CaptureFixture[str]) -> None:
    code, report = validate(EXAMPLE, capsys)

    assert code == 0
    assert report == {"scenario": str(EXAMPLE), "status": "valid", "problems": []}


def test_an_invalid_scenario_exits_1_with_every_problem(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "scenario.json"
    scenario = [
        {"scenario": [{"action": "browser_scroll", "params": {}}]},
        {"scenario": [{"action": "browser_click", "params": {}}]},
    ]
    path.write_text(json.dumps(scenario), encoding="utf-8")

    code, report = validate(path, capsys)

    assert code == 1
    assert report["status"] == "invalid"
    assert report["problems"] == [
        "step 1 action 1 browser_scroll: unknown tool 'browser_scroll': @playwright/mcp@0.0.84 has no such tool",
        "step 2 action 1 browser_click: 'target' is a required property",
    ]


def test_an_unreadable_file_is_invalid(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, report = validate(tmp_path / "missing.json", capsys)

    assert code == 1
    assert str(report["problems"][0]).startswith("cannot read")  # type: ignore[index]


def test_a_stale_tool_catalog_exits_2(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    def stale() -> None:
        raise CatalogError("tool catalog was generated for @playwright/mcp@0.0.1")

    monkeypatch.setattr("argos_agent.scenario.model.load_catalog", stale)

    code, report = validate(EXAMPLE, capsys)

    assert code == 2
    assert report == {
        "scenario": str(EXAMPLE),
        "status": "error",
        "problems": ["tool catalog was generated for @playwright/mcp@0.0.1"],
    }
