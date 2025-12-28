"""
Duplicate File Finder - Stage 1

Find duplicate files by content.

Design Rationale:
- Use file size as first filter
- Compare file hashes for equality
- Group duplicates together
"""

import hashlib
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class FileInfo:
    """Information about a file."""
    path: str
    size: int
    content: bytes


class DuplicateFinder:
    """Find duplicate files."""

    def __init__(self):
        self._files: Dict[str, FileInfo] = {}

    def add_file(self, path: str, content: bytes) -> None:
        """Add a file to the finder."""
        self._files[path] = FileInfo(path=path, size=len(content), content=content)

    def find_duplicates(self) -> List[List[str]]:
        """
        Find all duplicate files.

        Returns list of groups, where each group contains paths to identical files.
        Only groups with 2+ files are returned.
        """
        # Group by size first (quick filter)
        size_groups: Dict[int, List[str]] = {}
        for path, info in self._files.items():
            if info.size not in size_groups:
                size_groups[info.size] = []
            size_groups[info.size].append(path)

        # For same-size files, compare hashes
        duplicates = []
        for paths in size_groups.values():
            if len(paths) < 2:
                continue

            hash_groups: Dict[str, List[str]] = {}
            for path in paths:
                file_hash = self._hash_file(self._files[path].content)
                if file_hash not in hash_groups:
                    hash_groups[file_hash] = []
                hash_groups[file_hash].append(path)

            for group in hash_groups.values():
                if len(group) >= 2:
                    duplicates.append(sorted(group))

        return sorted(duplicates)

    def _hash_file(self, content: bytes) -> str:
        """Compute hash of file content."""
        return hashlib.md5(content).hexdigest()

    def file_count(self) -> int:
        """Return number of files."""
        return len(self._files)

    def duplicate_count(self) -> int:
        """Return number of duplicate files (files that have at least one copy)."""
        groups = self.find_duplicates()
        return sum(len(group) for group in groups)

    def clear(self) -> None:
        """Clear all files."""
        self._files.clear()
