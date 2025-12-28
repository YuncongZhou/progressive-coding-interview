"""
Versioned KV Store - Stage 3

Timestamp-based retrieval.

Design Rationale:
- Store (version, value, timestamp) tuples
- get_at_timestamp returns value that was current at given time
- Binary search could optimize, but linear is simpler for now
"""

import threading
from typing import Any


class TimestampVersionedKVStore:
    """KV store with timestamp-based retrieval."""

    def __init__(self):
        # {key: [(version, value, timestamp), ...]}
        self._store: dict[str, list[tuple[int, str, int]]] = {}
        self._lock = threading.Lock()

    def put(self, key: str, value: str, timestamp: int) -> int:
        """Stores value at timestamp, returns version."""
        with self._lock:
            if key not in self._store:
                self._store[key] = []
            version = len(self._store[key]) + 1
            self._store[key].append((version, value, timestamp))
            return version

    def get(self, key: str) -> tuple[str, int] | None:
        """Returns latest (value, version)."""
        with self._lock:
            if key not in self._store or not self._store[key]:
                return None
            version, value, _ = self._store[key][-1]
            return (value, version)

    def get_version(self, key: str, version: int) -> str | None:
        """Returns value at specific version."""
        with self._lock:
            if key not in self._store:
                return None
            for v, val, _ in self._store[key]:
                if v == version:
                    return val
            return None

    def get_at_timestamp(self, key: str, timestamp: int) -> str | None:
        """
        Returns value that was current at the given timestamp.

        Example: put("key", "v1", 10), put("key", "v2", 20)
        get_at_timestamp("key", 15) returns "v1"
        get_at_timestamp("key", 25) returns "v2"
        get_at_timestamp("key", 5) returns None
        """
        with self._lock:
            if key not in self._store:
                return None

            # Find the latest entry at or before timestamp
            result = None
            for _, value, ts in self._store[key]:
                if ts <= timestamp:
                    result = value
                else:
                    break
            return result
