"""Tests for CLI interface."""

import pytest
from click.testing import CliRunner
from pathlib import Path


def test_cli_imports():
    """CLI module should import without errors."""
    from ada_logs.cli import cli
    assert cli is not None


def test_cli_analyze_command_exists():
    """Analyze command should exist."""
    from ada_logs.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])

    assert result.exit_code == 0
    assert 'analyze' in result.output


def test_cli_analyze_minecraft_crash(minecraft_fixtures_dir):
    """Should analyze a Minecraft crash log."""
    from ada_logs.cli import cli

    crash_log = minecraft_fixtures_dir / "crash_optifine_sodium.log"

    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', str(crash_log)])

    assert result.exit_code == 0
    assert 'OptiFine' in result.output or 'Sodium' in result.output


def test_cli_analyze_with_for_kids_flag(minecraft_fixtures_dir):
    """Should use kid-friendly explanations with --for-kids flag."""
    from ada_logs.cli import cli

    crash_log = minecraft_fixtures_dir / "crash_optifine_sodium.log"

    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', str(crash_log), '--for-kids'])

    assert result.exit_code == 0
    # Should have kid-friendly language
    assert 'fighting' in result.output.lower() or 'work together' in result.output.lower()


def test_cli_analyze_out_of_memory(minecraft_fixtures_dir):
    """Should analyze OutOfMemoryError crash."""
    from ada_logs.cli import cli

    crash_log = minecraft_fixtures_dir / "crash_out_of_memory.log"

    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', str(crash_log), '--for-kids'])

    assert result.exit_code == 0
    assert 'memory' in result.output.lower() or 'RAM' in result.output.upper()


def test_cli_analyze_nonexistent_file():
    """Should handle nonexistent file gracefully."""
    from ada_logs.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', '/tmp/nonexistent.log'])

    assert result.exit_code != 0


def test_cli_analyze_json_output(minecraft_fixtures_dir):
    """Should support JSON output format."""
    from ada_logs.cli import cli

    crash_log = minecraft_fixtures_dir / "crash_optifine_sodium.log"

    runner = CliRunner()
    result = runner.invoke(cli, ['analyze', str(crash_log), '--json'])

    assert result.exit_code == 0
    # Should be valid JSON
    import json
    data = json.loads(result.output)
    assert 'error_type' in data
    assert 'confidence' in data


def test_cli_version():
    """Should show version."""
    from ada_logs.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])

    assert result.exit_code == 0
    assert '0.1.0' in result.output
