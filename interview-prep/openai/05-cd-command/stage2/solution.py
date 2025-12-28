"""
CD (Change Directory) Command - Stage 2

Add symbolic link support.

Design Rationale:
- Track symlinks as mappings from path to target
- Resolve symlinks during path traversal
- Handle nested symlinks (with max depth)
"""


class FileSystem:
    """File system with symbolic link support."""

    MAX_SYMLINK_DEPTH = 10

    def __init__(self):
        self._directories: set[str] = {"/"}
        self._symlinks: dict[str, str] = {}

    def mkdir(self, path: str) -> bool:
        """Create a directory."""
        path = self._normalize_path(path)
        if path in self._directories or path in self._symlinks:
            return False
        # Check parent exists
        parent = self._get_parent(path)
        if parent and parent not in self._directories:
            return False
        self._directories.add(path)
        return True

    def create_symlink(self, link_path: str, target: str) -> bool:
        """Create a symbolic link."""
        link_path = self._normalize_path(link_path)
        if link_path in self._directories or link_path in self._symlinks:
            return False
        self._symlinks[link_path] = target
        return True

    def cd(self, current_dir: str, new_dir: str) -> str:
        """
        Change directory with symlink resolution.

        Returns the resolved absolute path.
        """
        # Build path
        if new_dir.startswith("/"):
            path_parts = new_dir.split("/")
        else:
            path_parts = current_dir.split("/") + new_dir.split("/")

        # Process path components
        result = []
        for part in path_parts:
            if part == "" or part == ".":
                continue
            elif part == "..":
                if result:
                    result.pop()
            else:
                result.append(part)
                # Resolve symlinks at each step
                current_path = "/" + "/".join(result)
                resolved = self._resolve_symlink(current_path)
                if resolved != current_path:
                    # Symlink found, update result
                    result = self._path_to_parts(resolved)

        return "/" + "/".join(result) if result else "/"

    def _resolve_symlink(self, path: str, depth: int = 0) -> str:
        """Resolve symbolic link, handling nested symlinks."""
        if depth > self.MAX_SYMLINK_DEPTH:
            return path  # Prevent infinite loops

        if path in self._symlinks:
            target = self._symlinks[path]
            # If target is relative, resolve it
            if not target.startswith("/"):
                parent = self._get_parent(path)
                target = self._join_path(parent, target)
            return self._resolve_symlink(target, depth + 1)

        return path

    def _normalize_path(self, path: str) -> str:
        """Normalize path by removing trailing slash."""
        if path != "/" and path.endswith("/"):
            return path[:-1]
        return path

    def _get_parent(self, path: str) -> str | None:
        """Get parent directory of path."""
        if path == "/":
            return None
        parts = path.rstrip("/").split("/")
        if len(parts) <= 2:
            return "/"
        return "/".join(parts[:-1])

    def _path_to_parts(self, path: str) -> list[str]:
        """Convert path to list of parts."""
        return [p for p in path.split("/") if p]

    def _join_path(self, base: str, relative: str) -> str:
        """Join base path with relative path, resolving . and .."""
        if relative.startswith("/"):
            return self._normalize_components(relative)

        combined = base.rstrip("/") + "/" + relative
        return self._normalize_components(combined)

    def _normalize_components(self, path: str) -> str:
        """Normalize path by resolving . and .."""
        parts = path.split("/")
        result = []
        for part in parts:
            if part == "" or part == ".":
                continue
            elif part == "..":
                if result:
                    result.pop()
            else:
                result.append(part)
        return "/" + "/".join(result) if result else "/"


def cd(current_dir: str, new_dir: str) -> str:
    """Simple cd without filesystem (backwards compatible)."""
    if new_dir.startswith("/"):
        path_parts = new_dir.split("/")
    else:
        path_parts = current_dir.split("/") + new_dir.split("/")

    result = []
    for part in path_parts:
        if part == "" or part == ".":
            continue
        elif part == "..":
            if result:
                result.pop()
        else:
            result.append(part)

    return "/" + "/".join(result)
