"""Tests for GPU Credit Management Stage 1"""
import pytest
from solution import CreditManager


class TestCreditManagerStage1:
    def test_add_credits(self):
        cm = CreditManager()
        balance = cm.add_credits("user1", 100.0)
        assert balance == 100.0
        assert cm.get_balance("user1") == 100.0

    def test_add_credits_cumulative(self):
        cm = CreditManager()
        cm.add_credits("user1", 50.0)
        cm.add_credits("user1", 30.0)
        assert cm.get_balance("user1") == 80.0

    def test_deduct_credits_success(self):
        cm = CreditManager()
        cm.add_credits("user1", 100.0)
        result = cm.deduct_credits("user1", 30.0)
        assert result is True
        assert cm.get_balance("user1") == 70.0

    def test_deduct_credits_insufficient(self):
        cm = CreditManager()
        cm.add_credits("user1", 10.0)
        result = cm.deduct_credits("user1", 50.0)
        assert result is False
        assert cm.get_balance("user1") == 10.0

    def test_deduct_credits_nonexistent_user(self):
        cm = CreditManager()
        result = cm.deduct_credits("user1", 10.0)
        assert result is False

    def test_get_balance_nonexistent(self):
        cm = CreditManager()
        assert cm.get_balance("missing") == 0.0

    def test_has_credits(self):
        cm = CreditManager()
        cm.add_credits("user1", 50.0)
        assert cm.has_credits("user1", 30.0) is True
        assert cm.has_credits("user1", 50.0) is True
        assert cm.has_credits("user1", 51.0) is False

    def test_negative_amount_error(self):
        cm = CreditManager()
        with pytest.raises(ValueError):
            cm.add_credits("user1", -10.0)
        with pytest.raises(ValueError):
            cm.deduct_credits("user1", -10.0)

    def test_user_count(self):
        cm = CreditManager()
        cm.add_credits("user1", 10.0)
        cm.add_credits("user2", 20.0)
        assert cm.user_count() == 2

    def test_total_credits(self):
        cm = CreditManager()
        cm.add_credits("user1", 100.0)
        cm.add_credits("user2", 50.0)
        assert cm.total_credits() == 150.0
