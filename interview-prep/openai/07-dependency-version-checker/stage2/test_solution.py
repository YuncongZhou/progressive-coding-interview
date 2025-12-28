"""Tests for Dependency Version Checker Stage 2 - Complex Constraints"""
import pytest
from solution import DependencyChecker, satisfies


class TestDependencyCheckerStage2:
    def test_and_constraints(self):
        assert satisfies("2.5.0", ">=2.0.0, <3.0.0") is True
        assert satisfies("3.0.0", ">=2.0.0, <3.0.0") is False
        assert satisfies("1.9.0", ">=2.0.0, <3.0.0") is False

    def test_or_constraints(self):
        assert satisfies("1.0.0", "1.0.0 || 2.0.0") is True
        assert satisfies("2.0.0", "1.0.0 || 2.0.0") is True
        assert satisfies("1.5.0", "1.0.0 || 2.0.0") is False

    def test_complex_constraints(self):
        # Version 2.5 or >=3.0
        assert satisfies("2.5.0", "2.5.0 || >=3.0.0") is True
        assert satisfies("3.5.0", "2.5.0 || >=3.0.0") is True
        assert satisfies("2.4.0", "2.5.0 || >=3.0.0") is False

    def test_caret_constraint(self):
        assert satisfies("1.5.0", "^1.0.0") is True
        assert satisfies("1.0.0", "^1.0.0") is True
        assert satisfies("2.0.0", "^1.0.0") is False

    def test_tilde_constraint(self):
        assert satisfies("1.5.0", "~=1.0.0") is True
        assert satisfies("2.0.0", "~=1.0.0") is False

    def test_find_conflicts(self):
        checker = DependencyChecker()
        checker.install("a", "1.0.0")
        checker.install("b", "2.0.0")

        conflicts = checker.find_conflicts({
            "a": ">=2.0.0",
            "b": ">=1.0.0"
        })

        assert "a" in conflicts
        assert "b" not in conflicts
