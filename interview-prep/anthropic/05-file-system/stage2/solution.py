"""
File System Simulator - Stage 2

File system with directory support.

Design Rationale:
- Directories are just nodes with type "directory"
- list_directory returns names (not full paths) sorted
- delete_directory with recursive=True removes all contents
"""


class FileSystem:
    """Simulated file system with files and directories."""

    def __init__(self):
        self._nodes: dict[str, dict] = {"/": {"type": "directory"}}

    def _get_parent_path(self, path: str) -> str:
        if path == "/":
            return "/"
        parts = path.rstrip("/").rsplit("/", 1)
        return parts[0] if parts[0] else "/"

    def _parent_exists(self, path: str) -> bool:
        parent = self._get_parent_path(path)
        return parent in self._nodes and self._nodes[parent]["type"] == "directory"

    def _get_name(self, path: str) -> str:
        return path.rstrip("/").rsplit("/", 1)[-1]

    # Stage 1 methods
    def create_file(self, path: str, content: str = "") -> bool:
        if path in self._nodes:
            return False
        if not self._parent_exists(path):
            return False
        self._nodes[path] = {"type": "file", "content": content}
        return True

    def read_file(self, path: str) -> str | None:
        if path not in self._nodes:
            return None
        if self._nodes[path]["type"] != "file":
            return None
        return self._nodes[path]["content"]

    def delete_file(self, path: str) -> bool:
        if path not in self._nodes:
            return False
        if self._nodes[path]["type"] != "file":
            return False
        del self._nodes[path]
        return True

    def file_exists(self, path: str) -> bool:
        return path in self._nodes and self._nodes[path]["type"] == "file"

    # Stage 2 methods
    def create_directory(self, path: str) -> bool:
        """Creates directory. Returns False if already exists or parent doesn't exist."""
        if path in self._nodes:
            return False
        if not self._parent_exists(path):
            return False
        self._nodes[path] = {"type": "directory"}
        return True

    def list_directory(self, path: str) -> list[str] | None:
        """Lists contents of directory. Returns None if not found or is file."""
        if path not in self._nodes:
            return None
        if self._nodes[path]["type"] != "directory":
            return None

        path = path.rstrip("/")
        if path == "":
            path = "/"

        contents = []
        for node_path in self._nodes:
            if node_path == path:
                continue
            parent = self._get_parent_path(node_path)
            if parent == path:
                contents.append(self._get_name(node_path))

        return sorted(contents)

    def delete_directory(self, path: str, recursive: bool = False) -> bool:
        """Deletes directory. If not recursive, fails if not empty."""
        if path == "/":
            return False
        if path not in self._nodes:
            return False
        if self._nodes[path]["type"] != "directory":
            return False

        # Get contents
        contents = self.list_directory(path)
        if contents and not recursive:
            return False

        # If recursive, delete all contents first
        if recursive:
            path_prefix = path.rstrip("/") + "/"
            to_delete = [p for p in self._nodes if p.startswith(path_prefix)]
            for p in to_delete:
                del self._nodes[p]

        del self._nodes[path]
        return True
