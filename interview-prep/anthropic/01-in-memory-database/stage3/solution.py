"""
In-Memory Database - Stage 3

A simplified in-memory database with TTL (Time-To-Live) support.

Design Rationale:
- Refactored storage to {key: {field: {"value": str, "expires_at": int | None}}}
- expires_at = None means no expiration (infinite TTL)
- Original methods (set, get, delete) delegate to timestamp-aware versions
- Expiration check: field is expired if current_timestamp >= expires_at
- Lazy expiration: we don't actively clean up expired entries, just filter on read
"""

from typing import TypedDict


class FieldData(TypedDict):
    """Type for field data with optional expiration."""
    value: str
    expires_at: int | None


class InMemoryDB:
    """
    A simplified in-memory database supporting key-field-value storage
    with TTL and scanning capabilities.
    """

    def __init__(self):
        """Initialize an empty database."""
        self._data: dict[str, dict[str, FieldData]] = {}

    # ========== Stage 1 Methods (backward compatible) ==========

    def set(self, key: str, field: str, value: str) -> None:
        """Sets the field of the record with the given key (no TTL)."""
        self.set_at(key, field, value, timestamp=0)

    def get(self, key: str, field: str) -> str | None:
        """Returns the value of the field (assumes current time is 0)."""
        return self.get_at(key, field, timestamp=0)

    def delete(self, key: str, field: str) -> bool:
        """Removes the field from the record."""
        return self.delete_at(key, field, timestamp=0)

    # ========== Stage 2 Methods (backward compatible) ==========

    def scan(self, key: str) -> list[tuple[str, str]]:
        """Returns all field-value pairs sorted alphabetically by field name."""
        return self.scan_at(key, timestamp=0)

    def scan_by_prefix(self, key: str, prefix: str) -> list[tuple[str, str]]:
        """Returns field-value pairs where field starts with prefix."""
        return self.scan_by_prefix_at(key, prefix, timestamp=0)

    # ========== Stage 3 Methods (timestamp-aware) ==========

    def set_at(self, key: str, field: str, value: str, timestamp: int) -> None:
        """
        Sets the field at the given timestamp (no expiration).

        Args:
            key: The record key
            field: The field name
            value: The value to store
            timestamp: The timestamp when this operation occurs
        """
        if key not in self._data:
            self._data[key] = {}
        self._data[key][field] = {"value": value, "expires_at": None}

    def set_at_with_ttl(
        self, key: str, field: str, value: str, timestamp: int, ttl: int
    ) -> None:
        """
        Sets the field with expiration at timestamp + ttl.

        Args:
            key: The record key
            field: The field name
            value: The value to store
            timestamp: The timestamp when this operation occurs
            ttl: Time-to-live in timestamp units
        """
        if key not in self._data:
            self._data[key] = {}
        self._data[key][field] = {"value": value, "expires_at": timestamp + ttl}

    def get_at(self, key: str, field: str, timestamp: int) -> str | None:
        """
        Gets value if it exists and hasn't expired at the given timestamp.

        Args:
            key: The record key
            field: The field name
            timestamp: The timestamp to check against

        Returns:
            The value if found and not expired, None otherwise
        """
        if key not in self._data:
            return None
        if field not in self._data[key]:
            return None

        field_data = self._data[key][field]
        if self._is_expired(field_data, timestamp):
            return None
        return field_data["value"]

    def delete_at(self, key: str, field: str, timestamp: int) -> bool:
        """
        Deletes the field at the given timestamp.

        Only succeeds if the field exists and is not expired.

        Args:
            key: The record key
            field: The field name
            timestamp: The timestamp when this operation occurs

        Returns:
            True if deleted, False if not found or already expired
        """
        if key not in self._data:
            return False
        if field not in self._data[key]:
            return False

        field_data = self._data[key][field]
        if self._is_expired(field_data, timestamp):
            return False

        del self._data[key][field]
        return True

    def scan_at(self, key: str, timestamp: int) -> list[tuple[str, str]]:
        """
        Scans only non-expired fields at the given timestamp.

        Args:
            key: The record key
            timestamp: The timestamp to check against

        Returns:
            List of (field, value) tuples sorted by field name
        """
        if key not in self._data:
            return []

        result = [
            (field, data["value"])
            for field, data in self._data[key].items()
            if not self._is_expired(data, timestamp)
        ]
        return sorted(result, key=lambda x: x[0])

    def scan_by_prefix_at(
        self, key: str, prefix: str, timestamp: int
    ) -> list[tuple[str, str]]:
        """
        Prefix scan with TTL awareness.

        Args:
            key: The record key
            prefix: The prefix to filter by
            timestamp: The timestamp to check against

        Returns:
            List of (field, value) tuples sorted by field name
        """
        if key not in self._data:
            return []

        result = [
            (field, data["value"])
            for field, data in self._data[key].items()
            if field.startswith(prefix) and not self._is_expired(data, timestamp)
        ]
        return sorted(result, key=lambda x: x[0])

    def _is_expired(self, field_data: FieldData, timestamp: int) -> bool:
        """Check if field data is expired at the given timestamp."""
        expires_at = field_data["expires_at"]
        if expires_at is None:
            return False
        return timestamp >= expires_at
