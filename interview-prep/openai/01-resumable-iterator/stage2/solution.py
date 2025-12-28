"""
Resumable Iterator - Stage 2

Iterators for JSON files.

Design Rationale:
- JsonFileIterator loads JSON array from file
- MultipleJsonFileIterator tracks current file and position within file
- Empty files are skipped gracefully
"""

import json
from typing import Any


class ResumableIterator:
    """Base resumable iterator."""

    def __init__(self, data: list[Any]):
        self._data = data
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self) -> Any:
        if self._index >= len(self._data):
            raise StopIteration
        item = self._data[self._index]
        self._index += 1
        return item

    def get_state(self) -> dict:
        return {"index": self._index}

    def set_state(self, state: dict) -> None:
        self._index = state["index"]


class JsonFileIterator(ResumableIterator):
    """Iterates over records in a JSON file."""

    def __init__(self, filepath: str):
        with open(filepath, "r") as f:
            data = json.load(f)
        super().__init__(data)
        self._filepath = filepath

    def get_state(self) -> dict:
        return {"filepath": self._filepath, "index": self._index}

    def set_state(self, state: dict) -> None:
        self._index = state["index"]


class MultipleJsonFileIterator:
    """Iterates over records across multiple JSON files."""

    def __init__(self, filepaths: list[str]):
        self._filepaths = filepaths
        self._file_index = 0
        self._record_index = 0
        self._current_data: list[Any] = []
        self._load_current_file()

    def _load_current_file(self) -> None:
        """Load current file, skipping empty files."""
        while self._file_index < len(self._filepaths):
            filepath = self._filepaths[self._file_index]
            with open(filepath, "r") as f:
                self._current_data = json.load(f)
            if self._current_data:
                break
            self._file_index += 1
            self._record_index = 0

    def __iter__(self):
        return self

    def __next__(self) -> Any:
        while True:
            if self._record_index < len(self._current_data):
                item = self._current_data[self._record_index]
                self._record_index += 1
                return item

            # Move to next file
            self._file_index += 1
            self._record_index = 0

            if self._file_index >= len(self._filepaths):
                raise StopIteration

            self._load_current_file()

            if self._file_index >= len(self._filepaths):
                raise StopIteration

    def get_state(self) -> dict:
        return {
            "file_index": self._file_index,
            "record_index": self._record_index
        }

    def set_state(self, state: dict) -> None:
        self._file_index = state["file_index"]
        self._record_index = state["record_index"]
        if self._file_index < len(self._filepaths):
            with open(self._filepaths[self._file_index], "r") as f:
                self._current_data = json.load(f)
