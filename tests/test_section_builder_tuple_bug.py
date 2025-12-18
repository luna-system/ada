"""
Test for bug: section_builder expects dicts but retrieve_turns returns tuples.

Bug discovered: 2025-12-18
Context: After refactoring retrieve methods to return (text, metadata) tuples,
section_builder.format_conversation_history still expects dict objects.

TDD Approach:
1. Write test that reproduces the bug
2. Verify it fails
3. Fix section_builder to handle tuples
4. Verify test passes
"""

import pytest
from brain.prompt_builder.section_builder import SectionBuilder


def test_format_conversation_history_handles_tuples():
    """
    Test that format_conversation_history can handle (text, metadata) tuples
    from retrieve_turns() instead of just dicts.
    
    This is the actual return format from retrieve_turns after refactoring.
    """
    builder = SectionBuilder()
    
    # This is what retrieve_turns() actually returns now
    turns_as_tuples = [
        ("Hello Ada!", {"role": "user", "timestamp": "2025-12-18T10:00:00Z"}),
        ("Hi! How can I help?", {"role": "assistant", "timestamp": "2025-12-18T10:00:05Z"}),
        ("What's Python?", {"role": "user", "timestamp": "2025-12-18T10:01:00Z"}),
    ]
    
    # This should not crash with AttributeError: 'tuple' object has no attribute 'get'
    result = builder.format_conversation_history(turns_as_tuples)
    
    # Verify it formatted correctly
    assert "User: Hello Ada!" in result
    assert "Ada: Hi! How can I help?" in result
    assert "User: What's Python?" in result


def test_format_conversation_history_handles_dicts_for_backwards_compat():
    """
    Test that format_conversation_history still works with dicts
    for backwards compatibility.
    """
    builder = SectionBuilder()
    
    # Old format (dicts)
    turns_as_dicts = [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi!"},
    ]
    
    result = builder.format_conversation_history(turns_as_dicts)
    
    assert "User: Hello!" in result
    assert "Ada: Hi!" in result


def test_format_conversation_history_handles_empty_list():
    """Test that empty list returns appropriate message."""
    builder = SectionBuilder()
    
    result = builder.format_conversation_history([])
    
    assert "None (start of conversation)" in result


def test_format_conversation_history_handles_missing_role():
    """Test graceful handling of missing role in metadata."""
    builder = SectionBuilder()
    
    # Tuple with missing role
    turns = [
        ("Some message", {"timestamp": "2025-12-18T10:00:00Z"}),
    ]
    
    result = builder.format_conversation_history(turns)
    
    # Should default to "unknown" role which maps to "Ada"
    assert "Ada: Some message" in result
