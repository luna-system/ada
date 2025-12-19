"""Tests for Contextual Router.

Research foundation: v2.3.0 contextual malleability framework.
Context-matching beats universal approaches (r=0.924 vs r=0.726).
"""

import pytest
from brain.router import (
    ContextualRouter,
    RequestType,
    ResponsePath,
    RequestContext,
)


@pytest.fixture
def router():
    """Create ContextualRouter instance."""
    return ContextualRouter()


class TestRequestClassification:
    """Test request type classification."""

    def test_classify_code_completion(self, router):
        """Should classify code completion requests."""
        context = RequestContext(
            message="",  # Empty for completion
            has_code_before=True,
            has_code_after=True,
            language="python",
            is_completion=True,
        )
        
        result = router.classify(context)
        assert result == RequestType.CODE_COMPLETION

    def test_classify_chat(self, router):
        """Should classify conversational requests."""
        context = RequestContext(
            message="Can you explain how recursion works?",
            has_code_before=False,
            has_code_after=False,
            language=None,
            is_completion=False,
        )
        
        result = router.classify(context)
        assert result == RequestType.CHAT

    def test_classify_reasoning(self, router):
        """Should classify complex reasoning requests."""
        context = RequestContext(
            message="Analyze the trade-offs between quicksort and mergesort",
            has_code_before=False,
            has_code_after=False,
            language=None,
            is_completion=False,
            requires_reasoning=True,
        )
        
        result = router.classify(context)
        assert result == RequestType.REASONING

    def test_classify_quick_query(self, router):
        """Should classify simple factual queries."""
        context = RequestContext(
            message="What's the square root of 144?",
            has_code_before=False,
            has_code_after=False,
            language=None,
            is_completion=False,
            is_simple_query=True,
        )
        
        result = router.classify(context)
        assert result == RequestType.QUICK_QUERY


class TestRouting:
    """Test request routing to appropriate paths."""

    def test_route_code_completion(self, router):
        """Code completion should route to qwen2.5-coder with FIM."""
        context = RequestContext(
            message="",
            has_code_before=True,
            language="python",
            is_completion=True,
        )
        
        path = router.route(RequestType.CODE_COMPLETION, context)
        
        assert path.model == "qwen2.5-coder:7b"
        assert path.format == "fim"
        assert path.use_rag is False
        assert path.use_cache is True
        assert path.stream is True

    def test_route_chat(self, router):
        """Chat should route to deepseek-r1 with full RAG."""
        context = RequestContext(
            message="Tell me about your memory system",
            is_completion=False,
        )
        
        path = router.route(RequestType.CHAT, context)
        
        assert path.model == "deepseek-r1:latest"
        assert path.format == "chat"
        assert path.use_rag is True
        assert path.use_specialists is True
        assert path.stream is True

    def test_route_reasoning(self, router):
        """Reasoning should route to deepseek-r1 with thinking tags."""
        context = RequestContext(
            message="Analyze the complexity",
            requires_reasoning=True,
        )
        
        path = router.route(RequestType.REASONING, context)
        
        assert path.model == "deepseek-r1:latest"
        assert path.format == "chat"
        assert path.enable_thinking is True
        assert path.timeout > 30  # Longer timeout for reasoning

    def test_route_quick_query(self, router):
        """Quick queries should check cache first."""
        context = RequestContext(
            message="What is 2+2?",
            is_simple_query=True,
        )
        
        path = router.route(RequestType.QUICK_QUERY, context)
        
        assert path.use_cache is True
        assert path.cache_ttl > 0


class TestContextAnalysis:
    """Test context analysis heuristics."""

    def test_detect_code_context(self, router):
        """Should detect when code is present."""
        context = RequestContext(
            message="def add(a, b):",
            has_code_before=True,
        )
        
        assert router.has_code_context(context) is True

    def test_detect_language(self, router):
        """Should detect programming language from context."""
        contexts = [
            (RequestContext(message="def foo():"), "python"),
            (RequestContext(message="function foo() {"), "javascript"),
            (RequestContext(message="fn main() {"), "rust"),
        ]
        
        for context, expected_lang in contexts:
            detected = router.detect_language(context)
            assert detected == expected_lang

    def test_detect_reasoning_keywords(self, router):
        """Should detect reasoning indicators."""
        reasoning_phrases = [
            "analyze",
            "compare",
            "evaluate",
            "trade-offs",
            "pros and cons",
            "explain why",
        ]
        
        for phrase in reasoning_phrases:
            context = RequestContext(message=f"Can you {phrase} this?")
            assert router.requires_reasoning(context) is True

    def test_detect_simple_query(self, router):
        """Should detect simple factual queries."""
        simple_queries = [
            "What is 2+2?",
            "How many bytes in a megabyte?",
            "What's the capital of France?",
        ]
        
        for query in simple_queries:
            context = RequestContext(message=query)
            assert router.is_simple_query(context) is True


class TestCacheKeyGeneration:
    """Test cache key generation for different request types."""

    def test_cache_key_for_code_completion(self, router):
        """Code completion cache keys should be consistent."""
        context1 = RequestContext(
            message="",
            code_before="def add(a, b):",
            code_after="",
            language="python",
            is_completion=True,
        )
        context2 = RequestContext(
            message="",
            code_before="def add(a, b):",
            code_after="",
            language="python",
            is_completion=True,
        )
        
        key1 = router.generate_cache_key(RequestType.CODE_COMPLETION, context1)
        key2 = router.generate_cache_key(RequestType.CODE_COMPLETION, context2)
        
        # Same code should produce same key
        assert key1 == key2
        assert len(key1) == 16  # Should be 16-char hash

    def test_cache_key_for_quick_query(self, router):
        """Quick query cache keys should normalize the question."""
        contexts = [
            RequestContext(message="What is 2+2?"),
            RequestContext(message="what is 2+2"),  # Same without space, lowercase
            RequestContext(message="what is 2+2?"),  # Same with question mark
        ]
        
        keys = [router.generate_cache_key(RequestType.QUICK_QUERY, ctx) for ctx in contexts]
        
        # All variations should produce same cache key (after normalization)
        assert keys[0] == keys[1] == keys[2]


class TestModelSelection:
    """Test intelligent model selection."""

    def test_select_fastest_for_simple_completion(self, router):
        """Simple completions should use fastest model."""
        context = RequestContext(
            message="",
            code_before="x = ",
            language="python",
            is_completion=True,
            is_simple=True,
        )
        
        path = router.route(RequestType.CODE_COMPLETION, context)
        
        # Should prioritize speed over quality for simple completions
        assert "coder" in path.model
        assert path.max_tokens < 100

    def test_select_quality_for_complex_completion(self, router):
        """Complex completions should use better model."""
        context = RequestContext(
            message="",
            code_before="def complex_algorithm(data: List[Dict[str, Any]]):",
            language="python",
            is_completion=True,
            is_simple=False,
        )
        
        path = router.route(RequestType.CODE_COMPLETION, context)
        
        # Should prioritize quality for complex code
        assert path.max_tokens > 100


class TestStreamingConfiguration:
    """Test streaming configuration per request type."""

    def test_streaming_enabled_by_default(self, router):
        """Streaming should be enabled for all interactive requests."""
        for req_type in [RequestType.CODE_COMPLETION, RequestType.CHAT, RequestType.REASONING]:
            path = router.route(req_type, RequestContext(message="test"))
            assert path.stream is True

    def test_first_token_optimization(self, router):
        """Code completion should optimize for first token speed."""
        context = RequestContext(
            message="",
            is_completion=True,
        )
        
        path = router.route(RequestType.CODE_COMPLETION, context)
        
        # Should have settings that optimize for fast first token
        assert path.temperature <= 0.3  # Low temp = faster
        assert path.top_p >= 0.9  # High top_p = faster sampling


class TestErrorHandling:
    """Test error handling and fallbacks."""

    def test_fallback_to_chat_on_unknown_type(self, router):
        """Unknown request types should fall back to chat."""
        context = RequestContext(message="something weird")
        
        # Force unknown classification
        result = router.classify(RequestContext(message="", unknown_flag=True))
        path = router.route(result, context)
        
        # Should safely fall back
        assert path.model is not None
        assert path.format in ["chat", "fim"]

    def test_handle_missing_language(self, router):
        """Should gracefully handle missing language detection."""
        context = RequestContext(
            message="",
            code_before="some ambiguous code",
            is_completion=True,
            language=None,
        )
        
        # Should not crash
        path = router.route(RequestType.CODE_COMPLETION, context)
        assert path.model is not None


class TestPerformanceMetrics:
    """Test performance tracking and optimization."""

    def test_track_routing_time(self, router):
        """Router should track decision time."""
        context = RequestContext(message="test")
        
        path = router.route(RequestType.CHAT, context)
        
        assert hasattr(path, 'routing_time_ms')
        assert path.routing_time_ms < 10  # Should be fast!

    def test_track_cache_hits(self, router):
        """Router should track cache hit rate."""
        context = RequestContext(message="What is 2+2?", is_simple_query=True)
        
        # First request (miss)
        router.route(RequestType.QUICK_QUERY, context)
        
        # Second request (should hit)
        path = router.route(RequestType.QUICK_QUERY, context)
        
        # Check that router tracks cache metrics
        assert hasattr(router, 'cache_stats')
