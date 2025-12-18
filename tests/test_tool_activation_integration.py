"""Phase 3: Integration with Streaming Endpoint.

Tests for pre-execution tool activation in the chat endpoint.
"""

import pytest
from pathlib import Path

# Mark all async tests
pytestmark = pytest.mark.anyio


def test_pattern_matcher_initialization_in_app():
    """Pattern matcher loads at app startup."""
    # This will test that tool_matcher is initialized in app.py
    from brain.app import tool_matcher
    
    assert tool_matcher is not None
    assert tool_matcher.ready() == True
    assert len(tool_matcher.patterns) > 0


async def test_pre_execution_tool_matching():
    """Tools are matched BEFORE LLM execution."""
    from brain.specialists.tool_activation import ToolPatternMatcher
    
    pattern_file = Path(__file__).parent.parent / "data" / "tool_patterns.json"
    matcher = ToolPatternMatcher(patterns_file=str(pattern_file))
    
    # Simulate what happens in chat_stream_v1
    user_message = "How does calculate_importance work?"
    
    # PRE-EXECUTION: Pattern matching happens first
    matches = matcher.match(user_message)
    
    assert len(matches) > 0
    assert matches[0].tool_name == "codebase"
    assert matches[0].confidence >= 0.5


async def test_specialist_result_format():
    """Specialist results have correct format for prompt injection."""
    from brain.specialists.tool_activation import ToolPatternMatcher
    
    pattern_file = Path(__file__).parent.parent / "data" / "tool_patterns.json"
    matcher = ToolPatternMatcher(patterns_file=str(pattern_file))
    
    query = "Show me the ContextRetriever code"
    matches = matcher.match(query)
    
    # Create specialist result structure
    specialist_result = {
        "specialist": matches[0].tool_name,
        "confidence": matches[0].confidence,
        "params": matches[0].extracted_params,
        "result": "[Mock code result]"
    }
    
    # Verify structure
    assert "specialist" in specialist_result
    assert "confidence" in specialist_result
    assert "params" in specialist_result
    assert "result" in specialist_result
    assert specialist_result["specialist"] == "codebase"


async def test_high_confidence_threshold():
    """Only high-confidence matches trigger pre-execution."""
    from brain.specialists.tool_activation import ToolPatternMatcher
    
    pattern_file = Path(__file__).parent.parent / "data" / "tool_patterns.json"
    matcher = ToolPatternMatcher(patterns_file=str(pattern_file))
    
    CONFIDENCE_THRESHOLD = 0.5
    
    # High confidence query
    high_confidence_query = "Show me the calculate_importance function"
    matches = matcher.match(high_confidence_query)
    assert len(matches) > 0
    assert matches[0].confidence >= CONFIDENCE_THRESHOLD
    
    # Low confidence query (ambiguous)
    low_confidence_query = "calculate"
    matches = matcher.match(low_confidence_query)
    # Should either not match or be below threshold
    if len(matches) > 0:
        assert matches[0].confidence < CONFIDENCE_THRESHOLD


async def test_multiple_specialist_activation():
    """Multiple specialists can activate for one query."""
    from brain.specialists.tool_activation import ToolPatternMatcher
    
    pattern_file = Path(__file__).parent.parent / "data" / "tool_patterns.json"
    matcher = ToolPatternMatcher(patterns_file=str(pattern_file))
    
    # Query that could match multiple patterns
    query = "Search the web for information about ContextRetriever class"
    matches = matcher.match(query)
    
    # Should get matches (web_search likely to win)
    assert len(matches) > 0
    
    # Highest confidence should be first
    if len(matches) > 1:
        assert matches[0].confidence >= matches[1].confidence


def test_no_activation_for_conversational():
    """Conversational queries don't activate tools unnecessarily."""
    from brain.specialists.tool_activation import ToolPatternMatcher
    
    pattern_file = Path(__file__).parent.parent / "data" / "tool_patterns.json"
    matcher = ToolPatternMatcher(patterns_file=str(pattern_file))
    
    CONFIDENCE_THRESHOLD = 0.5
    
    conversational_queries = [
        "That makes sense, thanks!",
        "I understand now",
        "You're really helpful",
        "How are you?",
    ]
    
    for query in conversational_queries:
        matches = matcher.match(query)
        # Should either not match or be very low confidence
        if len(matches) > 0:
            assert matches[0].confidence < CONFIDENCE_THRESHOLD, \
                f"False positive: '{query}' matched with confidence {matches[0].confidence}"
