"""Tests for Versioned KV Store Stage 4 - Persistence"""
import pytest
import os
from solution import PersistentVersionedKVStore


class TestPersistentVersionedKVStore:
    def test_save_and_load(self, tmp_path):
        filepath = tmp_path / "store.dat"

        store = PersistentVersionedKVStore()
        store.put("key1", "value1", 10)
        store.put("key1", "value2", 20)
        store.put("key2", "other", 15)
        store.save_to_file(str(filepath))

        # Load into new store
        new_store = PersistentVersionedKVStore()
        new_store.load_from_file(str(filepath))

        assert new_store.get("key1") == ("value2", 2)
        assert new_store.get_version("key1", 1) == "value1"
        assert new_store.get("key2") == ("other", 1)

    def test_special_characters(self, tmp_path):
        filepath = tmp_path / "store.dat"

        store = PersistentVersionedKVStore()
        store.put("key|with|pipes", "value|with|pipes", 10)
        store.put("key\nwith\nnewlines", "value\nwith\nnewlines", 20)
        store.save_to_file(str(filepath))

        new_store = PersistentVersionedKVStore()
        new_store.load_from_file(str(filepath))

        assert new_store.get("key|with|pipes") == ("value|with|pipes", 1)
        assert new_store.get("key\nwith\nnewlines") == ("value\nwith\nnewlines", 1)

    def test_timestamp_preserved(self, tmp_path):
        filepath = tmp_path / "store.dat"

        store = PersistentVersionedKVStore()
        store.put("key", "v1", 10)
        store.put("key", "v2", 20)
        store.save_to_file(str(filepath))

        new_store = PersistentVersionedKVStore()
        new_store.load_from_file(str(filepath))

        assert new_store.get_at_timestamp("key", 15) == "v1"
        assert new_store.get_at_timestamp("key", 25) == "v2"

    def test_empty_store(self, tmp_path):
        filepath = tmp_path / "store.dat"

        store = PersistentVersionedKVStore()
        store.save_to_file(str(filepath))

        new_store = PersistentVersionedKVStore()
        new_store.load_from_file(str(filepath))
        assert new_store.get("any") is None
