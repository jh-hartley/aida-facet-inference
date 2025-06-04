"""Cache manager for similarity search results."""

import asyncio
from collections import OrderedDict
from typing import Any, Callable, TypeVar

from src.core.similarity_search.models import SimilaritySearchResponse

T = TypeVar("T")


class LRUCache:
    """Thread-safe LRU cache with fixed size."""

    def __init__(self, maxsize: int = 1000) -> None:
        self._cache: OrderedDict[str, SimilaritySearchResponse] = OrderedDict()
        self._maxsize = maxsize
        self._lock = asyncio.Lock()

    def _move_to_end(self, key: str) -> None:
        self._cache.move_to_end(key)

    def _remove_oldest(self) -> None:
        self._cache.popitem(last=False)

    async def get(self, key: str) -> SimilaritySearchResponse | None:
        async with self._lock:
            if key in self._cache:
                self._move_to_end(key)
                return self._cache[key]
            return None

    async def put(self, key: str, value: SimilaritySearchResponse) -> None:
        """
        Add an item to the cache.

        Args:
            key: The key to store
            value: The value to store
        """
        async with self._lock:
            if key in self._cache:
                self._cache.pop(key)
            elif len(self._cache) >= self._maxsize:
                self._remove_oldest()
            self._cache[key] = value

    def clear(self) -> None:
        self._cache.clear()


class SimilaritySearchCache:
    """Thread-safe cache for similarity search results."""

    def __init__(self, maxsize: int = 1000) -> None:
        self._cache = LRUCache(maxsize)

    async def get_or_fetch(
        self,
        product_key: str,
        fetch_func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> SimilaritySearchResponse:
        cached_result = await self._cache.get(product_key)
        if cached_result is not None:
            return cached_result

        result = await fetch_func(*args, **kwargs)
        if not isinstance(result, SimilaritySearchResponse):
            raise TypeError(
                f"Expected SimilaritySearchResponse, got {type(result)}"
            )
        await self._cache.put(product_key, result)
        return result

    def clear(self) -> None:
        """Clear the cache."""
        self._cache.clear()


SIMILARITY_CACHE = SimilaritySearchCache()
