"""Tests for Dependency Version Checker Stage 3 - Dependency Tree"""
import pytest
from solution import DependencyChecker


class TestDependencyCheckerStage3:
    def test_get_dependencies(self):
        checker = DependencyChecker()
        checker.install("requests", "2.28.0", {"urllib3": ">=1.26.0"})

        deps = checker.get_dependencies("requests")
        assert "urllib3" in deps

    def test_get_all_dependencies(self):
        checker = DependencyChecker()
        checker.install("base", "1.0.0", {})
        checker.install("middle", "1.0.0", {"base": ">=1.0.0"})
        checker.install("top", "1.0.0", {"middle": ">=1.0.0"})

        all_deps = checker.get_all_dependencies("top")
        assert "middle" in all_deps
        assert "base" in all_deps

    def test_check_tree_success(self):
        checker = DependencyChecker()
        checker.install("urllib3", "1.26.0", {})
        checker.install("requests", "2.28.0", {"urllib3": ">=1.26.0"})

        conflicts = checker.check_tree("requests")
        assert len(conflicts) == 0

    def test_check_tree_conflict(self):
        checker = DependencyChecker()
        checker.install("urllib3", "1.25.0", {})  # Too old
        checker.install("requests", "2.28.0", {"urllib3": ">=1.26.0"})

        conflicts = checker.check_tree("requests")
        assert len(conflicts) == 1
        assert "urllib3" in conflicts[0]

    def test_detect_cycles_no_cycle(self):
        checker = DependencyChecker()
        checker.install("a", "1.0.0", {"b": ">=1.0.0"})
        checker.install("b", "1.0.0", {})

        assert checker.detect_cycles("a") is False

    def test_detect_cycles_with_cycle(self):
        checker = DependencyChecker()
        checker.install("a", "1.0.0", {"b": ">=1.0.0"})
        checker.install("b", "1.0.0", {"a": ">=1.0.0"})

        assert checker.detect_cycles("a") is True

    def test_deep_tree(self):
        checker = DependencyChecker()
        checker.install("pkg0", "1.0.0", {})
        for i in range(1, 5):
            checker.install(f"pkg{i}", "1.0.0", {f"pkg{i-1}": ">=1.0.0"})

        all_deps = checker.get_all_dependencies("pkg4")
        assert len(all_deps) == 4
