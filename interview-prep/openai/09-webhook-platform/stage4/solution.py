"""
Webhook Platform - Stage 4

Rate limiting and analytics.

Design Rationale:
- Rate limit per webhook
- Track delivery metrics
- Generate reports
"""

from typing import Optional, List, Callable, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import time
import uuid
import hmac
import hashlib
import json


class DeliveryStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"


@dataclass
class Webhook:
    id: str
    url: str
    events: List[str]
    secret: str
    created_at: float
    active: bool = True
    rate_limit: int = 100  # per minute


@dataclass
class Delivery:
    id: str
    webhook_id: str
    event: str
    payload: Dict[str, Any]
    signature: str
    status: DeliveryStatus
    attempted_at: float
    latency_ms: Optional[float] = None
    response_code: Optional[int] = None


@dataclass
class WebhookStats:
    total_deliveries: int
    successful: int
    failed: int
    rate_limited: int
    avg_latency_ms: float
    success_rate: float


class WebhookPlatform:
    """Webhook platform with rate limiting and analytics."""

    def __init__(self, sender: Callable[[str, Dict, str], tuple[bool, int, float]] = None):
        """
        Args:
            sender: Function(url, payload, signature) -> (success, code, latency_ms)
        """
        self._webhooks: dict[str, Webhook] = {}
        self._deliveries: List[Delivery] = []
        self._sender = sender or self._default_sender
        self._rate_tracking: dict[str, List[float]] = defaultdict(list)

    def register(self, url: str, events: List[str],
                 secret: str = None, rate_limit: int = 100) -> tuple[str, str]:
        webhook_id = str(uuid.uuid4())[:8]
        secret = secret or str(uuid.uuid4())

        self._webhooks[webhook_id] = Webhook(
            id=webhook_id,
            url=url,
            events=events,
            secret=secret,
            created_at=time.time(),
            rate_limit=rate_limit
        )
        return webhook_id, secret

    def unregister(self, webhook_id: str) -> bool:
        if webhook_id not in self._webhooks:
            return False
        del self._webhooks[webhook_id]
        return True

    def _check_rate_limit(self, webhook_id: str, rate_limit: int) -> bool:
        """Check if webhook is within rate limit."""
        now = time.time()
        minute_ago = now - 60

        # Clean old entries
        self._rate_tracking[webhook_id] = [
            t for t in self._rate_tracking[webhook_id] if t > minute_ago
        ]

        return len(self._rate_tracking[webhook_id]) < rate_limit

    def sign_payload(self, secret: str, payload: Dict[str, Any]) -> str:
        payload_str = json.dumps(payload, sort_keys=True)
        return hmac.new(secret.encode(), payload_str.encode(), hashlib.sha256).hexdigest()

    def trigger(self, event: str, payload: Dict[str, Any]) -> int:
        count = 0
        for webhook in self._webhooks.values():
            if not webhook.active:
                continue
            if event not in webhook.events and "*" not in webhook.events:
                continue

            delivery_id = str(uuid.uuid4())[:8]

            if not self._check_rate_limit(webhook.id, webhook.rate_limit):
                self._deliveries.append(Delivery(
                    id=delivery_id,
                    webhook_id=webhook.id,
                    event=event,
                    payload=payload,
                    signature="",
                    status=DeliveryStatus.RATE_LIMITED,
                    attempted_at=time.time()
                ))
                count += 1
                continue

            self._rate_tracking[webhook.id].append(time.time())
            signature = self.sign_payload(webhook.secret, payload)
            success, code, latency = self._sender(webhook.url, payload, signature)

            self._deliveries.append(Delivery(
                id=delivery_id,
                webhook_id=webhook.id,
                event=event,
                payload=payload,
                signature=signature,
                status=DeliveryStatus.SUCCESS if success else DeliveryStatus.FAILED,
                attempted_at=time.time(),
                latency_ms=latency,
                response_code=code
            ))
            count += 1

        return count

    def get_stats(self, webhook_id: str) -> WebhookStats:
        """Get statistics for a webhook."""
        deliveries = [d for d in self._deliveries if d.webhook_id == webhook_id]

        if not deliveries:
            return WebhookStats(0, 0, 0, 0, 0.0, 0.0)

        successful = sum(1 for d in deliveries if d.status == DeliveryStatus.SUCCESS)
        failed = sum(1 for d in deliveries if d.status == DeliveryStatus.FAILED)
        rate_limited = sum(1 for d in deliveries if d.status == DeliveryStatus.RATE_LIMITED)

        latencies = [d.latency_ms for d in deliveries if d.latency_ms is not None]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

        total = len(deliveries)
        success_rate = successful / total if total > 0 else 0.0

        return WebhookStats(
            total_deliveries=total,
            successful=successful,
            failed=failed,
            rate_limited=rate_limited,
            avg_latency_ms=avg_latency,
            success_rate=success_rate
        )

    def get_all_stats(self) -> Dict[str, WebhookStats]:
        """Get stats for all webhooks."""
        return {wid: self.get_stats(wid) for wid in self._webhooks}

    def get_top_webhooks(self, limit: int = 10) -> List[tuple[str, int]]:
        """Get most active webhooks by delivery count."""
        counts: Dict[str, int] = defaultdict(int)
        for d in self._deliveries:
            counts[d.webhook_id] += 1
        return sorted(counts.items(), key=lambda x: -x[1])[:limit]

    def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        return self._webhooks.get(webhook_id)

    def get_deliveries(self, webhook_id: str = None,
                       status: DeliveryStatus = None) -> List[Delivery]:
        result = self._deliveries
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

    def _default_sender(self, url: str, payload: Dict, signature: str) -> tuple[bool, int, float]:
        return True, 200, 10.0
