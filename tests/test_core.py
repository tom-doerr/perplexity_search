import pytest
from plexsearch import __version__
from toml import load

def test_version_matches_pyproject():
    with open("pyproject.toml", "r") as f:
        pyproject = load(f)
    assert __version__ == pyproject["tool"]["poetry"]["version"]

def test_version_matches_changelog():
    with open("CHANGELOG.md", "r") as f:
        changelog = f.read()
    assert f"## [{__version__}]" in changelog
