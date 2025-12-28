"""
Inventory Management System - Stage 3

Multi-user inventory tracking with capacity limits.

Design Rationale:
- Global items dict for backward compatibility with Stage 1-2
- Separate user data structure: {user_id: {"capacity": int, "items": {name: qty}}}
- When capacity is reduced, remove largest items (by quantity) first
- "Largest items" means items with highest quantity, not highest quantity values
"""


class InventoryManager:
    """
    Inventory management system with multi-user support
    and capacity limits.
    """

    def __init__(self):
        """Initialize empty inventory."""
        # Global inventory for Stage 1-2 compatibility
        self._items: dict[str, int] = {}
        # Per-user data: {user_id: {"capacity": int, "items": {name: qty}}}
        self._users: dict[str, dict] = {}

    # ========== Stage 1 Methods ==========

    def add_item(self, name: str, quantity: int) -> bool:
        """Adds item with quantity to global inventory."""
        is_new = name not in self._items
        if is_new:
            self._items[name] = quantity
        else:
            self._items[name] += quantity
        return is_new

    def copy_item(self, source: str, destination: str) -> bool:
        """Copies quantity from source to destination."""
        if source not in self._items:
            return False
        quantity = self._items[source]
        if destination not in self._items:
            self._items[destination] = quantity
        else:
            self._items[destination] += quantity
        return True

    def get_item_quantity(self, name: str) -> int:
        """Returns quantity of item."""
        return self._items.get(name, 0)

    def remove_item(self, name: str, quantity: int) -> int:
        """Removes up to quantity from item."""
        if name not in self._items:
            return 0
        available = self._items[name]
        to_remove = min(quantity, available)
        self._items[name] -= to_remove
        return to_remove

    # ========== Stage 2 Methods ==========

    def find_items(self, prefix: str, suffix: str) -> list[tuple[str, int]]:
        """Returns items matching prefix AND suffix, sorted appropriately."""
        matches = [
            (name, qty)
            for name, qty in self._items.items()
            if name.startswith(prefix) and name.endswith(suffix)
        ]
        matches.sort(key=lambda x: (-x[1], x[0]))
        return matches

    # ========== Stage 3 Methods ==========

    def add_user(self, user_id: str, capacity: int) -> bool:
        """
        Creates user with item capacity.

        Args:
            user_id: User identifier
            capacity: Maximum total quantity of items

        Returns:
            False if user already exists, True otherwise
        """
        if user_id in self._users:
            return False
        self._users[user_id] = {"capacity": capacity, "items": {}}
        return True

    def add_item_by(self, user_id: str, name: str, quantity: int) -> bool:
        """
        Adds item for user. Returns False if would exceed capacity.

        Args:
            user_id: User identifier
            name: Item name
            quantity: Quantity to add

        Returns:
            False if user doesn't exist or would exceed capacity
        """
        if user_id not in self._users:
            return False

        user = self._users[user_id]
        current_total = sum(user["items"].values())

        if current_total + quantity > user["capacity"]:
            return False

        if name in user["items"]:
            user["items"][name] += quantity
        else:
            user["items"][name] = quantity
        return True

    def update_capacity(self, user_id: str, new_capacity: int) -> int:
        """
        Updates capacity. If reduced below current items,
        removes LARGEST items first until under capacity.

        Args:
            user_id: User identifier
            new_capacity: New capacity limit

        Returns:
            Number of items removed (not quantity, but distinct items)
        """
        if user_id not in self._users:
            return 0

        user = self._users[user_id]
        user["capacity"] = new_capacity

        current_total = sum(user["items"].values())
        items_removed = 0

        # While over capacity, remove largest items
        while current_total > new_capacity and user["items"]:
            # Find largest item (highest quantity)
            largest_name = max(user["items"], key=lambda x: user["items"][x])
            largest_qty = user["items"][largest_name]

            del user["items"][largest_name]
            current_total -= largest_qty
            items_removed += 1

        return items_removed

    def get_user_items(self, user_id: str) -> list[tuple[str, int]]:
        """
        Returns all items for user.

        Args:
            user_id: User identifier

        Returns:
            List of (name, quantity) tuples
        """
        if user_id not in self._users:
            return []
        return list(self._users[user_id]["items"].items())
