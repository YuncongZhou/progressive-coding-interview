"""
Tests for Inventory Management Stage 1

Stage 1 Requirements:
- add_item(name, quantity) - Adds item with quantity
- copy_item(source, destination) - Copies quantity from source to dest
- get_item_quantity(name) - Returns quantity or 0
- remove_item(name, quantity) - Removes up to quantity
"""
import pytest
from solution import InventoryManager


class TestInventoryManagerStage1:
    """Test suite for Stage 1 functionality."""

    def test_add_new_item_returns_true(self):
        """Adding a new item returns True."""
        inv = InventoryManager()
        result = inv.add_item("apple", 10)
        assert result is True

    def test_add_existing_item_returns_false(self):
        """Adding to an existing item returns False."""
        inv = InventoryManager()
        inv.add_item("apple", 10)
        result = inv.add_item("apple", 5)
        assert result is False

    def test_add_item_updates_quantity(self):
        """Adding to existing item updates quantity."""
        inv = InventoryManager()
        inv.add_item("apple", 10)
        inv.add_item("apple", 5)
        assert inv.get_item_quantity("apple") == 15

    def test_get_item_quantity(self):
        """Get item quantity returns correct value."""
        inv = InventoryManager()
        inv.add_item("apple", 10)
        assert inv.get_item_quantity("apple") == 10

    def test_get_nonexistent_item_returns_zero(self):
        """Get non-existent item returns 0."""
        inv = InventoryManager()
        assert inv.get_item_quantity("banana") == 0

    def test_copy_item_success(self):
        """Copy item copies quantity from source to dest."""
        inv = InventoryManager()
        inv.add_item("apple", 10)
        result = inv.copy_item("apple", "apple_copy")
        assert result is True
        assert inv.get_item_quantity("apple_copy") == 10
        # Source still has its quantity
        assert inv.get_item_quantity("apple") == 10

    def test_copy_item_nonexistent_source_returns_false(self):
        """Copy from non-existent source returns False."""
        inv = InventoryManager()
        result = inv.copy_item("nonexistent", "copy")
        assert result is False

    def test_copy_item_to_existing_dest_adds_quantity(self):
        """Copy to existing destination adds quantity."""
        inv = InventoryManager()
        inv.add_item("apple", 10)
        inv.add_item("basket", 5)
        inv.copy_item("apple", "basket")
        assert inv.get_item_quantity("basket") == 15

    def test_remove_item_full_amount(self):
        """Remove full amount available."""
        inv = InventoryManager()
        inv.add_item("apple", 10)
        removed = inv.remove_item("apple", 10)
        assert removed == 10
        assert inv.get_item_quantity("apple") == 0

    def test_remove_item_partial_amount(self):
        """Remove less than available."""
        inv = InventoryManager()
        inv.add_item("apple", 10)
        removed = inv.remove_item("apple", 5)
        assert removed == 5
        assert inv.get_item_quantity("apple") == 5

    def test_remove_item_more_than_available(self):
        """Remove more than available returns actual amount."""
        inv = InventoryManager()
        inv.add_item("apple", 10)
        removed = inv.remove_item("apple", 20)
        assert removed == 10
        assert inv.get_item_quantity("apple") == 0

    def test_remove_nonexistent_item(self):
        """Remove from non-existent item returns 0."""
        inv = InventoryManager()
        removed = inv.remove_item("banana", 5)
        assert removed == 0

    def test_remove_zero_quantity(self):
        """Remove zero quantity returns 0."""
        inv = InventoryManager()
        inv.add_item("apple", 10)
        removed = inv.remove_item("apple", 0)
        assert removed == 0
        assert inv.get_item_quantity("apple") == 10

    def test_add_zero_quantity(self):
        """Adding zero quantity still creates item."""
        inv = InventoryManager()
        result = inv.add_item("apple", 0)
        assert result is True
        assert inv.get_item_quantity("apple") == 0

    def test_multiple_items(self):
        """Multiple items can coexist."""
        inv = InventoryManager()
        inv.add_item("apple", 10)
        inv.add_item("banana", 20)
        inv.add_item("orange", 15)

        assert inv.get_item_quantity("apple") == 10
        assert inv.get_item_quantity("banana") == 20
        assert inv.get_item_quantity("orange") == 15
