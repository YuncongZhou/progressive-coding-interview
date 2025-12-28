"""Tests for In-Memory SQL Stage 3 - Complex WHERE"""
import pytest
from solution import InMemorySQL


class TestInMemorySQLStage3:
    def test_and_conditions(self):
        db = InMemorySQL()
        db.create_table("users", ["name", "age", "city"])
        db.insert("users", {"name": "Alice", "age": 30, "city": "NYC"})
        db.insert("users", {"name": "Bob", "age": 25, "city": "NYC"})
        db.insert("users", {"name": "Charlie", "age": 30, "city": "LA"})

        result = db.select_where_complex("users", ["name"],
                                         "age = 30 AND city = 'NYC'")
        assert result == [{"name": "Alice"}]

    def test_or_conditions(self):
        db = InMemorySQL()
        db.create_table("users", ["name", "age"])
        db.insert("users", {"name": "Alice", "age": 30})
        db.insert("users", {"name": "Bob", "age": 25})
        db.insert("users", {"name": "Charlie", "age": 35})

        result = db.select_where_complex("users", ["name"],
                                         "age = 25 OR age = 35")
        assert result == [{"name": "Bob"}, {"name": "Charlie"}]

    def test_greater_than(self):
        db = InMemorySQL()
        db.create_table("products", ["name", "price"])
        db.insert("products", {"name": "A", "price": 10})
        db.insert("products", {"name": "B", "price": 50})
        db.insert("products", {"name": "C", "price": 100})

        result = db.select_where_complex("products", ["name"], "price > 20")
        assert result == [{"name": "B"}, {"name": "C"}]

    def test_less_than_equal(self):
        db = InMemorySQL()
        db.create_table("products", ["name", "price"])
        db.insert("products", {"name": "A", "price": 10})
        db.insert("products", {"name": "B", "price": 50})
        db.insert("products", {"name": "C", "price": 100})

        result = db.select_where_complex("products", ["name"], "price <= 50")
        assert result == [{"name": "A"}, {"name": "B"}]

    def test_not_equal(self):
        db = InMemorySQL()
        db.create_table("users", ["name", "status"])
        db.insert("users", {"name": "Alice", "status": "active"})
        db.insert("users", {"name": "Bob", "status": "inactive"})

        result = db.select_where_complex("users", ["name"],
                                         "status != 'inactive'")
        assert result == [{"name": "Alice"}]

    def test_and_or_precedence(self):
        db = InMemorySQL()
        db.create_table("users", ["name", "age", "city"])
        db.insert("users", {"name": "Alice", "age": 30, "city": "NYC"})
        db.insert("users", {"name": "Bob", "age": 25, "city": "LA"})
        db.insert("users", {"name": "Charlie", "age": 35, "city": "NYC"})

        # AND has higher precedence: age = 30 AND city = 'NYC' OR age = 25
        # means: (age = 30 AND city = 'NYC') OR (age = 25)
        result = db.select_where_complex("users", ["name"],
                                         "age = 30 AND city = 'NYC' OR age = 25")
        assert result == [{"name": "Alice"}, {"name": "Bob"}]

    def test_numeric_comparison(self):
        db = InMemorySQL()
        db.create_table("orders", ["id", "total"])
        db.insert("orders", {"id": 1, "total": 99.99})
        db.insert("orders", {"id": 2, "total": 150.00})

        result = db.select_where_complex("orders", ["id"], "total >= 100")
        assert result == [{"id": 2}]

    def test_nonexistent_table(self):
        db = InMemorySQL()
        result = db.select_where_complex("missing", ["col"], "x = 1")
        assert result == []
