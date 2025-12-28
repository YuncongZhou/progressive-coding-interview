"""
Inventory Management System - Stage 1

Basic inventory tracking with add, copy, get, and remove operations.

Design Rationale:
- Simple dict {name: quantity} for O(1) access
- add_item returns True if new item, False if updating existing
- copy_item copies quantity from source to destination
- remove_item removes up to available quantity
"""


class InventoryManager:
    """
    Inventory management system for tracking item quantities.
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
