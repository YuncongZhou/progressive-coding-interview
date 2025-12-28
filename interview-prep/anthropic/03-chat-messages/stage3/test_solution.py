"""Tests for Chat Messages Stage 3"""
import pytest
from solution import ChatSystem


class TestChatSystemStage3:
    """Test suite for Stage 3 TTL functionality."""

    def test_send_message_with_expiry(self):
        chat = ChatSystem()
        result = chat.send_message_with_expiry("user1", "msg1", "Hello", 10, 5)
        assert result is True

    def test_get_message_at_before_expiry(self):
        chat = ChatSystem()
        chat.send_message_with_expiry("user1", "msg1", "Hello", 10, 5)
        msg = chat.get_message_at("msg1", 14)
        assert msg is not None
        assert msg["content"] == "Hello"

    def test_get_message_at_after_expiry(self):
        chat = ChatSystem()
        chat.send_message_with_expiry("user1", "msg1", "Hello", 10, 5)
        msg = chat.get_message_at("msg1", 15)
        assert msg is None

    def test_list_messages_at_excludes_expired(self):
        chat = ChatSystem()
        chat.send_message_with_expiry("user1", "msg1", "A", 10, 5)  # expires at 15
        chat.send_message_with_expiry("user1", "msg2", "B", 10, 10)  # expires at 20
        chat.send_message("user1", "msg3", "C")  # never expires

        result = chat.list_messages_at("user1", 16)
        assert "msg1" not in result
        assert "msg2" in result
        assert "msg3" in result

    def test_non_expiring_message(self):
        chat = ChatSystem()
        chat.send_message("user1", "msg1", "Hello")
        msg = chat.get_message_at("msg1", 1000000)
        assert msg is not None
