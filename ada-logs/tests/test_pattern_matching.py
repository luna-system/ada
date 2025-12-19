"""Tests for pattern matching engine."""

import pytest
from ada_logs.patterns.matcher import PatternMatcher


def test_pattern_matcher_loads_patterns():
    """PatternMatcher should load patterns from JSON."""
    matcher = PatternMatcher()
    assert len(matcher.patterns) > 0


def test_match_optifine_sodium():
    """Should match OptiFine + Sodium conflict pattern."""
    matcher = PatternMatcher()

    log_content = """
    Caused by: MixinTransformerError
    at optifine.shaders.Shaders.startup
    at me.jellysquid.mods.sodium.mixin.core.render
    """

    matches = matcher.match(log_content)

    assert len(matches) > 0
    # Should match optifine_sodium_conflict pattern
    assert any(m['id'] == 'optifine_sodium_conflict' for m in matches)


def test_match_out_of_memory():
    """Should match OutOfMemoryError pattern."""
    matcher = PatternMatcher()

    log_content = "java.lang.OutOfMemoryError: Java heap space"

    matches = matcher.match(log_content)

    assert len(matches) > 0
    assert any(m['id'] == 'out_of_memory' for m in matches)


def test_match_returns_pattern_data():
    """Match should return full pattern data."""
    matcher = PatternMatcher()

    log_content = "OutOfMemoryError"
    matches = matcher.match(log_content)

    assert len(matches) > 0
    match = matches[0]

    # Should include all pattern fields
    assert 'id' in match
    assert 'error_type' in match
    assert 'kid_explanation' in match
    assert 'fix' in match
    assert 'difficulty' in match
    assert 'confidence_boost' in match


def test_multiple_pattern_matches():
    """Should return all matching patterns."""
    matcher = PatternMatcher()

    # Log with both OOM and mixin error
    log_content = """
    OutOfMemoryError: Java heap space
    MixinTransformerError
    """

    matches = matcher.match(log_content)

    # Should match multiple patterns
    assert len(matches) >= 2


def test_best_match():
    """Should return the best (highest confidence) match."""
    matcher = PatternMatcher()

    log_content = "OutOfMemoryError: Java heap space"

    best = matcher.best_match(log_content)

    assert best is not None
    assert best['id'] == 'out_of_memory'
    assert best['confidence_boost'] > 0.9


def test_no_matches():
    """Should return empty list when no patterns match."""
    matcher = PatternMatcher()

    log_content = "This is not a Minecraft crash log"

    matches = matcher.match(log_content)

    assert matches == []


def test_best_match_none_when_no_matches():
    """best_match should return None when nothing matches."""
    matcher = PatternMatcher()

    log_content = "Not a crash log"

    best = matcher.best_match(log_content)

    assert best is None


def test_case_insensitive_matching():
    """Pattern matching should be case-insensitive."""
    matcher = PatternMatcher()

    # Test with different cases
    log_lower = "outofmemoryerror"
    log_upper = "OUTOFMEMORYERROR"
    log_mixed = "OutOfMemoryError"

    assert len(matcher.match(log_lower)) > 0
    assert len(matcher.match(log_upper)) > 0
    assert len(matcher.match(log_mixed)) > 0
