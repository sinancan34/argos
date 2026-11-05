"""How the pinned Playwright MCP server is started.

Launch options are given under the server's own flag names, as `npx @playwright/mcp@0.0.84 --help` lists them;
the server itself refuses one it does not take, and PlaywrightMCP then fails to start.
"""

import json
import tempfile
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType

from fastmcp.client.transports import StdioTransport

SERVER_COMMAND = "npx"
# Pinned: tool_catalog.json is generated from this version, and the client reads its text results.
SERVER_PACKAGE = "@playwright/mcp@0.0.84"
WORKDIR_PREFIX = "argos-mcp-"
# Every capability, so that every tool of the server can be called.
CAPABILITIES = ("network", "storage", "testing", "vision", "pdf", "devtools", "config")
# Past this size the server evicts its oldest output files, so scheduled runs do not fill the disk.
OUTPUT_MAX_BYTES = 50 * 1024 * 1024
# The names `--device` takes: the pinned server runs on the desktop defaults for any other name, without a word.
# Taken from the pinned server's Playwright (`Object.keys(require("playwright-core").devices)`); edit it by hand.
DEVICES_PATH = Path(__file__).with_name("devices.json")

# A flag that takes no value is True (given) or False (left out); one with a `<value>` takes a string.
LaunchValue = bool | str

# Used for every run unless the run gives the same flag itself.
FIXED_OPTIONS: Mapping[str, LaunchValue] = MappingProxyType(
    {
        # The profile lives in memory and is gone when the browser closes.
        "--isolated": True,
        "--caps": ",".join(CAPABILITIES),
        # Results carry no generated Playwright code; nothing reads it.
        "--codegen": "none",
        "--output-max-size": str(OUTPUT_MAX_BYTES),
    }
)


def load_devices(path: Path = DEVICES_PATH) -> frozenset[str]:
    """The device names in the list, or a ValueError naming the file when it is not a non-empty list of names."""
    try:
        content = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    if not isinstance(content, list) or not content or not all(isinstance(name, str) for name in content):
        raise ValueError(f"{path}: must be a non-empty JSON array of device names")
    return frozenset(content)


def option_args(flag: str, value: LaunchValue) -> list[str]:
    if isinstance(value, bool):
        return [flag] if value else []
    return [f"{flag}={value}"]


def server_args(options: Mapping[str, LaunchValue] | None = None) -> list[str]:
    """The npx arguments that start the pinned server with the fixed options and the run's own."""
    merged = {**FIXED_OPTIONS, **(options or {})}
    return ["-y", SERVER_PACKAGE, *(arg for flag, value in merged.items() for arg in option_args(flag, value))]


def server_transport(options: Mapping[str, LaunchValue] | None = None) -> StdioTransport:
    """The pinned server over stdio, started in a new private (0700) dir under the OS temp dir.

    The server writes snapshots and any file a tool names by a relative path into the folder it starts in, so
    sessions running at the same time do not overwrite each other's files, and other local users cannot read them.
    Closing the client ends the server, which closes the browser and discards its profile.
    """
    # ponytail: the dir and the files in it stay after the run as evidence; clean up by age once runs are scheduled.
    workdir = tempfile.mkdtemp(prefix=WORKDIR_PREFIX)
    return StdioTransport(SERVER_COMMAND, server_args(options), cwd=workdir, keep_alive=False)
