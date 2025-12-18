"""Phase 0: Test Infrastructure for Tool Awareness Framework.

These tests are written FIRST (TDD) and will initially FAIL.
They define the behavior we want before implementing it.
"""

import pytest
from pathlib import Path


def test_pattern_matcher_initialization():
    """Pattern matcher loads with empty patterns by default."""
    from brain.specialists.tool_activation import ToolPatternMatcher
    
    matcher = ToolPatternMatcher()
    assert matcher.patterns == []
    assert matcher.ready() == False


def test_pattern_matcher_loads_from_file():
    """Pattern matcher can load patterns from JSON."""
    from brain.specialists.tool_activation import ToolPatternMatcher
    
    fixture_path = Path(__file__).parent / "fixtures" / "tool_patterns.json"
    matcher = ToolPatternMatcher(patterns_file=str(fixture_path))
    
    assert len(matcher.patterns) > 0
    assert matcher.ready() == True


def test_simple_codebase_pattern_matching():
    """Detect codebase lookup intent from human language."""
    from brain.specialists.tool_activation import ToolPatternMatcher
    
    fixture_path = Path(__file__).parent / "fixtures" / "tool_patterns.json"
    matcher = ToolPatternMatcher(patterns_file=str(fixture_path))
    
    query = "How does calculate_importance work?"
    matches = matcher.match(query)
    
    assert len(matches) > 0
    assert matches[0].tool_name == "codebase"
    assert "calculate_importance" in matches[0].extracted_params["query"]


def test_pattern_confidence_scoring():
    """Patterns have confidence scores for ambiguous cases."""
    from brain.specialists.tool_activation import ToolPatternMatcher
    
    fixture_path = Path(__file__).parent / "fixtures" / "tool_patterns.json"
    matcher = ToolPatternMatcher(patterns_file=str(fixture_path))
    
    # Ambiguous - lookup or discussion?
    query = "calculate_importance"
    matches = matcher.match(query)
    
    # Should either not match or have low confidence
    assert len(matches) == 0 or matches[0].confidence < 0.8
    
    # Clear intent
    query = "Show me the code for calculate_importance"
    matches = matcher.match(query)
    
    assert len(matches) > 0
    assert matches[0].confidence > 0.8


def test_no_false_positives():
    """Don't activate tools when NOT appropriate."""
    from brain.specialists.tool_activation import ToolPatternMatcher
    
    fixture_path = Path(__file__).parent / "fixtures" / "tool_patterns.json"
    matcher = ToolPatternMatcher(patterns_file=str(fixture_path))
    
    # Discussion, not lookup
    query = "I think the importance calculation is interesting"
    matches = matcher.match(query)
    
    assert len(matches) == 0 or matches[0].confidence < 0.5
