"""
File System Simulator - Stage 3

File system with permissions.

Design Rationale:
- Permissions stored per path per user
- read_file_as checks read permission before reading
"""


class FileSystem:
    """File system with permissions."""

    def __init__(self):
        self._nodes: dict[str, dict] = {"/": {"type": "directory"}}
        self._permissions: dict[str, dict[str, set]] = {}  # path -> {user -> set of perms}

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

    def create_directory(self, path: str) -> bool:
        if path in self._nodes:
            return False
        if not self._parent_exists(path):
            return False
        self._nodes[path] = {"type": "directory"}
        return True

    def list_directory(self, path: str) -> list[str] | None:
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
        if path == "/":
            return False
        if path not in self._nodes:
            return False
        if self._nodes[path]["type"] != "directory":
            return False

        contents = self.list_directory(path)
        if contents and not recursive:
            return False

        if recursive:
            path_prefix = path.rstrip("/") + "/"
            to_delete = [p for p in self._nodes if p.startswith(path_prefix)]
            for p in to_delete:
                del self._nodes[p]

        del self._nodes[path]
        return True

    # Stage 3 methods
    def set_permission(self, path: str, user: str, permission: str) -> bool:
        """Sets permission ('read', 'write', 'execute') for user on path."""
        if path not in self._nodes:
            return False
        if path not in self._permissions:
            self._permissions[path] = {}
        if user not in self._permissions[path]:
            self._permissions[path][user] = set()
        self._permissions[path][user].add(permission)
        return True

    def check_permission(self, path: str, user: str, permission: str) -> bool:
        """Checks if user has permission on path."""
        if path not in self._permissions:
            return False
        if user not in self._permissions[path]:
            return False
        return permission in self._permissions[path][user]

    def read_file_as(self, path: str, user: str) -> str | None:
        """Reads file if user has read permission."""
        if not self.check_permission(path, user, "read"):
            return None
        return self.read_file(path)
