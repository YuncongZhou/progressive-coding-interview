"""
In-Memory SQL Database - Stage 2

SELECT with WHERE clause.

Design Rationale:
- Extend select to filter with single column WHERE
- Simple equality comparison
"""

from typing import Any


class InMemorySQL:
    """In-memory SQL database with WHERE support."""

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
        """SELECT columns FROM table WHERE where_column = where_value"""
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
