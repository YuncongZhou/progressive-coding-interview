"""
Tests for Chat Messages Stage 1

Stage 1 Requirements:
- send_message(user_id, message_id, content) - Sends a message
- get_message(message_id) - Returns message dict
- delete_message(message_id) - Deletes message
"""
import pytest
from solution import ChatSystem


class TestChatSystemStage1:
    """Test suite for Stage 1 functionality."""

    def test_send_and_get_message(self):
        """Send and retrieve a message."""
        chat = ChatSystem()
        result = chat.send_message("user1", "msg1", "Hello!")
        assert result is True

        msg = chat.get_message("msg1")
        assert msg == {"user_id": "user1", "content": "Hello!"}

    def test_send_duplicate_message_id_fails(self):
        """Sending with duplicate message_id returns False."""
        chat = ChatSystem()
        chat.send_message("user1", "msg1", "First")
        result = chat.send_message("user2", "msg1", "Second")
        assert result is False

    def test_get_nonexistent_message(self):
        """Getting non-existent message returns None."""
        chat = ChatSystem()
        assert chat.get_message("nonexistent") is None

    def test_delete_message(self):
        """Delete an existing message."""
        chat = ChatSystem()
        chat.send_message("user1", "msg1", "Hello!")
        result = chat.delete_message("msg1")
        assert result is True
        assert chat.get_message("msg1") is None

    def test_delete_nonexistent_message(self):
        """Delete non-existent message returns False."""
        chat = ChatSystem()
        assert chat.delete_message("nonexistent") is False

    def test_multiple_messages(self):
        """Multiple messages can coexist."""
        chat = ChatSystem()
        chat.send_message("user1", "msg1", "Hello")
        chat.send_message("user2", "msg2", "World")

        assert chat.get_message("msg1")["content"] == "Hello"
        assert chat.get_message("msg2")["content"] == "World"

    def test_empty_content(self):
        """Empty content is valid."""
        chat = ChatSystem()
        chat.send_message("user1", "msg1", "")
        assert chat.get_message("msg1")["content"] == ""
