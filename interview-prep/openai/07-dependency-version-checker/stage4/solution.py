"""
Dependency Version Checker - Stage 4

Version resolution and updates.

Design Rationale:
- Find compatible version combinations
- Suggest updates
- Generate lockfile
"""

import re
from typing import Optional, List, Set, Dict
from dataclasses import dataclass


def parse_version(version: str) -> tuple[int, ...]:
    parts = version.split(".")
    return tuple(int(p) for p in parts)


def compare_versions(v1: str, v2: str) -> int:
    t1 = parse_version(v1)
    t2 = parse_version(v2)
    max_len = max(len(t1), len(t2))
    t1 = t1 + (0,) * (max_len - len(t1))
    t2 = t2 + (0,) * (max_len - len(t2))
    return -1 if t1 < t2 else 1 if t1 > t2 else 0


def satisfies(version: str, constraint: str) -> bool:
    or_parts = constraint.split("||")
    for or_part in or_parts:
        and_parts = [p.strip() for p in or_part.split(",")]
        if all(_satisfies_simple(version, p) for p in and_parts if p):
            return True
    return False


def _satisfies_simple(version: str, constraint: str) -> bool:
    constraint = constraint.strip()
    match = re.match(r'^(>=|<=|>|<|=|==)?(.+)$', constraint)
    if not match:
        return False
    op = match.group(1) or "=="
    target = match.group(2).strip()
    cmp = compare_versions(version, target)
    if op in ("=", "=="):
        return cmp == 0
    elif op == ">=":
        return cmp >= 0
    elif op == "<=":
        return cmp <= 0
    elif op == ">":
        return cmp > 0
    elif op == "<":
        return cmp < 0
    return False


@dataclass
class Package:
    name: str
    version: str
    dependencies: dict[str, str]


@dataclass
class UpdateSuggestion:
    name: str
    current: str
    latest: str
    breaking: bool


class DependencyChecker:
    """Full dependency checker with resolution."""

    def __init__(self):
        self._installed: dict[str, Package] = {}
        self._registry: dict[str, List[str]] = {}  # name -> [versions]

    def register_versions(self, name: str, versions: List[str]) -> None:
        """Register available versions for a package."""
        self._registry[name] = sorted(versions, key=parse_version)

    def install(self, name: str, version: str,
                dependencies: dict[str, str] = None) -> None:
        self._installed[name] = Package(
            name=name, version=version, dependencies=dependencies or {}
        )

    def get_version(self, name: str) -> Optional[str]:
        pkg = self._installed.get(name)
        return pkg.version if pkg else None

    def check(self, name: str, constraint: str) -> bool:
        version = self.get_version(name)
        return satisfies(version, constraint) if version else False

    def find_compatible_version(self, name: str, constraint: str) -> Optional[str]:
        """Find best version satisfying constraint."""
        versions = self._registry.get(name, [])
        for version in reversed(versions):
            if satisfies(version, constraint):
                return version
        return None

    def resolve(self, requirements: dict[str, str]) -> Optional[dict[str, str]]:
        """
        Resolve compatible versions for all requirements.

        Returns dict of name -> version, or None if unresolvable.
        """
        resolved = {}

        for name, constraint in requirements.items():
            version = self.find_compatible_version(name, constraint)
            if version is None:
                return None
            resolved[name] = version

        return resolved

    def check_updates(self) -> List[UpdateSuggestion]:
        """Check for available updates."""
        suggestions = []

        for name, pkg in self._installed.items():
            versions = self._registry.get(name, [])
            if not versions:
                continue

            latest = versions[-1]
            if compare_versions(latest, pkg.version) > 0:
                # Check if major version changed
                current_major = parse_version(pkg.version)[0]
                latest_major = parse_version(latest)[0]

                suggestions.append(UpdateSuggestion(
                    name=name,
                    current=pkg.version,
                    latest=latest,
                    breaking=latest_major > current_major
                ))

        return suggestions

    def generate_lockfile(self) -> dict[str, str]:
        """Generate lockfile with exact versions."""
        return {name: pkg.version for name, pkg in self._installed.items()}

    def get_outdated(self) -> List[str]:
        """Get list of outdated packages."""
        return [s.name for s in self.check_updates()]

    def get_security_updates(self, vulnerable: Set[str]) -> List[str]:
        """
        Get packages that need security updates.

        vulnerable: Set of (name, version) tuples that are vulnerable.
        """
        updates = []
        for name, pkg in self._installed.items():
            key = f"{name}@{pkg.version}"
            if key in vulnerable:
                updates.append(name)
        return updates
