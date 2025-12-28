"""Tests for File System Stage 4"""
import pytest
from solution import FileSystem


class TestFileSystemStage4:
    def test_set_quota(self):
        fs = FileSystem()
        fs.set_quota("alice", 1000)
        # Should not raise

    def test_get_usage_empty(self):
        fs = FileSystem()
        assert fs.get_usage("alice") == 0

    def test_compress_file(self):
        fs = FileSystem()
        fs.create_file("/test.txt", "Hello World! " * 100)

        original_content = fs.read_file("/test.txt")
        result = fs.compress_file("/test.txt")
        assert result is True

        # Can still read the file
        assert fs.read_file("/test.txt") == original_content

    def test_compress_already_compressed(self):
        fs = FileSystem()
        fs.create_file("/test.txt", "Hello World!")
        fs.compress_file("/test.txt")
        result = fs.compress_file("/test.txt")
        assert result is False

    def test_deduplicate(self):
        fs = FileSystem()
        fs.create_file("/a.txt", "Same content")
        fs.create_file("/b.txt", "Same content")
        fs.create_file("/c.txt", "Different content")

        bytes_saved = fs.deduplicate()
        assert bytes_saved > 0
