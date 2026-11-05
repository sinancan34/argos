import stat
import tempfile
from pathlib import Path

import pytest

from argos_agent.playwright_mcp.server import (
    FIXED_OPTIONS,
    SERVER_PACKAGE,
    load_devices,
    server_args,
    server_transport,
)

pytestmark = pytest.mark.unit

FIXED = [
    "-y",
    "@playwright/mcp@0.0.84",
    "--isolated",
    "--caps=network,storage,testing,vision,pdf,devtools,config",
    "--codegen=none",
    "--output-max-size=52428800",
]


def test_default_launch_runs_the_pinned_server_with_the_fixed_options_only() -> None:
    assert SERVER_PACKAGE == "@playwright/mcp@0.0.84"
    assert set(FIXED_OPTIONS) == {"--isolated", "--caps", "--codegen", "--output-max-size"}
    assert server_args() == FIXED


def test_each_option_is_passed_under_its_own_flag_name() -> None:
    options = {
        "--headless": True,
        "--sandbox": False,
        "--device": "iPhone 15",
        "--viewport-size": "1280x720",
    }

    assert server_args(options) == [
        *FIXED,
        "--headless",
        "--device=iPhone 15",
        "--viewport-size=1280x720",
    ]


def test_an_option_given_for_the_run_replaces_a_fixed_one() -> None:
    assert server_args({"--codegen": "typescript", "--isolated": False}) == [
        "-y",
        SERVER_PACKAGE,
        "--caps=network,storage,testing,vision,pdf,devtools,config",
        "--codegen=typescript",
        "--output-max-size=52428800",
    ]


def test_transport_starts_the_server_with_npx_in_a_private_dir_of_its_own() -> None:
    transport = server_transport({"--headless": True})
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


def test_the_device_list_holds_the_pinned_server_s_device_names() -> None:
    devices = load_devices()

    assert {"iPhone 15", "Pixel 10", "Galaxy S24", "Desktop Chrome"} <= devices


@pytest.mark.parametrize("content", ['{"iPhone 15": {}}', '["iPhone 15", 15]', "[]", "not json"])
def test_a_device_list_that_is_not_a_list_of_names_is_refused(tmp_path: Path, content: str) -> None:
    path = tmp_path / "devices.json"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match="devices.json"):
        load_devices(path)
