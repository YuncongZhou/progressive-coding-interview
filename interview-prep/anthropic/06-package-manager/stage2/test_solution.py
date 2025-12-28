"""Tests for Package Manager Stage 2 - Dependencies"""
import pytest
from solution import PackageManager


class TestPackageManagerStage2:
    def test_install_with_deps(self):
        pm = PackageManager()
        pm.register_package("urllib3", "1.26.0", [])
        pm.register_package("requests", "2.28.0", ["urllib3"])

        installed = pm.install("requests", "2.28.0")
        assert installed == ["urllib3", "requests"]
        assert pm.is_installed("urllib3")
        assert pm.is_installed("requests")

    def test_install_no_deps(self):
        pm = PackageManager()
        pm.register_package("simple", "1.0.0", [])

        installed = pm.install("simple", "1.0.0")
        assert installed == ["simple"]

    def test_uninstall_with_dependent(self):
        pm = PackageManager()
        pm.register_package("urllib3", "1.26.0", [])
        pm.register_package("requests", "2.28.0", ["urllib3"])
        pm.install("requests", "2.28.0")

        success, error = pm.uninstall("urllib3")
        assert success is False
        assert "requests depends on urllib3" in error

    def test_uninstall_no_dependents(self):
        pm = PackageManager()
        pm.register_package("urllib3", "1.26.0", [])
        pm.register_package("requests", "2.28.0", ["urllib3"])
        pm.install("requests", "2.28.0")

        # Uninstall requests first
        success, error = pm.uninstall("requests")
        assert success is True

        # Now can uninstall urllib3
        success, error = pm.uninstall("urllib3")
        assert success is True

    def test_nested_deps(self):
        pm = PackageManager()
        pm.register_package("base", "1.0.0", [])
        pm.register_package("middle", "1.0.0", ["base"])
        pm.register_package("top", "1.0.0", ["middle"])

        installed = pm.install("top", "1.0.0")
        assert installed == ["base", "middle", "top"]

    def test_shared_deps(self):
        pm = PackageManager()
        pm.register_package("common", "1.0.0", [])
        pm.register_package("pkg1", "1.0.0", ["common"])
        pm.register_package("pkg2", "1.0.0", ["common"])

        pm.install("pkg1", "1.0.0")
        installed = pm.install("pkg2", "1.0.0")
        # common already installed
        assert installed == ["pkg2"]

    def test_get_dependents(self):
        pm = PackageManager()
        pm.register_package("base", "1.0.0", [])
        pm.register_package("pkg1", "1.0.0", ["base"])
        pm.register_package("pkg2", "1.0.0", ["base"])
        pm.install("pkg1", "1.0.0")
        pm.install("pkg2", "1.0.0")

        dependents = pm.get_dependents("base")
        assert sorted(dependents) == ["pkg1", "pkg2"]

    def test_get_dependencies(self):
        pm = PackageManager()
        pm.register_package("requests", "2.28.0", ["urllib3", "certifi"])

        deps = pm.get_dependencies("requests")
        assert set(deps) == {"urllib3", "certifi"}
