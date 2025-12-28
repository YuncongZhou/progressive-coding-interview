"""
Package Manager - Stage 2

Dependency resolution.

Design Rationale:
- Packages can declare dependencies
- Install dependencies automatically
- Prevent uninstall if other packages depend on it
"""

from typing import Optional


class PackageManager:
    """Package manager with dependency resolution."""

    def __init__(self):
        self._packages: dict[str, str] = {}  # name -> version
        self._dependencies: dict[str, list[str]] = {}  # name -> [dep names]

    def register_package(self, name: str, version: str,
                         dependencies: list[str] = None) -> None:
        """Register a package with its dependencies in the registry."""
        self._dependencies[name] = dependencies or []

    def install(self, name: str, version: str) -> list[str]:
        """
        Install a package and its dependencies.

        Returns list of packages installed (in order).
        """
        if name in self._packages:
            return []

        installed = []
        self._install_recursive(name, version, installed, set())
        return installed

    def _install_recursive(self, name: str, version: str,
                           installed: list[str], visiting: set) -> None:
        """Recursively install package and dependencies."""
        if name in self._packages or name in visiting:
            return

        visiting.add(name)

        # Install dependencies first
        for dep in self._dependencies.get(name, []):
            if dep not in self._packages:
                # Use a default version for dependencies
                self._install_recursive(dep, "latest", installed, visiting)

        # Install this package
        self._packages[name] = version
        installed.append(name)

    def uninstall(self, name: str) -> tuple[bool, Optional[str]]:
        """
        Uninstall a package.

        Returns (success, error_message).
        Error if other packages depend on this one.
        """
        if name not in self._packages:
            return False, "Package not installed"

        # Check if any installed package depends on this one
        for pkg in self._packages:
            if name in self._dependencies.get(pkg, []):
                return False, f"Cannot uninstall: {pkg} depends on {name}"

        del self._packages[name]
        return True, None

    def is_installed(self, name: str) -> bool:
        """Check if package is installed."""
        return name in self._packages

    def get_version(self, name: str) -> Optional[str]:
        """Get installed version of package."""
        return self._packages.get(name)

    def list_packages(self) -> list[tuple[str, str]]:
        """List all installed packages."""
        return sorted(self._packages.items())

    def get_dependents(self, name: str) -> list[str]:
        """Get list of installed packages that depend on this package."""
        dependents = []
        for pkg in self._packages:
            if name in self._dependencies.get(pkg, []):
                dependents.append(pkg)
        return sorted(dependents)

    def get_dependencies(self, name: str) -> list[str]:
        """Get list of dependencies for a package."""
        return self._dependencies.get(name, [])
