"""Tests for Database ORM Stage 4 - Validation and Hooks"""
import pytest
from solution import Model, StringField, IntField, EmailField, ValidationError


class User(Model):
    name = StringField(min_length=2, max_length=50)
    age = IntField(min_value=0, max_value=150, required=False, default=0)
    email = EmailField(required=False)


class TimestampedModel(Model):
    name = StringField()
    created_at = StringField(required=False)
    updated_at = StringField(required=False)

    def _pre_save(self):
        import time
        ts = str(time.time())
        if self.is_new:
            self.created_at = ts
        self.updated_at = ts


class TestORMStage4:
    def setup_method(self):
        User.clear()
        TimestampedModel.clear()

    def test_string_min_length(self):
        with pytest.raises(ValidationError):
            User(name="A").save()

    def test_string_max_length(self):
        with pytest.raises(ValidationError):
            User(name="A" * 100).save()

    def test_int_min_value(self):
        with pytest.raises(ValidationError):
            User(name="Alice", age=-5).save()

    def test_int_max_value(self):
        with pytest.raises(ValidationError):
            User(name="Alice", age=200).save()

    def test_email_validation(self):
        with pytest.raises(ValidationError):
            User(name="Alice", email="not-an-email").save()

    def test_valid_email(self):
        user = User(name="Alice", email="alice@example.com")
        user.save()
        assert user.email == "alice@example.com"

    def test_skip_validation(self):
        user = User(name="A")  # Too short
        user.save(validate=False)  # Should not raise
        assert User.count() == 1

    def test_pre_save_hook(self):
        obj = TimestampedModel(name="Test")
        obj.save()

        assert obj.created_at is not None
        assert obj.updated_at is not None

    def test_post_save_updates(self):
        obj = TimestampedModel(name="Test")
        obj.save()
        first_update = obj.updated_at

        import time
        time.sleep(0.01)
        obj.name = "Updated"
        obj.save()

        assert obj.updated_at != first_update

    def test_is_new(self):
        user = User(name="Alice")
        assert user.is_new is True

        user.save()
        assert user.is_new is False

    def test_valid_user(self):
        user = User(name="Alice", age=30, email="alice@test.com")
        user.save()
        assert User.get(user.id) is not None
