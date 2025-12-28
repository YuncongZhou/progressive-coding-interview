"""Tests for File System Stage 2"""
import pytest
from solution import FileSystem


class TestFileSystemStage2:
    def test_create_directory(self):
        fs = FileSystem()
        result = fs.create_directory("/foo")
        assert result is True

    def test_create_file_in_directory(self):
        fs = FileSystem()
        fs.create_directory("/foo")
        result = fs.create_file("/foo/bar.txt", "Hello")
        assert result is True
        assert fs.read_file("/foo/bar.txt") == "Hello"

    def test_list_directory(self):
        fs = FileSystem()
        fs.create_directory("/foo")
        fs.create_file("/foo/a.txt", "A")
        fs.create_file("/foo/b.txt", "B")

        result = fs.list_directory("/foo")
        assert result == ["a.txt", "b.txt"]

    def test_list_directory_root(self):
        fs = FileSystem()
        fs.create_directory("/foo")
        fs.create_file("/bar.txt", "Hello")

        result = fs.list_directory("/")
        assert set(result) == {"foo", "bar.txt"}

    def test_delete_empty_directory(self):
        fs = FileSystem()
        fs.create_directory("/foo")
        result = fs.delete_directory("/foo")
        assert result is True

    def test_delete_nonempty_directory_fails(self):
        fs = FileSystem()
        fs.create_directory("/foo")
        fs.create_file("/foo/bar.txt", "Hello")
        result = fs.delete_directory("/foo")
        assert result is False

    def test_delete_directory_recursive(self):
        fs = FileSystem()
        fs.create_directory("/foo")
        fs.create_file("/foo/bar.txt", "Hello")
        result = fs.delete_directory("/foo", recursive=True)
        assert result is True
        assert fs.list_directory("/foo") is None
