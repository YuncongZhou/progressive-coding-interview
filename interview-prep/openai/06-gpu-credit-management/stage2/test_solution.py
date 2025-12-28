"""Tests for GPU Credit Management Stage 2 - Usage Tracking"""
import pytest
import time
from solution import CreditManager


class TestCreditManagerStage2:
    def test_start_session(self):
        cm = CreditManager()
        cm.add_credits("user1", 100.0)
        result = cm.start_session("user1", "A100")
        assert result is True
        assert cm.has_active_session("user1") is True

    def test_start_session_insufficient_credits(self):
        cm = CreditManager()
        cm.add_credits("user1", 0.1)  # Not enough for 1 minute
        result = cm.start_session("user1", "A100")
        assert result is False

    def test_start_session_invalid_gpu(self):
        cm = CreditManager()
        cm.add_credits("user1", 100.0)
        result = cm.start_session("user1", "INVALID")
        assert result is False

    def test_start_session_already_active(self):
        cm = CreditManager()
        cm.add_credits("user1", 100.0)
        cm.start_session("user1", "A100")
        result = cm.start_session("user1", "V100")
        assert result is False

    def test_end_session(self):
        cm = CreditManager()
        cm.add_credits("user1", 100.0)
        cm.start_session("user1", "A100")
        time.sleep(0.1)
        cost = cm.end_session("user1")

        assert cost is not None
        assert cost > 0
        assert cm.has_active_session("user1") is False
        assert cm.get_balance("user1") < 100.0

    def test_end_session_no_active(self):
        cm = CreditManager()
        result = cm.end_session("user1")
        assert result is None

    def test_get_session_cost(self):
        cm = CreditManager()
        cm.add_credits("user1", 100.0)
        cm.start_session("user1", "A100")
        time.sleep(0.1)
        cost = cm.get_session_cost("user1")

        assert cost is not None
        assert cost > 0

    def test_usage_history(self):
        cm = CreditManager()
        cm.add_credits("user1", 100.0)
        cm.start_session("user1", "A100")
        cm.end_session("user1")

        history = cm.get_usage_history("user1")
        assert len(history) == 1
        assert history[0].gpu_type == "A100"
        assert history[0].cost > 0

    def test_total_usage_cost(self):
        cm = CreditManager()
        cm.add_credits("user1", 100.0)

        cm.start_session("user1", "A100")
        time.sleep(0.05)
        cm.end_session("user1")

        cm.start_session("user1", "V100")
        time.sleep(0.05)
        cm.end_session("user1")

        total = cm.get_total_usage_cost("user1")
        assert total > 0
        assert len(cm.get_usage_history("user1")) == 2

    def test_active_session_count(self):
        cm = CreditManager()
        cm.add_credits("user1", 100.0)
        cm.add_credits("user2", 100.0)

        cm.start_session("user1", "A100")
        assert cm.active_session_count() == 1

        cm.start_session("user2", "V100")
        assert cm.active_session_count() == 2

        cm.end_session("user1")
        assert cm.active_session_count() == 1
