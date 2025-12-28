"""
Duplicate File Finder - Stage 3

Efficient large file handling.

Design Rationale:
- Partial hash for initial comparison
- Full hash only when needed
- Memory-efficient streaming
"""

import hashlib
from typing import Dict, List, Set, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class FileInfo:
    """Information about a file."""
    path: str
    size: int
    partial_hash: Optional[str] = None
    full_hash: Optional[str] = None


class DuplicateFinder:
    """Efficient duplicate finder for large files."""

    PARTIAL_HASH_SIZE = 4096  # Read first 4KB for partial hash

    def __init__(self, file_reader: Callable[[str, int, int], bytes] = None):
        """
        Args:
            file_reader: Function(path, offset, length) -> bytes
        """
        self._file_reader = file_reader or self._default_reader
        self._files: Dict[str, FileInfo] = {}
        self._extensions: Set[str] = set()
        self._min_size: int = 0
        self._max_size: Optional[int] = None
        self._bytes_read = 0
        self._hashes_computed = 0

    def set_extensions(self, extensions: List[str]) -> None:
        self._extensions = set(ext.lower() for ext in extensions)

    def set_size_filter(self, min_size: int = 0, max_size: int = None) -> None:
        self._min_size = min_size
        self._max_size = max_size

    def add_file(self, path: str, size: int) -> None:
        """Add a file with known size (lazy content reading)."""
        if size < self._min_size:
            return
        if self._max_size is not None and size > self._max_size:
            return

        self._files[path] = FileInfo(path=path, size=size)

    def find_duplicates(self) -> List[List[str]]:
        """Find duplicates efficiently."""
        # Group by size
        size_groups: Dict[int, List[str]] = {}
        for path, info in self._files.items():
            if info.size not in size_groups:
                size_groups[info.size] = []
            size_groups[info.size].append(path)

        duplicates = []

        for paths in size_groups.values():
            if len(paths) < 2:
                continue

            # Use partial hash first
            partial_groups = self._group_by_partial_hash(paths)

            for partial_paths in partial_groups.values():
                if len(partial_paths) < 2:
                    continue

                # Use full hash for confirmation
                full_groups = self._group_by_full_hash(partial_paths)

                for group in full_groups.values():
                    if len(group) >= 2:
                        duplicates.append(sorted(group))

        return sorted(duplicates)

    def _group_by_partial_hash(self, paths: List[str]) -> Dict[str, List[str]]:
        """Group paths by partial hash."""
        groups: Dict[str, List[str]] = {}

        for path in paths:
            partial = self._get_partial_hash(path)
            if partial:
                if partial not in groups:
                    groups[partial] = []
                groups[partial].append(path)

        return groups

    def _group_by_full_hash(self, paths: List[str]) -> Dict[str, List[str]]:
        """Group paths by full hash."""
        groups: Dict[str, List[str]] = {}

        for path in paths:
            full = self._get_full_hash(path)
            if full:
                if full not in groups:
                    groups[full] = []
                groups[full].append(path)

        return groups

    def _get_partial_hash(self, path: str) -> Optional[str]:
        """Get partial hash (first N bytes)."""
        info = self._files.get(path)
        if not info:
            return None

        if info.partial_hash is None:
            try:
                content = self._file_reader(path, 0, self.PARTIAL_HASH_SIZE)
                self._bytes_read += len(content)
                self._hashes_computed += 1
                info.partial_hash = hashlib.md5(content).hexdigest()
            except Exception:
                return None

        return info.partial_hash

    def _get_full_hash(self, path: str) -> Optional[str]:
        """Get full file hash."""
        info = self._files.get(path)
        if not info:
            return None

        if info.full_hash is None:
            try:
                # Read in chunks for memory efficiency
                hasher = hashlib.md5()
                offset = 0
                chunk_size = 1024 * 1024  # 1MB chunks

                while True:
                    chunk = self._file_reader(path, offset, chunk_size)
                    if not chunk:
                        break
                    self._bytes_read += len(chunk)
                    hasher.update(chunk)
                    offset += len(chunk)
                    if len(chunk) < chunk_size:
                        break

                self._hashes_computed += 1
                info.full_hash = hasher.hexdigest()
            except Exception:
                return None

        return info.full_hash

    def _default_reader(self, path: str, offset: int, length: int) -> bytes:
        """Default file reader."""
        with open(path, 'rb') as f:
            f.seek(offset)
            return f.read(length)

    def file_count(self) -> int:
        return len(self._files)

    def bytes_read(self) -> int:
        """Total bytes read from files."""
        return self._bytes_read

    def hashes_computed(self) -> int:
        """Number of hash computations."""
        return self._hashes_computed

    def clear(self) -> None:
        self._files.clear()
        self._bytes_read = 0
        self._hashes_computed = 0
