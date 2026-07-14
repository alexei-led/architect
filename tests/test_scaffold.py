"""Scaffold smoke tests: package imports and expected source layout exists."""

from pathlib import Path

import architect_tools

REPO_ROOT = Path(__file__).resolve().parent.parent

EXPECTED_SOURCE_DIRS = [
    "src/agents",
    "src/skills",
    "src/resources/templates",
    "src/architect_tools",
    "src/packages",
    "tests",
]


def test_package_imports():
    assert architect_tools.__version__


def test_expected_source_dirs_exist():
    missing = [d for d in EXPECTED_SOURCE_DIRS if not (REPO_ROOT / d).is_dir()]
    assert not missing, f"missing source dirs: {missing}"
