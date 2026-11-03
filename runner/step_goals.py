import time
from typing import Any

from fastmcp import Client

from goal import Goal
from goal_evaluator import Providers, evaluate_goals, with_page_requests
from goal_waiter import wait_until_satisfied
from network_capture import NetworkCapture
from scenario import Step
from step_runner import open_tabs

# How long a step's pixels may take to appear before its unmet goals count as failed.
GOAL_WAIT_SECONDS = 60


def _all_passed(outcomes: list[dict[str, Any]]) -> bool:
    return all(outcome["status"] == "pass" for outcome in outcomes)


class StepGoals:
    """Checks each step's goals against the requests read while that step's window is open.

    The window opens right before the step runs, so requests read by then belong to earlier
    steps. It closes once the goals are met or GOAL_WAIT_SECONDS pass; requests read later
    are never credited to it.
    """

    def __init__(self, client: Client, capture: NetworkCapture, providers: Providers) -> None:
        self._client = client
        self._capture = capture
        self._providers = providers
        self._first_request = 0
        self._opened_ms = 0.0
        self.results: list[dict[str, Any]] = []

    async def before_step(self, number: int, step: Step) -> str | None:
        if not step.goals:
            return None
        self._opened_ms = time.time() * 1000
        await self._capture()
        self._first_request = len(self._capture.requests)
        return self._capture.error

    async def after_step(self, number: int, step: Step) -> str | None:
        if not step.goals:
            return None
        goals = step.goals
        await wait_until_satisfied(self._capture, lambda: _all_passed(self._outcomes(goals)), GOAL_WAIT_SECONDS)
        if self._capture.error is not None:
            return self._capture.error
        self.results = [*self.results, await self._report(number, step, goals)]
        return None

    def _outcomes(self, goals: list[Goal]) -> list[dict[str, Any]]:
        return evaluate_goals(goals, self._capture.requests[self._first_request :], self._providers)

    async def _report(self, number: int, step: Step, goals: list[Goal]) -> dict[str, Any]:
        outcomes = self._outcomes(goals)
        entry = {"step": number, "action": step.action}
        if _all_passed(outcomes):
            return {**entry, "status": "pass", "goals": outcomes}

        page_urls = await self._capture.read_page_urls(self._opened_ms)
        return {
            **entry,
            "status": "fail",
            "goals": with_page_requests(outcomes, goals, page_urls, self._providers),
            **await open_tabs(self._client),
        }
