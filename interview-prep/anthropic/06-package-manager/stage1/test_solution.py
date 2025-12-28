"""Tests for Package Manager Stage 1"""
import pytest
from solution import PackageManager


class TestPackageManagerStage1:
    def test_install(self):
        pm = PackageManager()
        assert pm.install("requests", "2.28.0") is True
        assert pm.is_installed("requests") is True

    def test_install_duplicate(self):
        pm = PackageManager()
        pm.install("requests", "2.28.0")
        assert pm.install("requests", "2.28.0") is False

    def test_install_different_version(self):
        pm = PackageManager()
        pm.install("requests", "2.28.0")
        assert pm.install("requests", "2.29.0") is True
        assert pm.get_version("requests") == "2.29.0"

    def test_uninstall(self):
        pm = PackageManager()
        pm.install("requests", "2.28.0")
        assert pm.uninstall("requests") is True
        assert pm.is_installed("requests") is False

    def test_uninstall_not_installed(self):
        pm = PackageManager()
        assert pm.uninstall("requests") is False

    def test_get_version(self):
        pm = PackageManager()
        pm.install("flask", "2.0.0")
        assert pm.get_version("flask") == "2.0.0"
        assert pm.get_version("missing") is None

    def test_list_packages(self):
        pm = PackageManager()
        pm.install("requests", "2.28.0")
        pm.install("flask", "2.0.0")
        pm.install("django", "4.0.0")

        packages = pm.list_packages()
        assert packages == [
            ("django", "4.0.0"),
            ("flask", "2.0.0"),
            ("requests", "2.28.0")
        ]

    def test_upgrade(self):
        pm = PackageManager()
        pm.install("requests", "2.28.0")
        assert pm.upgrade("requests", "2.29.0") is True
        assert pm.get_version("requests") == "2.29.0"

    def test_upgrade_not_installed(self):
        pm = PackageManager()
        assert pm.upgrade("requests", "2.29.0") is False
