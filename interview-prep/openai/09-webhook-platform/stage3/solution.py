"""
Webhook Platform - Stage 3

Signature verification and security.

Design Rationale:
- Sign payloads with secret
- Verify incoming requests
- Rotate secrets
"""

from typing import Optional, List, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum
import time
import uuid
import hmac
import hashlib
import json


class DeliveryStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class Webhook:
    id: str
    url: str
    events: List[str]
    secret: str
    created_at: float
    active: bool = True


@dataclass
class Delivery:
    id: str
    webhook_id: str
    event: str
    payload: Dict[str, Any]
    signature: str
    status: DeliveryStatus
    attempted_at: float
    attempts: int = 1
    response_code: Optional[int] = None


class WebhookPlatform:
    """Webhook platform with signature support."""

    MAX_RETRIES = 3

    def __init__(self, sender: Callable[[str, Dict, str], tuple[bool, int]] = None):
        """
        Args:
            sender: Function(url, payload, signature) -> (success, code)
        """
        self._webhooks: dict[str, Webhook] = {}
        self._deliveries: dict[str, Delivery] = {}
        self._sender = sender or self._default_sender

    def register(self, url: str, events: List[str],
                 secret: str = None) -> tuple[str, str]:
        """Register webhook. Returns (webhook_id, secret)."""
        webhook_id = str(uuid.uuid4())[:8]
        secret = secret or str(uuid.uuid4())

        self._webhooks[webhook_id] = Webhook(
            id=webhook_id,
            url=url,
            events=events,
            secret=secret,
            created_at=time.time()
        )
        return webhook_id, secret

    def unregister(self, webhook_id: str) -> bool:
        if webhook_id not in self._webhooks:
            return False
        del self._webhooks[webhook_id]
        return True

    def sign_payload(self, secret: str, payload: Dict[str, Any]) -> str:
        """Generate HMAC signature for payload."""
        payload_str = json.dumps(payload, sort_keys=True)
        return hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()

    def verify_signature(self, secret: str, payload: Dict[str, Any],
                         signature: str) -> bool:
        """Verify payload signature."""
        expected = self.sign_payload(secret, payload)
        return hmac.compare_digest(expected, signature)

    def rotate_secret(self, webhook_id: str) -> Optional[str]:
        """Rotate webhook secret. Returns new secret."""
        if webhook_id not in self._webhooks:
            return None
        new_secret = str(uuid.uuid4())
        self._webhooks[webhook_id].secret = new_secret
        return new_secret

    def trigger(self, event: str, payload: Dict[str, Any]) -> int:
        count = 0
        for webhook in self._webhooks.values():
            if not webhook.active:
                continue
            if event not in webhook.events and "*" not in webhook.events:
                continue

            signature = self.sign_payload(webhook.secret, payload)
            success, code = self._sender(webhook.url, payload, signature)

            delivery_id = str(uuid.uuid4())[:8]
            self._deliveries[delivery_id] = Delivery(
                id=delivery_id,
                webhook_id=webhook.id,
                event=event,
                payload=payload,
                signature=signature,
                status=DeliveryStatus.SUCCESS if success else DeliveryStatus.FAILED,
                attempted_at=time.time(),
                response_code=code
            )
            count += 1

        return count

    def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        return self._webhooks.get(webhook_id)

    def get_deliveries(self, webhook_id: str = None) -> List[Delivery]:
        result = list(self._deliveries.values())
        if webhook_id:
            result = [d for d in result if d.webhook_id == webhook_id]
        return result

    def list_webhooks(self) -> List[Webhook]:
        return list(self._webhooks.values())

    def set_active(self, webhook_id: str, active: bool) -> bool:
        if webhook_id not in self._webhooks:
            return False
        self._webhooks[webhook_id].active = active
        return True

    def _default_sender(self, url: str, payload: Dict, signature: str) -> tuple[bool, int]:
        return True, 200
