"""Tests for Spreadsheet Stage 3 - Functions and Ranges"""
import pytest
from solution import Spreadsheet


class TestSpreadsheetStage3:
    def test_sum_function(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "10")
        sheet.set_cell("A2", "20")
        sheet.set_cell("A3", "30")
        sheet.set_cell("B1", "=SUM(A1:A3)")
        assert sheet.get_cell("B1") == 60.0

    def test_average_function(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "10")
        sheet.set_cell("A2", "20")
        sheet.set_cell("A3", "30")
        sheet.set_cell("B1", "=AVERAGE(A1:A3)")
        assert sheet.get_cell("B1") == 20.0

    def test_min_function(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "50")
        sheet.set_cell("A2", "10")
        sheet.set_cell("A3", "30")
        sheet.set_cell("B1", "=MIN(A1:A3)")
        assert sheet.get_cell("B1") == 10.0

    def test_max_function(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "50")
        sheet.set_cell("A2", "10")
        sheet.set_cell("A3", "30")
        sheet.set_cell("B1", "=MAX(A1:A3)")
        assert sheet.get_cell("B1") == 50.0

    def test_range_expansion(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "1")
        sheet.set_cell("A2", "2")
        sheet.set_cell("A3", "3")
        sheet.set_cell("A4", "4")
        sheet.set_cell("A5", "5")
        sheet.set_cell("B1", "=SUM(A1:A5)")
        assert sheet.get_cell("B1") == 15.0

    def test_2d_range(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "1")
        sheet.set_cell("A2", "2")
        sheet.set_cell("B1", "3")
        sheet.set_cell("B2", "4")
        sheet.set_cell("C1", "=SUM(A1:B2)")
        assert sheet.get_cell("C1") == 10.0

    def test_function_with_individual_cells(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "10")
        sheet.set_cell("B1", "20")
        sheet.set_cell("C1", "=SUM(A1,B1)")
        assert sheet.get_cell("C1") == 30.0

    def test_circular_in_range(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "10")
        sheet.set_cell("A2", "=SUM(A1:A3)")
        sheet.set_cell("A3", "30")
        assert sheet.get_cell("A2") == "#CIRCULAR!"

    def test_get_dependencies_with_range(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "=SUM(B1:B3)")
        deps = sheet.get_dependencies("A1")
        assert set(deps) == {"B1", "B2", "B3"}

    def test_formula_with_range(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "10")
        sheet.set_cell("A2", "20")
        sheet.set_cell("B1", "=SUM(A1:A2)+5")
        # Basic formula with function
        sheet.set_cell("C1", "=SUM(A1:A2)")
        assert sheet.get_cell("C1") == 30.0

    def test_lowercase_function(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "10")
        sheet.set_cell("A2", "20")
        sheet.set_cell("B1", "=sum(A1:A2)")
        assert sheet.get_cell("B1") == 30.0

    def test_missing_cell_in_range(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "10")
        # A2 is empty
        sheet.set_cell("A3", "30")
        sheet.set_cell("B1", "=SUM(A1:A3)")
        # Should error because A2 is missing
        assert sheet.get_cell("B1") == "#ERROR!"
