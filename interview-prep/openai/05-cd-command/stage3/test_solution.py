"""Tests for CD Command Stage 3 - Validation and Home Directory"""
import pytest
from solution import FileSystem, PathError, cd


class TestCDCommandStage3:
    def test_backwards_compatible(self):
        assert cd("/foo", "bar") == "/foo/bar"
        assert cd("/foo", "..") == "/"

    def test_home_directory(self):
        fs = FileSystem(home_dir="/home/alice")
        result = fs.cd("/", "~")
        assert result == "/home/alice"

    def test_home_subdirectory(self):
        fs = FileSystem(home_dir="/home/alice")
        fs.mkdir("/home/alice/docs")
        result = fs.cd("/", "~/docs")
        assert result == "/home/alice/docs"

    def test_validation_valid_path(self):
        fs = FileSystem()
        fs.mkdir("/test")
        result = fs.cd("/", "/test", validate=True)
        assert result == "/test"

    def test_validation_invalid_path(self):
        fs = FileSystem()
        with pytest.raises(PathError):
            fs.cd("/", "/nonexistent", validate=True)

    def test_cd_safe_valid(self):
        fs = FileSystem()
        fs.mkdir("/test")
        result = fs.cd_safe("/", "/test")
        assert result == "/test"

    def test_cd_safe_invalid(self):
        fs = FileSystem()
        result = fs.cd_safe("/", "/nonexistent")
        assert result is None

    def test_mkdir_p(self):
        fs = FileSystem()
        fs.mkdir_p("/a/b/c/d")
        assert fs.exists("/a")
        assert fs.exists("/a/b")
        assert fs.exists("/a/b/c")
        assert fs.exists("/a/b/c/d")

    def test_exists(self):
        fs = FileSystem()
        fs.mkdir("/test")
        assert fs.exists("/test") is True
        assert fs.exists("/nonexistent") is False

    def test_symlink_validated(self):
        fs = FileSystem()
        fs.mkdir("/target")
        fs.create_symlink("/link", "/target")
        result = fs.cd("/", "/link", validate=True)
        assert result == "/target"

    def test_parent_navigation_validated(self):
        fs = FileSystem()
        fs.mkdir("/a")
        fs.mkdir("/a/b")
        result = fs.cd("/a/b", "..", validate=True)
        assert result == "/a"

    def test_complex_path_with_validation(self):
        fs = FileSystem()
        fs.mkdir("/a")
        fs.mkdir("/a/b")
        fs.mkdir("/a/c")
        result = fs.cd("/a/b", "../c", validate=True)
        assert result == "/a/c"

    def test_root_always_valid(self):
        fs = FileSystem()
        result = fs.cd("/anywhere", "/", validate=True)
        assert result == "/"

    def test_home_auto_created(self):
        fs = FileSystem(home_dir="/home/user")
        assert fs.exists("/home")
        assert fs.exists("/home/user")
