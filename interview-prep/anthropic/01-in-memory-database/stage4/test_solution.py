"""
Tests for In-Memory Database Stage 4

Stage 4 adds backup/compression with storage quotas:
- backup, restore (with TTL recalculation)
- set_user_quota, get_user_usage, set_with_user
"""
import pytest
from solution import InMemoryDB


class TestInMemoryDBStage1To3:
    """Regression tests for Stages 1-3 functionality."""

    def test_basic_set_get_delete(self):
        db = InMemoryDB()
        db.set("user1", "name", "Alice")
        assert db.get("user1", "name") == "Alice"
        assert db.delete("user1", "name") is True

    def test_scan_with_prefix(self):
        db = InMemoryDB()
        db.set("user1", "name", "Alice")
        db.set("user1", "nickname", "Ally")
        result = db.scan_by_prefix("user1", "n")
        assert result == [("name", "Alice"), ("nickname", "Ally")]

    def test_ttl_expiration(self):
        db = InMemoryDB()
        db.set_at_with_ttl("user1", "temp", "val", timestamp=10, ttl=5)
        assert db.get_at("user1", "temp", timestamp=14) == "val"
        assert db.get_at("user1", "temp", timestamp=15) is None


class TestInMemoryDBStage4Backup:
    """Test suite for Stage 4 backup/restore functionality."""

    def test_backup_creates_valid_backup_id(self):
        """Backup creates a valid backup ID."""
        db = InMemoryDB()
        db.set_at("user1", "name", "Alice", timestamp=10)
        backup_id = db.backup(timestamp=10)
        assert backup_id is not None
        assert isinstance(backup_id, str)
        assert len(backup_id) > 0

    def test_restore_brings_back_data(self):
        """Restore brings back data correctly."""
        db = InMemoryDB()
        db.set_at("user1", "name", "Alice", timestamp=10)
        db.set_at("user1", "email", "alice@example.com", timestamp=10)

        backup_id = db.backup(timestamp=10)

        # Clear the database
        db.delete_at("user1", "name", timestamp=15)
        db.delete_at("user1", "email", timestamp=15)
        assert db.get_at("user1", "name", timestamp=20) is None

        # Restore
        assert db.restore(backup_id, timestamp=20) is True
        assert db.get_at("user1", "name", timestamp=20) == "Alice"
        assert db.get_at("user1", "email", timestamp=20) == "alice@example.com"

    def test_restore_recalculates_ttls(self):
        """TTLs are recalculated on restore."""
        db = InMemoryDB()
        # Set a field with TTL at timestamp 10, expires at 20 (remaining TTL = 10)
        db.set_at_with_ttl("user1", "session", "abc", timestamp=10, ttl=10)

        # Backup at timestamp 12 (remaining TTL = 8)
        backup_id = db.backup(timestamp=12)

        # Clear and restore at timestamp 100
        db.delete_at("user1", "session", timestamp=15)
        db.restore(backup_id, timestamp=100)

        # New expiration should be 100 + 8 = 108
        assert db.get_at("user1", "session", timestamp=107) == "abc"
        assert db.get_at("user1", "session", timestamp=108) is None

    def test_backup_excludes_expired_data(self):
        """Backup only includes non-expired data."""
        db = InMemoryDB()
        db.set_at_with_ttl("user1", "temp", "val", timestamp=10, ttl=5)  # expires at 15
        db.set_at("user1", "perm", "permanent", timestamp=10)

        # Backup at timestamp 20 (temp is expired)
        backup_id = db.backup(timestamp=20)

        # Clear and restore
        db.delete_at("user1", "perm", timestamp=25)
        db.restore(backup_id, timestamp=30)

        # Only perm should be restored
        assert db.get_at("user1", "perm", timestamp=30) == "permanent"
        assert db.get_at("user1", "temp", timestamp=30) is None

    def test_restore_invalid_backup_id_returns_false(self):
        """Restore with invalid backup ID returns False."""
        db = InMemoryDB()
        assert db.restore("invalid_id", timestamp=10) is False

    def test_multiple_backups(self):
        """Multiple backups can be created and restored independently."""
        db = InMemoryDB()
        db.set_at("user1", "name", "Alice", timestamp=10)
        backup1 = db.backup(timestamp=10)

        db.set_at("user1", "name", "Bob", timestamp=20)
        backup2 = db.backup(timestamp=20)

        # Restore first backup
        db.restore(backup1, timestamp=30)
        assert db.get_at("user1", "name", timestamp=30) == "Alice"

        # Restore second backup
        db.restore(backup2, timestamp=40)
        assert db.get_at("user1", "name", timestamp=40) == "Bob"


class TestInMemoryDBStage4Quota:
    """Test suite for Stage 4 quota management."""

    def test_set_user_quota(self):
        """Set user quota works."""
        db = InMemoryDB()
        db.set_user_quota("alice", max_bytes=100)
        # Should not raise

    def test_get_user_usage_empty(self):
        """Get user usage returns 0 for user with no data."""
        db = InMemoryDB()
        assert db.get_user_usage("alice") == 0

    def test_set_with_user_tracks_usage(self):
        """Set with user tracks storage usage."""
        db = InMemoryDB()
        db.set_user_quota("alice", max_bytes=1000)

        # "key" = 3 bytes, "field" = 5 bytes, "value" = 5 bytes = 13 bytes
        result = db.set_with_user("alice", "key", "field", "value", timestamp=10)
        assert result is True
        assert db.get_user_usage("alice") == 13

    def test_quota_prevents_writes_when_exceeded(self):
        """Quota prevents writes when exceeded."""
        db = InMemoryDB()
        db.set_user_quota("alice", max_bytes=20)

        # First write: 3 + 5 + 5 = 13 bytes
        result1 = db.set_with_user("alice", "key", "field", "value", timestamp=10)
        assert result1 is True

        # Second write: 4 + 6 + 10 = 20 bytes, total would be 33
        result2 = db.set_with_user("alice", "key2", "field2", "bigvalue!!", timestamp=10)
        assert result2 is False
        assert db.get_at("key2", "field2", timestamp=10) is None

    def test_overwrite_updates_usage_correctly(self):
        """Overwriting a value updates usage correctly."""
        db = InMemoryDB()
        db.set_user_quota("alice", max_bytes=100)

        # First write: 3 + 5 + 5 = 13 bytes
        db.set_with_user("alice", "key", "field", "value", timestamp=10)
        assert db.get_user_usage("alice") == 13

        # Overwrite with longer value: 3 + 5 + 10 = 18 bytes
        result = db.set_with_user("alice", "key", "field", "longerval!", timestamp=20)
        assert result is True
        assert db.get_user_usage("alice") == 18

    def test_deleting_data_frees_quota(self):
        """Deleting data frees quota."""
        db = InMemoryDB()
        db.set_user_quota("alice", max_bytes=100)

        db.set_with_user("alice", "key", "field", "value", timestamp=10)
        assert db.get_user_usage("alice") == 13

        # Delete the field - usage should go back to 0
        db.delete_at("key", "field", timestamp=20)
        assert db.get_user_usage("alice") == 0

    def test_usage_tracking_accurate_multiple_fields(self):
        """Usage tracking is accurate with multiple fields."""
        db = InMemoryDB()
        db.set_user_quota("alice", max_bytes=1000)

        # key1:field1:val1 = 4+6+4 = 14
        db.set_with_user("alice", "key1", "field1", "val1", timestamp=10)
        # key1:field2:val2 = 4+6+4 = 14
        db.set_with_user("alice", "key1", "field2", "val2", timestamp=10)
        # key2:field1:val3 = 4+6+4 = 14
        db.set_with_user("alice", "key2", "field1", "val3", timestamp=10)

        assert db.get_user_usage("alice") == 42

    def test_set_with_user_no_quota_set(self):
        """Set with user when no quota is set should succeed (unlimited)."""
        db = InMemoryDB()
        result = db.set_with_user("alice", "key", "field", "value", timestamp=10)
        assert result is True
        assert db.get_at("key", "field", timestamp=10) == "value"

    def test_multiple_users_independent_quotas(self):
        """Multiple users have independent quotas."""
        db = InMemoryDB()
        db.set_user_quota("alice", max_bytes=20)
        db.set_user_quota("bob", max_bytes=20)

        # Alice uses 13 bytes with her own key
        db.set_with_user("alice", "key", "field", "value", timestamp=10)

        # Bob uses his own key - should still have full quota
        result = db.set_with_user("bob", "bkey", "field", "value", timestamp=10)
        assert result is True
        # bob: bkey(4) + field(5) + value(5) = 14
        assert db.get_user_usage("bob") == 14
        # alice: key(3) + field(5) + value(5) = 13
        assert db.get_user_usage("alice") == 13
