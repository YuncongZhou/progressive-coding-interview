"""
CD (Change Directory) Command - Stage 3

Path validation and error handling.

Design Rationale:
- Validate each path component exists
- Return error for invalid paths
- Support ~ for home directory
"""

from typing import Optional


class PathError(Exception):
    """Error for invalid path operations."""
    pass


class FileSystem:
    """File system with validation and home directory support."""

    MAX_SYMLINK_DEPTH = 10

    def __init__(self, home_dir: str = "/home/user"):
        self._directories: set[str] = {"/"}
        self._symlinks: dict[str, str] = {}
        self._home_dir = home_dir
        # Create home directory structure
        self._ensure_path_exists(home_dir)

    def _ensure_path_exists(self, path: str) -> None:
        """Create all directories in path."""
        parts = [p for p in path.split("/") if p]
        current = ""
        for part in parts:
            current = f"{current}/{part}"
            self._directories.add(current)

    def mkdir(self, path: str) -> bool:
        """Create a directory."""
        path = self._normalize_path(path)
        if path in self._directories or path in self._symlinks:
            return False
        parent = self._get_parent(path)
        if parent and parent not in self._directories:
            return False
        self._directories.add(path)
        return True

    def mkdir_p(self, path: str) -> bool:
        """Create directory and all parents."""
        path = self._normalize_path(path)
        self._ensure_path_exists(path)
        return True

    def create_symlink(self, link_path: str, target: str) -> bool:
        """Create a symbolic link."""
        link_path = self._normalize_path(link_path)
        if link_path in self._directories or link_path in self._symlinks:
            return False
        self._symlinks[link_path] = target
        return True

    def exists(self, path: str) -> bool:
        """Check if path exists (directory or symlink)."""
        path = self._normalize_path(path)
        return path in self._directories or path in self._symlinks

    def cd(self, current_dir: str, new_dir: str, validate: bool = True) -> str:
        """
        Change directory with validation.

        Args:
            current_dir: Current working directory
            new_dir: Target directory (can include ~)
            validate: If True, raise PathError for invalid paths

        Returns:
            Resolved absolute path

        Raises:
            PathError: If validate=True and path is invalid
        """
        # Handle home directory
        if new_dir == "~" or new_dir.startswith("~/"):
            new_dir = self._home_dir + new_dir[1:]

        # Build path
        if new_dir.startswith("/"):
            path_parts = new_dir.split("/")
        else:
            path_parts = current_dir.split("/") + new_dir.split("/")

        # Process and validate path components
        result = []
        for part in path_parts:
            if part == "" or part == ".":
                continue
            elif part == "..":
                if result:
                    result.pop()
            else:
                result.append(part)
                current_path = "/" + "/".join(result)

                # Resolve symlinks
                resolved = self._resolve_symlink(current_path)
                if resolved != current_path:
                    result = self._path_to_parts(resolved)
                    current_path = resolved

                # Validate path exists
                if validate and not self.exists(current_path):
                    raise PathError(f"No such directory: {current_path}")

        final_path = "/" + "/".join(result) if result else "/"

        if validate and final_path != "/" and not self.exists(final_path):
            raise PathError(f"No such directory: {final_path}")

        return final_path

    def cd_safe(self, current_dir: str, new_dir: str) -> Optional[str]:
        """
        Change directory, returning None on error.
        """
        try:
            return self.cd(current_dir, new_dir, validate=True)
        except PathError:
            return None

    def _resolve_symlink(self, path: str, depth: int = 0) -> str:
        """Resolve symbolic link."""
        if depth > self.MAX_SYMLINK_DEPTH:
            return path

        if path in self._symlinks:
            target = self._symlinks[path]
            if not target.startswith("/"):
                parent = self._get_parent(path)
                target = self._join_path(parent, target)
            return self._resolve_symlink(target, depth + 1)

        return path

    def _normalize_path(self, path: str) -> str:
        """Normalize path."""
        if path != "/" and path.endswith("/"):
            return path[:-1]
        return path

    def _get_parent(self, path: str) -> str | None:
        """Get parent directory."""
        if path == "/":
            return None
        parts = path.rstrip("/").split("/")
        if len(parts) <= 2:
            return "/"
        return "/".join(parts[:-1])

    def _path_to_parts(self, path: str) -> list[str]:
        """Convert path to parts."""
        return [p for p in path.split("/") if p]

    def _join_path(self, base: str, relative: str) -> str:
        """Join paths."""
        if relative.startswith("/"):
            return relative
        parts = self._path_to_parts(base) + self._path_to_parts(relative)
        return "/" + "/".join(parts)


def cd(current_dir: str, new_dir: str) -> str:
    """Simple cd without validation (backwards compatible)."""
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
