"""
Resumable Iterator - Stage 3

Async version using coroutines.

Design Rationale:
- Same state management as sync version
- Uses __aiter__ and __anext__ for async iteration
- State methods are also async for consistency
"""

from typing import Any


class AsyncResumableIterator:
    """Async version of resumable iterator."""

    def __init__(self, data: list[Any]):
        self._data = data
        self._index = 0

    def __aiter__(self):
        return self

    async def __anext__(self) -> Any:
        if self._index >= len(self._data):
            raise StopAsyncIteration
        item = self._data[self._index]
        self._index += 1
        return item

    async def get_state(self) -> dict:
        return {"index": self._index}

    async def set_state(self, state: dict) -> None:
        self._index = state["index"]
