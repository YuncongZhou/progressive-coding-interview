"""
GPU Credit Management - Stage 2

Usage tracking and billing.

Design Rationale:
- Track GPU usage time
- Calculate costs based on GPU type
- Usage history for billing
"""

from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime
import time


@dataclass
class UsageRecord:
    """Record of GPU usage."""
    user_id: str
    gpu_type: str
    start_time: float
    end_time: Optional[float]
    cost: float


class CreditManager:
    """Credit manager with usage tracking."""

    # Cost per second for each GPU type
    GPU_RATES = {
        "A100": 0.01,
        "V100": 0.005,
        "T4": 0.002,
    }

    def __init__(self):
        self._balances: dict[str, float] = {}
        self._active_sessions: dict[str, UsageRecord] = {}  # user_id -> record
        self._usage_history: List[UsageRecord] = []

    def add_credits(self, user_id: str, amount: float) -> float:
        if amount < 0:
            raise ValueError("Amount must be non-negative")
        if user_id not in self._balances:
            self._balances[user_id] = 0.0
        self._balances[user_id] += amount
        return self._balances[user_id]

    def get_balance(self, user_id: str) -> float:
        return self._balances.get(user_id, 0.0)

    def start_session(self, user_id: str, gpu_type: str) -> bool:
        """
        Start a GPU session.

        Returns True if session started, False if insufficient credits or invalid GPU.
        """
        if gpu_type not in self.GPU_RATES:
            return False

        if user_id in self._active_sessions:
            return False  # Already has active session

        # Require minimum balance for one minute
        min_balance = self.GPU_RATES[gpu_type] * 60
        if self.get_balance(user_id) < min_balance:
            return False

        self._active_sessions[user_id] = UsageRecord(
            user_id=user_id,
            gpu_type=gpu_type,
            start_time=time.time(),
            end_time=None,
            cost=0.0
        )
        return True

    def end_session(self, user_id: str) -> Optional[float]:
        """
        End a GPU session and charge user.

        Returns cost if session ended, None if no active session.
        """
        if user_id not in self._active_sessions:
            return None

        record = self._active_sessions.pop(user_id)
        record.end_time = time.time()

        # Calculate cost
        duration = record.end_time - record.start_time
        rate = self.GPU_RATES[record.gpu_type]
        record.cost = duration * rate

        # Deduct from balance
        self._balances[user_id] = max(0, self.get_balance(user_id) - record.cost)

        # Save to history
        self._usage_history.append(record)

        return record.cost

    def get_session_cost(self, user_id: str) -> Optional[float]:
        """Get current cost of active session."""
        if user_id not in self._active_sessions:
            return None

        record = self._active_sessions[user_id]
        duration = time.time() - record.start_time
        return duration * self.GPU_RATES[record.gpu_type]

    def has_active_session(self, user_id: str) -> bool:
        """Check if user has active session."""
        return user_id in self._active_sessions

    def get_usage_history(self, user_id: str) -> List[UsageRecord]:
        """Get user's usage history."""
        return [r for r in self._usage_history if r.user_id == user_id]

    def get_total_usage_cost(self, user_id: str) -> float:
        """Get total historical usage cost for user."""
        return sum(r.cost for r in self.get_usage_history(user_id))

    def user_count(self) -> int:
        return len(self._balances)

    def active_session_count(self) -> int:
        """Return number of active sessions."""
        return len(self._active_sessions)
