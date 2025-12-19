"""Tests for LogParser protocol."""

import pytest
from ada_logs.parsers.protocol import LogParser
from ada_logs.core import LogAnalysis


def test_log_parser_is_protocol():
    """LogParser should be a Protocol (structural typing)."""
    from typing import Protocol, runtime_checkable

    assert issubclass(LogParser.__class__, type(Protocol))


def test_log_parser_has_required_methods():
    """LogParser protocol should define parse() and detect_format()."""
    # This will be satisfied once we have an implementation
    # For now, just check the protocol exists
    assert hasattr(LogParser, 'parse')
    assert hasattr(LogParser, 'detect_format')


def test_minecraft_parser_implements_protocol():
    """MinecraftParser should implement LogParser protocol."""
    # Import will fail until we implement MinecraftParser
    # This test drives the implementation
    try:
        from ada_logs.parsers.minecraft import MinecraftParser
        parser = MinecraftParser()
        assert isinstance(parser, LogParser)
        assert hasattr(parser, 'parse')
        assert hasattr(parser, 'detect_format')
    except ImportError:
        pytest.skip("MinecraftParser not implemented yet")
