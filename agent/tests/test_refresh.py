import asyncio
import json
from pathlib import Path

import pytest
from fastmcp.client.transports import StdioTransport

from argos_agent.playwright_mcp import refresh as refresh_module
from argos_agent.playwright_mcp.catalog import CatalogError
from argos_agent.playwright_mcp.client import ServerError
from argos_agent.playwright_mcp.server import FIXED_OPTIONS, SERVER_PACKAGE
from tests.conftest import fake_server

pytestmark = pytest.mark.unit

HELP = """Usage: Playwright MCP [options]

Options:
  -V, --version                         output the version number
  --allowed-hosts <hosts...>            comma-separated list of hosts this
                                        server is allowed to serve from.
  --headless                            run browser in headless mode, headed by
                                        default
  --user-agent <ua string>              specify user agent string
  -h, --help                            display help for command
"""
FIXED_HELP = HELP + "".join(f"  {flag} <value>   fixed\n" for flag in FIXED_OPTIONS)


def test_help_lists_every_option_with_its_argument() -> None:
    assert refresh_module.parse_help(HELP) == {
        "--allowed-hosts": {"argument": "hosts..."},
        "--headless": {"argument": None},
        "--user-agent": {"argument": "ua string"},
    }


def test_server_tools_lists_every_tool_with_its_input_schema() -> None:
    tools = asyncio.run(refresh_module.server_tools(fake_server({}, [])))

    assert set(tools) == {"browser_navigate", "browser_click", "browser_mouse_wheel"}
    assert tools["browser_navigate"]["required"] == ["url"]


@pytest.fixture
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    """The server, faked: three tools, and a --help that lists the fixed options."""
    monkeypatch.setattr(refresh_module, "server_transport", lambda: fake_server({}, []))
    monkeypatch.setattr(refresh_module, "server_help", lambda: FIXED_HELP)


@pytest.mark.usefixtures("offline")
def test_refresh_writes_every_tool_and_option_of_the_server(tmp_path: Path) -> None:
    path = tmp_path / "tool_catalog.json"

    refresh_module.refresh(path)

    written = json.loads(path.read_text(encoding="utf-8"))
    assert written["server"] == SERVER_PACKAGE
    assert set(written["tools"]) == {"browser_navigate", "browser_click", "browser_mouse_wheel"}
    assert written["tools"]["browser_mouse_wheel"]["required"] == []
    assert set(written["options"]) == {"--allowed-hosts", "--headless", "--user-agent", *FIXED_OPTIONS}
    assert list(tmp_path.iterdir()) == [path]


def test_refresh_refuses_a_fixed_option_the_server_does_not_take(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(refresh_module, "server_transport", lambda: fake_server({}, []))
    monkeypatch.setattr(refresh_module, "server_help", lambda: HELP)
    path = tmp_path / "tool_catalog.json"

    with pytest.raises(CatalogError, match="--isolated"):
        refresh_module.refresh(path)

    assert not path.exists()


def test_refresh_fails_without_writing_when_the_server_cannot_be_listed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(refresh_module, "server_transport", lambda: StdioTransport("/nonexistent/argos-no-such", []))
    path = tmp_path / "tool_catalog.json"

    with pytest.raises(ServerError, match="cannot list the tools"):
        refresh_module.refresh(path)

    assert list(tmp_path.iterdir()) == []


def test_help_that_cannot_be_read_fails_with_server_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(refresh_module, "SERVER_COMMAND", "/nonexistent/argos-no-such")

    with pytest.raises(ServerError, match="cannot read the options"):
        refresh_module.server_help()


@pytest.mark.parametrize("failure", [CatalogError("bad"), ServerError("npx missing"), OSError("disk full")])
def test_main_fails_when_the_catalog_cannot_be_built(monkeypatch: pytest.MonkeyPatch, failure: Exception) -> None:
    def broken() -> None:
        raise failure

    monkeypatch.setattr(refresh_module, "refresh", broken)

    assert refresh_module.main() == 1


def test_main_succeeds_when_the_catalog_is_written(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(refresh_module, "refresh", lambda: None)

    assert refresh_module.main() == 0
