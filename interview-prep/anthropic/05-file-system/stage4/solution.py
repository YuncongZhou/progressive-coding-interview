"""
File System Simulator - Stage 4

File system with quotas and compression.

Design Rationale:
- Track file ownership and sizes
- Compression reduces storage usage
- Deduplication finds identical content and shares storage
"""

import hashlib
import zlib


class FileSystem:
    """File system with quotas and compression."""

    def __init__(self):
        self._nodes: dict[str, dict] = {"/": {"type": "directory"}}
        self._permissions: dict[str, dict[str, set]] = {}
        self._quotas: dict[str, int] = {}  # user -> max_bytes
        self._file_owners: dict[str, str] = {}  # path -> user

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

    def _get_file_size(self, path: str) -> int:
        if path not in self._nodes or self._nodes[path]["type"] != "file":
            return 0
        node = self._nodes[path]
        if node.get("compressed"):
            return len(node["content"])
        return len(node["content"])

    def create_file(self, path: str, content: str = "") -> bool:
        if path in self._nodes:
            return False
        if not self._parent_exists(path):
            return False
        self._nodes[path] = {"type": "file", "content": content, "compressed": False}
        return True

    def read_file(self, path: str) -> str | None:
        if path not in self._nodes:
            return None
        if self._nodes[path]["type"] != "file":
            return None
        node = self._nodes[path]
        if node.get("compressed"):
            return zlib.decompress(node["content"]).decode("utf-8")
        return node["content"]

    def delete_file(self, path: str) -> bool:
        if path not in self._nodes:
            return False
        if self._nodes[path]["type"] != "file":
            return False
        self._file_owners.pop(path, None)
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
        path = path.rstrip("/") or "/"
        contents = []
        for node_path in self._nodes:
            if node_path == path:
                continue
            if self._get_parent_path(node_path) == path:
                contents.append(self._get_name(node_path))
        return sorted(contents)

    def delete_directory(self, path: str, recursive: bool = False) -> bool:
        if path == "/":
            return False
        if path not in self._nodes or self._nodes[path]["type"] != "directory":
            return False
        contents = self.list_directory(path)
        if contents and not recursive:
            return False
        if recursive:
            path_prefix = path.rstrip("/") + "/"
            for p in [p for p in self._nodes if p.startswith(path_prefix)]:
                del self._nodes[p]
        del self._nodes[path]
        return True

    def set_permission(self, path: str, user: str, permission: str) -> bool:
        if path not in self._nodes:
            return False
        if path not in self._permissions:
            self._permissions[path] = {}
        if user not in self._permissions[path]:
            self._permissions[path][user] = set()
        self._permissions[path][user].add(permission)
        return True

    def check_permission(self, path: str, user: str, permission: str) -> bool:
        if path not in self._permissions or user not in self._permissions[path]:
            return False
        return permission in self._permissions[path][user]

    def read_file_as(self, path: str, user: str) -> str | None:
        if not self.check_permission(path, user, "read"):
            return None
        return self.read_file(path)

    # Stage 4 methods
    def set_quota(self, user: str, max_bytes: int) -> None:
        """Sets storage quota for user."""
        self._quotas[user] = max_bytes

    def get_usage(self, user: str) -> int:
        """Returns current storage usage in bytes for user."""
        total = 0
        for path, owner in self._file_owners.items():
            if owner == user and path in self._nodes:
                total += self._get_file_size(path)
        return total

    def compress_file(self, path: str) -> bool:
        """Compresses file to reduce storage usage."""
        if path not in self._nodes or self._nodes[path]["type"] != "file":
            return False
        if self._nodes[path].get("compressed"):
            return False
        content = self._nodes[path]["content"]
        compressed = zlib.compress(content.encode("utf-8"))
        self._nodes[path]["content"] = compressed
        self._nodes[path]["compressed"] = True
        return True

    def deduplicate(self) -> int:
        """Finds and deduplicates identical files. Returns bytes saved."""
        # Group files by content hash
        content_map: dict[str, list[str]] = {}
        for path, node in self._nodes.items():
            if node["type"] != "file":
                continue
            content = self.read_file(path)
            content_hash = hashlib.md5(content.encode()).hexdigest()
            if content_hash not in content_map:
                content_map[content_hash] = []
            content_map[content_hash].append(path)

        bytes_saved = 0
        for paths in content_map.values():
            if len(paths) <= 1:
                continue
            # Keep first, share content with others (simulate)
            original = paths[0]
            original_size = self._get_file_size(original)
            for dupe in paths[1:]:
                bytes_saved += self._get_file_size(dupe)
                # In a real implementation, we'd use hard links or similar
                # For simulation, just mark as reference
                self._nodes[dupe]["reference"] = original

        return bytes_saved
