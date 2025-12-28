"""
LRU Cache - Stage 1

Basic LRU (Least Recently Used) cache.

Design Rationale:
- Use OrderedDict for O(1) operations
- get() and put() update recency
- Evict least recently used when capacity reached
"""

from collections import OrderedDict
from typing import Optional, Any


class LRUCache:
    """Basic LRU cache implementation."""

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self._capacity = capacity
        self._cache: OrderedDict[str, Any] = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        """Get value by key. Returns None if not found."""
        if key not in self._cache:
            return None
        # Move to end (most recently used)
        self._cache.move_to_end(key)
        return self._cache[key]

    def put(self, key: str, value: Any) -> None:
        """Put key-value pair in cache."""
        if key in self._cache:
            # Update existing and move to end
            self._cache[key] = value
            self._cache.move_to_end(key)
        else:
            # Evict if at capacity
            if len(self._cache) >= self._capacity:
                self._cache.popitem(last=False)
            self._cache[key] = value

    def delete(self, key: str) -> bool:
        """Delete key from cache. Returns True if deleted."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def size(self) -> int:
        """Return current number of items in cache."""
        return len(self._cache)

    def capacity(self) -> int:
        """Return cache capacity."""
        return self._capacity

    def clear(self) -> None:
        """Clear all items from cache."""
        self._cache.clear()
