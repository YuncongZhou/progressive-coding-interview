"""
GPU Credit Management - Stage 3

Resource quotas and limits.

Design Rationale:
- Per-user quotas on GPU time
- Priority queuing for resources
- Fair scheduling
"""

from typing import Optional, List
from dataclasses import dataclass, field
from collections import deque
import time


@dataclass
class UsageRecord:
    user_id: str
    gpu_type: str
    start_time: float
    end_time: Optional[float]
    cost: float


@dataclass
class QueueEntry:
    user_id: str
    gpu_type: str
    priority: int
    enqueue_time: float


class CreditManager:
    """Credit manager with quotas and queuing."""

    GPU_RATES = {
        "A100": 0.01,
        "V100": 0.005,
        "T4": 0.002,
    }

    GPU_AVAILABILITY = {
        "A100": 2,
        "V100": 4,
        "T4": 8,
    }

    def __init__(self):
        self._balances: dict[str, float] = {}
        self._quotas: dict[str, dict[str, float]] = {}  # user -> {gpu: max_hours}
        self._usage_today: dict[str, dict[str, float]] = {}  # user -> {gpu: hours}
        self._active_sessions: dict[str, UsageRecord] = {}
        self._usage_history: List[UsageRecord] = []
        self._gpu_in_use: dict[str, int] = {gpu: 0 for gpu in self.GPU_AVAILABILITY}
        self._queue: deque[QueueEntry] = deque()

    def add_credits(self, user_id: str, amount: float) -> float:
        if amount < 0:
            raise ValueError("Amount must be non-negative")
        if user_id not in self._balances:
            self._balances[user_id] = 0.0
        self._balances[user_id] += amount
        return self._balances[user_id]

    def get_balance(self, user_id: str) -> float:
        return self._balances.get(user_id, 0.0)

    def set_quota(self, user_id: str, gpu_type: str, max_hours: float) -> None:
        """Set daily quota for user on specific GPU type."""
        if user_id not in self._quotas:
            self._quotas[user_id] = {}
        self._quotas[user_id][gpu_type] = max_hours

    def get_quota(self, user_id: str, gpu_type: str) -> Optional[float]:
        """Get user's quota for GPU type."""
        return self._quotas.get(user_id, {}).get(gpu_type)

    def get_usage_today(self, user_id: str, gpu_type: str) -> float:
        """Get user's usage today for GPU type (in hours)."""
        return self._usage_today.get(user_id, {}).get(gpu_type, 0.0)

    def check_quota(self, user_id: str, gpu_type: str) -> bool:
        """Check if user can use GPU (hasn't exceeded quota)."""
        quota = self.get_quota(user_id, gpu_type)
        if quota is None:
            return True  # No quota set
        usage = self.get_usage_today(user_id, gpu_type)
        return usage < quota

    def start_session(self, user_id: str, gpu_type: str, priority: int = 0) -> str:
        """
        Start or queue a GPU session.

        Returns "started", "queued", or "denied".
        """
        if gpu_type not in self.GPU_RATES:
            return "denied"

        if not self.check_quota(user_id, gpu_type):
            return "denied"

        min_balance = self.GPU_RATES[gpu_type] * 60
        if self.get_balance(user_id) < min_balance:
            return "denied"

        if user_id in self._active_sessions:
            return "denied"

        # Check availability
        if self._gpu_in_use[gpu_type] < self.GPU_AVAILABILITY[gpu_type]:
            self._start_session_now(user_id, gpu_type)
            return "started"
        else:
            self._queue.append(QueueEntry(
                user_id=user_id,
                gpu_type=gpu_type,
                priority=priority,
                enqueue_time=time.time()
            ))
            return "queued"

    def _start_session_now(self, user_id: str, gpu_type: str) -> None:
        self._gpu_in_use[gpu_type] += 1
        self._active_sessions[user_id] = UsageRecord(
            user_id=user_id,
            gpu_type=gpu_type,
            start_time=time.time(),
            end_time=None,
            cost=0.0
        )

    def end_session(self, user_id: str) -> Optional[float]:
        if user_id not in self._active_sessions:
            return None

        record = self._active_sessions.pop(user_id)
        record.end_time = time.time()
        self._gpu_in_use[record.gpu_type] -= 1

        duration = record.end_time - record.start_time
        rate = self.GPU_RATES[record.gpu_type]
        record.cost = duration * rate

        self._balances[user_id] = max(0, self.get_balance(user_id) - record.cost)
        self._usage_history.append(record)

        # Update daily usage
        if user_id not in self._usage_today:
            self._usage_today[user_id] = {}
        hours = duration / 3600
        self._usage_today[user_id][record.gpu_type] = \
            self._usage_today[user_id].get(record.gpu_type, 0.0) + hours

        # Process queue
        self._process_queue(record.gpu_type)

        return record.cost

    def _process_queue(self, gpu_type: str) -> None:
        """Process queue after a GPU becomes available."""
        # Sort by priority (higher first), then by time
        queue_list = list(self._queue)
        queue_list.sort(key=lambda e: (-e.priority, e.enqueue_time))

        for entry in queue_list:
            if entry.gpu_type != gpu_type:
                continue
            if self._gpu_in_use[gpu_type] >= self.GPU_AVAILABILITY[gpu_type]:
                break

            self._queue.remove(entry)
            self._start_session_now(entry.user_id, entry.gpu_type)

    def queue_position(self, user_id: str) -> Optional[int]:
        """Get user's position in queue (1-indexed)."""
        for i, entry in enumerate(self._queue):
            if entry.user_id == user_id:
                return i + 1
        return None

    def has_active_session(self, user_id: str) -> bool:
        return user_id in self._active_sessions

    def gpu_available(self, gpu_type: str) -> int:
        """Number of available GPUs of type."""
        return self.GPU_AVAILABILITY.get(gpu_type, 0) - self._gpu_in_use.get(gpu_type, 0)

    def reset_daily_usage(self) -> None:
        """Reset daily usage counters."""
        self._usage_today.clear()
