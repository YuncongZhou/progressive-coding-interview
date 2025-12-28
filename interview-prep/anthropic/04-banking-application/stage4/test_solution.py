"""Tests for Banking Application Stage 4"""
import pytest
from solution import Bank


class TestBankStage4:
    def test_set_transaction_fee(self):
        bank = Bank()
        bank.set_transaction_fee(2.0)  # 2% fee
        bank.create_account("acc1", 100)

        # Withdraw 50, fee = 1, total deducted = 51
        balance = bank.withdraw("acc1", 50)
        assert balance == 49

    def test_set_daily_limit(self):
        bank = Bank()
        bank.create_account("acc1", 100)
        result = bank.set_daily_limit("acc1", 50)
        assert result is True

    def test_rollback_deposit(self):
        bank = Bank()
        bank.create_account("acc1", 0)
        bank.deposit("acc1", 100)

        history = bank.get_transaction_history("acc1")
        tx_id = history[0]["tx_id"]

        result = bank.rollback_transaction(tx_id)
        assert result is True
        assert bank.get_balance("acc1") == 0

    def test_rollback_withdrawal(self):
        bank = Bank()
        bank.set_transaction_fee(2.0)
        bank.create_account("acc1", 100)
        bank.withdraw("acc1", 50)  # 50 + 1 fee = 51 deducted

        history = bank.get_transaction_history("acc1")
        tx_id = [tx for tx in history if tx["type"] == "withdrawal"][0]["tx_id"]

        result = bank.rollback_transaction(tx_id)
        assert result is True
        assert bank.get_balance("acc1") == 100  # original balance restored

    def test_rollback_expired(self):
        bank = Bank()
        bank.create_account("acc1", 0)
        bank.deposit("acc1", 100)

        history = bank.get_transaction_history("acc1")
        tx_id = history[0]["tx_id"]

        # Simulate time passing (more than 24 hours)
        for _ in range(30):
            bank.deposit("acc1", 1)  # advances timestamp

        result = bank.rollback_transaction(tx_id)
        assert result is False

    def test_transfer_with_fee(self):
        bank = Bank()
        bank.set_transaction_fee(5.0)  # 5% fee
        bank.create_account("acc1", 100)
        bank.create_account("acc2", 0)

        # Transfer 50, fee = 2.5, total from acc1 = 52.5
        result = bank.transfer("acc1", "acc2", 50)
        assert result is True
        assert bank.get_balance("acc1") == 47.5
        assert bank.get_balance("acc2") == 50  # recipient gets full amount
