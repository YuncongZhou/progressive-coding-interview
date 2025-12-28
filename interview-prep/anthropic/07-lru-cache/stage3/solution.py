"""
LRU Cache - Stage 3

Thread-safe implementation.

Design Rationale:
- Use RLock for thread safety
- Context manager support
- Atomic operations
"""

from collections import OrderedDict
from typing import Optional, Any
from threading import RLock
import time


class LRUCache:
    """Thread-safe LRU cache."""

    def __init__(self, capacity: int, default_ttl: float = None):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self._capacity = capacity
        self._default_ttl = default_ttl
        self._cache: OrderedDict[str, tuple[Any, float | None]] = OrderedDict()
        self._lock = RLock()

    def get(self, key: str) -> Optional[Any]:
        """Thread-safe get."""
        with self._lock:
            if key not in self._cache:
                return None

            value, expires_at = self._cache[key]
            if expires_at is not None and time.time() > expires_at:
                del self._cache[key]
                return None

            self._cache.move_to_end(key)
            return value

    def put(self, key: str, value: Any, ttl: float = None) -> None:
        """Thread-safe put."""
        with self._lock:
            effective_ttl = ttl if ttl is not None else self._default_ttl
            expires_at = time.time() + effective_ttl if effective_ttl else None

            if key in self._cache:
                self._cache[key] = (value, expires_at)
                self._cache.move_to_end(key)
            else:
                self._evict_expired_unsafe()
                if len(self._cache) >= self._capacity:
                    self._cache.popitem(last=False)
                self._cache[key] = (value, expires_at)

    def delete(self, key: str) -> bool:
        """Thread-safe delete."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def get_or_put(self, key: str, factory, ttl: float = None) -> Any:
        """
        Get value if exists, otherwise compute and store.
        Factory is only called if key doesn't exist.
        """
        with self._lock:
            value = self.get(key)
            if value is not None:
                return value
            value = factory()
            self.put(key, value, ttl)
            return value

    def update(self, key: str, updater, ttl: float = None) -> Optional[Any]:
        """
        Atomically update value using updater function.
        Returns new value or None if key doesn't exist.
        """
        with self._lock:
            current = self.get(key)
            if current is None:
                return None
            new_value = updater(current)
            self.put(key, new_value, ttl)
            return new_value

    def size(self) -> int:
        with self._lock:
            return len(self._cache)

    def active_size(self) -> int:
        with self._lock:
            now = time.time()
            return sum(1 for _, (_, exp) in self._cache.items()
                       if exp is None or now <= exp)

    def capacity(self) -> int:
        return self._capacity

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()

    def cleanup(self) -> int:
        with self._lock:
            return self._evict_expired_unsafe()

    def _evict_expired_unsafe(self) -> int:
        """Remove expired entries (must hold lock)."""
        now = time.time()
        expired = [k for k, (_, exp) in self._cache.items()
                   if exp is not None and now > exp]
        for key in expired:
            del self._cache[key]
        return len(expired)

    def get_ttl(self, key: str) -> Optional[float]:
        with self._lock:
            if key not in self._cache:
                return None
            _, expires_at = self._cache[key]
            if expires_at is None:
                return None
            return max(0, expires_at - time.time())
