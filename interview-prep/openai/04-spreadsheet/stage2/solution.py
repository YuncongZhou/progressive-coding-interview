"""
Spreadsheet - Stage 2

Circular dependency detection with error reporting.

Design Rationale:
- Return error message for circular dependencies
- Track dependency graph explicitly
- Provide clear error paths
"""

import re
from typing import Union


class SpreadsheetError(Exception):
    """Base error for spreadsheet operations."""
    pass


class CircularDependencyError(SpreadsheetError):
    """Raised when circular dependency detected."""
    pass


class Spreadsheet:
    """Spreadsheet with circular dependency detection."""

    def __init__(self):
        self._cells: dict[str, str] = {}

    def set_cell(self, cell: str, value: str) -> None:
        """Sets cell value."""
        self._cells[cell] = value

    def get_cell(self, cell: str) -> Union[float, str, None]:
        """
        Returns computed value of cell.
        Returns None if empty.
        Returns "#CIRCULAR!" for circular dependencies.
        Returns "#ERROR!" for other errors.
        """
        if cell not in self._cells:
            return None
        try:
            return self._evaluate(cell, set())
        except CircularDependencyError:
            return "#CIRCULAR!"
        except Exception:
            return "#ERROR!"

    def get_dependencies(self, cell: str) -> list[str]:
        """Return list of cells that this cell depends on."""
        if cell not in self._cells:
            return []

        value = self._cells[cell]
        if not value.startswith("="):
            return []

        formula = value[1:]
        # Find all cell references
        refs = re.findall(r'[A-Z]+[0-9]+', formula)
        return refs

    def _evaluate(self, cell: str, visited: set) -> float:
        """Evaluate cell value with cycle detection."""
        if cell in visited:
            raise CircularDependencyError(f"Circular dependency at {cell}")

        if cell not in self._cells:
            raise ValueError(f"Cell {cell} not found")

        visited.add(cell)
        value = self._cells[cell]

        # Plain number
        try:
            return float(value)
        except ValueError:
            pass

        # Formula (starts with =)
        if value.startswith("="):
            formula = value[1:]
            return self._evaluate_formula(formula, visited)

        raise ValueError(f"Invalid cell value: {value}")

    def _evaluate_formula(self, formula: str, visited: set) -> float:
        """Evaluate a formula like 'A1+B2' or 'A1*2'."""
        # Tokenize: split on operators while keeping them
        tokens = re.split(r'(\+|\-|\*|\/)', formula)
        tokens = [t.strip() for t in tokens if t.strip()]

        if not tokens:
            raise ValueError("Empty formula")

        # Evaluate first term
        result = self._get_term_value(tokens[0], visited)

        # Process remaining operations
        i = 1
        while i < len(tokens):
            if i + 1 >= len(tokens):
                raise ValueError("Incomplete formula")
            op = tokens[i]
            next_val = self._get_term_value(tokens[i + 1], visited)

            if op == '+':
                result += next_val
            elif op == '-':
                result -= next_val
            elif op == '*':
                result *= next_val
            elif op == '/':
                if next_val == 0:
                    raise ValueError("Division by zero")
                result /= next_val

            i += 2

        return result

    def _get_term_value(self, term: str, visited: set) -> float:
        """Get value of a term (number or cell reference)."""
        try:
            return float(term)
        except ValueError:
            # Cell reference
            return self._evaluate(term, visited.copy())
