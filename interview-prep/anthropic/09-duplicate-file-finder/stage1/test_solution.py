"""Tests for Duplicate File Finder Stage 1"""
import pytest
from solution import DuplicateFinder


class TestDuplicateFinderStage1:
    def test_no_duplicates(self):
        finder = DuplicateFinder()
        finder.add_file("/file1.txt", b"content1")
        finder.add_file("/file2.txt", b"content2")

        assert finder.find_duplicates() == []

    def test_simple_duplicate(self):
        finder = DuplicateFinder()
        finder.add_file("/file1.txt", b"same content")
        finder.add_file("/file2.txt", b"same content")

        duplicates = finder.find_duplicates()
        assert len(duplicates) == 1
        assert set(duplicates[0]) == {"/file1.txt", "/file2.txt"}

    def test_multiple_duplicate_groups(self):
        finder = DuplicateFinder()
        finder.add_file("/a1.txt", b"content_a")
        finder.add_file("/a2.txt", b"content_a")
        finder.add_file("/b1.txt", b"content_b")
        finder.add_file("/b2.txt", b"content_b")
        finder.add_file("/unique.txt", b"unique")

        duplicates = finder.find_duplicates()
        assert len(duplicates) == 2

    def test_three_way_duplicate(self):
        finder = DuplicateFinder()
        finder.add_file("/file1.txt", b"same")
        finder.add_file("/file2.txt", b"same")
        finder.add_file("/file3.txt", b"same")

        duplicates = finder.find_duplicates()
        assert len(duplicates) == 1
        assert len(duplicates[0]) == 3

    def test_same_size_different_content(self):
        finder = DuplicateFinder()
        finder.add_file("/file1.txt", b"aaaa")
        finder.add_file("/file2.txt", b"bbbb")

        assert finder.find_duplicates() == []

    def test_file_count(self):
        finder = DuplicateFinder()
        finder.add_file("/file1.txt", b"a")
        finder.add_file("/file2.txt", b"b")

        assert finder.file_count() == 2

    def test_duplicate_count(self):
        finder = DuplicateFinder()
        finder.add_file("/a1.txt", b"a")
        finder.add_file("/a2.txt", b"a")
        finder.add_file("/a3.txt", b"a")
        finder.add_file("/unique.txt", b"unique")

        assert finder.duplicate_count() == 3

    def test_clear(self):
        finder = DuplicateFinder()
        finder.add_file("/file1.txt", b"content")
        finder.clear()

        assert finder.file_count() == 0

    def test_empty_files(self):
        finder = DuplicateFinder()
        finder.add_file("/empty1.txt", b"")
        finder.add_file("/empty2.txt", b"")

        duplicates = finder.find_duplicates()
        assert len(duplicates) == 1
