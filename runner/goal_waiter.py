import asyncio
from typing import Awaitable, Callable, Protocol

POLL_SECONDS = 2.0


class Capture(Protocol):
    error: str | None

    def __call__(self) -> Awaitable[None]: ...


async def wait_until_satisfied(
    capture: Capture,
    satisfied: Callable[[], bool],
    wait_seconds: float,
    poll_seconds: float = POLL_SECONDS,
) -> None:
    """Reads requests until `satisfied` holds, a read fails or `wait_seconds` run out."""
    loop = asyncio.get_running_loop()
    deadline = loop.time() + wait_seconds

    while True:
        await capture()
        if capture.error is not None or satisfied():
            return
        remaining = deadline - loop.time()
        if remaining <= 0:
            return
        await asyncio.sleep(min(poll_seconds, remaining))
