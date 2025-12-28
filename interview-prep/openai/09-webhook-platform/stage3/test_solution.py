"""Tests for Webhook Platform Stage 3 - Security"""
import pytest
from solution import WebhookPlatform


class TestWebhookPlatformStage3:
    def test_register_returns_secret(self):
        platform = WebhookPlatform()
        webhook_id, secret = platform.register("http://example.com", ["*"])

        assert webhook_id is not None
        assert secret is not None
        assert len(secret) > 0

    def test_custom_secret(self):
        platform = WebhookPlatform()
        webhook_id, secret = platform.register(
            "http://example.com", ["*"], secret="my-secret"
        )

        assert secret == "my-secret"

    def test_sign_payload(self):
        platform = WebhookPlatform()
        sig1 = platform.sign_payload("secret", {"key": "value"})
        sig2 = platform.sign_payload("secret", {"key": "value"})
        sig3 = platform.sign_payload("secret", {"key": "other"})

        assert sig1 == sig2  # Same payload = same sig
        assert sig1 != sig3  # Different payload = different sig

    def test_verify_signature(self):
        platform = WebhookPlatform()
        payload = {"key": "value"}
        secret = "my-secret"

        sig = platform.sign_payload(secret, payload)
        assert platform.verify_signature(secret, payload, sig) is True
        assert platform.verify_signature(secret, payload, "wrong") is False
        assert platform.verify_signature("wrong-secret", payload, sig) is False

    def test_trigger_includes_signature(self):
        signatures = []

        def capturing_sender(url, payload, signature):
            signatures.append(signature)
            return True, 200

        platform = WebhookPlatform(sender=capturing_sender)
        platform.register("http://example.com", ["*"])
        platform.trigger("test.event", {"data": "test"})

        assert len(signatures) == 1
        assert len(signatures[0]) == 64  # SHA256 hex

    def test_rotate_secret(self):
        platform = WebhookPlatform()
        webhook_id, old_secret = platform.register("http://example.com", ["*"])

        new_secret = platform.rotate_secret(webhook_id)
        assert new_secret is not None
        assert new_secret != old_secret

        webhook = platform.get_webhook(webhook_id)
        assert webhook.secret == new_secret

    def test_rotate_secret_nonexistent(self):
        platform = WebhookPlatform()
        result = platform.rotate_secret("missing")
        assert result is None

    def test_delivery_has_signature(self):
        platform = WebhookPlatform()
        webhook_id, _ = platform.register("http://example.com", ["*"])
        platform.trigger("test.event", {"key": "value"})

        deliveries = platform.get_deliveries(webhook_id)
        assert len(deliveries) == 1
        assert deliveries[0].signature is not None
