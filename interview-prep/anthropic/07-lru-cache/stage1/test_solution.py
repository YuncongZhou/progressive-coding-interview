"""Tests for LRU Cache Stage 1"""
import pytest
from solution import LRUCache


class TestLRUCacheStage1:
    def test_basic_get_put(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        assert cache.get("a") == 1
        assert cache.get("b") == 2

    def test_get_nonexistent(self):
        cache = LRUCache(2)
        assert cache.get("missing") is None

    def test_eviction(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)  # Evicts "a"
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("c") == 3

    def test_access_updates_recency(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.get("a")  # Access "a", making it recent
        cache.put("c", 3)  # Evicts "b" (least recent)
        assert cache.get("a") == 1
        assert cache.get("b") is None
        assert cache.get("c") == 3

    def test_update_existing(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("a", 10)
        assert cache.get("a") == 10
        assert cache.size() == 1

    def test_delete(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        assert cache.delete("a") is True
        assert cache.get("a") is None
        assert cache.delete("missing") is False

    def test_size_and_capacity(self):
        cache = LRUCache(3)
        assert cache.capacity() == 3
        assert cache.size() == 0
        cache.put("a", 1)
        assert cache.size() == 1

    def test_clear(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.clear()
        assert cache.size() == 0
        assert cache.get("a") is None

    def test_invalid_capacity(self):
        with pytest.raises(ValueError):
            LRUCache(0)
        with pytest.raises(ValueError):
            LRUCache(-1)
