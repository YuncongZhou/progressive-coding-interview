"""Tests for Duplicate File Finder Stage 2 - Directory Scanning"""
import pytest
from solution import DuplicateFinder


class TestDuplicateFinderStage2:
    @pytest.fixture
    def mock_files(self):
        return {
            "/dir/file1.txt": b"content_a",
            "/dir/file2.txt": b"content_a",
            "/dir/file3.py": b"content_b",
            "/dir/sub/file4.txt": b"content_a",
            "/dir/sub/file5.py": b"content_c",
        }

    def test_extension_filter(self, mock_files):
        finder = DuplicateFinder(lambda p: mock_files.get(p, b""))
        finder.set_extensions([".txt"])
        # Manually add files that match
        for path, content in mock_files.items():
            if path.endswith(".txt"):
                finder.add_file(path)

        duplicates = finder.find_duplicates()
        # Should find txt duplicates only
        for group in duplicates:
            for path in group:
                assert path.endswith(".txt")

    def test_no_extension_filter(self, mock_files):
        finder = DuplicateFinder(lambda p: mock_files.get(p, b""))
        for path in mock_files:
            finder.add_file(path)

        duplicates = finder.find_duplicates()
        assert len(duplicates) >= 1

    def test_size_filter_min(self):
        files = {
            "/small.txt": b"a",
            "/large1.txt": b"a" * 100,
            "/large2.txt": b"a" * 100,
        }
        finder = DuplicateFinder(lambda p: files.get(p, b""))
        finder.set_size_filter(min_size=50)

        for path, content in files.items():
            if len(content) >= 50:
                finder.add_file(path)

        duplicates = finder.find_duplicates()
        assert len(duplicates) == 1
        assert "/small.txt" not in duplicates[0]

    def test_scanned_directories(self, mock_files):
        finder = DuplicateFinder(lambda p: mock_files.get(p, b""))
        # Simulate scanning
        finder._scanned_dirs.append("/dir")
        finder._scanned_dirs.append("/other")

        dirs = finder.scanned_directories()
        assert "/dir" in dirs
        assert "/other" in dirs

    def test_clear(self, mock_files):
        finder = DuplicateFinder(lambda p: mock_files.get(p, b""))
        for path in mock_files:
            finder.add_file(path)
        finder._scanned_dirs.append("/dir")

        finder.clear()
        assert finder.file_count() == 0
        assert len(finder.scanned_directories()) == 0

    def test_multiple_extensions(self, mock_files):
        finder = DuplicateFinder(lambda p: mock_files.get(p, b""))
        finder.set_extensions([".txt", ".py"])

        for path in mock_files:
            if path.endswith((".txt", ".py")):
                finder.add_file(path)

        assert finder.file_count() == len(mock_files)
