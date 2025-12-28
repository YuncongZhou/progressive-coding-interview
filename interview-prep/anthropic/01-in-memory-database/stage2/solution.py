"""
In-Memory Database - Stage 2

A simplified in-memory database with scanning capabilities.

Design Rationale:
- Using nested dict {key: {field: value}} for O(1) access on basic operations
- Scan operations sort at query time - O(n log n) per scan
- Prefix matching uses simple string startswith check
- Could optimize with sorted data structures if scans become the bottleneck
"""


class InMemoryDB:
    """
    A simplified in-memory database supporting key-field-value storage
    with scanning capabilities.

    Each key maps to a record containing multiple field-value pairs.
    """

    def __init__(self):
        """Initialize an empty database."""
        self._data: dict[str, dict[str, str]] = {}

    def set(self, key: str, field: str, value: str) -> None:
        """
        Sets the field of the record with the given key.

        Args:
            key: The record key
            field: The field name within the record
            value: The value to store
        """
        if key not in self._data:
            self._data[key] = {}
        self._data[key][field] = value

    def get(self, key: str, field: str) -> str | None:
        """
        Returns the value of the field in the record with the given key.

        Args:
            key: The record key
            field: The field name within the record

        Returns:
            The value if found, None otherwise
        """
        if key not in self._data:
            return None
        return self._data[key].get(field)

    def delete(self, key: str, field: str) -> bool:
        """
        Removes the field from the record.

        Args:
            key: The record key
            field: The field name to delete

        Returns:
            True if the field was deleted, False if not found
        """
        if key not in self._data:
            return False
        if field not in self._data[key]:
            return False
        del self._data[key][field]
        return True

    def scan(self, key: str) -> list[tuple[str, str]]:
        """
        Returns all field-value pairs for the key, sorted alphabetically by field name.

        Args:
            key: The record key to scan

        Returns:
            List of (field, value) tuples sorted by field name, or empty list if key doesn't exist
        """
        if key not in self._data:
            return []
        return sorted(self._data[key].items(), key=lambda x: x[0])

    def scan_by_prefix(self, key: str, prefix: str) -> list[tuple[str, str]]:
        """
        Returns field-value pairs where field starts with prefix,
        sorted alphabetically by field name.

        Args:
            key: The record key to scan
            prefix: The prefix to filter fields by

        Returns:
            List of (field, value) tuples for matching fields, sorted by field name,
            or empty list if no matches
        """
        if key not in self._data:
            return []
        matches = [
            (field, value)
            for field, value in self._data[key].items()
            if field.startswith(prefix)
        ]
        return sorted(matches, key=lambda x: x[0])
