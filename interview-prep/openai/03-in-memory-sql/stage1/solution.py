"""
In-Memory SQL Database - Stage 1

Basic SQL-like operations: CREATE TABLE, INSERT, SELECT.

Design Rationale:
- Tables stored as {table_name: {"columns": [...], "rows": [...]}}
- Rows are dicts with column names as keys
- SELECT supports column projection
"""

from typing import Any


class InMemorySQL:
    """In-memory SQL database."""

    def __init__(self):
        self._tables: dict[str, dict] = {}

    def create_table(self, table_name: str, columns: list[str]) -> bool:
        """Creates table with given column names. Returns False if exists."""
        if table_name in self._tables:
            return False
        self._tables[table_name] = {"columns": columns, "rows": []}
        return True

    def insert(self, table_name: str, values: dict[str, Any]) -> bool:
        """Inserts record. Returns False if table doesn't exist."""
        if table_name not in self._tables:
            return False
        self._tables[table_name]["rows"].append(values.copy())
        return True

    def select(self, table_name: str, columns: list[str] = None) -> list[dict]:
        """SELECT columns FROM table. None means all columns (*)."""
        if table_name not in self._tables:
            return []
        rows = self._tables[table_name]["rows"]

        if columns is None:
            return [row.copy() for row in rows]

        result = []
        for row in rows:
            projected = {col: row.get(col) for col in columns}
            result.append(projected)
        return result
