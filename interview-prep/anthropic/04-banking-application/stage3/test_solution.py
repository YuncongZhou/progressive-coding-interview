"""Tests for Banking Application Stage 3"""
import pytest
from solution import Bank


class TestBankStage3:
    def test_transfer_success(self):
        bank = Bank()
        bank.create_account("acc1", 100)
        bank.create_account("acc2", 50)

        result = bank.transfer("acc1", "acc2", 30)
        assert result is True
        assert bank.get_balance("acc1") == 70
        assert bank.get_balance("acc2") == 80

    def test_transfer_insufficient_funds(self):
        bank = Bank()
        bank.create_account("acc1", 100)
        bank.create_account("acc2", 50)

        result = bank.transfer("acc1", "acc2", 150)
        assert result is False
        assert bank.get_balance("acc1") == 100  # unchanged
        assert bank.get_balance("acc2") == 50   # unchanged

    def test_transfer_nonexistent_source(self):
        bank = Bank()
        bank.create_account("acc2", 50)
        result = bank.transfer("nonexistent", "acc2", 30)
        assert result is False

    def test_transfer_nonexistent_destination(self):
        bank = Bank()
        bank.create_account("acc1", 100)
        result = bank.transfer("acc1", "nonexistent", 30)
        assert result is False
