import stat
import tempfile
from pathlib import Path

import pytest

from argos_agent.playwright_mcp.server import LAUNCH_FLAGS, SERVER_PACKAGE, LaunchOptions, server_args, server_transport

pytestmark = pytest.mark.unit

FIXED = [
    "-y",
    "@playwright/mcp@0.0.84",
    "--isolated",
    "--caps=network,storage,testing,vision,pdf,devtools,config",
    "--codegen=none",
    "--output-max-size=52428800",
]


def test_default_launch_runs_the_pinned_server_with_fixed_flags_only() -> None:
    assert SERVER_PACKAGE == "@playwright/mcp@0.0.84"
    assert server_args() == FIXED


def test_each_launch_option_adds_its_documented_flag() -> None:
    options = LaunchOptions(headless=True, device="iPhone 15", viewport_size="1280x720", user_agent="Argos UA 1.0")

    assert server_args(options) == [
        *FIXED,
        "--headless",
        "--device=iPhone 15",
        "--viewport-size=1280x720",
        "--user-agent=Argos UA 1.0",
    ]


def test_launch_flags_name_every_flag_the_server_can_get() -> None:
    every_option = LaunchOptions(headless=True, device="d", viewport_size="1x1", user_agent="u")
    used = {arg.split("=", 1)[0] for arg in server_args(every_option) if arg.startswith("--")}

    assert used == set(LAUNCH_FLAGS)


def test_transport_starts_the_server_with_npx_in_a_private_dir_of_its_own() -> None:
    transport = server_transport(LaunchOptions(headless=True))
    other = server_transport()

    assert transport.command == "npx"
    assert transport.args == [*FIXED, "--headless"]
    assert transport.cwd is not None and other.cwd is not None
    workdir = Path(transport.cwd)
    assert workdir.parent == Path(tempfile.gettempdir())
    assert workdir.name.startswith("argos-mcp-")
    assert stat.S_IMODE(workdir.stat().st_mode) == 0o700
    assert transport.cwd != other.cwd
    for path in (transport.cwd, other.cwd):
        Path(path).rmdir()
