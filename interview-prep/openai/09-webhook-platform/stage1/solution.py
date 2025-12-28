"""
Webhook Platform - Stage 1

Basic webhook registration and delivery.

Design Rationale:
- Register webhooks with URLs
- Deliver events to webhooks
- Track delivery status
"""

from typing import Optional, List, Callable, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid


class DeliveryStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class Webhook:
    id: str
    url: str
    events: List[str]
    created_at: float
    active: bool = True


@dataclass
class Delivery:
    id: str
    webhook_id: str
    event: str
    payload: Dict[str, Any]
    status: DeliveryStatus
    attempted_at: float
    response_code: Optional[int] = None


class WebhookPlatform:
    """Basic webhook platform."""

    def __init__(self, sender: Callable[[str, Dict], tuple[bool, int]] = None):
        """
        Args:
            sender: Function(url, payload) -> (success, status_code)
        """
        self._webhooks: dict[str, Webhook] = {}
        self._deliveries: List[Delivery] = []
        self._sender = sender or self._default_sender

    def register(self, url: str, events: List[str]) -> str:
        """Register a webhook. Returns webhook ID."""
        webhook_id = str(uuid.uuid4())[:8]
        self._webhooks[webhook_id] = Webhook(
            id=webhook_id,
            url=url,
            events=events,
            created_at=time.time()
        )
        return webhook_id

    def unregister(self, webhook_id: str) -> bool:
        """Unregister a webhook."""
        if webhook_id not in self._webhooks:
            return False
        del self._webhooks[webhook_id]
        return True

    def trigger(self, event: str, payload: Dict[str, Any]) -> int:
        """
        Trigger an event, delivering to matching webhooks.

        Returns number of deliveries attempted.
        """
        count = 0
        for webhook in self._webhooks.values():
            if not webhook.active:
                continue
            if event not in webhook.events and "*" not in webhook.events:
                continue

            delivery_id = str(uuid.uuid4())[:8]
            success, code = self._sender(webhook.url, payload)

            self._deliveries.append(Delivery(
                id=delivery_id,
                webhook_id=webhook.id,
                event=event,
                payload=payload,
                status=DeliveryStatus.SUCCESS if success else DeliveryStatus.FAILED,
                attempted_at=time.time(),
                response_code=code
            ))
            count += 1

        return count

    def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        """Get webhook by ID."""
        return self._webhooks.get(webhook_id)

    def list_webhooks(self) -> List[Webhook]:
        """List all webhooks."""
        return list(self._webhooks.values())

    def get_deliveries(self, webhook_id: str = None) -> List[Delivery]:
        """Get deliveries, optionally filtered by webhook."""
        if webhook_id:
            return [d for d in self._deliveries if d.webhook_id == webhook_id]
        return self._deliveries.copy()

    def set_active(self, webhook_id: str, active: bool) -> bool:
        """Enable or disable a webhook."""
        if webhook_id not in self._webhooks:
            return False
        self._webhooks[webhook_id].active = active
        return True

    def _default_sender(self, url: str, payload: Dict) -> tuple[bool, int]:
        """Default sender (always succeeds)."""
        return True, 200
