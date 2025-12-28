"""
Tests for In-Memory Database Stage 1

Stage 1 Requirements:
- SET <key> <field> <value>
- GET <key> <field>
- DELETE <key> <field>
"""
import pytest
from solution import InMemoryDB


class TestInMemoryDBStage1:
    """Test suite for Stage 1 functionality."""

    def test_set_and_get_single_field(self):
        """Set and get a single field."""
        db = InMemoryDB()
        db.set("user1", "name", "Alice")
        assert db.get("user1", "name") == "Alice"

    def test_set_multiple_fields_same_key(self):
        """Set multiple fields on the same key."""
        db = InMemoryDB()
        db.set("user1", "name", "Alice")
        db.set("user1", "email", "alice@example.com")
        db.set("user1", "age", "30")

        assert db.get("user1", "name") == "Alice"
        assert db.get("user1", "email") == "alice@example.com"
        assert db.get("user1", "age") == "30"

    def test_get_nonexistent_key_returns_none(self):
        """Get non-existent key returns None."""
        db = InMemoryDB()
        assert db.get("nonexistent", "field") is None

    def test_get_nonexistent_field_returns_none(self):
        """Get non-existent field returns None."""
        db = InMemoryDB()
        db.set("user1", "name", "Alice")
        assert db.get("user1", "nonexistent") is None

    def test_delete_existing_field_returns_true(self):
        """Delete existing field returns True."""
        db = InMemoryDB()
        db.set("user1", "name", "Alice")
        assert db.delete("user1", "name") is True
        assert db.get("user1", "name") is None

    def test_delete_nonexistent_field_returns_false(self):
        """Delete non-existent field returns False."""
        db = InMemoryDB()
        db.set("user1", "name", "Alice")
        assert db.delete("user1", "nonexistent") is False

    def test_delete_nonexistent_key_returns_false(self):
        """Delete non-existent key returns False."""
        db = InMemoryDB()
        assert db.delete("nonexistent", "field") is False

    def test_set_overwrites_existing_value(self):
        """Set overwrites existing value."""
        db = InMemoryDB()
        db.set("user1", "name", "Alice")
        db.set("user1", "name", "Bob")
        assert db.get("user1", "name") == "Bob"

    def test_multiple_keys(self):
        """Multiple keys can coexist."""
        db = InMemoryDB()
        db.set("user1", "name", "Alice")
        db.set("user2", "name", "Bob")

        assert db.get("user1", "name") == "Alice"
        assert db.get("user2", "name") == "Bob"

    def test_delete_one_field_preserves_others(self):
        """Deleting one field preserves other fields on same key."""
        db = InMemoryDB()
        db.set("user1", "name", "Alice")
        db.set("user1", "email", "alice@example.com")

        db.delete("user1", "name")

        assert db.get("user1", "name") is None
        assert db.get("user1", "email") == "alice@example.com"

    def test_empty_string_value(self):
        """Empty string is a valid value."""
        db = InMemoryDB()
        db.set("user1", "name", "")
        assert db.get("user1", "name") == ""

    def test_empty_string_key_and_field(self):
        """Empty string is a valid key and field."""
        db = InMemoryDB()
        db.set("", "", "value")
        assert db.get("", "") == "value"
