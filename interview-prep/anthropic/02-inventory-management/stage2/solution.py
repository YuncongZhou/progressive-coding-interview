"""
Inventory Management System - Stage 2

Inventory tracking with pattern-based search functionality.

Design Rationale:
- Simple dict {name: quantity} for O(1) access on basic operations
- find_items scans all items and filters by prefix/suffix
- Sorting: quantity descending, then name ascending
- Using Python's sort with tuple key (-quantity, name) for correct ordering
"""


class InventoryManager:
    """
    Inventory management system for tracking item quantities
    with pattern-based search.
    """

    def __init__(self):
        """Initialize empty inventory."""
        self._items: dict[str, int] = {}

    def add_item(self, name: str, quantity: int) -> bool:
        """
        Adds item with quantity.

        Args:
            name: Item name
            quantity: Quantity to add

        Returns:
            True if new item, False if updated existing item
        """
        is_new = name not in self._items
        if is_new:
            self._items[name] = quantity
        else:
            self._items[name] += quantity
        return is_new

    def copy_item(self, source: str, destination: str) -> bool:
        """
        Copies quantity from source to destination.

        Args:
            source: Source item name
            destination: Destination item name

        Returns:
            False if source doesn't exist, True otherwise
        """
        if source not in self._items:
            return False

        quantity = self._items[source]
        if destination not in self._items:
            self._items[destination] = quantity
        else:
            self._items[destination] += quantity
        return True

    def get_item_quantity(self, name: str) -> int:
        """
        Returns quantity of item.

        Args:
            name: Item name

        Returns:
            Quantity or 0 if not found
        """
        return self._items.get(name, 0)

    def remove_item(self, name: str, quantity: int) -> int:
        """
        Removes up to quantity from item.

        Args:
            name: Item name
            quantity: Quantity to remove

        Returns:
            Actual amount removed
        """
        if name not in self._items:
            return 0

        available = self._items[name]
        to_remove = min(quantity, available)
        self._items[name] -= to_remove
        return to_remove

    def find_items(self, prefix: str, suffix: str) -> list[tuple[str, int]]:
        """
        Returns items matching prefix AND suffix, sorted by quantity
        descending, then lexicographically by name.

        Args:
            prefix: Prefix to match (empty string matches all)
            suffix: Suffix to match (empty string matches all)

        Returns:
            List of (name, quantity) tuples sorted as specified
        """
        matches = [
            (name, qty)
            for name, qty in self._items.items()
            if name.startswith(prefix) and name.endswith(suffix)
        ]
        # Sort by quantity descending (-qty), then name ascending
        matches.sort(key=lambda x: (-x[1], x[0]))
        return matches
