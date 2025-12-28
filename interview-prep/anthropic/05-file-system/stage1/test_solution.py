"""Tests for File System Stage 1"""
import pytest
from solution import FileSystem


class TestFileSystemStage1:
    def test_create_file(self):
        fs = FileSystem()
        result = fs.create_file("/test.txt", "Hello")
        assert result is True
        assert fs.file_exists("/test.txt")

    def test_create_file_no_parent(self):
        fs = FileSystem()
        result = fs.create_file("/foo/bar.txt", "Hello")
        assert result is False

    def test_read_file(self):
        fs = FileSystem()
        fs.create_file("/test.txt", "Hello World")
        content = fs.read_file("/test.txt")
        assert content == "Hello World"

    def test_read_nonexistent_file(self):
        fs = FileSystem()
        assert fs.read_file("/nonexistent.txt") is None

    def test_delete_file(self):
        fs = FileSystem()
        fs.create_file("/test.txt", "Hello")
        result = fs.delete_file("/test.txt")
        assert result is True
        assert not fs.file_exists("/test.txt")

    def test_delete_nonexistent_file(self):
        fs = FileSystem()
        result = fs.delete_file("/nonexistent.txt")
        assert result is False

    def test_file_exists(self):
        fs = FileSystem()
        assert not fs.file_exists("/test.txt")
        fs.create_file("/test.txt", "Hello")
        assert fs.file_exists("/test.txt")

    def test_create_duplicate_file_fails(self):
        fs = FileSystem()
        fs.create_file("/test.txt", "First")
        result = fs.create_file("/test.txt", "Second")
        assert result is False
