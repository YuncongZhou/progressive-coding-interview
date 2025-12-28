"""Tests for LRU Cache Stage 2 - TTL Support"""
import pytest
import time
from solution import LRUCache


class TestLRUCacheStage2:
    def test_basic_ttl(self):
        cache = LRUCache(10, default_ttl=0.1)
        cache.put("a", 1)
        assert cache.get("a") == 1
        time.sleep(0.15)
        assert cache.get("a") is None

    def test_no_ttl(self):
        cache = LRUCache(10)
        cache.put("a", 1)
        time.sleep(0.1)
        assert cache.get("a") == 1

    def test_custom_ttl(self):
        cache = LRUCache(10, default_ttl=1.0)
        cache.put("a", 1, ttl=0.1)
        time.sleep(0.15)
        assert cache.get("a") is None

    def test_longer_custom_ttl(self):
        cache = LRUCache(10, default_ttl=0.05)
        cache.put("a", 1, ttl=0.2)
        time.sleep(0.1)
        assert cache.get("a") == 1

    def test_active_size(self):
        cache = LRUCache(10, default_ttl=0.1)
        cache.put("a", 1)
        cache.put("b", 2, ttl=0.5)
        assert cache.active_size() == 2
        time.sleep(0.15)
        assert cache.active_size() == 1

    def test_cleanup(self):
        cache = LRUCache(10, default_ttl=0.1)
        cache.put("a", 1)
        cache.put("b", 2)
        time.sleep(0.15)
        removed = cache.cleanup()
        assert removed == 2
        assert cache.size() == 0

    def test_get_ttl(self):
        cache = LRUCache(10, default_ttl=1.0)
        cache.put("a", 1)
        ttl = cache.get_ttl("a")
        assert ttl is not None
        assert 0.9 < ttl <= 1.0

    def test_get_ttl_no_expiry(self):
        cache = LRUCache(10)
        cache.put("a", 1)
        assert cache.get_ttl("a") is None

    def test_evict_expired_before_lru(self):
        cache = LRUCache(2, default_ttl=0.1)
        cache.put("a", 1)
        time.sleep(0.15)
        cache.put("b", 2, ttl=1.0)
        cache.put("c", 3, ttl=1.0)  # Should evict expired "a"
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("c") == 3
