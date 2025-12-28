"""Tests for Package Manager Stage 3 - Version Constraints"""
import pytest
from solution import PackageManager


class TestPackageManagerStage3:
    def test_install_exact_version(self):
        pm = PackageManager()
        pm.register_package("requests", ["2.27.0", "2.28.0", "2.29.0"])

        success, installed = pm.install("requests", "==2.28.0")
        assert success is True
        assert pm.get_version("requests") == "2.28.0"

    def test_install_latest(self):
        pm = PackageManager()
        pm.register_package("requests", ["2.27.0", "2.28.0", "2.29.0"])

        success, installed = pm.install("requests")
        assert success is True
        assert pm.get_version("requests") == "2.29.0"

    def test_install_gte(self):
        pm = PackageManager()
        pm.register_package("requests", ["2.27.0", "2.28.0", "2.29.0"])

        success, installed = pm.install("requests", ">=2.28.0")
        assert success is True
        assert pm.get_version("requests") == "2.29.0"

    def test_install_lt(self):
        pm = PackageManager()
        pm.register_package("requests", ["2.27.0", "2.28.0", "2.29.0"])

        success, installed = pm.install("requests", "<2.29.0")
        assert success is True
        assert pm.get_version("requests") == "2.28.0"

    def test_install_compatible(self):
        pm = PackageManager()
        pm.register_package("requests", ["1.9.0", "2.0.0", "2.28.0", "3.0.0"])

        success, installed = pm.install("requests", "~=2.0.0")
        assert success is True
        assert pm.get_version("requests") == "2.28.0"

    def test_no_matching_version(self):
        pm = PackageManager()
        pm.register_package("requests", ["2.27.0", "2.28.0"])

        success, installed = pm.install("requests", ">=3.0.0")
        assert success is False

    def test_deps_with_constraints(self):
        pm = PackageManager()
        pm.register_package("urllib3", ["1.25.0", "1.26.0", "2.0.0"])
        pm.register_package("requests", ["2.28.0"], {
            "2.28.0": [("urllib3", ">=1.26.0")]
        })

        success, installed = pm.install("requests", "==2.28.0")
        assert success is True
        assert pm.get_version("urllib3") == "2.0.0"

    def test_deps_constraint_conflict(self):
        pm = PackageManager()
        pm.register_package("urllib3", ["1.25.0"])
        pm.register_package("requests", ["2.28.0"], {
            "2.28.0": [("urllib3", ">=1.26.0")]
        })

        success, installed = pm.install("requests", "==2.28.0")
        assert success is False

    def test_check_constraint(self):
        pm = PackageManager()
        pm.register_package("requests", ["2.28.0"])
        pm.install("requests", "==2.28.0")

        assert pm.check_constraint("requests", ">=2.0.0") is True
        assert pm.check_constraint("requests", "<2.0.0") is False
        assert pm.check_constraint("missing", ">=1.0.0") is False
