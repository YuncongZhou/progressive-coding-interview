"""
Duplicate File Finder - Stage 4

Actions and reporting.

Design Rationale:
- Provide actions: delete, link, move
- Generate reports with statistics
- Preview before action
"""

import hashlib
from typing import Dict, List, Set, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class DuplicateAction(Enum):
    """Actions for duplicate files."""
    DELETE = "delete"
    HARDLINK = "hardlink"
    SYMLINK = "symlink"
    MOVE = "move"


@dataclass
class FileInfo:
    path: str
    size: int
    partial_hash: Optional[str] = None
    full_hash: Optional[str] = None


@dataclass
class DuplicateGroup:
    """A group of duplicate files."""
    paths: List[str]
    size: int
    hash: str

    @property
    def count(self) -> int:
        return len(self.paths)

    @property
    def wasted_space(self) -> int:
        """Space that could be recovered (all but one copy)."""
        return self.size * (self.count - 1)


@dataclass
class Report:
    """Duplicate finder report."""
    total_files: int
    total_size: int
    duplicate_groups: int
    duplicate_files: int
    wasted_space: int
    groups: List[DuplicateGroup]


class DuplicateFinder:
    """Duplicate finder with actions and reporting."""

    PARTIAL_HASH_SIZE = 4096

    def __init__(self, file_reader: Callable[[str, int, int], bytes] = None,
                 file_deleter: Callable[[str], bool] = None,
                 file_linker: Callable[[str, str, str], bool] = None):
        self._file_reader = file_reader or self._default_reader
        self._file_deleter = file_deleter or self._default_deleter
        self._file_linker = file_linker or self._default_linker
        self._files: Dict[str, FileInfo] = {}
        self._extensions: Set[str] = set()
        self._min_size: int = 0
        self._max_size: Optional[int] = None
        self._action_log: List[str] = []

    def set_extensions(self, extensions: List[str]) -> None:
        self._extensions = set(ext.lower() for ext in extensions)

    def set_size_filter(self, min_size: int = 0, max_size: int = None) -> None:
        self._min_size = min_size
        self._max_size = max_size

    def add_file(self, path: str, size: int) -> None:
        if size < self._min_size:
            return
        if self._max_size is not None and size > self._max_size:
            return
        self._files[path] = FileInfo(path=path, size=size)

    def find_duplicates(self) -> List[DuplicateGroup]:
        """Find duplicates and return as groups."""
        # Group by size
        size_groups: Dict[int, List[str]] = {}
        for path, info in self._files.items():
            if info.size not in size_groups:
                size_groups[info.size] = []
            size_groups[info.size].append(path)

        groups = []

        for size, paths in size_groups.items():
            if len(paths) < 2:
                continue

            # Use partial hash first
            partial_groups = self._group_by_hash(paths, partial=True)

            for partial_paths in partial_groups.values():
                if len(partial_paths) < 2:
                    continue

                # Use full hash for confirmation
                full_groups = self._group_by_hash(partial_paths, partial=False)

                for hash_val, group_paths in full_groups.items():
                    if len(group_paths) >= 2:
                        groups.append(DuplicateGroup(
                            paths=sorted(group_paths),
                            size=size,
                            hash=hash_val
                        ))

        return sorted(groups, key=lambda g: -g.wasted_space)

    def generate_report(self) -> Report:
        """Generate a full report."""
        groups = self.find_duplicates()

        total_size = sum(info.size for info in self._files.values())
        duplicate_files = sum(g.count for g in groups)
        wasted_space = sum(g.wasted_space for g in groups)

        return Report(
            total_files=len(self._files),
            total_size=total_size,
            duplicate_groups=len(groups),
            duplicate_files=duplicate_files,
            wasted_space=wasted_space,
            groups=groups
        )

    def preview_action(self, group: DuplicateGroup,
                       action: DuplicateAction,
                       keep_index: int = 0) -> List[str]:
        """Preview what actions would be taken."""
        actions = []
        keep_path = group.paths[keep_index]

        for i, path in enumerate(group.paths):
            if i == keep_index:
                actions.append(f"KEEP: {path}")
            else:
                if action == DuplicateAction.DELETE:
                    actions.append(f"DELETE: {path}")
                elif action == DuplicateAction.HARDLINK:
                    actions.append(f"HARDLINK: {path} -> {keep_path}")
                elif action == DuplicateAction.SYMLINK:
                    actions.append(f"SYMLINK: {path} -> {keep_path}")
                elif action == DuplicateAction.MOVE:
                    actions.append(f"MOVE: {path} -> trash/")

        return actions

    def execute_action(self, group: DuplicateGroup,
                       action: DuplicateAction,
                       keep_index: int = 0) -> int:
        """
        Execute action on duplicate group.

        Returns number of files affected.
        """
        keep_path = group.paths[keep_index]
        affected = 0

        for i, path in enumerate(group.paths):
            if i == keep_index:
                continue

            try:
                if action == DuplicateAction.DELETE:
                    if self._file_deleter(path):
                        self._action_log.append(f"Deleted: {path}")
                        affected += 1
                elif action in (DuplicateAction.HARDLINK, DuplicateAction.SYMLINK):
                    link_type = action.value
                    if self._file_linker(path, keep_path, link_type):
                        self._action_log.append(f"{link_type}: {path} -> {keep_path}")
                        affected += 1
            except Exception as e:
                self._action_log.append(f"Error: {path}: {e}")

        return affected

    def get_action_log(self) -> List[str]:
        """Get log of all actions taken."""
        return self._action_log.copy()

    def _group_by_hash(self, paths: List[str], partial: bool) -> Dict[str, List[str]]:
        groups: Dict[str, List[str]] = {}
        for path in paths:
            h = self._get_partial_hash(path) if partial else self._get_full_hash(path)
            if h:
                if h not in groups:
                    groups[h] = []
                groups[h].append(path)
        return groups

    def _get_partial_hash(self, path: str) -> Optional[str]:
        info = self._files.get(path)
        if not info:
            return None
        if info.partial_hash is None:
            try:
                content = self._file_reader(path, 0, self.PARTIAL_HASH_SIZE)
                info.partial_hash = hashlib.md5(content).hexdigest()
            except Exception:
                return None
        return info.partial_hash

    def _get_full_hash(self, path: str) -> Optional[str]:
        info = self._files.get(path)
        if not info:
            return None
        if info.full_hash is None:
            try:
                hasher = hashlib.md5()
                offset = 0
                while True:
                    chunk = self._file_reader(path, offset, 1024*1024)
                    if not chunk:
                        break
                    hasher.update(chunk)
                    offset += len(chunk)
                    if len(chunk) < 1024*1024:
                        break
                info.full_hash = hasher.hexdigest()
            except Exception:
                return None
        return info.full_hash

    def _default_reader(self, path: str, offset: int, length: int) -> bytes:
        with open(path, 'rb') as f:
            f.seek(offset)
            return f.read(length)

    def _default_deleter(self, path: str) -> bool:
        import os
        os.remove(path)
        return True

    def _default_linker(self, path: str, target: str, link_type: str) -> bool:
        import os
        os.remove(path)
        if link_type == "hardlink":
            os.link(target, path)
        else:
            os.symlink(target, path)
        return True

    def file_count(self) -> int:
        return len(self._files)

    def clear(self) -> None:
        self._files.clear()
        self._action_log.clear()
