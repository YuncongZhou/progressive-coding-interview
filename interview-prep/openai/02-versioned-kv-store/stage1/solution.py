"""
Versioned Key-Value Store - Stage 1

A KV store that tracks version history.

Design Rationale:
- Each key maintains a list of (version, value) pairs
- Version numbers are per-key, starting at 1
- get() returns latest, get_version() returns specific version
"""


class VersionedKVStore:
    """Key-value store with version tracking."""

    def __init__(self):
        # {key: [(version, value), ...]}
        self._store: dict[str, list[tuple[int, str]]] = {}

    def put(self, key: str, value: str) -> int:
        """Stores value and returns the version number (starts at 1, increments)."""
        if key not in self._store:
            self._store[key] = []
        version = len(self._store[key]) + 1
        self._store[key].append((version, value))
        return version

    def get(self, key: str) -> tuple[str, int] | None:
        """Returns (value, version) or None if key doesn't exist."""
        if key not in self._store or not self._store[key]:
            return None
        version, value = self._store[key][-1]
        return (value, version)

    def get_version(self, key: str, version: int) -> str | None:
        """Returns value at specific version or None."""
        if key not in self._store:
            return None
        for v, val in self._store[key]:
            if v == version:
                return val
        return None
