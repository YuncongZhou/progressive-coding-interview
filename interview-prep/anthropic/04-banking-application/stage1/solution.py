"""
Banking Application - Stage 1

Basic banking with account creation, deposits, withdrawals.

Design Rationale:
- Accounts stored in dict {account_id: {"balance": float}}
- All monetary operations validate account existence
- Withdrawals fail if insufficient funds
"""


class Bank:
    """Simple banking system."""

    def __init__(self):
        self._accounts: dict[str, dict] = {}

    def create_account(self, account_id: str, initial_balance: float = 0) -> bool:
        """Creates account. Returns False if already exists."""
        if account_id in self._accounts:
            return False
        self._accounts[account_id] = {"balance": initial_balance}
        return True

    def deposit(self, account_id: str, amount: float) -> float | None:
        """Deposits amount. Returns new balance or None if account doesn't exist."""
        if account_id not in self._accounts:
            return None
        self._accounts[account_id]["balance"] += amount
        return self._accounts[account_id]["balance"]

    def withdraw(self, account_id: str, amount: float) -> float | None:
        """Withdraws if sufficient funds. Returns new balance or None if insufficient/not found."""
        if account_id not in self._accounts:
            return None
        if self._accounts[account_id]["balance"] < amount:
            return None
        self._accounts[account_id]["balance"] -= amount
        return self._accounts[account_id]["balance"]

    def get_balance(self, account_id: str) -> float | None:
        """Returns balance or None if not found."""
        if account_id not in self._accounts:
            return None
        return self._accounts[account_id]["balance"]
