import time
from collections.abc import Awaitable, Callable
from typing import Any

from fastmcp import Client

from argos_runner.criteria.evaluator import Providers, evaluate_criteria, with_page_requests
from argos_runner.criteria.network_capture import NetworkCapture
from argos_runner.criteria.success_criterion import SuccessCriterion
from argos_runner.criteria.waiter import wait_until_satisfied
from argos_runner.scenario.model import Action, Step
from argos_runner.step_runner import open_pages

# How long a step's pixels may take to appear before its unmet criteria count as failed.
CRITERIA_WAIT_SECONDS = 60


def _all_passed(outcomes: list[dict[str, Any]]) -> bool:
    return all(outcome["status"] == "pass" for outcome in outcomes)


class StepCriteria:
    """Checks each step's criteria against the requests read while that step's window is open.

    The window opens right before the step's first action, so requests read by then belong to
    earlier steps. It closes once the criteria are met or CRITERIA_WAIT_SECONDS pass; requests read later
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
        if not step.success_criteria:
            return None
        self._opened_ms = time.time() * 1000
        await self._capture()
        self._first_request = len(self._capture.requests)
        return self._capture.error

    async def after_step(self, number: int, step: Step) -> str | None:
        if not step.success_criteria:
            return None
        criteria = step.success_criteria
        await wait_until_satisfied(self._capture, lambda: _all_passed(self._outcomes(criteria)), CRITERIA_WAIT_SECONDS)
        if self._capture.error is not None:
            return self._capture.error
        self.results = [*self.results, await self._report(number, step, criteria)]
        return None

    async def around_action(self, action: Action, run: Callable[[], Awaitable[dict[str, Any]]]) -> dict[str, Any]:
        return await self._capture.around_action(action, run)

    def _outcomes(self, criteria: list[SuccessCriterion]) -> list[dict[str, Any]]:
        return evaluate_criteria(criteria, self._capture.requests[self._first_request :], self._providers)

    async def _report(self, number: int, step: Step, criteria: list[SuccessCriterion]) -> dict[str, Any]:
        outcomes = self._outcomes(criteria)
        entry = {"step": number}
        if _all_passed(outcomes):
            return {**entry, "status": "pass", "success_criteria": outcomes}

        page_urls = await self._capture.read_page_urls(self._opened_ms)
        return {
            **entry,
            "status": "fail",
            "success_criteria": with_page_requests(outcomes, criteria, page_urls, self._providers),
            **await open_pages(self._client),
        }
