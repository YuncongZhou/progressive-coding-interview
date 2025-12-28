"""Tests for Chat Messages Stage 4"""
import pytest
from solution import ChatSystem


class TestChatSystemStage4:
    """Test suite for Stage 4 zip/unzip functionality."""

    def test_zip_creates_backup_id(self):
        chat = ChatSystem()
        chat.send_message("user1", "msg1", "Hello")
        backup_id = chat.zip_messages("user1", 10)
        assert backup_id is not None
        assert len(backup_id) > 0

    def test_unzip_restores_messages(self):
        chat = ChatSystem()
        chat.send_message("user1", "msg1", "Hello")
        chat.send_message("user1", "msg2", "World")

        backup_id = chat.zip_messages("user1", 10)

        # Delete messages
        chat.delete_message("msg1")
        chat.delete_message("msg2")

        # Restore
        count = chat.unzip_messages(backup_id, 20)
        assert count == 2

        assert chat.get_message("msg1")["content"] == "Hello"
        assert chat.get_message("msg2")["content"] == "World"

    def test_unzip_recalculates_ttl(self):
        chat = ChatSystem()
        chat.send_message_with_expiry("user1", "msg1", "Hello", 10, 10)  # expires at 20

        # Backup at timestamp 15 (remaining TTL = 5)
        backup_id = chat.zip_messages("user1", 15)

        # Clear and restore at timestamp 100
        chat.delete_message("msg1")
        chat.unzip_messages(backup_id, 100)

        # New expiration = 100 + 5 = 105
        assert chat.get_message_at("msg1", 104) is not None
        assert chat.get_message_at("msg1", 105) is None

    def test_zip_excludes_expired(self):
        chat = ChatSystem()
        chat.send_message_with_expiry("user1", "msg1", "Expired", 10, 5)  # expires at 15
        chat.send_message("user1", "msg2", "Active")

        # Backup at timestamp 20 (msg1 is expired, should NOT be included)
        backup_id = chat.zip_messages("user1", 20)

        # Delete both messages
        chat.delete_message("msg1")
        chat.delete_message("msg2")

        # Restore from backup
        count = chat.unzip_messages(backup_id, 30)
        assert count == 1  # Only msg2 was backed up
        assert chat.get_message("msg2") is not None
        assert chat.get_message("msg1") is None  # Not restored because it was expired

    def test_unzip_invalid_backup_returns_zero(self):
        chat = ChatSystem()
        count = chat.unzip_messages("invalid_id", 10)
        assert count == 0
