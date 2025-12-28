"""
GPU Credit Management - Stage 4

Billing and reporting.

Design Rationale:
- Generate invoices
- Usage analytics
- Cost predictions
"""

from typing import Optional, List
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime, timedelta
import time


@dataclass
class UsageRecord:
    user_id: str
    gpu_type: str
    start_time: float
    end_time: Optional[float]
    cost: float


@dataclass
class Invoice:
    user_id: str
    period_start: datetime
    period_end: datetime
    total_cost: float
    usage_by_gpu: dict[str, float]  # gpu_type -> hours
    records: List[UsageRecord]


@dataclass
class UsageStats:
    total_hours: float
    total_cost: float
    avg_session_hours: float
    gpu_breakdown: dict[str, float]


class CreditManager:
    """Full-featured credit management system."""

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
        self._quotas: dict[str, dict[str, float]] = {}
        self._usage_today: dict[str, dict[str, float]] = {}
        self._active_sessions: dict[str, UsageRecord] = {}
        self._usage_history: List[UsageRecord] = []
        self._gpu_in_use: dict[str, int] = {gpu: 0 for gpu in self.GPU_AVAILABILITY}
        self._queue: deque = deque()
        self._invoices: List[Invoice] = []

    def add_credits(self, user_id: str, amount: float) -> float:
        if amount < 0:
            raise ValueError("Amount must be non-negative")
        if user_id not in self._balances:
            self._balances[user_id] = 0.0
        self._balances[user_id] += amount
        return self._balances[user_id]

    def get_balance(self, user_id: str) -> float:
        return self._balances.get(user_id, 0.0)

    def start_session(self, user_id: str, gpu_type: str) -> str:
        if gpu_type not in self.GPU_RATES:
            return "denied"

        min_balance = self.GPU_RATES[gpu_type] * 60
        if self.get_balance(user_id) < min_balance:
            return "denied"

        if user_id in self._active_sessions:
            return "denied"

        if self._gpu_in_use[gpu_type] < self.GPU_AVAILABILITY[gpu_type]:
            self._gpu_in_use[gpu_type] += 1
            self._active_sessions[user_id] = UsageRecord(
                user_id=user_id,
                gpu_type=gpu_type,
                start_time=time.time(),
                end_time=None,
                cost=0.0
            )
            return "started"
        return "denied"

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

        return record.cost

    def generate_invoice(self, user_id: str, start: datetime,
                         end: datetime) -> Invoice:
        """Generate invoice for time period."""
        start_ts = start.timestamp()
        end_ts = end.timestamp()

        relevant_records = [
            r for r in self._usage_history
            if r.user_id == user_id and r.end_time
            and start_ts <= r.start_time <= end_ts
        ]

        usage_by_gpu: dict[str, float] = {}
        total_cost = 0.0

        for record in relevant_records:
            duration_hours = (record.end_time - record.start_time) / 3600
            usage_by_gpu[record.gpu_type] = \
                usage_by_gpu.get(record.gpu_type, 0) + duration_hours
            total_cost += record.cost

        invoice = Invoice(
            user_id=user_id,
            period_start=start,
            period_end=end,
            total_cost=total_cost,
            usage_by_gpu=usage_by_gpu,
            records=relevant_records
        )
        self._invoices.append(invoice)
        return invoice

    def get_usage_stats(self, user_id: str) -> UsageStats:
        """Get usage statistics for user."""
        records = [r for r in self._usage_history
                   if r.user_id == user_id and r.end_time]

        if not records:
            return UsageStats(
                total_hours=0,
                total_cost=0,
                avg_session_hours=0,
                gpu_breakdown={}
            )

        total_seconds = sum(r.end_time - r.start_time for r in records)
        total_cost = sum(r.cost for r in records)

        gpu_breakdown: dict[str, float] = {}
        for record in records:
            hours = (record.end_time - record.start_time) / 3600
            gpu_breakdown[record.gpu_type] = \
                gpu_breakdown.get(record.gpu_type, 0) + hours

        return UsageStats(
            total_hours=total_seconds / 3600,
            total_cost=total_cost,
            avg_session_hours=(total_seconds / 3600) / len(records),
            gpu_breakdown=gpu_breakdown
        )

    def estimate_monthly_cost(self, user_id: str) -> float:
        """Estimate monthly cost based on recent usage."""
        now = time.time()
        week_ago = now - (7 * 24 * 3600)

        recent_records = [
            r for r in self._usage_history
            if r.user_id == user_id and r.end_time and r.start_time >= week_ago
        ]

        weekly_cost = sum(r.cost for r in recent_records)
        return weekly_cost * 4.33  # ~weeks per month

    def get_top_users(self, limit: int = 10) -> List[tuple[str, float]]:
        """Get top users by usage cost."""
        user_costs: dict[str, float] = {}

        for record in self._usage_history:
            if record.end_time:
                user_costs[record.user_id] = \
                    user_costs.get(record.user_id, 0) + record.cost

        sorted_users = sorted(user_costs.items(), key=lambda x: -x[1])
        return sorted_users[:limit]

    def get_gpu_utilization(self) -> dict[str, float]:
        """Get current GPU utilization percentage."""
        return {
            gpu: (self._gpu_in_use[gpu] / self.GPU_AVAILABILITY[gpu]) * 100
            for gpu in self.GPU_AVAILABILITY
        }

    def has_active_session(self, user_id: str) -> bool:
        return user_id in self._active_sessions

    def user_count(self) -> int:
        return len(self._balances)
