"""Tests for Spreadsheet Stage 2 - Circular Dependency Detection"""
import pytest
from solution import Spreadsheet


class TestSpreadsheetStage2:
    def test_basic_formula(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "10")
        sheet.set_cell("A2", "=A1+5")
        assert sheet.get_cell("A2") == 15.0

    def test_direct_circular(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "=A1")
        assert sheet.get_cell("A1") == "#CIRCULAR!"

    def test_indirect_circular(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "=B1")
        sheet.set_cell("B1", "=C1")
        sheet.set_cell("C1", "=A1")
        assert sheet.get_cell("A1") == "#CIRCULAR!"
        assert sheet.get_cell("B1") == "#CIRCULAR!"
        assert sheet.get_cell("C1") == "#CIRCULAR!"

    def test_no_circular(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "10")
        sheet.set_cell("B1", "=A1")
        sheet.set_cell("C1", "=B1+A1")
        assert sheet.get_cell("C1") == 20.0

    def test_missing_reference(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "=B1")
        assert sheet.get_cell("A1") == "#ERROR!"

    def test_get_dependencies_simple(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "=B1+C1")
        deps = sheet.get_dependencies("A1")
        assert set(deps) == {"B1", "C1"}

    def test_get_dependencies_number(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "42")
        assert sheet.get_dependencies("A1") == []

    def test_get_dependencies_empty(self):
        sheet = Spreadsheet()
        assert sheet.get_dependencies("A1") == []

    def test_division_by_zero(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "10")
        sheet.set_cell("B1", "0")
        sheet.set_cell("C1", "=A1/B1")
        assert sheet.get_cell("C1") == "#ERROR!"

    def test_complex_dependencies(self):
        sheet = Spreadsheet()
        sheet.set_cell("A1", "1")
        sheet.set_cell("B1", "=A1+1")
        sheet.set_cell("C1", "=B1+A1")
        sheet.set_cell("D1", "=C1*2")
        assert sheet.get_cell("D1") == 6.0
        deps = sheet.get_dependencies("C1")
        assert set(deps) == {"B1", "A1"}
