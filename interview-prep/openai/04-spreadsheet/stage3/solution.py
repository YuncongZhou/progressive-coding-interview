"""
Spreadsheet - Stage 3

SUM, AVERAGE functions and range support.

Design Rationale:
- Support range notation (A1:A5)
- Implement aggregate functions: SUM, AVERAGE, MIN, MAX
- Expand ranges before evaluation
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
    """Spreadsheet with functions and range support."""

    def __init__(self):
        self._cells: dict[str, str] = {}

    def set_cell(self, cell: str, value: str) -> None:
        """Sets cell value."""
        self._cells[cell] = value

    def get_cell(self, cell: str) -> Union[float, str, None]:
        """Returns computed value of cell."""
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
        # Expand ranges first
        formula = self._expand_ranges_in_formula(formula)
        # Find all cell references
        refs = re.findall(r'[A-Z]+[0-9]+', formula)
        return refs

    def _parse_cell_ref(self, ref: str) -> tuple[str, int]:
        """Parse cell reference into (column, row)."""
        match = re.match(r'([A-Z]+)(\d+)', ref)
        if not match:
            raise ValueError(f"Invalid cell reference: {ref}")
        return match.group(1), int(match.group(2))

    def _col_to_num(self, col: str) -> int:
        """Convert column letters to number (A=0, B=1, ...)."""
        result = 0
        for c in col:
            result = result * 26 + (ord(c) - ord('A') + 1)
        return result - 1

    def _num_to_col(self, num: int) -> str:
        """Convert number to column letters (0=A, 1=B, ...)."""
        result = ""
        num += 1
        while num > 0:
            num -= 1
            result = chr(ord('A') + num % 26) + result
            num //= 26
        return result

    def _expand_range(self, range_str: str) -> list[str]:
        """Expand range like A1:A5 to [A1, A2, A3, A4, A5]."""
        parts = range_str.split(":")
        if len(parts) != 2:
            return [range_str]

        start_col, start_row = self._parse_cell_ref(parts[0])
        end_col, end_row = self._parse_cell_ref(parts[1])

        start_col_num = self._col_to_num(start_col)
        end_col_num = self._col_to_num(end_col)

        cells = []
        for col_num in range(start_col_num, end_col_num + 1):
            for row in range(start_row, end_row + 1):
                cells.append(f"{self._num_to_col(col_num)}{row}")

        return cells

    def _expand_ranges_in_formula(self, formula: str) -> str:
        """Replace ranges with comma-separated cells."""
        # Find ranges like A1:B5
        pattern = r'([A-Z]+\d+):([A-Z]+\d+)'
        matches = list(re.finditer(pattern, formula))

        # Replace from end to preserve positions
        for match in reversed(matches):
            range_str = match.group(0)
            cells = self._expand_range(range_str)
            formula = formula[:match.start()] + ",".join(cells) + formula[match.end():]

        return formula

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
        """Evaluate a formula with function support."""
        # Check for functions
        func_match = re.match(r'(SUM|AVERAGE|MIN|MAX)\((.*)\)', formula, re.IGNORECASE)
        if func_match:
            func_name = func_match.group(1).upper()
            args = func_match.group(2)
            return self._evaluate_function(func_name, args, visited)

        # Expand ranges if any
        formula = self._expand_ranges_in_formula(formula)

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

    def _evaluate_function(self, func_name: str, args: str, visited: set) -> float:
        """Evaluate a function like SUM(A1:A5)."""
        # Expand ranges
        args = self._expand_ranges_in_formula(args)

        # Split by comma to get individual cells/values
        parts = [p.strip() for p in args.split(",")]
        values = []

        for part in parts:
            if part:
                val = self._get_term_value(part, visited.copy())
                values.append(val)

        if not values:
            raise ValueError("No values for function")

        if func_name == "SUM":
            return sum(values)
        elif func_name == "AVERAGE":
            return sum(values) / len(values)
        elif func_name == "MIN":
            return min(values)
        elif func_name == "MAX":
            return max(values)
        else:
            raise ValueError(f"Unknown function: {func_name}")

    def _get_term_value(self, term: str, visited: set) -> float:
        """Get value of a term (number or cell reference)."""
        try:
            return float(term)
        except ValueError:
            # Cell reference
            return self._evaluate(term, visited.copy())
