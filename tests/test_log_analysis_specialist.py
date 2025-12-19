"""Tests for Log Analysis specialist."""

import pytest
from brain.specialists.log_analysis_specialist import LogAnalysisSpecialist


@pytest.fixture
def specialist():
    """Create LogAnalysisSpecialist instance."""
    return LogAnalysisSpecialist()


@pytest.fixture
def minecraft_crash_log():
    """Sample Minecraft crash log."""
    return """
    ---- Minecraft Crash Report ----
    Time: 2024-12-18
    Description: Mixin error

    java.lang.RuntimeException: MixinTransformerError
    at net.optifine.shaders.Shaders.startup
    at me.jellysquid.mods.sodium.mixin.core.render

    Fabric Mods:
        optifine: OptiFine HD U I5
        sodium: Sodium 0.5.8
    """


def test_specialist_exists(specialist):
    """LogAnalysisSpecialist should exist and have capability."""
    assert specialist is not None
    assert specialist.capability is not None
    assert specialist.capability.name == "log_analysis"


def test_should_activate_on_log_filename(specialist):
    """Should activate when filename ends with .log."""
    context = {'filename': 'crash-2024-12-18.log'}
    assert specialist.should_activate(context) is True


def test_should_not_activate_on_non_log_file(specialist):
    """Should not activate for non-.log files."""
    context = {'filename': 'notes.txt'}
    assert specialist.should_activate(context) is False


def test_should_activate_with_flag(specialist):
    """Should activate when analyze_logs flag is set."""
    context = {'analyze_logs': True}
    assert specialist.should_activate(context) is True


def test_process_minecraft_crash(specialist, minecraft_crash_log):
    """Should process Minecraft crash log and return analysis."""
    result = specialist.process(
        file_content=minecraft_crash_log,
        filename='crash.log'
    )

    assert result.success is True
    assert 'LOG ANALYSIS' in result.context_text.upper()
    assert result.data is not None
    assert 'error_type' in result.data


def test_process_includes_kid_friendly_explanation(specialist, minecraft_crash_log):
    """Should include kid-friendly explanation in context."""
    result = specialist.process(
        file_content=minecraft_crash_log,
        filename='crash.log'
    )

    assert result.success is True
    # Should have kid-friendly language
    context_lower = result.context_text.lower()
    assert any(word in context_lower for word in ['fighting', 'mods', 'optifine', 'sodium'])


def test_process_empty_log_returns_error(specialist):
    """Should return error for empty log content."""
    result = specialist.process(
        file_content='',
        filename='crash.log'
    )

    assert result.success is False
    assert 'error' in result.error_code.lower() or 'empty' in result.error_code.lower()


def test_process_unsupported_format_returns_error(specialist):
    """Should return error for unsupported log format."""
    result = specialist.process(
        file_content='This is not a log file\njust some random text',
        filename='random.log'
    )

    assert result.success is False


def test_result_metadata_includes_error_type(specialist, minecraft_crash_log):
    """Result metadata should include error type."""
    result = specialist.process(
        file_content=minecraft_crash_log,
        filename='crash.log'
    )

    assert result.success is True
    assert 'error_type' in result.metadata


def test_capability_has_correct_priority(specialist):
    """Specialist should have MEDIUM priority."""
    from brain.specialists.protocol import SpecialistPriority

    assert specialist.capability.context_priority == SpecialistPriority.MEDIUM


def test_capability_has_correct_tags(specialist):
    """Specialist should have appropriate tags."""
    tags = specialist.capability.tags

    assert 'logs' in tags
    assert 'analysis' in tags
