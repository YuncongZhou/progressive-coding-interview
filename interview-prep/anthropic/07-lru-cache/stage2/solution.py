"""
LRU Cache - Stage 2

TTL (Time-To-Live) support.

Design Rationale:
- Each entry has an expiration time
- Expired entries are removed on access
- Background cleanup optional
"""

from collections import OrderedDict
from typing import Optional, Any
import time


class LRUCache:
    """LRU cache with TTL support."""

    def __init__(self, capacity: int, default_ttl: float = None):
        """
        Args:
            capacity: Maximum number of items
            default_ttl: Default TTL in seconds (None = no expiration)
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self._capacity = capacity
        self._default_ttl = default_ttl
        self._cache: OrderedDict[str, tuple[Any, float | None]] = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        """Get value by key. Returns None if not found or expired."""
        if key not in self._cache:
            return None

        value, expires_at = self._cache[key]

        # Check expiration
        if expires_at is not None and time.time() > expires_at:
            del self._cache[key]
            return None

        # Move to end (most recently used)
        self._cache.move_to_end(key)
        return value

    def put(self, key: str, value: Any, ttl: float = None) -> None:
        """
        Put key-value pair in cache.

        Args:
            ttl: Optional TTL override (None = use default)
        """
        # Determine expiration time
        effective_ttl = ttl if ttl is not None else self._default_ttl
        expires_at = time.time() + effective_ttl if effective_ttl else None

        if key in self._cache:
            self._cache[key] = (value, expires_at)
            self._cache.move_to_end(key)
        else:
            # Evict expired first, then LRU if still at capacity
            self._evict_expired()
            if len(self._cache) >= self._capacity:
                self._cache.popitem(last=False)
            self._cache[key] = (value, expires_at)

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def size(self) -> int:
        """Return current number of items (including expired)."""
        return len(self._cache)

    def active_size(self) -> int:
        """Return number of non-expired items."""
        now = time.time()
        count = 0
        for key, (_, expires_at) in self._cache.items():
            if expires_at is None or now <= expires_at:
                count += 1
        return count

    def capacity(self) -> int:
        """Return cache capacity."""
        return self._capacity

    def clear(self) -> None:
        """Clear all items from cache."""
        self._cache.clear()

    def _evict_expired(self) -> int:
        """Remove expired entries. Returns number removed."""
        now = time.time()
        expired = [k for k, (_, exp) in self._cache.items()
                   if exp is not None and now > exp]
        for key in expired:
            del self._cache[key]
        return len(expired)

    def cleanup(self) -> int:
        """Manually trigger cleanup of expired entries."""
        return self._evict_expired()

    def get_ttl(self, key: str) -> Optional[float]:
        """Get remaining TTL for a key. None if not found or no TTL."""
        if key not in self._cache:
            return None
        _, expires_at = self._cache[key]
        if expires_at is None:
            return None
        remaining = expires_at - time.time()
        return max(0, remaining)
