"""Tests for CD Command Stage 1"""
import pytest
from solution import cd


class TestCDCommandStage1:
    def test_absolute_path(self):
        result = cd("/foo", "/bar")
        assert result == "/bar"

    def test_relative_path(self):
        result = cd("/foo", "bar")
        assert result == "/foo/bar"

    def test_parent_dir(self):
        result = cd("/foo/bar", "..")
        assert result == "/foo"

    def test_current_dir(self):
        result = cd("/foo", ".")
        assert result == "/foo"

    def test_multiple_levels(self):
        result = cd("/foo/bar", "../../baz")
        assert result == "/baz"

    def test_root(self):
        result = cd("/foo", "/")
        assert result == "/"

    def test_trailing_slash_normalized(self):
        result = cd("/foo/", "bar/")
        assert result == "/foo/bar"

    def test_deep_path(self):
        result = cd("/a/b/c/d", "../../e/f")
        assert result == "/a/b/e/f"

    def test_go_past_root(self):
        result = cd("/foo", "../../..")
        assert result == "/"
