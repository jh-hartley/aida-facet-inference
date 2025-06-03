from asyncio import Semaphore, gather
from typing import Awaitable, Callable, Sequence, TypeVar

T = TypeVar("T")
R = TypeVar("R")


class AsyncConcurrencyManager:
    """Manages concurrent execution of async operations with rate limiting."""

    def __init__(self, max_concurrent: int = 32):
        self.semaphore = Semaphore(max_concurrent)

    async def execute(
        self, func: Callable[[T], Awaitable[R]], items: Sequence[T]
    ) -> Sequence[R]:
        """
        Execute a function concurrently on a sequence of items.
        """

        async def limited_execute(item: T) -> R:
            async with self.semaphore:
                return await func(item)

        tasks = [limited_execute(item) for item in items]
        return await gather(*tasks)
