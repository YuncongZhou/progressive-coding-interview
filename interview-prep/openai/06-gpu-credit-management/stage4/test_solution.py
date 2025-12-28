"""Tests for GPU Credit Management Stage 4 - Billing and Reporting"""
import pytest
import time
from datetime import datetime, timedelta
from solution import CreditManager


class TestCreditManagerStage4:
    def test_generate_invoice(self):
        cm = CreditManager()
        cm.add_credits("user1", 1000.0)

        cm.start_session("user1", "A100")
        time.sleep(0.05)
        cm.end_session("user1")

        now = datetime.now()
        invoice = cm.generate_invoice(
            "user1",
            now - timedelta(hours=1),
            now + timedelta(hours=1)
        )

        assert invoice.user_id == "user1"
        assert invoice.total_cost > 0
        assert "A100" in invoice.usage_by_gpu
        assert len(invoice.records) == 1

    def test_usage_stats(self):
        cm = CreditManager()
        cm.add_credits("user1", 1000.0)

        cm.start_session("user1", "A100")
        time.sleep(0.05)
        cm.end_session("user1")

        cm.start_session("user1", "V100")
        time.sleep(0.05)
        cm.end_session("user1")

        stats = cm.get_usage_stats("user1")

        assert stats.total_hours > 0
        assert stats.total_cost > 0
        assert "A100" in stats.gpu_breakdown
        assert "V100" in stats.gpu_breakdown

    def test_usage_stats_empty(self):
        cm = CreditManager()
        stats = cm.get_usage_stats("user1")

        assert stats.total_hours == 0
        assert stats.total_cost == 0

    def test_estimate_monthly_cost(self):
        cm = CreditManager()
        cm.add_credits("user1", 1000.0)

        cm.start_session("user1", "A100")
        time.sleep(0.05)
        cm.end_session("user1")

        estimate = cm.estimate_monthly_cost("user1")
        assert estimate >= 0

    def test_top_users(self):
        cm = CreditManager()
        cm.add_credits("user1", 1000.0)
        cm.add_credits("user2", 1000.0)
        cm.add_credits("user3", 1000.0)

        # user1 uses expensive GPU
        cm.start_session("user1", "A100")
        time.sleep(0.05)
        cm.end_session("user1")

        # user2 uses cheaper GPU
        cm.start_session("user2", "T4")
        time.sleep(0.05)
        cm.end_session("user2")

        top = cm.get_top_users(limit=2)
        assert len(top) <= 2
        # user1 should be first (higher cost GPU)
        if len(top) >= 2:
            assert top[0][0] == "user1"

    def test_gpu_utilization(self):
        cm = CreditManager()
        cm.add_credits("user1", 100.0)

        util_before = cm.get_gpu_utilization()
        assert util_before["A100"] == 0.0

        cm.start_session("user1", "A100")
        util_during = cm.get_gpu_utilization()
        assert util_during["A100"] > 0

        cm.end_session("user1")
        util_after = cm.get_gpu_utilization()
        assert util_after["A100"] == 0.0

    def test_invoice_period_filtering(self):
        cm = CreditManager()
        cm.add_credits("user1", 1000.0)

        cm.start_session("user1", "A100")
        cm.end_session("user1")

        # Invoice for future period should be empty
        future = datetime.now() + timedelta(days=1)
        invoice = cm.generate_invoice(
            "user1",
            future,
            future + timedelta(hours=1)
        )

        assert invoice.total_cost == 0
        assert len(invoice.records) == 0
