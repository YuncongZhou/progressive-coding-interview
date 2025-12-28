"""Tests for Banking Application Stage 1"""
import pytest
from solution import Bank


class TestBankStage1:
    def test_create_account(self):
        bank = Bank()
        assert bank.create_account("acc1", 100) is True
        assert bank.get_balance("acc1") == 100

    def test_create_duplicate_account_fails(self):
        bank = Bank()
        bank.create_account("acc1")
        assert bank.create_account("acc1") is False

    def test_deposit(self):
        bank = Bank()
        bank.create_account("acc1", 100)
        balance = bank.deposit("acc1", 50)
        assert balance == 150

    def test_deposit_nonexistent_account(self):
        bank = Bank()
        assert bank.deposit("nonexistent", 50) is None

    def test_withdraw(self):
        bank = Bank()
        bank.create_account("acc1", 100)
        balance = bank.withdraw("acc1", 30)
        assert balance == 70

    def test_withdraw_insufficient_funds(self):
        bank = Bank()
        bank.create_account("acc1", 100)
        assert bank.withdraw("acc1", 150) is None
        assert bank.get_balance("acc1") == 100  # unchanged

    def test_withdraw_nonexistent_account(self):
        bank = Bank()
        assert bank.withdraw("nonexistent", 50) is None

    def test_get_balance(self):
        bank = Bank()
        bank.create_account("acc1", 100)
        assert bank.get_balance("acc1") == 100

    def test_get_balance_nonexistent(self):
        bank = Bank()
        assert bank.get_balance("nonexistent") is None
