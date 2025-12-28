"""
Package Manager - Stage 4

Conflict detection and resolution.

Design Rationale:
- Detect version conflicts between dependencies
- Provide resolution strategies
- Support lock files for reproducibility
"""

import re
from typing import Optional
from dataclasses import dataclass


@dataclass
class Conflict:
    """Represents a version conflict."""
    package: str
    required_by: list[tuple[str, str]]  # [(pkg_name, constraint), ...]


class PackageManager:
    """Package manager with conflict detection."""

    def __init__(self):
        self._packages: dict[str, str] = {}
        self._registry: dict[str, dict] = {}
        self._resolved_versions: dict[str, str] = {}  # Cache resolved versions

    def register_package(self, name: str, versions: list[str],
                         dependencies: dict[str, list[str]] = None) -> None:
        """Register package with versions and dependencies."""
        self._registry[name] = {
            "versions": sorted(versions, key=self._version_tuple),
            "dependencies": dependencies or {}
        }

    def install(self, name: str, constraint: str = None,
                resolve_conflicts: bool = True) -> tuple[bool, list[str], list[Conflict]]:
        """
        Install a package.

        Returns (success, installed_list, conflicts).
        """
        if name not in self._registry:
            return False, [], []

        # Collect all requirements
        requirements: dict[str, list[tuple[str, str]]] = {}
        self._collect_requirements(name, constraint, requirements, "root")

        # Check for conflicts and find compatible versions
        conflicts = []
        resolved = {}

        for pkg, reqs in requirements.items():
            if pkg not in self._registry:
                conflicts.append(Conflict(pkg, reqs))
                continue

            versions = self._registry[pkg]["versions"]
            compatible = None

            # Find a version that satisfies all constraints
            for version in reversed(versions):
                constraints = [c for _, c in reqs]
                if all(self._matches_constraint(version, c) for c in constraints):
                    compatible = version
                    break

            if compatible is None:
                conflicts.append(Conflict(pkg, reqs))
            else:
                resolved[pkg] = compatible

        if conflicts:
            if not resolve_conflicts:
                return False, [], conflicts
            # Even with resolve_conflicts=True, if there are real conflicts, fail
            return False, [], conflicts

        # Store resolved versions
        self._resolved_versions = resolved

        # Install packages in dependency order
        installed = []
        success = self._install_ordered(name, installed, set())
        return success, installed, []

    def _collect_requirements(self, name: str, constraint: str,
                              requirements: dict, requirer: str) -> None:
        """Collect all version requirements recursively."""
        if name not in requirements:
            requirements[name] = []

        if constraint:
            requirements[name].append((requirer, constraint))

        if name not in self._registry:
            return

        # Use the best available version to get deps
        version = self._find_version(name, constraint)
        if version is None:
            return

        deps = self._registry[name]["dependencies"].get(version, [])
        for dep_name, dep_constraint in deps:
            # Check if already visited with this exact constraint
            existing = requirements.get(dep_name, [])
            if any(c == dep_constraint for _, c in existing):
                continue
            self._collect_requirements(dep_name, dep_constraint, requirements, name)

    def _install_ordered(self, name: str, installed: list[str],
                         visiting: set) -> bool:
        """Install packages in dependency order using resolved versions."""
        if name in self._packages:
            return True
        if name in visiting:
            return True  # Already processing
        if name not in self._registry:
            return False

        visiting.add(name)

        # Use the resolved version
        version = self._resolved_versions.get(name)
        if version is None:
            return False

        # Install dependencies first
        deps = self._registry[name]["dependencies"].get(version, [])
        for dep_name, _ in deps:
            if not self._install_ordered(dep_name, installed, visiting):
                return False

        self._packages[name] = version
        installed.append(f"{name}=={version}")
        return True

    def _find_version(self, name: str, constraint: str = None) -> Optional[str]:
        """Find best matching version."""
        if name not in self._registry:
            return None

        versions = self._registry[name]["versions"]
        if not versions:
            return None

        if constraint is None:
            return versions[-1]

        matching = [v for v in versions if self._matches_constraint(v, constraint)]
        return matching[-1] if matching else None

    def _matches_constraint(self, version: str, constraint: str) -> bool:
        """Check if version matches constraint."""
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
            return v_tuple >= t_tuple and v_tuple[0] == t_tuple[0]

        return False

    def _version_tuple(self, version: str) -> tuple:
        """Convert version to tuple."""
        parts = []
        for part in version.split("."):
            try:
                parts.append(int(part))
            except ValueError:
                parts.append(part)
        return tuple(parts)

    def generate_lockfile(self) -> dict[str, str]:
        """Generate lockfile with exact versions."""
        return dict(sorted(self._packages.items()))

    def install_from_lockfile(self, lockfile: dict[str, str]) -> bool:
        """Install exact versions from lockfile."""
        for name, version in lockfile.items():
            if name in self._registry:
                self._packages[name] = version
        return True

    def is_installed(self, name: str) -> bool:
        return name in self._packages

    def get_version(self, name: str) -> Optional[str]:
        return self._packages.get(name)

    def list_packages(self) -> list[tuple[str, str]]:
        return sorted(self._packages.items())
