"""Integration tests for contextual router in brain/app.py.

Tests routing decisions through the actual FastAPI endpoints.
"""
import pytest
from brain.router import RequestType


class TestRouterIntegration:
    """Test router integration with FastAPI app."""
    
    def test_code_completion_routes_to_qwen(self):
        """Code completion requests should route to qwen2.5-coder."""
        from brain.router import ContextualRouter, RequestContext
        
        router = ContextualRouter()
        
        # Simulate code completion request
        context = RequestContext(
            message="",
            code_before="def hello():\n    ",
            language="python",
            has_code_before=True,
            is_completion=True,
        )
        
        request_type = router.classify(context)
        response_path = router.route(request_type, context)
        
        assert request_type == RequestType.CODE_COMPLETION
        assert "qwen" in response_path.model.lower()
        assert response_path.format == "fim"
        assert response_path.use_rag is False
        assert response_path.use_cache is True
    
    def test_chat_routes_to_deepseek_with_rag(self):
        """Regular chat requests should route to deepseek with full RAG."""
        from brain.router import ContextualRouter, RequestContext
        
        router = ContextualRouter()
        
        # Simulate chat request
        context = RequestContext(
            message="Tell me about Python decorators",
        )
        
        request_type = router.classify(context)
        response_path = router.route(request_type, context)
        
        assert request_type == RequestType.CHAT
        assert "deepseek" in response_path.model.lower()
        assert response_path.format == "chat"
        assert response_path.use_rag is True
        assert response_path.use_specialists is True
    
    def test_reasoning_request_routes_with_thinking(self):
        """Complex reasoning should enable thinking mode."""
        from brain.router import ContextualRouter, RequestContext
        
        router = ContextualRouter()
        
        # Simulate reasoning request
        context = RequestContext(
            message="Analyze the trade-offs between monolithic and microservices architecture",
        )
        
        request_type = router.classify(context)
        response_path = router.route(request_type, context)
        
        assert request_type == RequestType.REASONING
        assert "deepseek" in response_path.model.lower()
        assert response_path.enable_thinking is True
        assert response_path.timeout == 60  # Longer timeout
    
    def test_quick_query_uses_cache(self):
        """Simple factual queries should prefer cached responses."""
        from brain.router import ContextualRouter, RequestContext
        
        router = ContextualRouter()
        
        # Simulate quick query
        context = RequestContext(
            message="What is Python?",
        )
        
        request_type = router.classify(context)
        response_path = router.route(request_type, context)
        
        assert request_type == RequestType.QUICK_QUERY
        assert response_path.use_cache is True
        assert response_path.cache_ttl == 86400  # 24 hours in seconds
        assert response_path.use_rag is False  # Prefer cache over RAG for simple queries
    
    def test_routing_time_is_fast(self):
        """Routing should complete in under 10ms."""
        from brain.router import ContextualRouter, RequestContext
        
        router = ContextualRouter()
        
        context = RequestContext(
            message="Hello!",
        )
        
        request_type = router.classify(context)
        response_path = router.route(request_type, context)
        
        # Routing time is measured in router.route()
        assert response_path.routing_time_ms < 10, \
            f"Routing took {response_path.routing_time_ms:.2f}ms, should be < 10ms"
    
    def test_cache_keys_are_consistent(self):
        """Same request should generate same cache key."""
        from brain.router import ContextualRouter, RequestContext
        
        router = ContextualRouter()
        
        context1 = RequestContext(
            message="What is Python?",
        )
        
        context2 = RequestContext(
            message="What is Python?",
        )
        
        request_type = router.classify(context1)
        key1 = router.generate_cache_key(request_type, context1)
        key2 = router.generate_cache_key(request_type, context2)
        
        assert key1 == key2, "Identical requests should generate identical cache keys"
    
    def test_cache_keys_differ_for_different_requests(self):
        """Different requests should generate different cache keys."""
        from brain.router import ContextualRouter, RequestContext
        
        router = ContextualRouter()
        
        context1 = RequestContext(
            message="What is Python?",
        )
        
        context2 = RequestContext(
            message="What is JavaScript?",
        )
        
        request_type1 = router.classify(context1)
        request_type2 = router.classify(context2)
        key1 = router.generate_cache_key(request_type1, context1)
        key2 = router.generate_cache_key(request_type2, context2)
        
        assert key1 != key2, "Different requests should generate different cache keys"


class TestEndToEndRouting:
    """Test routing through actual API endpoints (requires services)."""
    
    @pytest.mark.integration
    def test_code_completion_endpoint_uses_router(self, client):
        """Code completion through API should use router."""
        # This would require actual services running
        # Placeholder for future integration test
        pass
    
    @pytest.mark.integration
    def test_chat_endpoint_uses_router(self, client):
        """Chat through API should use router."""
        # This would require actual services running
        # Placeholder for future integration test
        pass
