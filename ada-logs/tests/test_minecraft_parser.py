"""Tests for Minecraft log parser."""

import pytest
from ada_logs.parsers.minecraft import MinecraftParser
from ada_logs.core import LogAnalysis


@pytest.fixture
def optifine_crash(minecraft_fixtures_dir):
    """Load OptiFine + Sodium conflict crash log."""
    return (minecraft_fixtures_dir / "crash_optifine_sodium.log").read_text()


@pytest.fixture
def out_of_memory_crash(minecraft_fixtures_dir):
    """Load OutOfMemoryError crash log."""
    return (minecraft_fixtures_dir / "crash_out_of_memory.log").read_text()


def test_minecraft_parser_exists():
    """MinecraftParser class should exist."""
    parser = MinecraftParser()
    assert parser is not None


def test_detect_minecraft_format(optifine_crash):
    """Should detect Minecraft crash report format."""
    parser = MinecraftParser()
    assert parser.detect_format(optifine_crash) is True


def test_detect_non_minecraft_format():
    """Should reject non-Minecraft logs."""
    parser = MinecraftParser()
    random_log = "2024-12-18 ERROR: Some random error\nNot a Minecraft crash"
    assert parser.detect_format(random_log) is False


def test_parse_optifine_sodium_conflict(optifine_crash):
    """Detect OptiFine + Sodium mod conflict."""
    parser = MinecraftParser()
    analysis = parser.parse(optifine_crash)

    assert isinstance(analysis, LogAnalysis)
    assert analysis.error_type == 'mod_conflict'
    assert 'OptiFine' in analysis.conflicting_mods or 'optifine' in str(analysis.conflicting_mods).lower()
    assert 'Sodium' in analysis.conflicting_mods or 'sodium' in str(analysis.conflicting_mods).lower()
    assert analysis.confidence > 0.7
    assert len(analysis.kid_explanation) > 0
    assert len(analysis.fix) > 0


def test_parse_out_of_memory(out_of_memory_crash):
    """Detect OutOfMemoryError."""
    parser = MinecraftParser()
    analysis = parser.parse(out_of_memory_crash)

    assert isinstance(analysis, LogAnalysis)
    assert analysis.error_type == 'out_of_memory'
    assert analysis.confidence > 0.9  # Very confident on OOM
    assert 'memory' in analysis.kid_explanation.lower() or 'ram' in analysis.kid_explanation.lower()
    assert analysis.difficulty in ['easy', 'medium', 'hard']


def test_parse_returns_valid_confidence():
    """Confidence should be between 0 and 1."""
    parser = MinecraftParser()
    crash_log = """
    ---- Minecraft Crash Report ----
    Time: 2024-12-18
    Description: Test

    java.lang.OutOfMemoryError: Java heap space
    """

    analysis = parser.parse(crash_log)
    assert 0.0 <= analysis.confidence <= 1.0


def test_parse_includes_actionable_fix(optifine_crash):
    """Fix should include actionable steps."""
    parser = MinecraftParser()
    analysis = parser.parse(optifine_crash)

    fix_lower = analysis.fix.lower()
    # Should mention removing/deleting a mod
    assert any(word in fix_lower for word in ['remove', 'delete', 'uninstall', 'disable'])


def test_kid_explanation_is_kid_friendly(out_of_memory_crash):
    """Kid explanation should avoid technical jargon."""
    parser = MinecraftParser()
    analysis = parser.parse(out_of_memory_crash)

    explanation_lower = analysis.kid_explanation.lower()

    # Should NOT use super technical terms
    technical_jargon = ['heap space', 'bytebuffer', 'jvm', 'stack trace']
    for jargon in technical_jargon:
        assert jargon not in explanation_lower

    # Should use kid-friendly language
    assert len(analysis.kid_explanation) > 20  # Not too short
    assert len(analysis.kid_explanation) < 500  # Not too long


def test_analysis_to_dict():
    """LogAnalysis should convert to dictionary."""
    parser = MinecraftParser()
    crash_log = """
    ---- Minecraft Crash Report ----
    java.lang.OutOfMemoryError: Java heap space
    """

    analysis = parser.parse(crash_log)
    result = analysis.to_dict()

    assert isinstance(result, dict)
    assert 'error_type' in result
    assert 'confidence' in result
    assert 'kid_explanation' in result
    assert 'fix' in result
