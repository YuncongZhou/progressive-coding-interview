"""Tests for In-Memory SQL Stage 2 - WHERE clause"""
import pytest
from solution import InMemorySQL


class TestInMemorySQLStage2:
    def test_select_where_equals(self):
        db = InMemorySQL()
        db.create_table("users", ["id", "name", "age"])
        db.insert("users", {"id": 1, "name": "Alice", "age": 30})
        db.insert("users", {"id": 2, "name": "Bob", "age": 25})
        db.insert("users", {"id": 3, "name": "Alice", "age": 35})

        result = db.select_where("users", ["id", "age"], "name", "Alice")
        assert len(result) == 2
        assert result[0] == {"id": 1, "age": 30}
        assert result[1] == {"id": 3, "age": 35}

    def test_select_where_no_match(self):
        db = InMemorySQL()
        db.create_table("users", ["id", "name"])
        db.insert("users", {"id": 1, "name": "Alice"})

        result = db.select_where("users", ["id"], "name", "Charlie")
        assert result == []

    def test_select_where_numeric(self):
        db = InMemorySQL()
        db.create_table("products", ["id", "price"])
        db.insert("products", {"id": 1, "price": 100})
        db.insert("products", {"id": 2, "price": 200})
        db.insert("products", {"id": 3, "price": 100})

        result = db.select_where("products", ["id"], "price", 100)
        assert result == [{"id": 1}, {"id": 3}]
