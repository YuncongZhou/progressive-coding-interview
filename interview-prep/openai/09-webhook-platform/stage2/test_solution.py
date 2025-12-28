"""Tests for Webhook Platform Stage 2 - Retries"""
import pytest
from solution import WebhookPlatform, DeliveryStatus


class TestWebhookPlatformStage2:
    def test_retry_on_failure(self):
        fail_count = [0]

        def failing_sender(url, payload):
            fail_count[0] += 1
            return False, 500

        platform = WebhookPlatform(sender=failing_sender)
        platform.register("http://example.com/hook", ["*"])
        platform.trigger("test.event", {})

        deliveries = platform.get_deliveries(status=DeliveryStatus.RETRYING)
        assert len(deliveries) == 1

    def test_retry_scheduling(self):
        def failing_sender(url, payload):
            return False, 500

        platform = WebhookPlatform(sender=failing_sender)
        platform.register("http://example.com/hook", ["*"])
        platform.trigger("test.event", {})

        pending = platform.get_pending_retries()
        assert len(pending) == 1
        assert pending[0].next_retry_at is not None

    def test_max_retries(self):
        def failing_sender(url, payload):
            return False, 500

        platform = WebhookPlatform(sender=failing_sender)
        platform.BASE_DELAY = 0  # No delay for testing
        platform.MAX_RETRIES = 2

        platform.register("http://example.com/hook", ["*"])
        platform.trigger("test.event", {})

        # Process retries until exhausted
        for _ in range(5):
            platform.process_retries()

        failed = platform.get_deliveries(status=DeliveryStatus.FAILED)
        assert len(failed) >= 1

    def test_successful_retry(self):
        attempt = [0]

        def flaky_sender(url, payload):
            attempt[0] += 1
            return attempt[0] >= 2, 200 if attempt[0] >= 2 else 500

        platform = WebhookPlatform(sender=flaky_sender)
        platform.BASE_DELAY = 0

        platform.register("http://example.com/hook", ["*"])
        platform.trigger("test.event", {})

        # Should be retrying
        assert len(platform.get_deliveries(status=DeliveryStatus.RETRYING)) == 1

        # Process retry
        platform.process_retries()

        # Should now be successful
        assert len(platform.get_deliveries(status=DeliveryStatus.SUCCESS)) == 1

    def test_filter_by_status(self):
        def half_fail(url, payload):
            return "success" in url, 200

        platform = WebhookPlatform(sender=half_fail)
        platform.register("http://success.com/hook", ["*"])
        platform.register("http://fail.com/hook", ["*"])
        platform.trigger("test.event", {})

        success = platform.get_deliveries(status=DeliveryStatus.SUCCESS)
        retrying = platform.get_deliveries(status=DeliveryStatus.RETRYING)

        assert len(success) == 1
        assert len(retrying) == 1
