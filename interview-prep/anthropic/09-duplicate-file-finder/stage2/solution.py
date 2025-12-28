"""
Duplicate File Finder - Stage 2

Directory scanning with recursion.

Design Rationale:
- Scan directory trees recursively
- Filter by file extensions
- Track scan progress
"""

import hashlib
from typing import Dict, List, Set, Optional, Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileInfo:
    """Information about a file."""
    path: str
    size: int
    hash: Optional[str] = None


class DuplicateFinder:
    """Find duplicate files with directory scanning."""

    def __init__(self, file_reader: Callable[[str], bytes] = None):
        """
        Args:
            file_reader: Function to read file content (for testing)
        """
        self._file_reader = file_reader or self._default_reader
        self._files: Dict[str, FileInfo] = {}
        self._extensions: Set[str] = set()
        self._min_size: int = 0
        self._max_size: Optional[int] = None
        self._scanned_dirs: List[str] = []

    def set_extensions(self, extensions: List[str]) -> None:
        """Set file extensions to include (e.g., ['.txt', '.py'])."""
        self._extensions = set(ext.lower() for ext in extensions)

    def set_size_filter(self, min_size: int = 0, max_size: int = None) -> None:
        """Set file size filter."""
        self._min_size = min_size
        self._max_size = max_size

    def scan_directory(self, path: str, recursive: bool = True) -> int:
        """
        Scan a directory for files.

        Returns number of files added.
        """
        self._scanned_dirs.append(path)
        count = 0
        dir_path = Path(path)

        if recursive:
            files = dir_path.rglob('*')
        else:
            files = dir_path.glob('*')

        for file_path in files:
            if file_path.is_file():
                if self._should_include(file_path):
                    self.add_file(str(file_path))
                    count += 1

        return count

    def _should_include(self, path: Path) -> bool:
        """Check if file should be included based on filters."""
        # Extension filter
        if self._extensions:
            if path.suffix.lower() not in self._extensions:
                return False

        # Size filter (we need to get size)
        try:
            size = path.stat().st_size
            if size < self._min_size:
                return False
            if self._max_size is not None and size > self._max_size:
                return False
        except OSError:
            return False

        return True

    def add_file(self, path: str) -> None:
        """Add a file to the finder."""
        try:
            content = self._file_reader(path)
            self._files[path] = FileInfo(path=path, size=len(content))
        except Exception:
            pass  # Skip files we can't read

    def find_duplicates(self) -> List[List[str]]:
        """Find all duplicate files."""
        # Group by size first
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
                file_hash = self._get_hash(path)
                if file_hash:
                    if file_hash not in hash_groups:
                        hash_groups[file_hash] = []
                    hash_groups[file_hash].append(path)

            for group in hash_groups.values():
                if len(group) >= 2:
                    duplicates.append(sorted(group))

        return sorted(duplicates)

    def _get_hash(self, path: str) -> Optional[str]:
        """Get file hash, computing if needed."""
        info = self._files.get(path)
        if not info:
            return None

        if info.hash is None:
            try:
                content = self._file_reader(path)
                info.hash = hashlib.md5(content).hexdigest()
            except Exception:
                return None

        return info.hash

    def _default_reader(self, path: str) -> bytes:
        """Default file reader."""
        with open(path, 'rb') as f:
            return f.read()

    def file_count(self) -> int:
        return len(self._files)

    def scanned_directories(self) -> List[str]:
        """Return list of scanned directories."""
        return self._scanned_dirs.copy()

    def clear(self) -> None:
        self._files.clear()
        self._scanned_dirs.clear()
