"""
Chat Messages System - Stage 2

Chat messages with list and prefix filtering.

Design Rationale:
- Track messages per user for efficient listing
- Prefix filtering with sorted lexicographic output
"""


class ChatSystem:
    """Chat message storage system with listing capabilities."""

    def __init__(self):
        """Initialize empty chat system."""
        self._messages: dict[str, dict] = {}
        self._user_messages: dict[str, set[str]] = {}  # user_id -> set of message_ids

    def send_message(self, user_id: str, message_id: str, content: str) -> bool:
        """Sends a message."""
        if message_id in self._messages:
            return False
        self._messages[message_id] = {"user_id": user_id, "content": content}
        if user_id not in self._user_messages:
            self._user_messages[user_id] = set()
        self._user_messages[user_id].add(message_id)
        return True

    def get_message(self, message_id: str) -> dict | None:
        """Returns message dict."""
        if message_id not in self._messages:
            return None
        return self._messages[message_id].copy()

    def delete_message(self, message_id: str) -> bool:
        """Deletes a message."""
        if message_id not in self._messages:
            return False
        user_id = self._messages[message_id]["user_id"]
        if user_id in self._user_messages:
            self._user_messages[user_id].discard(message_id)
        del self._messages[message_id]
        return True

    def list_messages(self, user_id: str) -> list[str]:
        """
        Returns all message_ids for user, sorted lexicographically.

        Args:
            user_id: The user identifier

        Returns:
            Sorted list of message_ids
        """
        if user_id not in self._user_messages:
            return []
        return sorted(self._user_messages[user_id])

    def list_messages_by_prefix(self, user_id: str, prefix: str) -> list[str]:
        """
        Returns message_ids starting with prefix, sorted lexicographically.

        Args:
            user_id: The user identifier
            prefix: Prefix to filter by

        Returns:
            Sorted list of matching message_ids
        """
        if user_id not in self._user_messages:
            return []
        matches = [mid for mid in self._user_messages[user_id] if mid.startswith(prefix)]
        return sorted(matches)
