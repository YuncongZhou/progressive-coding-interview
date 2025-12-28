"""
Versioned KV Store - Stage 4

File persistence with custom serialization (no JSON library).

Design Rationale:
- Custom format: key|version|value|timestamp per line
- Escape special characters (|, newline) in values
- Load reconstructs full history
"""

import threading
from typing import Any


class PersistentVersionedKVStore:
    """KV store with file persistence using custom serialization."""

    DELIMITER = "|"
    ESCAPE = "\\"

    def __init__(self):
        self._store: dict[str, list[tuple[int, str, int]]] = {}
        self._lock = threading.Lock()

    def put(self, key: str, value: str, timestamp: int) -> int:
        with self._lock:
            if key not in self._store:
                self._store[key] = []
            version = len(self._store[key]) + 1
            self._store[key].append((version, value, timestamp))
            return version

    def get(self, key: str) -> tuple[str, int] | None:
        with self._lock:
            if key not in self._store or not self._store[key]:
                return None
            version, value, _ = self._store[key][-1]
            return (value, version)

    def get_version(self, key: str, version: int) -> str | None:
        with self._lock:
            if key not in self._store:
                return None
            for v, val, _ in self._store[key]:
                if v == version:
                    return val
            return None

    def get_at_timestamp(self, key: str, timestamp: int) -> str | None:
        with self._lock:
            if key not in self._store:
                return None
            result = None
            for _, value, ts in self._store[key]:
                if ts <= timestamp:
                    result = value
                else:
                    break
            return result

    def _escape(self, s: str) -> str:
        """Escape special characters."""
        result = s.replace(self.ESCAPE, self.ESCAPE + self.ESCAPE)
        result = result.replace(self.DELIMITER, self.ESCAPE + self.DELIMITER)
        result = result.replace("\n", self.ESCAPE + "n")
        return result

    def _unescape(self, s: str) -> str:
        """Unescape special characters."""
        result = []
        i = 0
        while i < len(s):
            if s[i] == self.ESCAPE and i + 1 < len(s):
                next_char = s[i + 1]
                if next_char == self.ESCAPE:
                    result.append(self.ESCAPE)
                elif next_char == self.DELIMITER:
                    result.append(self.DELIMITER)
                elif next_char == "n":
                    result.append("\n")
                else:
                    result.append(s[i])
                    i -= 1
                i += 2
            else:
                result.append(s[i])
                i += 1
        return "".join(result)

    def save_to_file(self, filepath: str) -> None:
        """Persists store to file using custom serialization."""
        with self._lock:
            with open(filepath, "w") as f:
                for key, entries in self._store.items():
                    for version, value, timestamp in entries:
                        escaped_key = self._escape(key)
                        escaped_value = self._escape(value)
                        line = f"{escaped_key}{self.DELIMITER}{version}{self.DELIMITER}{escaped_value}{self.DELIMITER}{timestamp}\n"
                        f.write(line)

    def load_from_file(self, filepath: str) -> None:
        """Loads store from file."""
        with self._lock:
            self._store.clear()
            with open(filepath, "r") as f:
                for line in f:
                    line = line.rstrip("\n")
                    if not line:
                        continue
                    # Parse: key|version|value|timestamp
                    parts = self._split_escaped(line)
                    if len(parts) != 4:
                        continue
                    key = self._unescape(parts[0])
                    version = int(parts[1])
                    value = self._unescape(parts[2])
                    timestamp = int(parts[3])

                    if key not in self._store:
                        self._store[key] = []
                    self._store[key].append((version, value, timestamp))

    def _split_escaped(self, s: str) -> list[str]:
        """Split by delimiter, respecting escapes."""
        parts = []
        current = []
        i = 0
        while i < len(s):
            if s[i] == self.ESCAPE and i + 1 < len(s):
                current.append(s[i])
                current.append(s[i + 1])
                i += 2
            elif s[i] == self.DELIMITER:
                parts.append("".join(current))
                current = []
                i += 1
            else:
                current.append(s[i])
                i += 1
        parts.append("".join(current))
        return parts
