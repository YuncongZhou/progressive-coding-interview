"""
In-Memory Database - Stage 4

A simplified in-memory database with backup/compression and storage quotas.

Design Rationale:
- Backups store remaining TTL (not absolute expiration) for recalculation on restore
- Simple zlib compression for backup data
- Quota tracking: sum of key + field + value byte lengths per user
- User ownership tracked separately from the data to maintain backward compatibility
"""

import json
import uuid
import zlib
from typing import TypedDict


class FieldData(TypedDict):
    """Type for field data with optional expiration."""
    value: str
    expires_at: int | None


class BackupEntry(TypedDict):
    """Type for backup entry with remaining TTL."""
    value: str
    remaining_ttl: int | None  # None means no expiration


class InMemoryDB:
    """
    A simplified in-memory database supporting key-field-value storage
    with TTL, scanning, backup/restore, and quota management.
    """

    def __init__(self):
        """Initialize an empty database."""
        self._data: dict[str, dict[str, FieldData]] = {}
        self._backups: dict[str, bytes] = {}  # backup_id -> compressed data
        self._user_quotas: dict[str, int] = {}  # user_id -> max_bytes
        # Track ownership: (key, field) -> user_id
        self._ownership: dict[tuple[str, str], str] = {}

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
        """Sets the field at the given timestamp (no expiration)."""
        if key not in self._data:
            self._data[key] = {}
        self._data[key][field] = {"value": value, "expires_at": None}

    def set_at_with_ttl(
        self, key: str, field: str, value: str, timestamp: int, ttl: int
    ) -> None:
        """Sets the field with expiration at timestamp + ttl."""
        if key not in self._data:
            self._data[key] = {}
        self._data[key][field] = {"value": value, "expires_at": timestamp + ttl}

    def get_at(self, key: str, field: str, timestamp: int) -> str | None:
        """Gets value if it exists and hasn't expired at the given timestamp."""
        if key not in self._data:
            return None
        if field not in self._data[key]:
            return None

        field_data = self._data[key][field]
        if self._is_expired(field_data, timestamp):
            return None
        return field_data["value"]

    def delete_at(self, key: str, field: str, timestamp: int) -> bool:
        """Deletes the field at the given timestamp."""
        if key not in self._data:
            return False
        if field not in self._data[key]:
            return False

        field_data = self._data[key][field]
        if self._is_expired(field_data, timestamp):
            return False

        # Update ownership tracking
        owner = self._ownership.pop((key, field), None)
        if owner:
            pass  # Ownership removed

        del self._data[key][field]
        return True

    def scan_at(self, key: str, timestamp: int) -> list[tuple[str, str]]:
        """Scans only non-expired fields at the given timestamp."""
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
        """Prefix scan with TTL awareness."""
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

    # ========== Stage 4 Methods (backup/restore and quotas) ==========

    def backup(self, timestamp: int) -> str:
        """
        Creates a compressed backup of all non-expired data.

        Stores remaining TTL (not absolute expiration) so it can be
        recalculated on restore relative to the new timestamp.

        Args:
            timestamp: The current timestamp

        Returns:
            Backup ID string
        """
        backup_data: dict[str, dict[str, BackupEntry]] = {}

        for key, fields in self._data.items():
            key_data: dict[str, BackupEntry] = {}
            for field, field_data in fields.items():
                if not self._is_expired(field_data, timestamp):
                    expires_at = field_data["expires_at"]
                    if expires_at is None:
                        remaining_ttl = None
                    else:
                        remaining_ttl = expires_at - timestamp

                    key_data[field] = {
                        "value": field_data["value"],
                        "remaining_ttl": remaining_ttl,
                    }
            if key_data:
                backup_data[key] = key_data

        # Serialize and compress
        json_data = json.dumps(backup_data)
        compressed = zlib.compress(json_data.encode("utf-8"))

        backup_id = str(uuid.uuid4())
        self._backups[backup_id] = compressed

        return backup_id

    def restore(self, backup_id: str, timestamp: int) -> bool:
        """
        Restores from backup, recalculating TTLs relative to new timestamp.

        Args:
            backup_id: The backup ID to restore from
            timestamp: The current timestamp for TTL recalculation

        Returns:
            True if restored successfully, False if backup not found
        """
        if backup_id not in self._backups:
            return False

        compressed = self._backups[backup_id]
        json_data = zlib.decompress(compressed).decode("utf-8")
        backup_data: dict[str, dict[str, BackupEntry]] = json.loads(json_data)

        # Restore data
        for key, fields in backup_data.items():
            if key not in self._data:
                self._data[key] = {}

            for field, entry in fields.items():
                remaining_ttl = entry["remaining_ttl"]
                if remaining_ttl is None:
                    expires_at = None
                else:
                    expires_at = timestamp + remaining_ttl

                self._data[key][field] = {
                    "value": entry["value"],
                    "expires_at": expires_at,
                }

        return True

    def set_user_quota(self, user_id: str, max_bytes: int) -> None:
        """
        Sets storage quota for a user.

        Args:
            user_id: The user identifier
            max_bytes: Maximum storage in bytes
        """
        self._user_quotas[user_id] = max_bytes

    def get_user_usage(self, user_id: str) -> int:
        """
        Returns current storage usage in bytes.

        Storage is calculated as sum of key + field + value byte lengths
        for all fields owned by the user.

        Args:
            user_id: The user identifier

        Returns:
            Current storage usage in bytes
        """
        total = 0
        for (key, field), owner in self._ownership.items():
            if owner == user_id:
                # Check if field still exists
                if key in self._data and field in self._data[key]:
                    value = self._data[key][field]["value"]
                    total += len(key) + len(field) + len(value)
        return total

    def set_with_user(
        self, user_id: str, key: str, field: str, value: str, timestamp: int
    ) -> bool:
        """
        Sets field if user has quota.

        Args:
            user_id: The user performing the set
            key: The record key
            field: The field name
            value: The value to store
            timestamp: The timestamp when this operation occurs

        Returns:
            True if set successfully, False if quota exceeded
        """
        new_size = len(key) + len(field) + len(value)

        # Calculate what the new usage would be
        current_usage = self.get_user_usage(user_id)

        # If overwriting an existing field owned by this user, subtract old size
        if (key, field) in self._ownership and self._ownership[(key, field)] == user_id:
            if key in self._data and field in self._data[key]:
                old_value = self._data[key][field]["value"]
                current_usage -= len(key) + len(field) + len(old_value)

        new_usage = current_usage + new_size

        # Check quota (if set)
        if user_id in self._user_quotas:
            if new_usage > self._user_quotas[user_id]:
                return False

        # Perform the set
        self.set_at(key, field, value, timestamp)
        self._ownership[(key, field)] = user_id

        return True
