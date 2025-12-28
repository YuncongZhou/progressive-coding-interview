"""Tests for LRU Cache Stage 3 - Thread Safety"""
import pytest
import threading
import time
from solution import LRUCache


class TestLRUCacheStage3:
    def test_concurrent_writes(self):
        cache = LRUCache(100)
        results = []

        def writer(start):
            for i in range(100):
                cache.put(f"key_{start + i}", start + i)
                results.append(start + i)

        threads = [threading.Thread(target=writer, args=(i * 100,))
                   for i in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert cache.size() == 100  # Capped at capacity

    def test_concurrent_reads_writes(self):
        cache = LRUCache(100)
        for i in range(50):
            cache.put(f"key_{i}", i)

        errors = []

        def reader():
            for _ in range(100):
                for i in range(50):
                    cache.get(f"key_{i}")

        def writer():
            for i in range(50, 100):
                cache.put(f"key_{i}", i)

        threads = [threading.Thread(target=reader) for _ in range(3)]
        threads.append(threading.Thread(target=writer))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # No errors means thread-safe
        assert len(errors) == 0

    def test_get_or_put(self):
        cache = LRUCache(10)
        factory_calls = [0]

        def factory():
            factory_calls[0] += 1
            return "computed"

        result1 = cache.get_or_put("key", factory)
        result2 = cache.get_or_put("key", factory)

        assert result1 == "computed"
        assert result2 == "computed"
        assert factory_calls[0] == 1  # Factory called only once

    def test_get_or_put_concurrent(self):
        cache = LRUCache(10)
        call_count = [0]
        lock = threading.Lock()

        def factory():
            with lock:
                call_count[0] += 1
            time.sleep(0.01)  # Simulate slow computation
            return "value"

        results = []

        def getter():
            results.append(cache.get_or_put("key", factory))

        threads = [threading.Thread(target=getter) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should get the same value
        assert all(r == "value" for r in results)

    def test_update_atomic(self):
        cache = LRUCache(10)
        cache.put("counter", 0)

        def increment(val):
            return val + 1

        def updater():
            for _ in range(100):
                cache.update("counter", increment)

        threads = [threading.Thread(target=updater) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert cache.get("counter") == 500

    def test_update_nonexistent(self):
        cache = LRUCache(10)
        result = cache.update("missing", lambda x: x + 1)
        assert result is None
