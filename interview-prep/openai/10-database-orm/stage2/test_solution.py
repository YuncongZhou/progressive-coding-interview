"""Tests for Database ORM Stage 2 - Querying"""
import pytest
from solution import Model, StringField, IntField, BoolField


class User(Model):
    name = StringField()
    age = IntField(required=False, default=0)
    active = BoolField(required=False, default=True)


class TestORMStage2:
    def setup_method(self):
        User.clear()

    def test_filter(self):
        User(name="Alice", age=30).save()
        User(name="Bob", age=25).save()
        User(name="Charlie", age=30).save()

        result = User.query().filter(age=30).all()
        assert len(result) == 2

    def test_filter_chain(self):
        User(name="Alice", age=30, active=True).save()
        User(name="Bob", age=30, active=False).save()

        result = User.query().filter(age=30).filter(active=True).all()
        assert len(result) == 1
        assert result[0].name == "Alice"

    def test_filter_by(self):
        User(name="Alice", age=30).save()
        User(name="Bob", age=25).save()

        result = User.query().filter_by(lambda u: u.age > 26).all()
        assert len(result) == 1

    def test_order_by(self):
        User(name="Charlie", age=30).save()
        User(name="Alice", age=25).save()
        User(name="Bob", age=35).save()

        result = User.query().order_by("age").all()
        assert result[0].age == 25
        assert result[-1].age == 35

    def test_order_by_desc(self):
        User(name="A", age=30).save()
        User(name="B", age=25).save()

        result = User.query().order_by("age", descending=True).all()
        assert result[0].age == 30

    def test_limit(self):
        for i in range(5):
            User(name=f"User{i}").save()

        result = User.query().limit(3).all()
        assert len(result) == 3

    def test_offset(self):
        for i in range(5):
            User(name=f"User{i}", age=i).save()

        result = User.query().order_by("age").offset(2).all()
        assert len(result) == 3

    def test_first_last(self):
        User(name="A", age=1).save()
        User(name="B", age=2).save()

        first = User.query().order_by("age").first()
        last = User.query().order_by("age").last()

        assert first.age == 1
        assert last.age == 2

    def test_exists(self):
        User(name="Alice").save()

        assert User.query().filter(name="Alice").exists() is True
        assert User.query().filter(name="Bob").exists() is False

    def test_count(self):
        User(name="A", active=True).save()
        User(name="B", active=True).save()
        User(name="C", active=False).save()

        assert User.query().filter(active=True).count() == 2
