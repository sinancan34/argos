"""runner: runs a scenario JSON and checks its success criteria.

    runner scenario.json [--headless] [--device NAME] [--user-data-dir DIR]

The JSON report goes to stdout; the exit code is 0 (success), 1 (fail) or 2 (error).
"""

import argparse
import asyncio
import difflib
import json
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

from argos_agent.playwright_mcp.server import DEVICES_PATH, LaunchValue, load_devices
from argos_agent.runner.run import Pacing, run

EXIT_CODES = {"success": 0, "fail": 1, "error": 2}


def existing_dir(value: str) -> Path:
    """A profile dir that must already exist: for a missing one the browser would start signed out, unnoticed."""
    path = Path(value).expanduser().resolve()
    if not path.is_dir():
        raise argparse.ArgumentTypeError(f"{value} is not an existing directory")
    return path


def known_device(value: str) -> str:
    """A device name from devices.json: for any other the server would run on the desktop, unnoticed."""
    try:
        devices = load_devices()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc
    if value in devices:
        return value
    close = difflib.get_close_matches(value, devices, n=3, cutoff=0.6)
    hint = f"; did you mean {', '.join(map(repr, close))}?" if close else ""
    raise argparse.ArgumentTypeError(f"unknown device {value!r}{hint} (known devices are in {DEVICES_PATH})")


def launch_options(args: argparse.Namespace) -> dict[str, LaunchValue]:
    options: dict[str, LaunchValue] = {"--headless": True} if args.headless else {}
    if args.device:
        options = {**options, "--device": args.device}
    if args.user_data_dir:
        # The fixed in-memory profile would ignore the dir, so the run turns it off.
        options = {**options, "--isolated": False, "--user-data-dir": str(args.user_data_dir)}
    return options


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="runner", description="Run a scenario JSON and check its success criteria.")
    parser.add_argument("scenario", type=Path, help="the scenario JSON file")
    parser.add_argument("--headless", action="store_true", help="run the browser without a window")
    parser.add_argument(
        "--device", type=known_device, help='device to emulate, as Playwright names it, for example "iPhone 15"'
    )
    parser.add_argument(
        "--user-data-dir", type=existing_dir, help="browser profile dir to run on, for example one already signed in"
    )
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.WARNING)
    options = launch_options(args)
    report = asyncio.run(run(args.scenario, options=options, pacing=Pacing()))
    sys.stdout.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return EXIT_CODES[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
