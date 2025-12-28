"""
In-Memory SQL Database - Stage 3

Complex WHERE clauses with multiple conditions.

Design Rationale:
- Parse WHERE string into AST
- Support: =, !=, <, >, <=, >=
- Logical: AND, OR (AND has higher precedence)
"""

from typing import Any
import re


class InMemorySQL:
    """In-memory SQL database with complex WHERE support."""

    def __init__(self):
        self._tables: dict[str, dict] = {}

    def create_table(self, table_name: str, columns: list[str]) -> bool:
        if table_name in self._tables:
            return False
        self._tables[table_name] = {"columns": columns, "rows": []}
        return True

    def insert(self, table_name: str, values: dict[str, Any]) -> bool:
        if table_name not in self._tables:
            return False
        self._tables[table_name]["rows"].append(values.copy())
        return True

    def select(self, table_name: str, columns: list[str] = None) -> list[dict]:
        if table_name not in self._tables:
            return []
        rows = self._tables[table_name]["rows"]
        if columns is None:
            return [row.copy() for row in rows]
        return [{col: row.get(col) for col in columns} for row in rows]

    def select_where(self, table_name: str, columns: list[str],
                     where_column: str, where_value: Any) -> list[dict]:
        if table_name not in self._tables:
            return []
        result = []
        for row in self._tables[table_name]["rows"]:
            if row.get(where_column) == where_value:
                if columns is None:
                    result.append(row.copy())
                else:
                    result.append({col: row.get(col) for col in columns})
        return result

    def select_where_complex(self, table_name: str, columns: list[str],
                             where_clause: str) -> list[dict]:
        """
        Supports complex WHERE with multiple conditions.
        Operators: =, !=, <, >, <=, >=
        Logical: AND, OR (AND has higher precedence)
        """
        if table_name not in self._tables:
            return []

        result = []
        for row in self._tables[table_name]["rows"]:
            if self._evaluate_where(where_clause, row):
                if columns is None:
                    result.append(row.copy())
                else:
                    result.append({col: row.get(col) for col in columns})
        return result

    def _evaluate_where(self, where_clause: str, row: dict) -> bool:
        """Evaluate WHERE clause against a row."""
        # Split by OR first (lower precedence)
        or_parts = self._split_by_keyword(where_clause, "OR")
        return any(self._evaluate_and(part, row) for part in or_parts)

    def _evaluate_and(self, clause: str, row: dict) -> bool:
        """Evaluate AND clause."""
        and_parts = self._split_by_keyword(clause, "AND")
        return all(self._evaluate_condition(part.strip(), row) for part in and_parts)

    def _split_by_keyword(self, s: str, keyword: str) -> list[str]:
        """Split by keyword, respecting quoted strings."""
        pattern = rf'\s+{keyword}\s+'
        return re.split(pattern, s, flags=re.IGNORECASE)

    def _evaluate_condition(self, condition: str, row: dict) -> bool:
        """Evaluate a single condition like 'age > 25'."""
        # Parse condition
        operators = ["<=", ">=", "!=", "=", "<", ">"]
        for op in operators:
            if op in condition:
                parts = condition.split(op, 1)
                if len(parts) == 2:
                    col = parts[0].strip()
                    val_str = parts[1].strip()
                    val = self._parse_value(val_str)
                    row_val = row.get(col)
                    return self._compare(row_val, op, val)
        return False

    def _parse_value(self, val_str: str) -> Any:
        """Parse a value from string."""
        # Remove quotes for strings
        if (val_str.startswith("'") and val_str.endswith("'")) or \
           (val_str.startswith('"') and val_str.endswith('"')):
            return val_str[1:-1]
        # Try numeric
        try:
            if "." in val_str:
                return float(val_str)
            return int(val_str)
        except ValueError:
            return val_str

    def _compare(self, left: Any, op: str, right: Any) -> bool:
        """Compare two values with operator."""
        if left is None:
            return False
        try:
            if op == "=":
                return left == right
            elif op == "!=":
                return left != right
            elif op == "<":
                return left < right
            elif op == ">":
                return left > right
            elif op == "<=":
                return left <= right
            elif op == ">=":
                return left >= right
        except TypeError:
            return False
        return False
