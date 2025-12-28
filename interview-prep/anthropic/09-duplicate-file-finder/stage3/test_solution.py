"""Tests for Duplicate File Finder Stage 3 - Efficient Large Files"""
import pytest
from solution import DuplicateFinder


class TestDuplicateFinderStage3:
    def test_partial_hash_optimization(self):
        # Files with same first 4KB but different later content
        file_a = b"x" * 5000 + b"a" * 1000
        file_b = b"x" * 5000 + b"b" * 1000

        files = {"/a.txt": file_a, "/b.txt": file_b}

        def reader(path, offset, length):
            content = files.get(path, b"")
            return content[offset:offset+length]

        finder = DuplicateFinder(reader)
        finder.add_file("/a.txt", len(file_a))
        finder.add_file("/b.txt", len(file_b))

        duplicates = finder.find_duplicates()
        assert len(duplicates) == 0  # Should detect difference

    def test_true_duplicates_found(self):
        content = b"same content " * 1000
        files = {"/a.txt": content, "/b.txt": content}

        def reader(path, offset, length):
            c = files.get(path, b"")
            return c[offset:offset+length]

        finder = DuplicateFinder(reader)
        finder.add_file("/a.txt", len(content))
        finder.add_file("/b.txt", len(content))

        duplicates = finder.find_duplicates()
        assert len(duplicates) == 1

    def test_bytes_read_tracking(self):
        content = b"a" * 100
        files = {"/a.txt": content, "/b.txt": content}

        def reader(path, offset, length):
            c = files.get(path, b"")
            return c[offset:offset+length]

        finder = DuplicateFinder(reader)
        finder.add_file("/a.txt", len(content))
        finder.add_file("/b.txt", len(content))

        finder.find_duplicates()
        assert finder.bytes_read() > 0

    def test_hashes_computed(self):
        files = {
            "/a.txt": b"content_a",
            "/b.txt": b"content_a",
            "/c.txt": b"different",
        }

        def reader(path, offset, length):
            c = files.get(path, b"")
            return c[offset:offset+length]

        finder = DuplicateFinder(reader)
        finder.add_file("/a.txt", 9)
        finder.add_file("/b.txt", 9)
        finder.add_file("/c.txt", 9)

        finder.find_duplicates()
        assert finder.hashes_computed() > 0

    def test_size_filter(self):
        files = {
            "/small.txt": b"a",
            "/large.txt": b"a" * 1000,
        }

        def reader(path, offset, length):
            c = files.get(path, b"")
            return c[offset:offset+length]

        finder = DuplicateFinder(reader)
        finder.set_size_filter(min_size=100)
        finder.add_file("/small.txt", 1)  # Should be filtered out
        finder.add_file("/large.txt", 1000)

        assert finder.file_count() == 1

    def test_skips_non_duplicates_early(self):
        # Different sizes should not trigger any hash computation
        files = {
            "/a.txt": b"short",
            "/b.txt": b"this is a longer file",
        }

        def reader(path, offset, length):
            c = files.get(path, b"")
            return c[offset:offset+length]

        finder = DuplicateFinder(reader)
        finder.add_file("/a.txt", 5)
        finder.add_file("/b.txt", 21)

        finder.find_duplicates()
        # No hashes needed since sizes differ
        assert finder.hashes_computed() == 0

    def test_clear(self):
        finder = DuplicateFinder(lambda p, o, l: b"")
        finder.add_file("/a.txt", 100)
        finder._bytes_read = 1000
        finder._hashes_computed = 5

        finder.clear()
        assert finder.file_count() == 0
        assert finder.bytes_read() == 0
        assert finder.hashes_computed() == 0
