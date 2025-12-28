"""Tests for Webhook Platform Stage 4 - Rate Limiting and Analytics"""
import pytest
from solution import WebhookPlatform, DeliveryStatus


class TestWebhookPlatformStage4:
    def test_rate_limit(self):
        platform = WebhookPlatform()
        webhook_id, _ = platform.register("http://example.com", ["*"], rate_limit=2)

        platform.trigger("event1", {})
        platform.trigger("event2", {})
        platform.trigger("event3", {})

        rate_limited = platform.get_deliveries(status=DeliveryStatus.RATE_LIMITED)
        assert len(rate_limited) == 1

    def test_get_stats(self):
        def sender(url, payload, sig):
            return True, 200, 15.0

        platform = WebhookPlatform(sender=sender)
        webhook_id, _ = platform.register("http://example.com", ["*"])

        platform.trigger("event1", {})
        platform.trigger("event2", {})

        stats = platform.get_stats(webhook_id)
        assert stats.total_deliveries == 2
        assert stats.successful == 2
        assert stats.success_rate == 1.0
        assert stats.avg_latency_ms == 15.0

    def test_stats_with_failures(self):
        call_count = [0]

        def flaky_sender(url, payload, sig):
            call_count[0] += 1
            success = call_count[0] % 2 == 0
            return success, 200 if success else 500, 10.0

        platform = WebhookPlatform(sender=flaky_sender)
        webhook_id, _ = platform.register("http://example.com", ["*"])

        platform.trigger("event1", {})
        platform.trigger("event2", {})

        stats = platform.get_stats(webhook_id)
        assert stats.successful == 1
        assert stats.failed == 1
        assert stats.success_rate == 0.5

    def test_get_all_stats(self):
        platform = WebhookPlatform()
        wid1, _ = platform.register("http://a.com", ["*"])
        wid2, _ = platform.register("http://b.com", ["*"])

        platform.trigger("event", {})

        all_stats = platform.get_all_stats()
        assert wid1 in all_stats
        assert wid2 in all_stats

    def test_get_top_webhooks(self):
        platform = WebhookPlatform()
        wid1, _ = platform.register("http://a.com", ["event1"])
        wid2, _ = platform.register("http://b.com", ["event1", "event2"])

        platform.trigger("event1", {})
        platform.trigger("event2", {})

        top = platform.get_top_webhooks(limit=2)
        assert len(top) == 2
        assert top[0][0] == wid2  # More deliveries

    def test_latency_tracking(self):
        def slow_sender(url, payload, sig):
            return True, 200, 100.0

        platform = WebhookPlatform(sender=slow_sender)
        webhook_id, _ = platform.register("http://example.com", ["*"])
        platform.trigger("event", {})

        deliveries = platform.get_deliveries(webhook_id)
        assert deliveries[0].latency_ms == 100.0

    def test_empty_stats(self):
        platform = WebhookPlatform()
        webhook_id, _ = platform.register("http://example.com", ["*"])

        stats = platform.get_stats(webhook_id)
        assert stats.total_deliveries == 0
        assert stats.success_rate == 0.0
