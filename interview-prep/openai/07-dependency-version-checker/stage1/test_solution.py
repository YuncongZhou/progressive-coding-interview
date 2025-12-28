"""Tests for Dependency Version Checker Stage 1"""
import pytest
from solution import DependencyChecker, satisfies, compare_versions


class TestDependencyCheckerStage1:
    def test_compare_versions(self):
        assert compare_versions("1.0.0", "1.0.0") == 0
        assert compare_versions("1.0.0", "2.0.0") == -1
        assert compare_versions("2.0.0", "1.0.0") == 1
        assert compare_versions("1.2.0", "1.10.0") == -1

    def test_satisfies_exact(self):
        assert satisfies("1.0.0", "1.0.0") is True
        assert satisfies("1.0.0", "==1.0.0") is True
        assert satisfies("1.0.0", "1.0.1") is False

    def test_satisfies_gte(self):
        assert satisfies("2.0.0", ">=1.0.0") is True
        assert satisfies("1.0.0", ">=1.0.0") is True
        assert satisfies("0.9.0", ">=1.0.0") is False

    def test_satisfies_lt(self):
        assert satisfies("0.9.0", "<1.0.0") is True
        assert satisfies("1.0.0", "<1.0.0") is False

    def test_install_and_check(self):
        checker = DependencyChecker()
        checker.install("requests", "2.28.0")

        assert checker.check("requests", ">=2.0.0") is True
        assert checker.check("requests", "<3.0.0") is True
        assert checker.check("requests", ">=3.0.0") is False

    def test_check_missing(self):
        checker = DependencyChecker()
        assert checker.check("missing", ">=1.0.0") is False

    def test_check_all(self):
        checker = DependencyChecker()
        checker.install("requests", "2.28.0")
        checker.install("flask", "2.0.0")

        results = checker.check_all({
            "requests": ">=2.0.0",
            "flask": ">=3.0.0",
            "missing": ">=1.0.0"
        })

        assert results["requests"] is True
        assert results["flask"] is False
        assert results["missing"] is False
