"""
Tests for In-Memory Database Stage 2

Stage 2 adds scanning capabilities:
- SCAN <key> - returns all field-value pairs sorted alphabetically by field
- SCAN_BY_PREFIX <key> <prefix> - returns field-value pairs where field starts with prefix
"""
import pytest
from solution import InMemoryDB


class TestInMemoryDBStage1:
    """Test suite for Stage 1 functionality (regression tests)."""

    def test_set_and_get_single_field(self):
        db = InMemoryDB()
        db.set("user1", "name", "Alice")
        assert db.get("user1", "name") == "Alice"

    def test_set_multiple_fields_same_key(self):
        db = InMemoryDB()
        db.set("user1", "name", "Alice")
        db.set("user1", "email", "alice@example.com")
        assert db.get("user1", "name") == "Alice"
        assert db.get("user1", "email") == "alice@example.com"

    def test_get_nonexistent_key_returns_none(self):
        db = InMemoryDB()
        assert db.get("nonexistent", "field") is None

    def test_delete_existing_field_returns_true(self):
        db = InMemoryDB()
        db.set("user1", "name", "Alice")
        assert db.delete("user1", "name") is True

    def test_delete_nonexistent_field_returns_false(self):
        db = InMemoryDB()
        assert db.delete("nonexistent", "field") is False


class TestInMemoryDBStage2:
    """Test suite for Stage 2 scanning functionality."""

    def test_scan_returns_all_fields_sorted(self):
        """Scan returns all fields sorted alphabetically."""
        db = InMemoryDB()
        db.set("user1", "zebra", "z_value")
        db.set("user1", "apple", "a_value")
        db.set("user1", "mango", "m_value")

        result = db.scan("user1")
        assert result == [
            ("apple", "a_value"),
            ("mango", "m_value"),
            ("zebra", "z_value"),
        ]

    def test_scan_nonexistent_key_returns_empty_list(self):
        """Scan on non-existent key returns empty list."""
        db = InMemoryDB()
        assert db.scan("nonexistent") == []

    def test_scan_empty_record_returns_empty_list(self):
        """Scan on key with all fields deleted returns empty list."""
        db = InMemoryDB()
        db.set("user1", "name", "Alice")
        db.delete("user1", "name")
        assert db.scan("user1") == []

    def test_scan_by_prefix_filters_correctly(self):
        """Scan by prefix filters correctly."""
        db = InMemoryDB()
        db.set("user1", "name", "Alice")
        db.set("user1", "nickname", "Ally")
        db.set("user1", "email", "alice@example.com")
        db.set("user1", "age", "30")

        result = db.scan_by_prefix("user1", "n")
        assert result == [("name", "Alice"), ("nickname", "Ally")]

    def test_scan_by_prefix_no_matches_returns_empty_list(self):
        """Scan by prefix with no matches returns empty list."""
        db = InMemoryDB()
        db.set("user1", "name", "Alice")
        db.set("user1", "email", "alice@example.com")

        result = db.scan_by_prefix("user1", "z")
        assert result == []

    def test_scan_by_prefix_is_case_sensitive(self):
        """Scan by prefix is case-sensitive."""
        db = InMemoryDB()
        db.set("user1", "Name", "Alice")
        db.set("user1", "name", "alice_lower")
        db.set("user1", "nickname", "Ally")

        result = db.scan_by_prefix("user1", "n")
        assert result == [("name", "alice_lower"), ("nickname", "Ally")]

        result_upper = db.scan_by_prefix("user1", "N")
        assert result_upper == [("Name", "Alice")]

    def test_scan_by_prefix_nonexistent_key(self):
        """Scan by prefix on non-existent key returns empty list."""
        db = InMemoryDB()
        assert db.scan_by_prefix("nonexistent", "a") == []

    def test_scan_by_prefix_empty_prefix_returns_all(self):
        """Empty prefix returns all fields (matches everything)."""
        db = InMemoryDB()
        db.set("user1", "zebra", "z_value")
        db.set("user1", "apple", "a_value")

        result = db.scan_by_prefix("user1", "")
        assert result == [("apple", "a_value"), ("zebra", "z_value")]

    def test_scan_by_prefix_full_field_name(self):
        """Prefix can be the full field name."""
        db = InMemoryDB()
        db.set("user1", "name", "Alice")
        db.set("user1", "names", "Multiple")

        result = db.scan_by_prefix("user1", "name")
        assert result == [("name", "Alice"), ("names", "Multiple")]

    def test_scan_single_field(self):
        """Scan with single field."""
        db = InMemoryDB()
        db.set("user1", "only", "one")

        result = db.scan("user1")
        assert result == [("only", "one")]
