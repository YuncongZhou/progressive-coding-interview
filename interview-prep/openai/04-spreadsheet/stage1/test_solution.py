"""Tests for Spreadsheet Stage 1"""
import pytest
from solution import Spreadsheet


class TestSpreadsheetStage1:
    def test_set_and_get_number(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "42")
        assert sheet.get_cell("A1") == 42.0

    def test_reference(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "10")
        sheet.set_cell("B1", "=A1")
        assert sheet.get_cell("B1") == 10.0

    def test_formula_addition(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "10")
        sheet.set_cell("A2", "20")
        sheet.set_cell("A3", "=A1+A2")
        assert sheet.get_cell("A3") == 30.0

    def test_formula_subtraction(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "50")
        sheet.set_cell("A2", "30")
        sheet.set_cell("A3", "=A1-A2")
        assert sheet.get_cell("A3") == 20.0

    def test_formula_multiplication(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "5")
        sheet.set_cell("A2", "4")
        sheet.set_cell("A3", "=A1*A2")
        assert sheet.get_cell("A3") == 20.0

    def test_formula_division(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "20")
        sheet.set_cell("A2", "4")
        sheet.set_cell("A3", "=A1/A2")
        assert sheet.get_cell("A3") == 5.0

    def test_empty_cell(self):
        sheet = Spreadsheet()
        assert sheet.get_cell("A1") is None

    def test_chain_reference(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "5")
        sheet.set_cell("B1", "=A1")
        sheet.set_cell("C1", "=B1+10")
        assert sheet.get_cell("C1") == 15.0
