"""Tests for In-Memory SQL Stage 1"""
import pytest
from solution import InMemorySQL


class TestInMemorySQLStage1:
    def test_create_table(self):
        db = InMemorySQL()
        result = db.create_table("users", ["id", "name", "age"])
        assert result is True

    def test_create_duplicate_table(self):
        db = InMemorySQL()
        db.create_table("users", ["id", "name"])
        result = db.create_table("users", ["id", "name"])
        assert result is False

    def test_insert(self):
        db = InMemorySQL()
        db.create_table("users", ["id", "name"])
        result = db.insert("users", {"id": 1, "name": "Alice"})
        assert result is True

    def test_insert_nonexistent_table(self):
        db = InMemorySQL()
        result = db.insert("nonexistent", {"id": 1})
        assert result is False

    def test_select_all(self):
        db = InMemorySQL()
        db.create_table("users", ["id", "name"])
        db.insert("users", {"id": 1, "name": "Alice"})
        db.insert("users", {"id": 2, "name": "Bob"})

        result = db.select("users")
        assert len(result) == 2
        assert result[0] == {"id": 1, "name": "Alice"}
        assert result[1] == {"id": 2, "name": "Bob"}

    def test_select_columns(self):
        db = InMemorySQL()
        db.create_table("users", ["id", "name", "age"])
        db.insert("users", {"id": 1, "name": "Alice", "age": 30})

        result = db.select("users", ["name"])
        assert result == [{"name": "Alice"}]

    def test_select_nonexistent_table(self):
        db = InMemorySQL()
        result = db.select("nonexistent")
        assert result == []
