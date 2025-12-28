"""Tests for Package Manager Stage 4 - Conflict Detection"""
import pytest
from solution import PackageManager, Conflict


class TestPackageManagerStage4:
    def test_no_conflicts(self):
        pm = PackageManager()
        pm.register_package("base", ["1.0.0", "2.0.0"])
        pm.register_package("pkg1", ["1.0.0"], {"1.0.0": [("base", ">=1.0.0")]})
        pm.register_package("pkg2", ["1.0.0"], {"1.0.0": [("base", ">=1.0.0")]})
        pm.register_package("app", ["1.0.0"], {
            "1.0.0": [("pkg1", ">=1.0.0"), ("pkg2", ">=1.0.0")]
        })

        success, installed, conflicts = pm.install("app")
        assert success is True
        assert len(conflicts) == 0
        assert "base==2.0.0" in installed

    def test_detect_conflict(self):
        pm = PackageManager()
        pm.register_package("base", ["1.0.0", "2.0.0"])
        pm.register_package("pkg1", ["1.0.0"], {"1.0.0": [("base", "==1.0.0")]})
        pm.register_package("pkg2", ["1.0.0"], {"1.0.0": [("base", "==2.0.0")]})
        pm.register_package("app", ["1.0.0"], {
            "1.0.0": [("pkg1", ">=1.0.0"), ("pkg2", ">=1.0.0")]
        })

        success, installed, conflicts = pm.install("app", resolve_conflicts=False)
        assert success is False
        assert len(conflicts) == 1
        assert conflicts[0].package == "base"

    def test_resolve_conflict_with_compatible_version(self):
        pm = PackageManager()
        pm.register_package("base", ["1.0.0", "1.5.0", "2.0.0"])
        pm.register_package("pkg1", ["1.0.0"], {"1.0.0": [("base", ">=1.0.0")]})
        pm.register_package("pkg2", ["1.0.0"], {"1.0.0": [("base", "<=1.5.0")]})
        pm.register_package("app", ["1.0.0"], {
            "1.0.0": [("pkg1", ">=1.0.0"), ("pkg2", ">=1.0.0")]
        })

        success, installed, conflicts = pm.install("app")
        assert success is True
        assert pm.get_version("base") == "1.5.0"

    def test_generate_lockfile(self):
        pm = PackageManager()
        pm.register_package("urllib3", ["1.26.0"])
        pm.register_package("requests", ["2.28.0"], {
            "2.28.0": [("urllib3", ">=1.26.0")]
        })

        pm.install("requests")
        lockfile = pm.generate_lockfile()

        assert lockfile == {"requests": "2.28.0", "urllib3": "1.26.0"}

    def test_install_from_lockfile(self):
        pm = PackageManager()
        pm.register_package("requests", ["2.27.0", "2.28.0"])
        pm.register_package("urllib3", ["1.25.0", "1.26.0"])

        lockfile = {"requests": "2.27.0", "urllib3": "1.25.0"}
        pm.install_from_lockfile(lockfile)

        assert pm.get_version("requests") == "2.27.0"
        assert pm.get_version("urllib3") == "1.25.0"

    def test_complex_dependency_tree(self):
        pm = PackageManager()
        pm.register_package("a", ["1.0.0"])
        pm.register_package("b", ["1.0.0"], {"1.0.0": [("a", ">=1.0.0")]})
        pm.register_package("c", ["1.0.0"], {"1.0.0": [("a", ">=1.0.0")]})
        pm.register_package("d", ["1.0.0"], {
            "1.0.0": [("b", ">=1.0.0"), ("c", ">=1.0.0")]
        })

        success, installed, conflicts = pm.install("d")
        assert success is True
        # a should only be installed once
        assert installed.count("a==1.0.0") == 1

    def test_unresolvable_conflict(self):
        pm = PackageManager()
        pm.register_package("base", ["1.0.0"])
        pm.register_package("pkg1", ["1.0.0"], {"1.0.0": [("base", "==1.0.0")]})
        pm.register_package("pkg2", ["1.0.0"], {"1.0.0": [("base", ">=2.0.0")]})
        pm.register_package("app", ["1.0.0"], {
            "1.0.0": [("pkg1", ">=1.0.0"), ("pkg2", ">=1.0.0")]
        })

        success, installed, conflicts = pm.install("app")
        # Should fail because no version of base satisfies both constraints
        assert success is False
