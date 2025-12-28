"""Tests for GPU Credit Management Stage 3 - Quotas and Queuing"""
import pytest
from solution import CreditManager


class TestCreditManagerStage3:
    def test_set_and_check_quota(self):
        cm = CreditManager()
        cm.set_quota("user1", "A100", 2.0)  # 2 hours max

        assert cm.get_quota("user1", "A100") == 2.0
        assert cm.check_quota("user1", "A100") is True

    def test_quota_exceeded(self):
        cm = CreditManager()
        cm.add_credits("user1", 1000.0)
        cm.set_quota("user1", "A100", 0.001)  # Very small quota

        cm.start_session("user1", "A100")
        cm.end_session("user1")

        # Usage might exceed quota
        # Next session should be denied if exceeded
        usage = cm.get_usage_today("user1", "A100")
        assert usage > 0

    def test_queuing_when_full(self):
        cm = CreditManager()
        # Fill all A100s
        for i in range(cm.GPU_AVAILABILITY["A100"]):
            cm.add_credits(f"user{i}", 100.0)
            cm.start_session(f"user{i}", "A100")

        # Next user should be queued
        cm.add_credits("waiting", 100.0)
        result = cm.start_session("waiting", "A100")

        assert result == "queued"
        assert cm.queue_position("waiting") == 1

    def test_queue_processing(self):
        cm = CreditManager()
        cm.add_credits("user1", 100.0)
        cm.add_credits("user2", 100.0)

        # Set low availability for testing
        cm.GPU_AVAILABILITY["T4"] = 1

        cm.start_session("user1", "T4")
        cm.start_session("user2", "T4")  # Should be queued

        assert cm.has_active_session("user1") is True
        assert cm.has_active_session("user2") is False
        assert cm.queue_position("user2") == 1

        cm.end_session("user1")

        # user2 should now have active session
        assert cm.has_active_session("user2") is True
        assert cm.queue_position("user2") is None

    def test_priority_queue(self):
        cm = CreditManager()
        cm.GPU_AVAILABILITY["T4"] = 1

        cm.add_credits("user1", 100.0)
        cm.add_credits("low", 100.0)
        cm.add_credits("high", 100.0)

        cm.start_session("user1", "T4")
        cm.start_session("low", "T4", priority=1)
        cm.start_session("high", "T4", priority=10)

        cm.end_session("user1")

        # High priority should start first
        assert cm.has_active_session("high") is True
        assert cm.has_active_session("low") is False

    def test_gpu_available(self):
        cm = CreditManager()
        initial = cm.gpu_available("A100")

        cm.add_credits("user1", 100.0)
        cm.start_session("user1", "A100")

        assert cm.gpu_available("A100") == initial - 1

        cm.end_session("user1")
        assert cm.gpu_available("A100") == initial

    def test_reset_daily_usage(self):
        cm = CreditManager()
        cm.add_credits("user1", 100.0)
        cm.start_session("user1", "A100")
        cm.end_session("user1")

        assert cm.get_usage_today("user1", "A100") > 0

        cm.reset_daily_usage()
        assert cm.get_usage_today("user1", "A100") == 0
