"""
Resumable Iterator - Stage 1

An iterator that can save and restore its position.

Design Rationale:
- Simple list-based iterator with index tracking
- State is just the current index
- Allows pausing iteration and resuming from saved position
"""

from typing import Any


class ResumableIterator:
    """An iterator that can save and restore its position."""

    def __init__(self, data: list[Any]):
        self._data = data
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self) -> Any:
        """Returns next item or raises StopIteration."""
        if self._index >= len(self._data):
            raise StopIteration
        item = self._data[self._index]
        self._index += 1
        return item

    def get_state(self) -> dict:
        """Returns serializable state that can restore position."""
        return {"index": self._index}

    def set_state(self, state: dict) -> None:
        """Restores position from saved state."""
        self._index = state["index"]
