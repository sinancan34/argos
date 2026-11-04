"""runner: runs a scenario JSON and checks its success criteria.

    runner scenario.json [--headless]

The JSON report goes to stdout; the exit code is 0 (success), 1 (fail) or 2 (error).
"""

import argparse
import asyncio
import json
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

from argos_agent.playwright_mcp.server import LaunchValue
from argos_agent.runner.run import Pacing, run

EXIT_CODES = {"success": 0, "fail": 1, "error": 2}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="runner", description="Run a scenario JSON and check its success criteria.")
    parser.add_argument("scenario", type=Path, help="the scenario JSON file")
    parser.add_argument("--headless", action="store_true", help="run the browser without a window")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.WARNING)
    options: dict[str, LaunchValue] = {"--headless": True} if args.headless else {}
    report = asyncio.run(run(args.scenario, options=options, pacing=Pacing()))
    sys.stdout.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return EXIT_CODES[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
