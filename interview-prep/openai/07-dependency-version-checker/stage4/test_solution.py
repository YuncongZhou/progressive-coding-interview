"""Tests for Dependency Version Checker Stage 4 - Resolution"""
import pytest
from solution import DependencyChecker


class TestDependencyCheckerStage4:
    def test_find_compatible_version(self):
        checker = DependencyChecker()
        checker.register_versions("requests", ["2.26.0", "2.27.0", "2.28.0"])

        version = checker.find_compatible_version("requests", ">=2.27.0")
        assert version == "2.28.0"

    def test_find_compatible_version_constrained(self):
        checker = DependencyChecker()
        checker.register_versions("requests", ["2.26.0", "2.27.0", "2.28.0"])

        version = checker.find_compatible_version("requests", ">=2.26.0, <2.28.0")
        assert version == "2.27.0"

    def test_resolve_success(self):
        checker = DependencyChecker()
        checker.register_versions("a", ["1.0.0", "2.0.0"])
        checker.register_versions("b", ["1.0.0", "2.0.0"])

        result = checker.resolve({
            "a": ">=1.0.0",
            "b": ">=1.0.0"
        })

        assert result is not None
        assert result["a"] == "2.0.0"
        assert result["b"] == "2.0.0"

    def test_resolve_failure(self):
        checker = DependencyChecker()
        checker.register_versions("a", ["1.0.0"])

        result = checker.resolve({"a": ">=2.0.0"})
        assert result is None

    def test_check_updates(self):
        checker = DependencyChecker()
        checker.register_versions("requests", ["2.26.0", "2.27.0", "2.28.0"])
        checker.install("requests", "2.26.0")

        updates = checker.check_updates()
        assert len(updates) == 1
        assert updates[0].name == "requests"
        assert updates[0].current == "2.26.0"
        assert updates[0].latest == "2.28.0"

    def test_breaking_update(self):
        checker = DependencyChecker()
        checker.register_versions("pkg", ["1.0.0", "2.0.0"])
        checker.install("pkg", "1.0.0")

        updates = checker.check_updates()
        assert updates[0].breaking is True

    def test_generate_lockfile(self):
        checker = DependencyChecker()
        checker.install("a", "1.0.0")
        checker.install("b", "2.0.0")

        lockfile = checker.generate_lockfile()
        assert lockfile == {"a": "1.0.0", "b": "2.0.0"}

    def test_get_outdated(self):
        checker = DependencyChecker()
        checker.register_versions("a", ["1.0.0", "2.0.0"])
        checker.register_versions("b", ["1.0.0"])
        checker.install("a", "1.0.0")
        checker.install("b", "1.0.0")

        outdated = checker.get_outdated()
        assert "a" in outdated
        assert "b" not in outdated
