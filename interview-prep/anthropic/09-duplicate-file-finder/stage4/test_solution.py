"""Tests for Duplicate File Finder Stage 4 - Actions and Reporting"""
import pytest
from solution import DuplicateFinder, DuplicateAction, DuplicateGroup


class TestDuplicateFinderStage4:
    @pytest.fixture
    def mock_files(self):
        return {
            "/a.txt": b"duplicate content",
            "/b.txt": b"duplicate content",
            "/c.txt": b"duplicate content",
            "/unique.txt": b"unique",
        }

    @pytest.fixture
    def finder(self, mock_files):
        def reader(path, offset, length):
            c = mock_files.get(path, b"")
            return c[offset:offset+length]

        f = DuplicateFinder(reader)
        for path, content in mock_files.items():
            f.add_file(path, len(content))
        return f

    def test_generate_report(self, finder):
        report = finder.generate_report()

        assert report.total_files == 4
        assert report.duplicate_groups == 1
        assert report.duplicate_files == 3
        assert report.wasted_space > 0

    def test_wasted_space_calculation(self, finder):
        groups = finder.find_duplicates()
        group = groups[0]

        # 3 files of same content, wasted space = size * 2
        assert group.wasted_space == group.size * 2

    def test_preview_delete(self, finder):
        groups = finder.find_duplicates()
        preview = finder.preview_action(groups[0], DuplicateAction.DELETE, keep_index=0)

        assert any("KEEP" in p for p in preview)
        assert any("DELETE" in p for p in preview)
        assert sum(1 for p in preview if "DELETE" in p) == 2

    def test_preview_hardlink(self, finder):
        groups = finder.find_duplicates()
        preview = finder.preview_action(groups[0], DuplicateAction.HARDLINK, keep_index=0)

        assert any("HARDLINK" in p for p in preview)

    def test_execute_delete(self, mock_files):
        deleted = []

        def deleter(path):
            deleted.append(path)
            return True

        def reader(path, offset, length):
            c = mock_files.get(path, b"")
            return c[offset:offset+length]

        finder = DuplicateFinder(reader, file_deleter=deleter)
        for path, content in mock_files.items():
            finder.add_file(path, len(content))

        groups = finder.find_duplicates()
        affected = finder.execute_action(groups[0], DuplicateAction.DELETE, keep_index=0)

        assert affected == 2
        assert len(deleted) == 2
        assert groups[0].paths[0] not in deleted  # Keep file not deleted

    def test_action_log(self, mock_files):
        def reader(path, offset, length):
            c = mock_files.get(path, b"")
            return c[offset:offset+length]

        finder = DuplicateFinder(reader, file_deleter=lambda p: True)
        for path, content in mock_files.items():
            finder.add_file(path, len(content))

        groups = finder.find_duplicates()
        finder.execute_action(groups[0], DuplicateAction.DELETE)

        log = finder.get_action_log()
        assert len(log) == 2
        assert all("Deleted" in entry for entry in log)

    def test_report_groups_sorted_by_wasted_space(self):
        files = {
            "/small1.txt": b"a" * 10,
            "/small2.txt": b"a" * 10,
            "/large1.txt": b"b" * 1000,
            "/large2.txt": b"b" * 1000,
        }

        def reader(path, offset, length):
            c = files.get(path, b"")
            return c[offset:offset+length]

        finder = DuplicateFinder(reader)
        for path, content in files.items():
            finder.add_file(path, len(content))

        report = finder.generate_report()
        # Large files group should be first (more wasted space)
        assert report.groups[0].size == 1000

    def test_duplicate_group_properties(self):
        group = DuplicateGroup(
            paths=["/a.txt", "/b.txt", "/c.txt"],
            size=100,
            hash="abc123"
        )

        assert group.count == 3
        assert group.wasted_space == 200  # 100 * 2
