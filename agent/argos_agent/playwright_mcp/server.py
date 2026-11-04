"""How the pinned Playwright MCP server is started.

Every flag used here is documented at https://playwright.dev/mcp/configuration/options.
"""

import tempfile
from dataclasses import dataclass

from fastmcp.client.transports import StdioTransport

SERVER_COMMAND = "npx"
WORKDIR_PREFIX = "argos-mcp-"
# Pinned: tool_catalog.json is generated from this version, and the client reads its text results.
SERVER_PACKAGE = "@playwright/mcp@0.0.84"
# The capabilities whose tools playwright.dev/mcp documents; core tools need none.
CAPABILITIES = ("network", "storage", "testing", "vision", "pdf", "devtools", "config")
# Past this size the server evicts its oldest output files, so scheduled runs do not fill the temp dir.
OUTPUT_MAX_BYTES = 50 * 1024 * 1024
FIXED_ARGS = (
    # The profile lives in memory and is gone when the browser closes.
    "--isolated",
    f"--caps={','.join(CAPABILITIES)}",
    # Results carry no generated Playwright code; nothing reads it.
    "--codegen=none",
    f"--output-max-size={OUTPUT_MAX_BYTES}",
)
# Every flag the server can be started with; refresh.py checks each one against the docs.
LAUNCH_FLAGS = (
    "--isolated",
    "--caps",
    "--codegen",
    "--output-max-size",
    "--headless",
    "--device",
    "--viewport-size",
    "--user-agent",
)


@dataclass(frozen=True)
class LaunchOptions:
    """The launch flags a run may set; each field is the documented flag of the same name."""

    headless: bool = False
    device: str | None = None
    viewport_size: str | None = None
    user_agent: str | None = None


def server_args(options: LaunchOptions | None = None) -> list[str]:
    """The npx arguments that start the pinned server with the fixed flags and the run's options."""
    chosen = options or LaunchOptions()
    valued = (
        ("--device", chosen.device),
        ("--viewport-size", chosen.viewport_size),
        ("--user-agent", chosen.user_agent),
    )
    return [
        "-y",
        SERVER_PACKAGE,
        *FIXED_ARGS,
        *(["--headless"] if chosen.headless else []),
        *(f"{flag}={value}" for flag, value in valued if value),
    ]


def server_transport(options: LaunchOptions | None = None) -> StdioTransport:
    """The pinned server over stdio, started in a new private (0700) dir under the OS temp dir.

    The server writes snapshots and any file a tool names by a relative path into the folder it starts in, so
    sessions running at the same time do not overwrite each other's files, and other local users cannot read them.
    Closing the client ends the server, which closes the browser and discards its profile.
    """
    # ponytail: the dir and the files in it stay after the run as evidence; clean up by age once runs are scheduled.
    workdir = tempfile.mkdtemp(prefix=WORKDIR_PREFIX)
    return StdioTransport(SERVER_COMMAND, server_args(options), cwd=workdir, keep_alive=False)
