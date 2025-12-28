"""Tests for Versioned KV Store Stage 2 - Thread Safety"""
import pytest
import threading
from solution import ThreadSafeVersionedKVStore


class TestThreadSafeVersionedKVStore:
    def test_basic_put_get(self):
        store = ThreadSafeVersionedKVStore()
        v1 = store.put("key", "value1")
        assert v1 == 1
        assert store.get("key") == ("value1", 1)

    def test_concurrent_puts_unique_versions(self):
        """Multiple threads updating same key get different versions."""
        store = ThreadSafeVersionedKVStore()
        results = []
        errors = []

        def put_value(value):
            try:
                version = store.put("key", value)
                results.append(version)
            except Exception as e:
                errors.append(e)

        threads = []
        for i in range(10):
            t = threading.Thread(target=put_value, args=(f"value{i}",))
            threads.append(t)

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        # All versions should be unique
        assert len(set(results)) == 10
        # Versions should be 1-10
        assert sorted(results) == list(range(1, 11))

    def test_concurrent_reads_safe(self):
        """Concurrent reads don't cause issues."""
        store = ThreadSafeVersionedKVStore()
        store.put("key", "value")

        results = []

        def read_value():
            for _ in range(100):
                result = store.get("key")
                results.append(result)

        threads = [threading.Thread(target=read_value) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert all(r == ("value", 1) for r in results)
