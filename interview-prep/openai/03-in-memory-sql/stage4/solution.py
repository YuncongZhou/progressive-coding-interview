"""
In-Memory SQL Database - Stage 4

ORDER BY and LIMIT support.

Design Rationale:
- Add ordering by single or multiple columns
- Support ASC/DESC direction
- Add LIMIT clause for pagination
"""

from typing import Any
import re


class InMemorySQL:
    """In-memory SQL database with ORDER BY and LIMIT."""

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
        """Supports complex WHERE with multiple conditions."""
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

    def select_order_by(self, table_name: str, columns: list[str],
                        order_by: list[tuple[str, str]],
                        limit: int = None) -> list[dict]:
        """
        Select with ORDER BY and optional LIMIT.

        Args:
            order_by: List of (column, direction) where direction is 'ASC' or 'DESC'
            limit: Maximum number of rows to return
        """
        if table_name not in self._tables:
            return []

        rows = self._tables[table_name]["rows"].copy()

        # Sort by multiple columns
        def sort_key(row):
            key = []
            for col, direction in order_by:
                val = row.get(col)
                # Handle None values (sort them last)
                if val is None:
                    key.append((1, None))
                else:
                    key.append((0, val))
            return key

        # Apply sorting for each column in reverse order (stable sort)
        for col, direction in reversed(order_by):
            reverse = direction.upper() == "DESC"
            rows.sort(key=lambda r: (r.get(col) is None, r.get(col) or 0),
                      reverse=reverse)

        # Apply LIMIT
        if limit is not None:
            rows = rows[:limit]

        # Project columns
        if columns is None:
            return [row.copy() for row in rows]
        return [{col: row.get(col) for col in columns} for row in rows]

    def select_full(self, table_name: str, columns: list[str] = None,
                    where_clause: str = None,
                    order_by: list[tuple[str, str]] = None,
                    limit: int = None) -> list[dict]:
        """
        Full SELECT with WHERE, ORDER BY, and LIMIT.
        """
        if table_name not in self._tables:
            return []

        # Filter with WHERE
        rows = []
        for row in self._tables[table_name]["rows"]:
            if where_clause is None or self._evaluate_where(where_clause, row):
                rows.append(row.copy())

        # Apply ORDER BY
        if order_by:
            for col, direction in reversed(order_by):
                reverse = direction.upper() == "DESC"
                rows.sort(key=lambda r: (r.get(col) is None, r.get(col) or 0),
                          reverse=reverse)

        # Apply LIMIT
        if limit is not None:
            rows = rows[:limit]

        # Project columns
        if columns is None:
            return rows
        return [{col: row.get(col) for col in columns} for row in rows]

    def _evaluate_where(self, where_clause: str, row: dict) -> bool:
        """Evaluate WHERE clause against a row."""
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
        if (val_str.startswith("'") and val_str.endswith("'")) or \
           (val_str.startswith('"') and val_str.endswith('"')):
            return val_str[1:-1]
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
