"""
Webhook Platform - Stage 2

Retry logic and backoff.

Design Rationale:
- Retry failed deliveries
- Exponential backoff
- Max retry attempts
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
    RETRYING = "retrying"


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
    attempts: int = 1
    next_retry_at: Optional[float] = None
    response_code: Optional[int] = None


class WebhookPlatform:
    """Webhook platform with retry support."""

    MAX_RETRIES = 3
    BASE_DELAY = 1.0  # seconds

    def __init__(self, sender: Callable[[str, Dict], tuple[bool, int]] = None):
        self._webhooks: dict[str, Webhook] = {}
        self._deliveries: dict[str, Delivery] = {}
        self._pending_retries: List[str] = []
        self._sender = sender or self._default_sender

    def register(self, url: str, events: List[str]) -> str:
        webhook_id = str(uuid.uuid4())[:8]
        self._webhooks[webhook_id] = Webhook(
            id=webhook_id,
            url=url,
            events=events,
            created_at=time.time()
        )
        return webhook_id

    def unregister(self, webhook_id: str) -> bool:
        if webhook_id not in self._webhooks:
            return False
        del self._webhooks[webhook_id]
        return True

    def trigger(self, event: str, payload: Dict[str, Any]) -> int:
        count = 0
        for webhook in self._webhooks.values():
            if not webhook.active:
                continue
            if event not in webhook.events and "*" not in webhook.events:
                continue

            delivery = self._attempt_delivery(webhook, event, payload)
            self._deliveries[delivery.id] = delivery
            count += 1

        return count

    def _attempt_delivery(self, webhook: Webhook, event: str,
                          payload: Dict, attempt: int = 1) -> Delivery:
        delivery_id = str(uuid.uuid4())[:8]
        success, code = self._sender(webhook.url, payload)

        if success:
            return Delivery(
                id=delivery_id,
                webhook_id=webhook.id,
                event=event,
                payload=payload,
                status=DeliveryStatus.SUCCESS,
                attempted_at=time.time(),
                attempts=attempt,
                response_code=code
            )
        else:
            status = DeliveryStatus.RETRYING if attempt < self.MAX_RETRIES else DeliveryStatus.FAILED
            delay = self.BASE_DELAY * (2 ** (attempt - 1))  # Exponential backoff

            delivery = Delivery(
                id=delivery_id,
                webhook_id=webhook.id,
                event=event,
                payload=payload,
                status=status,
                attempted_at=time.time(),
                attempts=attempt,
                next_retry_at=time.time() + delay if status == DeliveryStatus.RETRYING else None,
                response_code=code
            )

            if status == DeliveryStatus.RETRYING:
                self._pending_retries.append(delivery_id)

            return delivery

    def process_retries(self) -> int:
        """Process pending retries. Returns count processed."""
        now = time.time()
        processed = 0

        for delivery_id in list(self._pending_retries):
            delivery = self._deliveries.get(delivery_id)
            if not delivery or delivery.next_retry_at is None:
                self._pending_retries.remove(delivery_id)
                continue

            if now >= delivery.next_retry_at:
                self._pending_retries.remove(delivery_id)
                webhook = self._webhooks.get(delivery.webhook_id)
                if webhook:
                    new_delivery = self._attempt_delivery(
                        webhook, delivery.event, delivery.payload,
                        attempt=delivery.attempts + 1
                    )
                    self._deliveries[new_delivery.id] = new_delivery
                    processed += 1

        return processed

    def get_pending_retries(self) -> List[Delivery]:
        """Get list of deliveries pending retry."""
        return [self._deliveries[did] for did in self._pending_retries
                if did in self._deliveries]

    def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        return self._webhooks.get(webhook_id)

    def get_delivery(self, delivery_id: str) -> Optional[Delivery]:
        return self._deliveries.get(delivery_id)

    def get_deliveries(self, webhook_id: str = None,
                       status: DeliveryStatus = None) -> List[Delivery]:
        result = list(self._deliveries.values())
        if webhook_id:
            result = [d for d in result if d.webhook_id == webhook_id]
        if status:
            result = [d for d in result if d.status == status]
        return result

    def list_webhooks(self) -> List[Webhook]:
        return list(self._webhooks.values())

    def set_active(self, webhook_id: str, active: bool) -> bool:
        if webhook_id not in self._webhooks:
            return False
        self._webhooks[webhook_id].active = active
        return True

    def _default_sender(self, url: str, payload: Dict) -> tuple[bool, int]:
        return True, 200
