"""Command-line interface for ada-logs.

Provides commands for analyzing and compressing log files.
"""

import json
import sys
from pathlib import Path
from typing import Optional

import click

from ada_logs import __version__
from ada_logs.parsers.minecraft import MinecraftParser
from ada_logs.core import LogAnalysis


@click.group()
@click.version_option(version=__version__, prog_name='ada-logs')
def cli():
    """Ada Log Intelligence - Understand your logs! 📊

    Built for kids troubleshooting Minecraft AND DevOps analyzing production logs.
    Uses biomimetic importance scoring from Ada's cognitive architecture.
    """
    pass


@cli.command()
@click.argument('log_file', type=click.Path(exists=True, path_type=Path))
@click.option('--format', default='auto',
              help='Log format (minecraft, syslog, auto)')
@click.option('--for-kids', is_flag=True,
              help='Use kid-friendly explanations (recommended!)')
@click.option('--json', 'output_json', is_flag=True,
              help='Output as JSON instead of human-readable text')
def analyze(log_file: Path, format: str, for_kids: bool, output_json: bool):
    """Analyze a log file and explain errors.

    Examples:

        \b
        # Analyze a Minecraft crash
        ada-logs analyze crash.log --for-kids

        \b
        # Get JSON output for scripting
        ada-logs analyze crash.log --json
    """
    try:
        # Read log file
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            log_content = f.read()

        # Detect format if auto
        if format == 'auto':
            parser = _detect_parser(log_content)
            if parser is None:
                click.echo("❌ Could not detect log format. Try specifying --format", err=True)
                sys.exit(1)
        elif format == 'minecraft':
            parser = MinecraftParser()
        else:
            click.echo(f"❌ Unsupported format: {format}", err=True)
            sys.exit(1)

        # Parse log
        analysis = parser.parse(log_content)

        # Output
        if output_json:
            click.echo(json.dumps(analysis.to_dict(), indent=2))
        else:
            _print_analysis(analysis, for_kids=for_kids)

    except FileNotFoundError:
        click.echo(f"❌ File not found: {log_file}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error analyzing log: {e}", err=True)
        sys.exit(1)


def _detect_parser(log_content: str) -> Optional[object]:
    """Auto-detect which parser to use.

    Args:
        log_content: Raw log content

    Returns:
        Parser instance or None if no match
    """
    # Try Minecraft first (most common for our use case)
    minecraft_parser = MinecraftParser()
    if minecraft_parser.detect_format(log_content):
        return minecraft_parser

    # TODO: Add syslog, JSON, etc.

    return None


def _print_analysis(analysis: LogAnalysis, for_kids: bool = False):
    """Print analysis in human-readable format.

    Args:
        analysis: LogAnalysis result
        for_kids: Whether to emphasize kid-friendly language
    """
    # Header
    click.echo()
    click.secho("🔍 LOG ANALYSIS", bold=True, fg='cyan')
    click.echo("=" * 60)
    click.echo()

    # Error type
    click.secho(f"Error Type: ", bold=True, nl=False)
    click.echo(analysis.error_type.replace('_', ' ').title())

    # Confidence
    confidence_color = 'green' if analysis.confidence > 0.8 else 'yellow'
    click.secho(f"Confidence: ", bold=True, nl=False)
    click.secho(f"{analysis.confidence:.0%}", fg=confidence_color)

    # Difficulty
    difficulty_emoji = {
        'easy': '✅',
        'medium': '⚠️',
        'hard': '🔴'
    }
    emoji = difficulty_emoji.get(analysis.difficulty, '❓')
    click.secho(f"Difficulty: ", bold=True, nl=False)
    click.echo(f"{emoji} {analysis.difficulty.title()}")

    click.echo()

    # Explanation
    click.secho("What Happened:", bold=True, fg='yellow')
    click.echo(analysis.kid_explanation)
    click.echo()

    # Fix
    click.secho("How to Fix:", bold=True, fg='green')
    click.echo(analysis.fix)
    click.echo()

    # Conflicting mods (if any)
    if analysis.conflicting_mods:
        click.secho("Mods Involved:", bold=True, fg='magenta')
        for mod in analysis.conflicting_mods[:5]:  # Show max 5
            click.echo(f"  • {mod}")
        if len(analysis.conflicting_mods) > 5:
            click.echo(f"  ... and {len(analysis.conflicting_mods) - 5} more")
        click.echo()

    # Footer
    click.echo("=" * 60)
    if for_kids:
        click.secho("💚 Don't worry - crashes happen! You've got this!", fg='green')
    else:
        click.secho("💚 Analysis complete", fg='green')
    click.echo()


@cli.command()
@click.argument('log_file', type=click.Path(exists=True, path_type=Path))
@click.option('--ratio', default=100, type=int,
              help='Target compression ratio (default: 100:1)')
@click.option('--output', '-o', type=click.Path(path_type=Path),
              help='Output file (default: stdout)')
def compress(log_file: Path, ratio: int, output: Optional[Path]):
    """Compress a log file using biomimetic importance scoring.

    Preserves all errors while compressing info/debug logs.

    Examples:

        \b
        # Compress to 100:1 ratio
        ada-logs compress app.log --ratio 100 > compressed.log

        \b
        # Compress to file
        ada-logs compress app.log -o compressed.log
    """
    click.echo("🚧 Compression coming in Phase 2!")
    click.echo("For now, try 'ada-logs analyze' to understand your logs.")
    sys.exit(0)


if __name__ == '__main__':
    cli()
