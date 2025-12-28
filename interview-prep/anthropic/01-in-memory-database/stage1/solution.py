"""
In-Memory Database - Stage 1

A simplified in-memory database supporting basic key-field-value operations.

Design Rationale:
- Using nested dict {key: {field: value}} for O(1) access on all operations
- Simple and clean design that models the hierarchical structure naturally
- No premature optimization - focusing on correctness first
"""


class InMemoryDB:
    """
    A simplified in-memory database supporting key-field-value storage.

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
