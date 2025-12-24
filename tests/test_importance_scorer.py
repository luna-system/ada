"""Tests for importance_scorer.py - Biomimetic scoring for tool results."""

import pytest
from brain.reasoning.importance_scorer import (
    ToolResultScorer,
    DetailLevel,
    ScoredResult,
)


def test_scorer_initialization():
    """Test scorer initializes with query context."""
    scorer = ToolResultScorer(query="authentication logic")
    
    assert "authentication" in scorer.query_keywords
    assert "logic" in scorer.query_keywords
    assert scorer.weights['surprise'] == 0.60
    assert scorer.weights['relevance'] == 0.20


def test_calculate_surprise_new_content():
    """Test surprise score for novel content."""
    scorer = ToolResultScorer(query="test")
    
    code_content = """
    async def authenticate(token: str):
        jwt.decode(token, secret_key)
        return user_id
    """
    
    surprise = scorer.calculate_surprise(code_content)
    
    # New content should have high surprise
    assert 0.6 < surprise <= 1.0


def test_calculate_surprise_repeated_content():
    """Test habituation reduces surprise for repeated patterns."""
    scorer = ToolResultScorer(query="test")
    
    content = "some repeated content"
    
    # First time
    surprise1 = scorer.calculate_surprise(content)
    
    # Second time (pattern now in seen_patterns)
    surprise2 = scorer.calculate_surprise(content)
    
    # Second time should have lower surprise
    assert surprise2 < surprise1


def test_calculate_relevance_keyword_match():
    """Test relevance scoring with keyword matches."""
    scorer = ToolResultScorer(query="authentication jwt")
    
    relevant_content = """
    import jwt
    
    def authenticate_user(token):
        # JWT authentication logic
        decoded = jwt.decode(token)
        return decoded['user_id']
    """
    
    relevance = scorer.calculate_relevance(relevant_content)
    
    # Should have high relevance (keywords match)
    assert relevance > 0.5


def test_calculate_relevance_no_match():
    """Test low relevance for unrelated content."""
    scorer = ToolResultScorer(query="authentication")
    
    unrelated_content = """
    def calculate_fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    """
    
    relevance = scorer.calculate_relevance(unrelated_content)
    
    # Should have low relevance
    assert relevance < 0.3


def test_calculate_importance_combines_signals():
    """Test multi-signal importance calculation."""
    scorer = ToolResultScorer(query="auth")
    
    content = "class AuthHandler: JWT authentication implementation"
    
    importance, signals = scorer.calculate_importance(content, "brain_read_file")
    
    # Should have all signal components
    assert 'surprise' in signals
    assert 'relevance' in signals
    assert 'decay' in signals
    assert 'habituation' in signals
    assert 'final' in signals
    
    # Final importance should be weighted combination
    expected = (
        signals['surprise'] * 0.60 +
        signals['relevance'] * 0.20 +
        signals['decay'] * 0.10 +
        signals['habituation'] * 0.10
    )
    assert abs(importance - expected) < 0.001


def test_get_detail_level_thresholds():
    """Test detail level assignment based on importance."""
    scorer = ToolResultScorer(query="test")
    
    # FULL: ≥0.75
    assert scorer.get_detail_level(0.85) == DetailLevel.FULL
    assert scorer.get_detail_level(0.75) == DetailLevel.FULL
    
    # CHUNKS: 0.50-0.74
    assert scorer.get_detail_level(0.60) == DetailLevel.CHUNKS
    assert scorer.get_detail_level(0.50) == DetailLevel.CHUNKS
    
    # SUMMARY: 0.20-0.49
    assert scorer.get_detail_level(0.30) == DetailLevel.SUMMARY
    assert scorer.get_detail_level(0.20) == DetailLevel.SUMMARY
    
    # DROPPED: <0.20
    assert scorer.get_detail_level(0.15) == DetailLevel.DROPPED
    assert scorer.get_detail_level(0.05) == DetailLevel.DROPPED


def test_compress_content_full():
    """Test FULL detail level preserves all content."""
    scorer = ToolResultScorer(query="test")
    
    content = "complete code here"
    result = scorer.compress_content(content, DetailLevel.FULL, {})
    
    assert result == content


def test_compress_content_chunks():
    """Test CHUNKS detail level trims middle section."""
    scorer = ToolResultScorer(query="test")
    
    # Long content
    content = "a" * 1000
    result = scorer.compress_content(content, DetailLevel.CHUNKS, {})
    
    # Should be trimmed
    assert len(result) < len(content)
    assert "trimmed for brevity" in result


def test_compress_content_summary():
    """Test SUMMARY detail level provides natural language."""
    scorer = ToolResultScorer(query="test")
    
    # Longer content so summary is actually shorter
    content = "line1\n" * 100  # 600 chars
    metadata = {
        'tool_name': 'brain_read_file',
        'file_path': 'test.py'
    }
    
    result = scorer.compress_content(content, DetailLevel.SUMMARY, metadata)
    
    # Should be summarized
    assert "test.py" in result
    assert len(result) < len(content)


def test_compress_content_dropped():
    """Test DROPPED detail level returns empty string."""
    scorer = ToolResultScorer(query="test")
    
    content = "some content"
    result = scorer.compress_content(content, DetailLevel.DROPPED, {})
    
    assert result == ""


def test_score_tool_result_high_importance():
    """Test scoring a highly relevant tool result."""
    scorer = ToolResultScorer(query="authentication")
    
    content = """
    def authenticate_user(credentials):
        # Main authentication logic
        token = verify_credentials(credentials)
        return token
    """
    
    result = scorer.score_tool_result(
        content=content,
        tool_name="brain_read_file",
        params={"file_path": "auth.py", "start_line": 1, "end_line": 10}
    )
    
    # Should have high importance
    assert result.importance > 0.5
    
    # Should keep full or chunks detail
    assert result.detail_level in [DetailLevel.FULL, DetailLevel.CHUNKS]
    
    # Should preserve content (not dropped)
    assert len(result.content) > 0
    
    # Should have signal breakdown
    assert 'surprise' in result.signals
    assert 'relevance' in result.signals


def test_score_tool_result_low_importance():
    """Test scoring an irrelevant tool result."""
    scorer = ToolResultScorer(query="authentication")
    
    # Unrelated content
    content = "import os\nimport sys\n# Generic imports"
    
    result = scorer.score_tool_result(
        content=content,
        tool_name="brain_read_file",
        params={"file_path": "utils.py"}
    )
    
    # Should have lower importance
    assert result.importance < 0.7
    
    # Signal breakdown should be present
    assert result.signals['relevance'] < 0.5


def test_contextual_relevance_auth():
    """Test contextual keyword matching for auth-related queries."""
    scorer = ToolResultScorer(query="auth")
    
    # Content with auth-related terms
    content = "JWT token authentication with bcrypt password hashing"
    
    relevance = scorer.calculate_relevance(content)
    
    # Should boost relevance for related terms
    assert relevance > 0.3


def test_habituation_penalty():
    """Test habituation reduces importance for repeated patterns."""
    scorer = ToolResultScorer(query="test")
    
    # Use unique content each time to isolate habituation effect
    content1 = "unique code pattern A"
    content2 = "unique code pattern B"
    
    # First calculation - both are new
    importance1, signals1 = scorer.calculate_importance(content1, "brain_read_file")
    
    # Second calculation with different content - also new
    importance2, signals2 = scorer.calculate_importance(content2, "brain_read_file")
    
    # Third calculation repeating content1 - now habituated
    importance3, signals3 = scorer.calculate_importance(content1, "brain_read_file")
    
    # Both new contents should have high habituation (1.0)
    assert signals1['habituation'] == 1.0
    assert signals2['habituation'] == 1.0
    
    # Repeated content should have lower habituation (0.4)
    assert signals3['habituation'] == 0.4
    assert signals3['habituation'] < signals1['habituation']
    
    # Overall importance should decrease for repeated content
    assert importance3 < importance1


def test_custom_weights():
    """Test scorer with custom weight overrides."""
    custom_weights = {
        'surprise': 0.8,
        'relevance': 0.1,
        'decay': 0.05,
        'habituation': 0.05
    }
    
    scorer = ToolResultScorer(query="test", weights=custom_weights)
    
    assert scorer.weights['surprise'] == 0.8
    assert scorer.weights['relevance'] == 0.1


def test_information_density_scoring():
    """Test surprise favors high-density code over boilerplate."""
    scorer = ToolResultScorer(query="test")
    
    # Dense code
    dense_code = """
    async def process(data):
        result = await transform(data)
        return validate(result)
    """
    
    # Boilerplate
    boilerplate = """
    # File header
    # Copyright notice
    # Long comment
    """
    
    surprise_dense = scorer.calculate_surprise(dense_code)
    surprise_boilerplate = scorer.calculate_surprise(boilerplate)
    
    # Dense code should have higher surprise
    assert surprise_dense > surprise_boilerplate


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
