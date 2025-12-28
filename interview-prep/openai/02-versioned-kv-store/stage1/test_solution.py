"""Tests for Versioned KV Store Stage 1"""
import pytest
from solution import VersionedKVStore


class TestVersionedKVStoreStage1:
    def test_put_returns_version(self):
        store = VersionedKVStore()
        v1 = store.put("key", "value1")
        v2 = store.put("key", "value2")
        assert v1 == 1
        assert v2 == 2

    def test_get_returns_latest(self):
        store = VersionedKVStore()
        store.put("key", "v1")
        store.put("key", "v2")
        result = store.get("key")
        assert result == ("v2", 2)

    def test_get_nonexistent(self):
        store = VersionedKVStore()
        assert store.get("nonexistent") is None

    def test_get_version(self):
        store = VersionedKVStore()
        store.put("key", "v1")
        store.put("key", "v2")
        store.put("key", "v3")

        assert store.get_version("key", 1) == "v1"
        assert store.get_version("key", 2) == "v2"
        assert store.get_version("key", 3) == "v3"

    def test_get_version_nonexistent(self):
        store = VersionedKVStore()
        store.put("key", "v1")
        assert store.get_version("key", 99) is None
        assert store.get_version("nonexistent", 1) is None
