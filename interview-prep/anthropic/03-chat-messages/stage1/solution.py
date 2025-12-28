"""
Chat Messages System - Stage 1

Basic chat message storage and retrieval.

Design Rationale:
- Messages stored in dict by message_id for O(1) lookup
- Each message contains user_id and content
- Simple structure that can be extended for future stages
"""


class ChatSystem:
    """Chat message storage system."""

    def __init__(self):
        """Initialize empty chat system."""
        self._messages: dict[str, dict] = {}

    def send_message(self, user_id: str, message_id: str, content: str) -> bool:
        """
        Sends a message.

        Args:
            user_id: The user sending the message
            message_id: Unique message identifier
            content: Message content

        Returns:
            False if message_id already exists
        """
        if message_id in self._messages:
            return False
        self._messages[message_id] = {"user_id": user_id, "content": content}
        return True

    def get_message(self, message_id: str) -> dict | None:
        """
        Returns message dict with user_id and content.

        Args:
            message_id: The message identifier

        Returns:
            Message dict or None if not found
        """
        if message_id not in self._messages:
            return None
        return self._messages[message_id].copy()

    def delete_message(self, message_id: str) -> bool:
        """
        Deletes a message.

        Args:
            message_id: The message identifier

        Returns:
            False if not found
        """
        if message_id not in self._messages:
            return False
        del self._messages[message_id]
        return True
