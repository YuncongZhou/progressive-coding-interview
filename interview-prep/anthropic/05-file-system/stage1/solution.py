"""
File System Simulator - Stage 1

Basic file operations.

Design Rationale:
- Store files in dict {path: {"type": "file", "content": str}}
- Root "/" always exists
- Validate parent directory exists before creating files
"""


class FileSystem:
    """Simulated file system with basic file operations."""

    def __init__(self):
        self._nodes: dict[str, dict] = {"/": {"type": "directory"}}

    def _get_parent_path(self, path: str) -> str:
        """Get parent directory path."""
        if path == "/":
            return "/"
        parts = path.rstrip("/").rsplit("/", 1)
        return parts[0] if parts[0] else "/"

    def _parent_exists(self, path: str) -> bool:
        """Check if parent directory exists."""
        parent = self._get_parent_path(path)
        return parent in self._nodes and self._nodes[parent]["type"] == "directory"

    def create_file(self, path: str, content: str = "") -> bool:
        """Creates file at path. Returns False if already exists or parent dir doesn't exist."""
        if path in self._nodes:
            return False
        if not self._parent_exists(path):
            return False
        self._nodes[path] = {"type": "file", "content": content}
        return True

    def read_file(self, path: str) -> str | None:
        """Reads file content. Returns None if not found or is directory."""
        if path not in self._nodes:
            return None
        if self._nodes[path]["type"] != "file":
            return None
        return self._nodes[path]["content"]

    def delete_file(self, path: str) -> bool:
        """Deletes file. Returns False if not found or is directory."""
        if path not in self._nodes:
            return False
        if self._nodes[path]["type"] != "file":
            return False
        del self._nodes[path]
        return True

    def file_exists(self, path: str) -> bool:
        """Returns True if file exists at path."""
        return path in self._nodes and self._nodes[path]["type"] == "file"
