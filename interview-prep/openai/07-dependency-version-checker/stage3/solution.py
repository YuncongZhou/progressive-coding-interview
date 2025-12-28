"""
Dependency Version Checker - Stage 3

Dependency tree and resolution.

Design Rationale:
- Track package dependencies
- Check transitive dependencies
- Detect conflicts in tree
"""

import re
from typing import Optional, List, Set
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
    dependencies: dict[str, str]  # name -> constraint


class DependencyChecker:
    """Check dependencies with tree resolution."""

    def __init__(self):
        self._installed: dict[str, Package] = {}

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

    def get_dependencies(self, name: str) -> dict[str, str]:
        """Get direct dependencies of package."""
        pkg = self._installed.get(name)
        return pkg.dependencies if pkg else {}

    def get_all_dependencies(self, name: str) -> Set[str]:
        """Get all transitive dependencies."""
        result = set()
        self._collect_deps(name, result, set())
        return result

    def _collect_deps(self, name: str, result: Set[str], visited: Set[str]):
        if name in visited:
            return
        visited.add(name)

        pkg = self._installed.get(name)
        if not pkg:
            return

        for dep_name in pkg.dependencies:
            result.add(dep_name)
            self._collect_deps(dep_name, result, visited)

    def check_tree(self, name: str) -> List[str]:
        """Check all dependencies in tree. Returns list of conflicts."""
        conflicts = []
        self._check_tree_recursive(name, conflicts, set())
        return conflicts

    def _check_tree_recursive(self, name: str, conflicts: List[str],
                              visited: Set[str]) -> None:
        if name in visited:
            return
        visited.add(name)

        pkg = self._installed.get(name)
        if not pkg:
            return

        for dep_name, constraint in pkg.dependencies.items():
            if not self.check(dep_name, constraint):
                conflicts.append(f"{name} requires {dep_name} {constraint}")
            self._check_tree_recursive(dep_name, conflicts, visited)

    def detect_cycles(self, name: str) -> bool:
        """Detect if package has circular dependencies."""
        return self._has_cycle(name, set(), set())

    def _has_cycle(self, name: str, path: Set[str], visited: Set[str]) -> bool:
        if name in path:
            return True
        if name in visited:
            return False

        path.add(name)
        visited.add(name)

        pkg = self._installed.get(name)
        if pkg:
            for dep in pkg.dependencies:
                if self._has_cycle(dep, path, visited):
                    return True

        path.remove(name)
        return False
