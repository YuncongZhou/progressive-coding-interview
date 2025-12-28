"""
Tests for Inventory Management Stage 2

Stage 2 adds:
- find_items(prefix, suffix) - Returns items matching prefix AND suffix,
  sorted by quantity descending, then lexicographically by name
"""
import pytest
from solution import InventoryManager


class TestInventoryManagerStage1:
    """Regression tests for Stage 1."""

    def test_add_and_get(self):
        inv = InventoryManager()
        inv.add_item("apple", 10)
        assert inv.get_item_quantity("apple") == 10

    def test_copy_item(self):
        inv = InventoryManager()
        inv.add_item("apple", 10)
        assert inv.copy_item("apple", "apple_copy") is True

    def test_remove_item(self):
        inv = InventoryManager()
        inv.add_item("apple", 10)
        assert inv.remove_item("apple", 5) == 5


class TestInventoryManagerStage2:
    """Test suite for Stage 2 find_items functionality."""

    def test_find_items_with_prefix_and_suffix(self):
        """Find items matching both prefix and suffix."""
        inv = InventoryManager()
        inv.add_item("red_apple", 10)
        inv.add_item("red_orange", 15)
        inv.add_item("green_apple", 5)
        inv.add_item("red_grape", 20)

        # prefix="red", suffix="e" matches red_apple, red_orange, red_grape
        result = inv.find_items("red", "e")
        # Sort by quantity desc, then name asc
        # red_grape (20), red_orange (15), red_apple (10)
        assert result == [("red_grape", 20), ("red_orange", 15), ("red_apple", 10)]

    def test_find_items_empty_prefix_matches_all(self):
        """Empty prefix matches all items (suffix still applies)."""
        inv = InventoryManager()
        inv.add_item("apple", 10)
        inv.add_item("grape", 15)
        inv.add_item("banana", 5)

        result = inv.find_items("", "e")
        # apple, grape match (end with e)
        # Sort: grape (15), apple (10)
        assert result == [("grape", 15), ("apple", 10)]

    def test_find_items_empty_suffix_matches_all(self):
        """Empty suffix matches all items (prefix still applies)."""
        inv = InventoryManager()
        inv.add_item("apple", 10)
        inv.add_item("apricot", 15)
        inv.add_item("banana", 5)

        result = inv.find_items("ap", "")
        # apple, apricot match (start with ap)
        # Sort: apricot (15), apple (10)
        assert result == [("apricot", 15), ("apple", 10)]

    def test_find_items_both_empty_returns_all(self):
        """Empty prefix and suffix returns all items."""
        inv = InventoryManager()
        inv.add_item("apple", 10)
        inv.add_item("banana", 15)

        result = inv.find_items("", "")
        assert result == [("banana", 15), ("apple", 10)]

    def test_find_items_no_matches(self):
        """No matches returns empty list."""
        inv = InventoryManager()
        inv.add_item("apple", 10)
        inv.add_item("banana", 15)

        result = inv.find_items("xyz", "abc")
        assert result == []

    def test_find_items_sort_by_quantity_desc(self):
        """Results sorted by quantity descending."""
        inv = InventoryManager()
        inv.add_item("item_a", 5)
        inv.add_item("item_b", 10)
        inv.add_item("item_c", 15)

        result = inv.find_items("item", "")
        assert result == [("item_c", 15), ("item_b", 10), ("item_a", 5)]

    def test_find_items_sort_by_name_for_equal_quantity(self):
        """For equal quantities, sort by name ascending."""
        inv = InventoryManager()
        inv.add_item("zebra", 10)
        inv.add_item("apple", 10)
        inv.add_item("mango", 10)

        result = inv.find_items("", "")
        # All have same quantity, sort by name asc
        assert result == [("apple", 10), ("mango", 10), ("zebra", 10)]

    def test_find_items_mixed_sort(self):
        """Mixed sorting: quantity desc, then name asc."""
        inv = InventoryManager()
        inv.add_item("zebra", 20)
        inv.add_item("apple", 10)
        inv.add_item("mango", 10)
        inv.add_item("banana", 20)

        result = inv.find_items("", "")
        # zebra, banana have 20: banana < zebra
        # apple, mango have 10: apple < mango
        assert result == [("banana", 20), ("zebra", 20), ("apple", 10), ("mango", 10)]

    def test_find_items_case_sensitive(self):
        """Prefix and suffix matching is case-sensitive."""
        inv = InventoryManager()
        inv.add_item("Apple", 10)
        inv.add_item("apple", 5)
        inv.add_item("APPLE", 15)

        result = inv.find_items("A", "")
        assert result == [("APPLE", 15), ("Apple", 10)]

    def test_find_items_prefix_equals_suffix(self):
        """Prefix can equal suffix."""
        inv = InventoryManager()
        inv.add_item("aa", 10)
        inv.add_item("aba", 5)
        inv.add_item("ab", 15)

        result = inv.find_items("a", "a")
        assert result == [("aa", 10), ("aba", 5)]

    def test_find_items_full_name_match(self):
        """Full name as both prefix and suffix."""
        inv = InventoryManager()
        inv.add_item("test", 10)
        inv.add_item("testing", 5)

        result = inv.find_items("test", "test")
        assert result == [("test", 10)]
