"""
Spreadsheet - Stage 1

Spreadsheet with formula support.

Design Rationale:
- Cells can contain numbers, references (=A1), or formulas (=A1+B2)
- get_cell computes value via DFS on every call
- Supported operations: +, -, *, /
"""

import re


class Spreadsheet:
    """Spreadsheet with formula support."""

    def __init__(self):
        self._cells: dict[str, str] = {}

    def set_cell(self, cell: str, value: str) -> None:
        """Sets cell value."""
        self._cells[cell] = value

    def get_cell(self, cell: str) -> float | None:
        """Returns computed value of cell. None if empty or has error."""
        if cell not in self._cells:
            return None
        return self._evaluate(cell, set())

    def _evaluate(self, cell: str, visited: set) -> float | None:
        """Evaluate cell value with cycle detection."""
        if cell in visited:
            return None  # Cycle detected
        if cell not in self._cells:
            return None

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

        return None

    def _evaluate_formula(self, formula: str, visited: set) -> float | None:
        """Evaluate a formula like 'A1+B2' or 'A1*2'."""
        # Tokenize: split on operators while keeping them
        tokens = re.split(r'(\+|\-|\*|\/)', formula)
        tokens = [t.strip() for t in tokens if t.strip()]

        if not tokens:
            return None

        # Evaluate first term
        result = self._get_term_value(tokens[0], visited)
        if result is None:
            return None

        # Process remaining operations
        i = 1
        while i < len(tokens):
            if i + 1 >= len(tokens):
                return None
            op = tokens[i]
            next_val = self._get_term_value(tokens[i + 1], visited)
            if next_val is None:
                return None

            if op == '+':
                result += next_val
            elif op == '-':
                result -= next_val
            elif op == '*':
                result *= next_val
            elif op == '/':
                if next_val == 0:
                    return None
                result /= next_val

            i += 2

        return result

    def _get_term_value(self, term: str, visited: set) -> float | None:
        """Get value of a term (number or cell reference)."""
        try:
            return float(term)
        except ValueError:
            # Cell reference
            return self._evaluate(term, visited.copy())
