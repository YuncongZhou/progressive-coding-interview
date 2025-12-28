"""Tests for CD Command Stage 2 - Symbolic Links"""
import pytest
from solution import FileSystem, cd


class TestCDCommandStage2:
    def test_simple_cd(self):
        # Backwards compatible
        assert cd("/foo", "bar") == "/foo/bar"

    def test_symlink_resolution(self):
        fs = FileSystem()
        fs.mkdir("/home")
        fs.mkdir("/home/user")
        fs.mkdir("/var")
        fs.mkdir("/var/log")
        fs.create_symlink("/logs", "/var/log")

        result = fs.cd("/home/user", "/logs")
        assert result == "/var/log"

    def test_relative_symlink(self):
        fs = FileSystem()
        fs.mkdir("/a")
        fs.mkdir("/a/b")
        fs.mkdir("/a/c")
        fs.create_symlink("/a/b/link", "../c")

        result = fs.cd("/", "/a/b/link")
        assert result == "/a/c"

    def test_nested_symlinks(self):
        fs = FileSystem()
        fs.mkdir("/real")
        fs.create_symlink("/link1", "/real")
        fs.create_symlink("/link2", "/link1")

        result = fs.cd("/", "/link2")
        assert result == "/real"

    def test_symlink_in_path(self):
        fs = FileSystem()
        fs.mkdir("/home")
        fs.mkdir("/home/user")
        fs.mkdir("/home/user/docs")
        fs.create_symlink("/u", "/home/user")

        result = fs.cd("/", "/u/docs")
        assert result == "/home/user/docs"

    def test_mkdir_creates_directory(self):
        fs = FileSystem()
        assert fs.mkdir("/test") is True
        assert fs.mkdir("/test") is False  # Already exists

    def test_create_symlink(self):
        fs = FileSystem()
        fs.mkdir("/target")
        assert fs.create_symlink("/link", "/target") is True
        assert fs.create_symlink("/link", "/other") is False  # Already exists

    def test_cd_with_parent_through_symlink(self):
        fs = FileSystem()
        fs.mkdir("/a")
        fs.mkdir("/a/b")
        fs.mkdir("/x")
        fs.mkdir("/x/y")
        fs.create_symlink("/a/b/link", "/x/y")

        result = fs.cd("/", "/a/b/link/..")
        assert result == "/x"

    def test_symlink_to_root(self):
        fs = FileSystem()
        fs.create_symlink("/root_link", "/")

        result = fs.cd("/home", "/root_link")
        assert result == "/"
