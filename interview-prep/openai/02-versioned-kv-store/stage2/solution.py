"""
Versioned KV Store - Stage 2

Thread-safe version.

Design Rationale:
- Use threading.Lock for thread safety
- Lock protects put operations to ensure unique versions
- Fine-grained locking per key would be more scalable but adds complexity
"""

import threading
from typing import Any


class ThreadSafeVersionedKVStore:
    """Thread-safe key-value store with version tracking."""

    def __init__(self):
        self._store: dict[str, list[tuple[int, str]]] = {}
        self._lock = threading.Lock()

    def put(self, key: str, value: str) -> int:
        """Stores value and returns version number (thread-safe)."""
        with self._lock:
            if key not in self._store:
                self._store[key] = []
            version = len(self._store[key]) + 1
            self._store[key].append((version, value))
            return version

    def get(self, key: str) -> tuple[str, int] | None:
        """Returns (value, version) or None."""
        with self._lock:
            if key not in self._store or not self._store[key]:
                return None
            version, value = self._store[key][-1]
            return (value, version)

    def get_version(self, key: str, version: int) -> str | None:
        """Returns value at specific version."""
        with self._lock:
            if key not in self._store:
                return None
            for v, val in self._store[key]:
                if v == version:
                    return val
            return None
