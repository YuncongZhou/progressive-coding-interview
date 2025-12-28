"""
Tests for Inventory Management Stage 3

Stage 3 adds multi-user support with capacity:
- add_user(user_id, capacity) - Creates user with item capacity
- add_item_by(user_id, name, quantity) - Adds item for user
- update_capacity(user_id, new_capacity) - Updates capacity
- get_user_items(user_id) - Returns all items for user
"""
import pytest
from solution import InventoryManager


class TestInventoryManagerStage1And2:
    """Regression tests for Stages 1-2."""

    def test_basic_operations(self):
        inv = InventoryManager()
        inv.add_item("apple", 10)
        assert inv.get_item_quantity("apple") == 10

    def test_find_items(self):
        inv = InventoryManager()
        inv.add_item("apple", 10)
        inv.add_item("apricot", 15)
        result = inv.find_items("ap", "")
        assert result == [("apricot", 15), ("apple", 10)]


class TestInventoryManagerStage3:
    """Test suite for Stage 3 multi-user functionality."""

    def test_add_user_new(self):
        """Add new user returns True."""
        inv = InventoryManager()
        result = inv.add_user("alice", 10)
        assert result is True

    def test_add_user_existing_returns_false(self):
        """Add existing user returns False."""
        inv = InventoryManager()
        inv.add_user("alice", 10)
        result = inv.add_user("alice", 20)
        assert result is False

    def test_add_item_by_user(self):
        """Add item for user works."""
        inv = InventoryManager()
        inv.add_user("alice", 100)
        result = inv.add_item_by("alice", "apple", 10)
        assert result is True

    def test_add_item_by_exceeds_capacity_fails(self):
        """Add item that exceeds capacity fails."""
        inv = InventoryManager()
        inv.add_user("alice", 10)
        inv.add_item_by("alice", "apple", 5)  # 5 items
        result = inv.add_item_by("alice", "banana", 6)  # Would be 11 items
        assert result is False

    def test_add_item_by_at_capacity_succeeds(self):
        """Add item that exactly reaches capacity succeeds."""
        inv = InventoryManager()
        inv.add_user("alice", 10)
        inv.add_item_by("alice", "apple", 5)
        result = inv.add_item_by("alice", "banana", 5)  # Exactly 10
        assert result is True

    def test_get_user_items(self):
        """Get user items returns all items."""
        inv = InventoryManager()
        inv.add_user("alice", 100)
        inv.add_item_by("alice", "apple", 10)
        inv.add_item_by("alice", "banana", 5)

        result = inv.get_user_items("alice")
        assert set(result) == {("apple", 10), ("banana", 5)}

    def test_get_user_items_nonexistent_user(self):
        """Get items for non-existent user returns empty list."""
        inv = InventoryManager()
        result = inv.get_user_items("nonexistent")
        assert result == []

    def test_update_capacity_increase(self):
        """Increasing capacity returns 0 (no items removed)."""
        inv = InventoryManager()
        inv.add_user("alice", 10)
        inv.add_item_by("alice", "apple", 5)
        removed = inv.update_capacity("alice", 20)
        assert removed == 0

    def test_update_capacity_decrease_no_removal(self):
        """Decreasing capacity but still above items returns 0."""
        inv = InventoryManager()
        inv.add_user("alice", 20)
        inv.add_item_by("alice", "apple", 5)
        removed = inv.update_capacity("alice", 10)
        assert removed == 0

    def test_update_capacity_removes_largest_first(self):
        """When capacity reduced below items, removes largest items first."""
        inv = InventoryManager()
        inv.add_user("alice", 100)
        inv.add_item_by("alice", "small", 5)   # 5 items
        inv.add_item_by("alice", "medium", 10)  # 15 total
        inv.add_item_by("alice", "large", 20)   # 35 total

        # Reduce to capacity 10 - need to remove 25 items
        # Should remove large (20) first, then medium (10) = 30 removed
        # But we only need to remove 25, so it should stop after removing enough
        removed = inv.update_capacity("alice", 10)

        # large (20) removed, then medium partially or fully removed
        # Actually, the requirement says "removes LARGEST items first"
        # So we remove whole items, starting with largest
        # After removing large (20), we have 15 items left
        # After removing medium (10), we have 5 items left
        # 5 <= 10 capacity, so we stop
        # Total removed = 30 items from 2 items
        assert removed == 2  # Number of items removed (not quantity)

    def test_update_capacity_removes_all_if_needed(self):
        """Can remove all items if capacity reduced to 0."""
        inv = InventoryManager()
        inv.add_user("alice", 100)
        inv.add_item_by("alice", "apple", 10)
        inv.add_item_by("alice", "banana", 20)

        removed = inv.update_capacity("alice", 0)
        assert removed == 2
        assert inv.get_user_items("alice") == []

    def test_add_item_by_nonexistent_user(self):
        """Add item for non-existent user fails."""
        inv = InventoryManager()
        result = inv.add_item_by("nonexistent", "apple", 10)
        assert result is False

    def test_update_capacity_nonexistent_user(self):
        """Update capacity for non-existent user returns 0."""
        inv = InventoryManager()
        removed = inv.update_capacity("nonexistent", 10)
        assert removed == 0

    def test_multiple_users_independent(self):
        """Multiple users have independent inventories."""
        inv = InventoryManager()
        inv.add_user("alice", 100)
        inv.add_user("bob", 100)

        inv.add_item_by("alice", "apple", 10)
        inv.add_item_by("bob", "banana", 20)

        alice_items = inv.get_user_items("alice")
        bob_items = inv.get_user_items("bob")

        assert alice_items == [("apple", 10)]
        assert bob_items == [("banana", 20)]

    def test_add_to_existing_item_by_user(self):
        """Adding to existing item updates quantity."""
        inv = InventoryManager()
        inv.add_user("alice", 100)
        inv.add_item_by("alice", "apple", 10)
        inv.add_item_by("alice", "apple", 5)

        items = inv.get_user_items("alice")
        assert items == [("apple", 15)]
