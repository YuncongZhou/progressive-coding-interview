"""
Dependency Version Checker - Stage 2

Complex constraints with AND/OR.

Design Rationale:
- Support comma-separated AND constraints
- Support || for OR constraints
"""

import re
from typing import Optional, List


def parse_version(version: str) -> tuple[int, ...]:
    parts = version.split(".")
    return tuple(int(p) for p in parts)


def compare_versions(v1: str, v2: str) -> int:
    t1 = parse_version(v1)
    t2 = parse_version(v2)
    max_len = max(len(t1), len(t2))
    t1 = t1 + (0,) * (max_len - len(t1))
    t2 = t2 + (0,) * (max_len - len(t2))

    if t1 < t2:
        return -1
    elif t1 > t2:
        return 1
    return 0


def satisfies_simple(version: str, constraint: str) -> bool:
    """Check single constraint."""
    constraint = constraint.strip()
    match = re.match(r'^(>=|<=|>|<|=|==|~=|\^)?(.+)$', constraint)
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
    elif op == "~=":
        # Compatible release
        v = parse_version(version)
        t = parse_version(target)
        return v >= t and v[0] == t[0]
    elif op == "^":
        # Caret: allow changes that don't modify left-most non-zero
        v = parse_version(version)
        t = parse_version(target)
        return v >= t and v[0] == t[0]

    return False


def satisfies(version: str, constraint: str) -> bool:
    """Check constraint with AND (,) and OR (||)."""
    # Split by OR first
    or_parts = constraint.split("||")

    for or_part in or_parts:
        # Each OR part is AND of constraints
        and_parts = [p.strip() for p in or_part.split(",")]
        if all(satisfies_simple(version, p) for p in and_parts if p):
            return True

    return False


class DependencyChecker:
    """Check dependency versions with complex constraints."""

    def __init__(self):
        self._installed: dict[str, str] = {}

    def install(self, name: str, version: str) -> None:
        self._installed[name] = version

    def get_version(self, name: str) -> Optional[str]:
        return self._installed.get(name)

    def check(self, name: str, constraint: str) -> bool:
        version = self._installed.get(name)
        if version is None:
            return False
        return satisfies(version, constraint)

    def check_all(self, requirements: dict[str, str]) -> dict[str, bool]:
        return {name: self.check(name, constraint)
                for name, constraint in requirements.items()}

    def find_conflicts(self, requirements: dict[str, str]) -> List[str]:
        """Find packages that don't satisfy constraints."""
        return [name for name, constraint in requirements.items()
                if not self.check(name, constraint)]
