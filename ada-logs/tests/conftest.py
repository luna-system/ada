"""Pytest configuration and shared fixtures for ada-logs tests."""

import pytest
from pathlib import Path


@pytest.fixture
def fixtures_dir():
    """Path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def minecraft_fixtures_dir(fixtures_dir):
    """Path to Minecraft test fixtures."""
    return fixtures_dir / "minecraft"
