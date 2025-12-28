"""Tests for File System Stage 3"""
import pytest
from solution import FileSystem


class TestFileSystemStage3:
    def test_set_permission(self):
        fs = FileSystem()
        fs.create_file("/test.txt", "Hello")
        result = fs.set_permission("/test.txt", "alice", "read")
        assert result is True

    def test_check_permission(self):
        fs = FileSystem()
        fs.create_file("/test.txt", "Hello")
        fs.set_permission("/test.txt", "alice", "read")

        assert fs.check_permission("/test.txt", "alice", "read") is True
        assert fs.check_permission("/test.txt", "alice", "write") is False
        assert fs.check_permission("/test.txt", "bob", "read") is False

    def test_read_file_as_with_permission(self):
        fs = FileSystem()
        fs.create_file("/test.txt", "Hello")
        fs.set_permission("/test.txt", "alice", "read")

        content = fs.read_file_as("/test.txt", "alice")
        assert content == "Hello"

    def test_read_file_as_without_permission(self):
        fs = FileSystem()
        fs.create_file("/test.txt", "Hello")

        content = fs.read_file_as("/test.txt", "alice")
        assert content is None
