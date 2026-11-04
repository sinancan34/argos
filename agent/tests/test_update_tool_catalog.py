import asyncio
import json
from pathlib import Path

import pytest
from fastmcp.client.transports import StdioTransport

from argos_agent.playwright_mcp import catalog as catalog_module
from argos_agent.playwright_mcp.catalog import CatalogError
from argos_agent.playwright_mcp.scripts import update_tool_catalog
from argos_agent.playwright_mcp.server import SERVER_PACKAGE
from tests.conftest import fake_server

pytestmark = pytest.mark.unit


def test_server_tools_lists_every_tool_with_its_input_schema() -> None:
    tools = asyncio.run(catalog_module.server_tools(fake_server({}, [])))

    assert set(tools) == {"browser_navigate", "browser_click", "browser_mouse_wheel"}
    assert tools["browser_navigate"]["required"] == ["url"]


def test_write_catalog_creates_the_file_with_every_tool(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(catalog_module, "server_transport", lambda: fake_server({}, []))
    path = tmp_path / "tool_catalog.json"

    catalog_module.write_catalog(path)

    written = json.loads(path.read_text(encoding="utf-8"))
    assert written["server"] == SERVER_PACKAGE
    assert set(written["tools"]) == {"browser_navigate", "browser_click", "browser_mouse_wheel"}
    assert written["tools"]["browser_mouse_wheel"]["required"] == []


def test_write_catalog_replaces_an_existing_catalog(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(catalog_module, "server_transport", lambda: fake_server({}, []))
    path = tmp_path / "tool_catalog.json"
    path.write_text(json.dumps({"server": "@playwright/mcp@0.0.1", "tools": {"old_tool": {}}}), encoding="utf-8")

    with caplog.at_level("INFO"):
        catalog_module.write_catalog(path)

    written = json.loads(path.read_text(encoding="utf-8"))
    assert written["server"] == SERVER_PACKAGE
    assert "old_tool" not in written["tools"]
    assert caplog.messages[-1].startswith("updated ")


def test_write_catalog_fails_without_writing_when_the_server_cannot_be_listed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(catalog_module, "server_transport", lambda: StdioTransport("/nonexistent/argos-no-such", []))
    path = tmp_path / "tool_catalog.json"

    with pytest.raises(CatalogError, match="cannot list the tools"):
        catalog_module.write_catalog(path)

    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("failure", [CatalogError("npx missing"), OSError("disk full")])
def test_main_fails_when_the_catalog_cannot_be_built(monkeypatch: pytest.MonkeyPatch, failure: Exception) -> None:
    def broken() -> None:
        raise failure

    monkeypatch.setattr(update_tool_catalog, "write_catalog", broken)

    assert update_tool_catalog.main() == 1


def test_main_succeeds_when_the_catalog_is_written(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(update_tool_catalog, "write_catalog", lambda: None)

    assert update_tool_catalog.main() == 0
