"""Tests for Chat Messages Stage 2"""
import pytest
from solution import ChatSystem


class TestChatSystemStage2:
    """Test suite for Stage 2 functionality."""

    def test_list_messages(self):
        """List all messages for user."""
        chat = ChatSystem()
        chat.send_message("user1", "msg_c", "C")
        chat.send_message("user1", "msg_a", "A")
        chat.send_message("user1", "msg_b", "B")

        result = chat.list_messages("user1")
        assert result == ["msg_a", "msg_b", "msg_c"]

    def test_list_messages_empty_user(self):
        """List messages for user with no messages."""
        chat = ChatSystem()
        assert chat.list_messages("nonexistent") == []

    def test_list_messages_by_prefix(self):
        """List messages filtered by prefix."""
        chat = ChatSystem()
        chat.send_message("user1", "hello_1", "Hi")
        chat.send_message("user1", "hello_2", "Hello")
        chat.send_message("user1", "goodbye_1", "Bye")

        result = chat.list_messages_by_prefix("user1", "hello")
        assert result == ["hello_1", "hello_2"]

    def test_list_messages_by_prefix_no_matches(self):
        """Prefix with no matches returns empty list."""
        chat = ChatSystem()
        chat.send_message("user1", "msg1", "Hello")
        assert chat.list_messages_by_prefix("user1", "xyz") == []
