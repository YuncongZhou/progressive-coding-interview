"""
LRU Cache - Stage 4

Statistics and monitoring.

Design Rationale:
- Track hits, misses, evictions
- Calculate hit rate
- Export metrics for monitoring
"""

from collections import OrderedDict
from typing import Optional, Any
from threading import RLock
from dataclasses import dataclass
import time


@dataclass
class CacheStats:
    """Cache statistics."""
    hits: int
    misses: int
    evictions: int
    expirations: int
    size: int
    capacity: int

    @property
    def hit_rate(self) -> float:
        """Calculate hit rate (0.0 to 1.0)."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    @property
    def miss_rate(self) -> float:
        """Calculate miss rate (0.0 to 1.0)."""
        return 1.0 - self.hit_rate


class LRUCache:
    """LRU cache with statistics."""

    def __init__(self, capacity: int, default_ttl: float = None):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self._capacity = capacity
        self._default_ttl = default_ttl
        self._cache: OrderedDict[str, tuple[Any, float | None]] = OrderedDict()
        self._lock = RLock()

        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._expirations = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value, tracking statistics."""
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            value, expires_at = self._cache[key]
            if expires_at is not None and time.time() > expires_at:
                del self._cache[key]
                self._expirations += 1
                self._misses += 1
                return None

            self._hits += 1
            self._cache.move_to_end(key)
            return value

    def put(self, key: str, value: Any, ttl: float = None) -> None:
        """Put value, tracking evictions."""
        with self._lock:
            effective_ttl = ttl if ttl is not None else self._default_ttl
            expires_at = time.time() + effective_ttl if effective_ttl else None

            if key in self._cache:
                self._cache[key] = (value, expires_at)
                self._cache.move_to_end(key)
            else:
                # Evict expired first
                expired = self._evict_expired_unsafe()
                self._expirations += expired

                if len(self._cache) >= self._capacity:
                    self._cache.popitem(last=False)
                    self._evictions += 1

                self._cache[key] = (value, expires_at)

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def get_or_put(self, key: str, factory, ttl: float = None) -> Any:
        with self._lock:
            value = self.get(key)
            if value is not None:
                return value
            value = factory()
            self.put(key, value, ttl)
            return value

    def size(self) -> int:
        with self._lock:
            return len(self._cache)

    def capacity(self) -> int:
        return self._capacity

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()

    def stats(self) -> CacheStats:
        """Get current cache statistics."""
        with self._lock:
            return CacheStats(
                hits=self._hits,
                misses=self._misses,
                evictions=self._evictions,
                expirations=self._expirations,
                size=len(self._cache),
                capacity=self._capacity
            )

    def reset_stats(self) -> None:
        """Reset all statistics to zero."""
        with self._lock:
            self._hits = 0
            self._misses = 0
            self._evictions = 0
            self._expirations = 0

    def cleanup(self) -> int:
        with self._lock:
            count = self._evict_expired_unsafe()
            self._expirations += count
            return count

    def _evict_expired_unsafe(self) -> int:
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

    def keys(self) -> list[str]:
        """Get list of all keys (most recent last)."""
        with self._lock:
            return list(self._cache.keys())

    def items(self) -> list[tuple[str, Any]]:
        """Get list of (key, value) pairs."""
        with self._lock:
            now = time.time()
            return [(k, v) for k, (v, exp) in self._cache.items()
                    if exp is None or now <= exp]
