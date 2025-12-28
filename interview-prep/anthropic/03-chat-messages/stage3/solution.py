"""
Chat Messages System - Stage 3

Chat messages with TTL (expiration) support.

Design Rationale:
- Messages store optional expires_at timestamp
- Filtering by timestamp on read operations
"""


class ChatSystem:
    """Chat message storage system with TTL support."""

    def __init__(self):
        self._messages: dict[str, dict] = {}
        self._user_messages: dict[str, set[str]] = {}

    def send_message(self, user_id: str, message_id: str, content: str) -> bool:
        """Sends a message (no expiration)."""
        if message_id in self._messages:
            return False
        self._messages[message_id] = {
            "user_id": user_id,
            "content": content,
            "expires_at": None
        }
        if user_id not in self._user_messages:
            self._user_messages[user_id] = set()
        self._user_messages[user_id].add(message_id)
        return True

    def get_message(self, message_id: str) -> dict | None:
        if message_id not in self._messages:
            return None
        msg = self._messages[message_id]
        return {"user_id": msg["user_id"], "content": msg["content"]}

    def delete_message(self, message_id: str) -> bool:
        if message_id not in self._messages:
            return False
        user_id = self._messages[message_id]["user_id"]
        if user_id in self._user_messages:
            self._user_messages[user_id].discard(message_id)
        del self._messages[message_id]
        return True

    def list_messages(self, user_id: str) -> list[str]:
        if user_id not in self._user_messages:
            return []
        return sorted(self._user_messages[user_id])

    def list_messages_by_prefix(self, user_id: str, prefix: str) -> list[str]:
        if user_id not in self._user_messages:
            return []
        matches = [mid for mid in self._user_messages[user_id] if mid.startswith(prefix)]
        return sorted(matches)

    # Stage 3 methods

    def send_message_with_expiry(
        self, user_id: str, message_id: str, content: str, timestamp: int, ttl: int
    ) -> bool:
        """Message expires at timestamp + ttl."""
        if message_id in self._messages:
            return False
        self._messages[message_id] = {
            "user_id": user_id,
            "content": content,
            "expires_at": timestamp + ttl
        }
        if user_id not in self._user_messages:
            self._user_messages[user_id] = set()
        self._user_messages[user_id].add(message_id)
        return True

    def get_message_at(self, message_id: str, timestamp: int) -> dict | None:
        """Returns message if not expired at given timestamp."""
        if message_id not in self._messages:
            return None
        msg = self._messages[message_id]
        if msg["expires_at"] is not None and timestamp >= msg["expires_at"]:
            return None
        return {"user_id": msg["user_id"], "content": msg["content"]}

    def list_messages_at(self, user_id: str, timestamp: int) -> list[str]:
        """Lists only non-expired messages at timestamp."""
        if user_id not in self._user_messages:
            return []
        result = []
        for mid in self._user_messages[user_id]:
            msg = self._messages[mid]
            if msg["expires_at"] is None or timestamp < msg["expires_at"]:
                result.append(mid)
        return sorted(result)
