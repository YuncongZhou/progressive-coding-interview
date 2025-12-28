"""Tests for LRU Cache Stage 4 - Statistics"""
import pytest
import time
from solution import LRUCache, CacheStats


class TestLRUCacheStage4:
    def test_hit_count(self):
        cache = LRUCache(10)
        cache.put("a", 1)
        cache.get("a")
        cache.get("a")

        stats = cache.stats()
        assert stats.hits == 2

    def test_miss_count(self):
        cache = LRUCache(10)
        cache.get("missing")
        cache.get("also_missing")

        stats = cache.stats()
        assert stats.misses == 2

    def test_hit_rate(self):
        cache = LRUCache(10)
        cache.put("a", 1)
        cache.get("a")  # hit
        cache.get("a")  # hit
        cache.get("b")  # miss

        stats = cache.stats()
        assert stats.hit_rate == pytest.approx(2/3)

    def test_eviction_count(self):
        cache = LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)  # Evicts "a"
        cache.put("d", 4)  # Evicts "b"

        stats = cache.stats()
        assert stats.evictions == 2

    def test_expiration_count(self):
        cache = LRUCache(10, default_ttl=0.1)
        cache.put("a", 1)
        cache.put("b", 2)
        time.sleep(0.15)
        cache.get("a")  # Triggers expiration
        cache.get("b")  # Triggers expiration

        stats = cache.stats()
        assert stats.expirations == 2

    def test_reset_stats(self):
        cache = LRUCache(10)
        cache.put("a", 1)
        cache.get("a")
        cache.get("missing")

        cache.reset_stats()
        stats = cache.stats()

        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.evictions == 0

    def test_stats_size_capacity(self):
        cache = LRUCache(5)
        cache.put("a", 1)
        cache.put("b", 2)

        stats = cache.stats()
        assert stats.size == 2
        assert stats.capacity == 5

    def test_keys(self):
        cache = LRUCache(10)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.get("a")  # Move to end

        keys = cache.keys()
        assert keys == ["b", "a"]

    def test_items(self):
        cache = LRUCache(10)
        cache.put("a", 1)
        cache.put("b", 2)

        items = cache.items()
        assert ("a", 1) in items
        assert ("b", 2) in items

    def test_items_excludes_expired(self):
        cache = LRUCache(10, default_ttl=0.1)
        cache.put("a", 1)
        cache.put("b", 2, ttl=1.0)
        time.sleep(0.15)

        items = cache.items()
        assert len(items) == 1
        assert ("b", 2) in items
