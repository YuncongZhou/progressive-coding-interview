"""Tests for In-Memory SQL Stage 4 - ORDER BY and LIMIT"""
import pytest
from solution import InMemorySQL


class TestInMemorySQLStage4:
    def test_order_by_asc(self):
        db = InMemorySQL()
        db.create_table("users", ["name", "age"])
        db.insert("users", {"name": "Charlie", "age": 35})
        db.insert("users", {"name": "Alice", "age": 25})
        db.insert("users", {"name": "Bob", "age": 30})

        result = db.select_order_by("users", ["name"], [("age", "ASC")])
        assert result == [
            {"name": "Alice"},
            {"name": "Bob"},
            {"name": "Charlie"}
        ]

    def test_order_by_desc(self):
        db = InMemorySQL()
        db.create_table("users", ["name", "age"])
        db.insert("users", {"name": "Alice", "age": 25})
        db.insert("users", {"name": "Bob", "age": 30})
        db.insert("users", {"name": "Charlie", "age": 35})

        result = db.select_order_by("users", ["name"], [("age", "DESC")])
        assert result == [
            {"name": "Charlie"},
            {"name": "Bob"},
            {"name": "Alice"}
        ]

    def test_order_by_string(self):
        db = InMemorySQL()
        db.create_table("users", ["name", "age"])
        db.insert("users", {"name": "Charlie", "age": 35})
        db.insert("users", {"name": "Alice", "age": 25})
        db.insert("users", {"name": "Bob", "age": 30})

        result = db.select_order_by("users", ["name", "age"], [("name", "ASC")])
        assert result == [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30},
            {"name": "Charlie", "age": 35}
        ]

    def test_limit(self):
        db = InMemorySQL()
        db.create_table("nums", ["val"])
        for i in range(10):
            db.insert("nums", {"val": i})

        result = db.select_order_by("nums", ["val"], [("val", "ASC")], limit=3)
        assert result == [{"val": 0}, {"val": 1}, {"val": 2}]

    def test_order_by_with_limit(self):
        db = InMemorySQL()
        db.create_table("products", ["name", "price"])
        db.insert("products", {"name": "A", "price": 100})
        db.insert("products", {"name": "B", "price": 50})
        db.insert("products", {"name": "C", "price": 200})
        db.insert("products", {"name": "D", "price": 75})

        # Top 2 most expensive
        result = db.select_order_by("products", ["name"],
                                    [("price", "DESC")], limit=2)
        assert result == [{"name": "C"}, {"name": "A"}]

    def test_full_select(self):
        db = InMemorySQL()
        db.create_table("users", ["name", "age", "city"])
        db.insert("users", {"name": "Alice", "age": 30, "city": "NYC"})
        db.insert("users", {"name": "Bob", "age": 25, "city": "LA"})
        db.insert("users", {"name": "Charlie", "age": 35, "city": "NYC"})
        db.insert("users", {"name": "Diana", "age": 28, "city": "NYC"})

        # NYC users, ordered by age desc, limit 2
        result = db.select_full(
            "users",
            columns=["name", "age"],
            where_clause="city = 'NYC'",
            order_by=[("age", "DESC")],
            limit=2
        )
        assert result == [
            {"name": "Charlie", "age": 35},
            {"name": "Alice", "age": 30}
        ]

    def test_full_select_no_where(self):
        db = InMemorySQL()
        db.create_table("nums", ["val"])
        db.insert("nums", {"val": 3})
        db.insert("nums", {"val": 1})
        db.insert("nums", {"val": 2})

        result = db.select_full("nums", ["val"], order_by=[("val", "ASC")])
        assert result == [{"val": 1}, {"val": 2}, {"val": 3}]

    def test_nonexistent_table(self):
        db = InMemorySQL()
        result = db.select_order_by("missing", ["col"], [("col", "ASC")])
        assert result == []
