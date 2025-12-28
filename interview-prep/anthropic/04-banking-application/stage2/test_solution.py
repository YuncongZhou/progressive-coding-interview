"""Tests for Banking Application Stage 2"""
import pytest
from solution import Bank


class TestBankStage2:
    def test_transaction_history(self):
        bank = Bank()
        bank.create_account("acc1", 100)
        bank.deposit("acc1", 50)
        bank.withdraw("acc1", 30)

        history = bank.get_transaction_history("acc1")
        assert len(history) == 3
        assert history[0]["type"] == "deposit"
        assert history[0]["amount"] == 100
        assert history[1]["type"] == "deposit"
        assert history[1]["amount"] == 50
        assert history[2]["type"] == "withdrawal"
        assert history[2]["amount"] == 30

    def test_get_transactions_by_type(self):
        bank = Bank()
        bank.create_account("acc1", 100)
        bank.deposit("acc1", 50)
        bank.withdraw("acc1", 30)

        deposits = bank.get_transactions_by_type("acc1", "deposit")
        assert len(deposits) == 2

        withdrawals = bank.get_transactions_by_type("acc1", "withdrawal")
        assert len(withdrawals) == 1

    def test_transaction_has_balance_after(self):
        bank = Bank()
        bank.create_account("acc1", 100)
        bank.deposit("acc1", 50)

        history = bank.get_transaction_history("acc1")
        assert history[0]["balance_after"] == 100
        assert history[1]["balance_after"] == 150
