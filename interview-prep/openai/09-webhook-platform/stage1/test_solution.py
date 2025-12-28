"""Tests for Webhook Platform Stage 1"""
import pytest
from solution import WebhookPlatform, DeliveryStatus


class TestWebhookPlatformStage1:
    def test_register(self):
        platform = WebhookPlatform()
        webhook_id = platform.register("http://example.com/hook", ["order.created"])

        assert webhook_id is not None
        webhook = platform.get_webhook(webhook_id)
        assert webhook.url == "http://example.com/hook"

    def test_unregister(self):
        platform = WebhookPlatform()
        webhook_id = platform.register("http://example.com/hook", ["*"])
        assert platform.unregister(webhook_id) is True
        assert platform.get_webhook(webhook_id) is None

    def test_trigger_matching(self):
        platform = WebhookPlatform()
        platform.register("http://example.com/hook", ["order.created"])

        count = platform.trigger("order.created", {"order_id": 123})
        assert count == 1

    def test_trigger_not_matching(self):
        platform = WebhookPlatform()
        platform.register("http://example.com/hook", ["order.created"])

        count = platform.trigger("order.cancelled", {"order_id": 123})
        assert count == 0

    def test_trigger_wildcard(self):
        platform = WebhookPlatform()
        platform.register("http://example.com/hook", ["*"])

        count = platform.trigger("any.event", {"data": "test"})
        assert count == 1

    def test_deliveries(self):
        platform = WebhookPlatform()
        webhook_id = platform.register("http://example.com/hook", ["*"])
        platform.trigger("test.event", {"key": "value"})

        deliveries = platform.get_deliveries(webhook_id)
        assert len(deliveries) == 1
        assert deliveries[0].event == "test.event"
        assert deliveries[0].status == DeliveryStatus.SUCCESS

    def test_failed_delivery(self):
        def failing_sender(url, payload):
            return False, 500

        platform = WebhookPlatform(sender=failing_sender)
        webhook_id = platform.register("http://example.com/hook", ["*"])
        platform.trigger("test.event", {})

        deliveries = platform.get_deliveries(webhook_id)
        assert deliveries[0].status == DeliveryStatus.FAILED
        assert deliveries[0].response_code == 500

    def test_inactive_webhook(self):
        platform = WebhookPlatform()
        webhook_id = platform.register("http://example.com/hook", ["*"])
        platform.set_active(webhook_id, False)

        count = platform.trigger("test.event", {})
        assert count == 0

    def test_list_webhooks(self):
        platform = WebhookPlatform()
        platform.register("http://a.com", ["event1"])
        platform.register("http://b.com", ["event2"])

        webhooks = platform.list_webhooks()
        assert len(webhooks) == 2
