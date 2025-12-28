"""
Banking Application - Stage 4

Banking with transaction fees, daily limits, and rollback.

Design Rationale:
- Transaction fees as percentage of withdrawal/transfer amount
- Daily limits tracked per account
- Rollback reverses a transaction within 24 hours (timestamp-based)
"""


class Bank:
    """Banking system with fees, limits, and rollback."""

    def __init__(self):
        self._accounts: dict[str, dict] = {}
        self._tx_counter = 0
        self._fee_percent = 0.0
        self._transactions: dict[str, dict] = {}  # tx_id -> transaction details

    def _next_timestamp(self) -> int:
        self._tx_counter += 1
        return self._tx_counter

    def _generate_tx_id(self) -> str:
        return f"tx_{self._tx_counter}"

    def create_account(self, account_id: str, initial_balance: float = 0) -> bool:
        if account_id in self._accounts:
            return False
        self._accounts[account_id] = {
            "balance": initial_balance,
            "transactions": [],
            "daily_limit": None,
            "daily_withdrawn": {}  # day -> amount
        }
        if initial_balance > 0:
            tx_id = self._generate_tx_id()
            self._accounts[account_id]["transactions"].append({
                "tx_id": tx_id,
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
        tx_id = self._generate_tx_id()
        timestamp = self._next_timestamp()
        tx = {
            "tx_id": tx_id,
            "type": "deposit",
            "amount": amount,
            "timestamp": timestamp,
            "balance_after": new_balance,
            "account_id": account_id
        }
        self._accounts[account_id]["transactions"].append(tx)
        self._transactions[tx_id] = tx
        return new_balance

    def withdraw(self, account_id: str, amount: float) -> float | None:
        if account_id not in self._accounts:
            return None

        fee = amount * (self._fee_percent / 100)
        total = amount + fee

        if self._accounts[account_id]["balance"] < total:
            return None

        self._accounts[account_id]["balance"] -= total
        new_balance = self._accounts[account_id]["balance"]
        tx_id = self._generate_tx_id()
        timestamp = self._next_timestamp()
        tx = {
            "tx_id": tx_id,
            "type": "withdrawal",
            "amount": amount,
            "fee": fee,
            "timestamp": timestamp,
            "balance_after": new_balance,
            "account_id": account_id
        }
        self._accounts[account_id]["transactions"].append(tx)
        self._transactions[tx_id] = tx
        return new_balance

    def get_balance(self, account_id: str) -> float | None:
        if account_id not in self._accounts:
            return None
        return self._accounts[account_id]["balance"]

    def get_transaction_history(self, account_id: str) -> list[dict]:
        if account_id not in self._accounts:
            return []
        return self._accounts[account_id]["transactions"].copy()

    def get_transactions_by_type(self, account_id: str, tx_type: str) -> list[dict]:
        if account_id not in self._accounts:
            return []
        return [tx for tx in self._accounts[account_id]["transactions"] if tx["type"] == tx_type]

    def transfer(self, from_account: str, to_account: str, amount: float) -> bool:
        if from_account not in self._accounts or to_account not in self._accounts:
            return False

        fee = amount * (self._fee_percent / 100)
        total = amount + fee

        if self._accounts[from_account]["balance"] < total:
            return False

        timestamp = self._next_timestamp()
        tx_id = self._generate_tx_id()

        self._accounts[from_account]["balance"] -= total
        self._accounts[from_account]["transactions"].append({
            "tx_id": tx_id,
            "type": "transfer_out",
            "amount": amount,
            "fee": fee,
            "timestamp": timestamp,
            "balance_after": self._accounts[from_account]["balance"],
            "to_account": to_account
        })

        self._accounts[to_account]["balance"] += amount
        self._accounts[to_account]["transactions"].append({
            "tx_id": tx_id,
            "type": "transfer_in",
            "amount": amount,
            "timestamp": timestamp,
            "balance_after": self._accounts[to_account]["balance"],
            "from_account": from_account
        })

        return True

    def set_transaction_fee(self, fee_percent: float) -> None:
        """Sets fee percentage for withdrawals and transfers."""
        self._fee_percent = fee_percent

    def set_daily_limit(self, account_id: str, limit: float) -> bool:
        """Sets daily withdrawal limit for account."""
        if account_id not in self._accounts:
            return False
        self._accounts[account_id]["daily_limit"] = limit
        return True

    def rollback_transaction(self, transaction_id: str) -> bool:
        """Reverses a transaction if within 24 hours."""
        if transaction_id not in self._transactions:
            return False

        tx = self._transactions[transaction_id]
        current_time = self._tx_counter

        # Check 24-hour limit (assuming 1 unit = 1 hour)
        if current_time - tx["timestamp"] > 24:
            return False

        account_id = tx["account_id"]

        if tx["type"] == "deposit":
            # Reverse deposit: subtract amount
            if self._accounts[account_id]["balance"] < tx["amount"]:
                return False
            self._accounts[account_id]["balance"] -= tx["amount"]
        elif tx["type"] == "withdrawal":
            # Reverse withdrawal: add back amount + fee
            total_refund = tx["amount"] + tx.get("fee", 0)
            self._accounts[account_id]["balance"] += total_refund

        # Record rollback
        rollback_tx = {
            "tx_id": self._generate_tx_id(),
            "type": "rollback",
            "original_tx_id": transaction_id,
            "timestamp": self._next_timestamp(),
            "balance_after": self._accounts[account_id]["balance"]
        }
        self._accounts[account_id]["transactions"].append(rollback_tx)

        del self._transactions[transaction_id]
        return True
