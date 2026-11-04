import asyncio
import json
from pathlib import Path

import pytest
from fastmcp.client.transports import StdioTransport

from argos_agent.playwright_mcp import refresh as refresh_module
from argos_agent.playwright_mcp.client import ServerError
from argos_agent.playwright_mcp.docs import DocsError, Documentation, DocumentedParam
from argos_agent.playwright_mcp.server import LAUNCH_FLAGS, SERVER_PACKAGE
from tests.conftest import fake_server

pytestmark = pytest.mark.unit


def documentation(flags: frozenset[str] = frozenset(LAUNCH_FLAGS)) -> Documentation:
    return Documentation(
        tools={"browser_navigate": {"url": DocumentedParam(required=True)}, "browser_ghost": {}}, flags=flags
    )


@pytest.fixture
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    """The docs and the server, faked: three server tools, one of them documented."""
    monkeypatch.setattr(refresh_module, "read_documentation", documentation)
    monkeypatch.setattr(refresh_module, "server_transport", lambda: fake_server({}, []))


def test_server_tools_lists_every_tool_with_its_input_schema() -> None:
    tools = asyncio.run(refresh_module.server_tools(fake_server({}, [])))

    assert set(tools) == {"browser_navigate", "browser_click", "browser_mouse_wheel"}
    assert tools["browser_navigate"]["required"] == ["url"]


@pytest.mark.usefixtures("offline")
def test_refresh_writes_only_the_documented_tools_and_lists_the_rest(tmp_path: Path) -> None:
    path = tmp_path / "tool_catalog.json"

    excluded = refresh_module.refresh(path)

    written = json.loads(path.read_text(encoding="utf-8"))
    assert written["server"] == SERVER_PACKAGE
    assert set(written["tools"]) == {"browser_navigate"}
    assert written["excluded"] == list(excluded)
    assert "browser_click: not documented" in excluded
    assert "browser_ghost: documented, but the server has no such tool" in excluded
    assert list(tmp_path.iterdir()) == [path]


def test_refresh_refuses_launch_flags_the_docs_do_not_name(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(refresh_module, "read_documentation", lambda: documentation(frozenset({"--headless"})))
    path = tmp_path / "tool_catalog.json"

    with pytest.raises(DocsError, match="--isolated"):
        refresh_module.refresh(path)

    assert not path.exists()


def test_refresh_fails_without_writing_when_the_server_cannot_be_listed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(refresh_module, "read_documentation", documentation)
    monkeypatch.setattr(refresh_module, "server_transport", lambda: StdioTransport("/nonexistent/argos-no-such", []))
    path = tmp_path / "tool_catalog.json"

    with pytest.raises(ServerError, match="cannot list the tools"):
        refresh_module.refresh(path)

    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("failure", [DocsError("docs down"), ServerError("npx missing"), OSError("disk full")])
def test_main_fails_when_the_docs_or_the_server_cannot_be_read(
    monkeypatch: pytest.MonkeyPatch, failure: Exception
) -> None:
    def broken() -> tuple[str, ...]:
        raise failure

    monkeypatch.setattr(refresh_module, "refresh", broken)

    assert refresh_module.main() == 1


def test_main_lists_what_was_excluded(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
    monkeypatch.setattr(refresh_module, "refresh", lambda: ("browser_emulate_media: not documented",))

    with caplog.at_level("INFO"):
        assert refresh_module.main() == 0

    assert "excluded: browser_emulate_media: not documented" in caplog.text
