"""
Tests for In-Memory Database Stage 3

Stage 3 adds TTL (Time-To-Live) with explicit timestamps:
- set_at, set_at_with_ttl
- get_at, delete_at
- scan_at, scan_by_prefix_at
"""
import pytest
from solution import InMemoryDB


class TestInMemoryDBStage1:
    """Regression tests for Stage 1 functionality."""

    def test_set_and_get_single_field(self):
        db = InMemoryDB()
        db.set("user1", "name", "Alice")
        assert db.get("user1", "name") == "Alice"

    def test_delete_existing_field_returns_true(self):
        db = InMemoryDB()
        db.set("user1", "name", "Alice")
        assert db.delete("user1", "name") is True


class TestInMemoryDBStage2:
    """Regression tests for Stage 2 functionality."""

    def test_scan_returns_all_fields_sorted(self):
        db = InMemoryDB()
        db.set("user1", "zebra", "z_value")
        db.set("user1", "apple", "a_value")
        result = db.scan("user1")
        assert result == [("apple", "a_value"), ("zebra", "z_value")]

    def test_scan_by_prefix_filters_correctly(self):
        db = InMemoryDB()
        db.set("user1", "name", "Alice")
        db.set("user1", "nickname", "Ally")
        db.set("user1", "email", "alice@example.com")
        result = db.scan_by_prefix("user1", "n")
        assert result == [("name", "Alice"), ("nickname", "Ally")]


class TestInMemoryDBStage3:
    """Test suite for Stage 3 TTL functionality."""

    def test_set_at_and_get_at_basic(self):
        """Basic set_at and get_at operations."""
        db = InMemoryDB()
        db.set_at("user1", "name", "Alice", timestamp=10)
        assert db.get_at("user1", "name", timestamp=10) == "Alice"
        assert db.get_at("user1", "name", timestamp=100) == "Alice"

    def test_field_expires_after_ttl(self):
        """Field expires after TTL."""
        db = InMemoryDB()
        db.set_at_with_ttl("user1", "session", "abc123", timestamp=10, ttl=5)
        # Accessible before expiration (timestamp + ttl = 15)
        assert db.get_at("user1", "session", timestamp=10) == "abc123"
        assert db.get_at("user1", "session", timestamp=14) == "abc123"
        # Expired at exactly timestamp + ttl
        assert db.get_at("user1", "session", timestamp=15) is None
        assert db.get_at("user1", "session", timestamp=20) is None

    def test_field_accessible_before_expiration(self):
        """Field is accessible before expiration."""
        db = InMemoryDB()
        db.set_at_with_ttl("user1", "token", "xyz", timestamp=100, ttl=50)
        assert db.get_at("user1", "token", timestamp=100) == "xyz"
        assert db.get_at("user1", "token", timestamp=149) == "xyz"
        assert db.get_at("user1", "token", timestamp=150) is None

    def test_set_without_ttl_never_expires(self):
        """Set without TTL never expires."""
        db = InMemoryDB()
        db.set_at("user1", "permanent", "data", timestamp=10)
        assert db.get_at("user1", "permanent", timestamp=10) == "data"
        assert db.get_at("user1", "permanent", timestamp=10000000) == "data"

    def test_overwriting_resets_ttl(self):
        """Overwriting a field resets/removes TTL."""
        db = InMemoryDB()
        db.set_at_with_ttl("user1", "field", "v1", timestamp=10, ttl=5)
        # Would expire at 15
        assert db.get_at("user1", "field", timestamp=14) == "v1"

        # Overwrite with no TTL
        db.set_at("user1", "field", "v2", timestamp=12)
        # Now it should never expire
        assert db.get_at("user1", "field", timestamp=20) == "v2"
        assert db.get_at("user1", "field", timestamp=1000) == "v2"

    def test_overwriting_with_new_ttl(self):
        """Overwriting with new TTL uses the new expiration."""
        db = InMemoryDB()
        db.set_at_with_ttl("user1", "field", "v1", timestamp=10, ttl=5)
        # Would expire at 15

        # Overwrite with new TTL at timestamp 12
        db.set_at_with_ttl("user1", "field", "v2", timestamp=12, ttl=10)
        # New expiration is at 22

        assert db.get_at("user1", "field", timestamp=15) == "v2"  # Old expiration passed
        assert db.get_at("user1", "field", timestamp=21) == "v2"
        assert db.get_at("user1", "field", timestamp=22) is None

    def test_scan_at_excludes_expired_fields(self):
        """Scan excludes expired fields."""
        db = InMemoryDB()
        db.set_at_with_ttl("user1", "temp1", "a", timestamp=10, ttl=5)  # expires at 15
        db.set_at_with_ttl("user1", "temp2", "b", timestamp=10, ttl=10)  # expires at 20
        db.set_at("user1", "perm", "c", timestamp=10)  # never expires

        # At timestamp 12, all fields are valid
        result = db.scan_at("user1", timestamp=12)
        assert result == [("perm", "c"), ("temp1", "a"), ("temp2", "b")]

        # At timestamp 16, temp1 is expired
        result = db.scan_at("user1", timestamp=16)
        assert result == [("perm", "c"), ("temp2", "b")]

        # At timestamp 25, only perm remains
        result = db.scan_at("user1", timestamp=25)
        assert result == [("perm", "c")]

    def test_scan_by_prefix_at_excludes_expired(self):
        """Scan by prefix excludes expired fields."""
        db = InMemoryDB()
        db.set_at_with_ttl("user1", "name", "Alice", timestamp=10, ttl=5)
        db.set_at_with_ttl("user1", "nickname", "Ally", timestamp=10, ttl=20)
        db.set_at("user1", "email", "a@b.com", timestamp=10)

        # At timestamp 12, both name fields valid
        result = db.scan_by_prefix_at("user1", "n", timestamp=12)
        assert result == [("name", "Alice"), ("nickname", "Ally")]

        # At timestamp 16, name expired
        result = db.scan_by_prefix_at("user1", "n", timestamp=16)
        assert result == [("nickname", "Ally")]

    def test_delete_at_works_correctly(self):
        """Delete at timestamp works correctly."""
        db = InMemoryDB()
        db.set_at("user1", "name", "Alice", timestamp=10)
        assert db.get_at("user1", "name", timestamp=15) == "Alice"

        assert db.delete_at("user1", "name", timestamp=20) is True
        assert db.get_at("user1", "name", timestamp=25) is None

    def test_delete_at_nonexistent_returns_false(self):
        """Delete at returns False for non-existent field."""
        db = InMemoryDB()
        assert db.delete_at("user1", "nonexistent", timestamp=10) is False

    def test_delete_at_expired_field_returns_false(self):
        """Delete at returns False for already expired field."""
        db = InMemoryDB()
        db.set_at_with_ttl("user1", "temp", "val", timestamp=10, ttl=5)
        # Expired at timestamp 15
        assert db.delete_at("user1", "temp", timestamp=20) is False

    def test_get_at_nonexistent_key_returns_none(self):
        """Get at returns None for non-existent key."""
        db = InMemoryDB()
        assert db.get_at("nonexistent", "field", timestamp=10) is None

    def test_scan_at_nonexistent_key_returns_empty(self):
        """Scan at returns empty list for non-existent key."""
        db = InMemoryDB()
        assert db.scan_at("nonexistent", timestamp=10) == []

    def test_backward_compatibility_with_stage1_methods(self):
        """Original set/get/delete methods still work."""
        db = InMemoryDB()
        db.set("user1", "name", "Alice")
        assert db.get("user1", "name") == "Alice"
        assert db.delete("user1", "name") is True
        assert db.get("user1", "name") is None

    def test_zero_ttl_expires_immediately(self):
        """TTL of 0 means expires immediately at the set timestamp."""
        db = InMemoryDB()
        db.set_at_with_ttl("user1", "instant", "val", timestamp=10, ttl=0)
        # Expires at timestamp 10, so not accessible at 10 or after
        assert db.get_at("user1", "instant", timestamp=10) is None
        assert db.get_at("user1", "instant", timestamp=9) == "val"
