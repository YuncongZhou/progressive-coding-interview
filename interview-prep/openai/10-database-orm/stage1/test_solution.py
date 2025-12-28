"""Tests for Database ORM Stage 1"""
import pytest
from solution import Model, StringField, IntField, BoolField


class User(Model):
    name = StringField()
    age = IntField(required=False, default=0)
    active = BoolField(required=False, default=True)


class TestORMStage1:
    def setup_method(self):
        User.clear()

    def test_create_model(self):
        user = User(name="Alice", age=30)
        assert user.name == "Alice"
        assert user.age == 30
        assert user.id is not None

    def test_required_field(self):
        with pytest.raises(ValueError):
            User()

    def test_default_field(self):
        user = User(name="Bob")
        assert user.age == 0
        assert user.active is True

    def test_save_and_get(self):
        user = User(name="Charlie")
        user.save()

        retrieved = User.get(user.id)
        assert retrieved is not None
        assert retrieved.name == "Charlie"

    def test_delete(self):
        user = User(name="David")
        user.save()

        assert user.delete() is True
        assert User.get(user.id) is None

    def test_all(self):
        User(name="A").save()
        User(name="B").save()

        all_users = User.all()
        assert len(all_users) == 2

    def test_count(self):
        User(name="A").save()
        User(name="B").save()

        assert User.count() == 2

    def test_to_dict(self):
        user = User(name="Eve", age=25)
        d = user.to_dict()

        assert d['name'] == "Eve"
        assert d['age'] == 25
        assert 'id' in d

    def test_clear(self):
        User(name="A").save()
        User.clear()
        assert User.count() == 0
