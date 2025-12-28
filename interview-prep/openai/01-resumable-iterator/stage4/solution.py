"""
Resumable Iterator - Stage 4

2D and 3D nested list iterators.

Design Rationale:
- Track position in each dimension
- State includes all dimension indices
- Flatten nested structures during iteration
"""

from typing import Any


class Resumable2DIterator:
    """Iterates over 2D nested list, flattening the iteration."""

    def __init__(self, data: list[list[Any]]):
        self._data = data
        self._outer_index = 0
        self._inner_index = 0
        self._skip_empty_rows()

    def _skip_empty_rows(self):
        """Skip empty inner lists."""
        while self._outer_index < len(self._data) and not self._data[self._outer_index]:
            self._outer_index += 1
            self._inner_index = 0

    def __iter__(self):
        return self

    def __next__(self) -> Any:
        if self._outer_index >= len(self._data):
            raise StopIteration

        item = self._data[self._outer_index][self._inner_index]
        self._inner_index += 1

        if self._inner_index >= len(self._data[self._outer_index]):
            self._outer_index += 1
            self._inner_index = 0
            self._skip_empty_rows()

        return item

    def get_state(self) -> dict:
        return {
            "outer_index": self._outer_index,
            "inner_index": self._inner_index
        }

    def set_state(self, state: dict) -> None:
        self._outer_index = state["outer_index"]
        self._inner_index = state["inner_index"]


class Resumable3DIterator:
    """Iterates over 3D nested list, flattening the iteration."""

    def __init__(self, data: list[list[list[Any]]]):
        self._data = data
        self._i = 0  # outermost
        self._j = 0  # middle
        self._k = 0  # innermost
        self._advance_to_valid()

    def _advance_to_valid(self):
        """Advance indices to next valid position."""
        while self._i < len(self._data):
            if self._j >= len(self._data[self._i]):
                self._i += 1
                self._j = 0
                self._k = 0
                continue
            if self._k >= len(self._data[self._i][self._j]):
                self._j += 1
                self._k = 0
                continue
            # Found valid position
            break

    def __iter__(self):
        return self

    def __next__(self) -> Any:
        if self._i >= len(self._data):
            raise StopIteration

        item = self._data[self._i][self._j][self._k]
        self._k += 1
        self._advance_to_valid()
        return item

    def get_state(self) -> dict:
        return {"i": self._i, "j": self._j, "k": self._k}

    def set_state(self, state: dict) -> None:
        self._i = state["i"]
        self._j = state["j"]
        self._k = state["k"]
