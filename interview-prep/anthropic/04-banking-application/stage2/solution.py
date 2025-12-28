"""
Banking Application - Stage 2

Banking with transaction history.

Design Rationale:
- Each account tracks a list of transactions
- Transaction includes type, amount, timestamp, balance_after
"""

import time


class Bank:
    """Banking system with transaction history."""

    def __init__(self):
        self._accounts: dict[str, dict] = {}
        self._tx_counter = 0

    def _next_timestamp(self) -> int:
        self._tx_counter += 1
        return self._tx_counter

    def create_account(self, account_id: str, initial_balance: float = 0) -> bool:
        if account_id in self._accounts:
            return False
        self._accounts[account_id] = {"balance": initial_balance, "transactions": []}
        if initial_balance > 0:
            self._accounts[account_id]["transactions"].append({
                "type": "deposit",
                "amount": initial_balance,
                "timestamp": self._next_timestamp(),
                "balance_after": initial_balance
            })
        return True

    def deposit(self, account_id: str, amount: float) -> float | None:
        if account_id not in self._accounts:
            return None
        self._accounts[account_id]["balance"] += amount
        new_balance = self._accounts[account_id]["balance"]
        self._accounts[account_id]["transactions"].append({
            "type": "deposit",
            "amount": amount,
            "timestamp": self._next_timestamp(),
            "balance_after": new_balance
        })
        return new_balance

    def withdraw(self, account_id: str, amount: float) -> float | None:
        if account_id not in self._accounts:
            return None
        if self._accounts[account_id]["balance"] < amount:
            return None
        self._accounts[account_id]["balance"] -= amount
        new_balance = self._accounts[account_id]["balance"]
        self._accounts[account_id]["transactions"].append({
            "type": "withdrawal",
            "amount": amount,
            "timestamp": self._next_timestamp(),
            "balance_after": new_balance
        })
        return new_balance

    def get_balance(self, account_id: str) -> float | None:
        if account_id not in self._accounts:
            return None
        return self._accounts[account_id]["balance"]

    def get_transaction_history(self, account_id: str) -> list[dict]:
        """Returns list of transactions: {type, amount, timestamp, balance_after}"""
        if account_id not in self._accounts:
            return []
        return self._accounts[account_id]["transactions"].copy()

    def get_transactions_by_type(self, account_id: str, tx_type: str) -> list[dict]:
        """Filters transactions by type ('deposit' or 'withdrawal')."""
        if account_id not in self._accounts:
            return []
        return [tx for tx in self._accounts[account_id]["transactions"] if tx["type"] == tx_type]
