"""
Dependency Version Checker - Stage 1

Check if dependencies satisfy version requirements.

Design Rationale:
- Parse semantic versions
- Compare versions with operators
"""

import re
from typing import Optional


def parse_version(version: str) -> tuple[int, ...]:
    """Parse version string to tuple."""
    parts = version.split(".")
    return tuple(int(p) for p in parts)


def compare_versions(v1: str, v2: str) -> int:
    """Compare two versions. Returns -1, 0, or 1."""
    t1 = parse_version(v1)
    t2 = parse_version(v2)

    # Pad to same length
    max_len = max(len(t1), len(t2))
    t1 = t1 + (0,) * (max_len - len(t1))
    t2 = t2 + (0,) * (max_len - len(t2))

    if t1 < t2:
        return -1
    elif t1 > t2:
        return 1
    return 0


def satisfies(version: str, constraint: str) -> bool:
    """Check if version satisfies constraint."""
    constraint = constraint.strip()

    # Parse constraint
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


class DependencyChecker:
    """Check dependency versions."""

    def __init__(self):
        self._installed: dict[str, str] = {}

    def install(self, name: str, version: str) -> None:
        """Record installed package version."""
        self._installed[name] = version

    def get_version(self, name: str) -> Optional[str]:
        """Get installed version."""
        return self._installed.get(name)

    def check(self, name: str, constraint: str) -> bool:
        """Check if installed version satisfies constraint."""
        version = self._installed.get(name)
        if version is None:
            return False
        return satisfies(version, constraint)

    def check_all(self, requirements: dict[str, str]) -> dict[str, bool]:
        """Check multiple requirements."""
        return {name: self.check(name, constraint)
                for name, constraint in requirements.items()}
