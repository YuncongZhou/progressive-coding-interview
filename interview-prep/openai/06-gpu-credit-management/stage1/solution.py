"""
GPU Credit Management - Stage 1

Basic credit management system.

Design Rationale:
- Track user credit balances
- Simple add/deduct operations
- Balance checking
"""

from typing import Optional


class CreditManager:
    """Basic GPU credit manager."""

    def __init__(self):
        self._balances: dict[str, float] = {}

    def add_credits(self, user_id: str, amount: float) -> float:
        """
        Add credits to user account.

        Returns new balance.
        """
        if amount < 0:
            raise ValueError("Amount must be non-negative")

        if user_id not in self._balances:
            self._balances[user_id] = 0.0

        self._balances[user_id] += amount
        return self._balances[user_id]

    def deduct_credits(self, user_id: str, amount: float) -> bool:
        """
        Deduct credits from user account.

        Returns True if successful, False if insufficient balance.
        """
        if amount < 0:
            raise ValueError("Amount must be non-negative")

        balance = self._balances.get(user_id, 0.0)
        if balance < amount:
            return False

        self._balances[user_id] = balance - amount
        return True

    def get_balance(self, user_id: str) -> float:
        """Get user's current balance."""
        return self._balances.get(user_id, 0.0)

    def has_credits(self, user_id: str, amount: float) -> bool:
        """Check if user has enough credits."""
        return self.get_balance(user_id) >= amount

    def user_count(self) -> int:
        """Return number of users with accounts."""
        return len(self._balances)

    def total_credits(self) -> float:
        """Return total credits across all users."""
        return sum(self._balances.values())
