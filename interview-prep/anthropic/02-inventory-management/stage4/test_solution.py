"""
Tests for Inventory Management Stage 4

Stage 4 adds duplicate items:
- add_duplicate_items(user_id, name) - Creates '<name>.dupe' with half quantity
- remove_duplicate_items(user_id, name) - Merges '<name>.dupe' back into '<name>'
"""
import pytest
from solution import InventoryManager


class TestInventoryManagerStage1To3:
    """Regression tests for Stages 1-3."""

    def test_basic_operations(self):
        inv = InventoryManager()
        inv.add_item("apple", 10)
        assert inv.get_item_quantity("apple") == 10

    def test_user_operations(self):
        inv = InventoryManager()
        inv.add_user("alice", 100)
        inv.add_item_by("alice", "apple", 10)
        assert inv.get_user_items("alice") == [("apple", 10)]


class TestInventoryManagerStage4:
    """Test suite for Stage 4 duplicate functionality."""

    def test_add_duplicate_items_creates_dupe(self):
        """add_duplicate_items creates '<name>.dupe' with half quantity."""
        inv = InventoryManager()
        inv.add_user("alice", 100)
        inv.add_item_by("alice", "apple", 10)

        result = inv.add_duplicate_items("alice", "apple")
        assert result == "apple.dupe"

        items = dict(inv.get_user_items("alice"))
        assert items["apple"] == 10
        assert items["apple.dupe"] == 5  # Half of 10

    def test_add_duplicate_items_rounds_down(self):
        """Half quantity rounds down."""
        inv = InventoryManager()
        inv.add_user("alice", 100)
        inv.add_item_by("alice", "apple", 7)

        inv.add_duplicate_items("alice", "apple")

        items = dict(inv.get_user_items("alice"))
        assert items["apple.dupe"] == 3  # 7 // 2 = 3

    def test_add_duplicate_items_nonexistent_returns_none(self):
        """add_duplicate_items returns None if original doesn't exist."""
        inv = InventoryManager()
        inv.add_user("alice", 100)

        result = inv.add_duplicate_items("alice", "nonexistent")
        assert result is None

    def test_add_duplicate_items_nonexistent_user(self):
        """add_duplicate_items returns None for non-existent user."""
        inv = InventoryManager()
        result = inv.add_duplicate_items("nonexistent", "apple")
        assert result is None

    def test_remove_duplicate_items_merges_back(self):
        """remove_duplicate_items merges '<name>.dupe' back into '<name>'."""
        inv = InventoryManager()
        inv.add_user("alice", 100)
        inv.add_item_by("alice", "apple", 10)
        inv.add_duplicate_items("alice", "apple")

        # apple = 10, apple.dupe = 5
        result = inv.remove_duplicate_items("alice", "apple")
        assert result is True

        items = dict(inv.get_user_items("alice"))
        assert items["apple"] == 15  # 10 + 5
        assert "apple.dupe" not in items

    def test_remove_duplicate_items_no_original(self):
        """remove_duplicate_items returns False if original doesn't exist."""
        inv = InventoryManager()
        inv.add_user("alice", 100)
        inv.add_item_by("alice", "apple.dupe", 5)

        result = inv.remove_duplicate_items("alice", "apple")
        assert result is False

    def test_remove_duplicate_items_no_dupe(self):
        """remove_duplicate_items returns False if dupe doesn't exist."""
        inv = InventoryManager()
        inv.add_user("alice", 100)
        inv.add_item_by("alice", "apple", 10)

        result = inv.remove_duplicate_items("alice", "apple")
        assert result is False

    def test_remove_duplicate_items_nonexistent_user(self):
        """remove_duplicate_items returns False for non-existent user."""
        inv = InventoryManager()
        result = inv.remove_duplicate_items("nonexistent", "apple")
        assert result is False

    def test_add_duplicate_zero_quantity(self):
        """Duplicate of item with quantity 1 has quantity 0."""
        inv = InventoryManager()
        inv.add_user("alice", 100)
        inv.add_item_by("alice", "apple", 1)

        inv.add_duplicate_items("alice", "apple")

        items = dict(inv.get_user_items("alice"))
        assert items["apple.dupe"] == 0  # 1 // 2 = 0

    def test_duplicate_respects_capacity(self):
        """Creating duplicate fails if it would exceed capacity."""
        inv = InventoryManager()
        inv.add_user("alice", 15)  # Capacity for 15 items
        inv.add_item_by("alice", "apple", 10)  # 10 used

        # Trying to add 5 more (.dupe) = 15 total, should succeed
        result = inv.add_duplicate_items("alice", "apple")
        assert result == "apple.dupe"

    def test_duplicate_exceeds_capacity_fails(self):
        """Creating duplicate that exceeds capacity fails."""
        inv = InventoryManager()
        inv.add_user("alice", 14)  # Capacity for 14 items
        inv.add_item_by("alice", "apple", 10)  # 10 used

        # Trying to add 5 more (.dupe) = 15 total, should fail
        result = inv.add_duplicate_items("alice", "apple")
        # Based on the problem description, it should return None if it can't be done
        # But the requirement doesn't explicitly mention capacity checking
        # Let's assume it should respect capacity
        assert result is None or result == "apple.dupe"
        # If it succeeded, check capacity wasn't exceeded
        if result == "apple.dupe":
            items = dict(inv.get_user_items("alice"))
            total = sum(items.values())
            assert total <= 14
