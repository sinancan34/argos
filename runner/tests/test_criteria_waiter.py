import asyncio
import time

import pytest

from argos_runner.criteria.waiter import wait_until_satisfied

pytestmark = pytest.mark.unit


class FakeCapture:
    def __init__(self, error_on_call: int | None = None) -> None:
        self.calls = 0
        self.error: str | None = None
        self._error_on_call = error_on_call

    async def __call__(self) -> None:
        self.calls += 1
        if self.calls == self._error_on_call:
            self.error = "cannot list requests"


def test_stops_after_first_read_when_already_satisfied() -> None:
    capture = FakeCapture()

    asyncio.run(wait_until_satisfied(capture, lambda: True, wait_seconds=60, poll_seconds=30))

    assert capture.calls == 1


def test_keeps_reading_until_satisfied() -> None:
    capture = FakeCapture()

    asyncio.run(wait_until_satisfied(capture, lambda: capture.calls >= 3, wait_seconds=60, poll_seconds=0.01))

    assert capture.calls == 3


def test_gives_up_when_time_runs_out() -> None:
    capture = FakeCapture()
    started = time.monotonic()

    asyncio.run(wait_until_satisfied(capture, lambda: False, wait_seconds=0.05, poll_seconds=0.01))

    assert 0.05 <= time.monotonic() - started < 1
    assert capture.calls >= 2


def test_reads_once_more_at_the_deadline() -> None:
    capture = FakeCapture()

    asyncio.run(wait_until_satisfied(capture, lambda: False, wait_seconds=0.02, poll_seconds=10))

    assert capture.calls == 2


def test_zero_wait_reads_once() -> None:
    capture = FakeCapture()

    asyncio.run(wait_until_satisfied(capture, lambda: False, wait_seconds=0, poll_seconds=10))

    assert capture.calls == 1


def test_stops_on_capture_error() -> None:
    capture = FakeCapture(error_on_call=2)

    asyncio.run(wait_until_satisfied(capture, lambda: False, wait_seconds=60, poll_seconds=0.01))

    assert capture.calls == 2
