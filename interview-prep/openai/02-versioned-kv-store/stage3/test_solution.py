"""Tests for Versioned KV Store Stage 3 - Timestamp"""
import pytest
from solution import TimestampVersionedKVStore


class TestTimestampVersionedKVStore:
    def test_get_at_timestamp_basic(self):
        store = TimestampVersionedKVStore()
        store.put("key", "v1", timestamp=10)
        store.put("key", "v2", timestamp=20)

        assert store.get_at_timestamp("key", 15) == "v1"
        assert store.get_at_timestamp("key", 25) == "v2"
        assert store.get_at_timestamp("key", 10) == "v1"
        assert store.get_at_timestamp("key", 20) == "v2"

    def test_get_at_timestamp_before_first(self):
        store = TimestampVersionedKVStore()
        store.put("key", "v1", timestamp=10)
        assert store.get_at_timestamp("key", 5) is None

    def test_get_at_timestamp_nonexistent_key(self):
        store = TimestampVersionedKVStore()
        assert store.get_at_timestamp("nonexistent", 10) is None

    def test_multiple_updates(self):
        store = TimestampVersionedKVStore()
        store.put("key", "a", timestamp=10)
        store.put("key", "b", timestamp=20)
        store.put("key", "c", timestamp=30)

        assert store.get_at_timestamp("key", 5) is None
        assert store.get_at_timestamp("key", 10) == "a"
        assert store.get_at_timestamp("key", 15) == "a"
        assert store.get_at_timestamp("key", 20) == "b"
        assert store.get_at_timestamp("key", 25) == "b"
        assert store.get_at_timestamp("key", 30) == "c"
        assert store.get_at_timestamp("key", 100) == "c"
