import asyncio
import json
from pathlib import Path

import pytest
from fastmcp.client.transports import StdioTransport

from argos_agent.playwright_mcp import refresh as refresh_module
from argos_agent.playwright_mcp.catalog import CatalogError
from argos_agent.playwright_mcp.client import ServerError
from argos_agent.playwright_mcp.server import SERVER_PACKAGE
from tests.conftest import fake_server

pytestmark = pytest.mark.unit


def test_server_tools_lists_every_tool_with_its_input_schema() -> None:
    tools = asyncio.run(refresh_module.server_tools(fake_server({}, [])))

    assert set(tools) == {"browser_navigate", "browser_click", "browser_mouse_wheel"}
    assert tools["browser_navigate"]["required"] == ["url"]


def test_refresh_writes_every_tool_of_the_server(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(refresh_module, "server_transport", lambda: fake_server({}, []))
    path = tmp_path / "tool_catalog.json"

    refresh_module.refresh(path)

    written = json.loads(path.read_text(encoding="utf-8"))
    assert written["server"] == SERVER_PACKAGE
    assert set(written["tools"]) == {"browser_navigate", "browser_click", "browser_mouse_wheel"}
    assert written["tools"]["browser_mouse_wheel"]["required"] == []


def test_refresh_replaces_an_existing_catalog(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(refresh_module, "server_transport", lambda: fake_server({}, []))
    path = tmp_path / "tool_catalog.json"
    path.write_text(json.dumps({"server": "@playwright/mcp@0.0.1", "tools": {"old_tool": {}}}), encoding="utf-8")

    with caplog.at_level("INFO"):
        refresh_module.refresh(path)

    written = json.loads(path.read_text(encoding="utf-8"))
    assert written["server"] == SERVER_PACKAGE
    assert "old_tool" not in written["tools"]
    assert caplog.messages[-1].startswith("updated ")


def test_refresh_fails_without_writing_when_the_server_cannot_be_listed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(refresh_module, "server_transport", lambda: StdioTransport("/nonexistent/argos-no-such", []))
    path = tmp_path / "tool_catalog.json"

    with pytest.raises(ServerError, match="cannot list the tools"):
        refresh_module.refresh(path)

    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("failure", [CatalogError("bad"), ServerError("npx missing"), OSError("disk full")])
def test_main_fails_when_the_catalog_cannot_be_built(monkeypatch: pytest.MonkeyPatch, failure: Exception) -> None:
    def broken() -> None:
        raise failure

    monkeypatch.setattr(refresh_module, "refresh", broken)

    assert refresh_module.main() == 1


def test_main_succeeds_when_the_catalog_is_written(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(refresh_module, "refresh", lambda: None)

    assert refresh_module.main() == 0
