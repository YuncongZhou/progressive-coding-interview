"""
Package Manager - Stage 1

Basic package installation and removal.

Design Rationale:
- Track installed packages with versions
- Simple install/uninstall operations
- List installed packages
"""

from typing import Optional


class PackageManager:
    """Basic package manager."""

    def __init__(self):
        self._packages: dict[str, str] = {}  # name -> version

    def install(self, name: str, version: str) -> bool:
        """
        Install a package.

        Returns True if installed, False if already installed with same version.
        """
        if name in self._packages and self._packages[name] == version:
            return False
        self._packages[name] = version
        return True

    def uninstall(self, name: str) -> bool:
        """
        Uninstall a package.

        Returns True if uninstalled, False if not installed.
        """
        if name not in self._packages:
            return False
        del self._packages[name]
        return True

    def is_installed(self, name: str) -> bool:
        """Check if package is installed."""
        return name in self._packages

    def get_version(self, name: str) -> Optional[str]:
        """Get installed version of package."""
        return self._packages.get(name)

    def list_packages(self) -> list[tuple[str, str]]:
        """List all installed packages as (name, version) tuples."""
        return sorted(self._packages.items())

    def upgrade(self, name: str, new_version: str) -> bool:
        """
        Upgrade package to new version.

        Returns True if upgraded, False if not installed.
        """
        if name not in self._packages:
            return False
        self._packages[name] = new_version
        return True
