"""
Package Manager - Stage 3

Version constraints support.

Design Rationale:
- Support version constraints: ==, >=, <=, >, <, ~=
- Validate constraints during install
- Find compatible versions
"""

import re
from typing import Optional


class PackageManager:
    """Package manager with version constraints."""

    def __init__(self):
        self._packages: dict[str, str] = {}
        self._registry: dict[str, dict] = {}  # name -> {versions: [...], deps: {...}}

    def register_package(self, name: str, versions: list[str],
                         dependencies: dict[str, list[str]] = None) -> None:
        """
        Register a package with available versions.

        Args:
            versions: List of available versions
            dependencies: {version: [(dep_name, constraint), ...]}
        """
        self._registry[name] = {
            "versions": sorted(versions, key=self._version_tuple),
            "dependencies": dependencies or {}
        }

    def install(self, name: str, constraint: str = None) -> tuple[bool, list[str]]:
        """
        Install a package with optional version constraint.

        Returns (success, list of installed packages).
        """
        if name not in self._registry:
            return False, []

        # Find matching version
        version = self._find_version(name, constraint)
        if version is None:
            return False, []

        installed = []
        success = self._install_recursive(name, version, installed, set())
        return success, installed

    def _find_version(self, name: str, constraint: str = None) -> Optional[str]:
        """Find the best matching version for constraint."""
        if name not in self._registry:
            return None

        versions = self._registry[name]["versions"]
        if not versions:
            return None

        if constraint is None:
            return versions[-1]  # Latest

        matching = [v for v in versions if self._matches_constraint(v, constraint)]
        return matching[-1] if matching else None

    def _matches_constraint(self, version: str, constraint: str) -> bool:
        """Check if version matches constraint."""
        # Parse constraint
        match = re.match(r'^(==|>=|<=|>|<|~=)?(.+)$', constraint)
        if not match:
            return False

        op = match.group(1) or "=="
        target = match.group(2)

        v_tuple = self._version_tuple(version)
        t_tuple = self._version_tuple(target)

        if op == "==":
            return v_tuple == t_tuple
        elif op == ">=":
            return v_tuple >= t_tuple
        elif op == "<=":
            return v_tuple <= t_tuple
        elif op == ">":
            return v_tuple > t_tuple
        elif op == "<":
            return v_tuple < t_tuple
        elif op == "~=":
            # Compatible release: >=X.Y, <X+1.0
            return v_tuple >= t_tuple and v_tuple[0] == t_tuple[0]

        return False

    def _version_tuple(self, version: str) -> tuple:
        """Convert version string to comparable tuple."""
        parts = []
        for part in version.split("."):
            try:
                parts.append(int(part))
            except ValueError:
                parts.append(part)
        return tuple(parts)

    def _install_recursive(self, name: str, version: str,
                           installed: list[str], visiting: set) -> bool:
        """Recursively install package and dependencies."""
        if name in self._packages:
            return True

        if name in visiting:
            return False  # Circular dependency

        visiting.add(name)

        # Get dependencies for this version
        deps = self._registry[name]["dependencies"].get(version, [])

        # Install dependencies first
        for dep_name, constraint in deps:
            dep_version = self._find_version(dep_name, constraint)
            if dep_version is None:
                return False
            if not self._install_recursive(dep_name, dep_version, installed, visiting):
                return False

        # Install this package
        self._packages[name] = version
        installed.append(f"{name}=={version}")
        return True

    def is_installed(self, name: str) -> bool:
        """Check if package is installed."""
        return name in self._packages

    def get_version(self, name: str) -> Optional[str]:
        """Get installed version."""
        return self._packages.get(name)

    def list_packages(self) -> list[tuple[str, str]]:
        """List installed packages."""
        return sorted(self._packages.items())

    def check_constraint(self, name: str, constraint: str) -> bool:
        """Check if installed version matches constraint."""
        if name not in self._packages:
            return False
        return self._matches_constraint(self._packages[name], constraint)
