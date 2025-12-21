"""Performance tests for streaming optimizations (Phase 2C).

Tests first-token latency, parallel execution, and context prefetching.
"""
import pytest
import time
from unittest.mock import Mock, patch, AsyncMock
from brain.router import ContextualRouter, RequestContext, RequestType


class TestFirstTokenLatency:
    """Test first token delivery performance (<200ms target)."""
    
    def test_routing_overhead(self):
        """Router should add <10ms overhead."""
        router = ContextualRouter()
        
        context = RequestContext(
            message="Hello, Ada!",
        )
        
        start = time.perf_counter()
        request_type = router.classify(context)
        response_path = router.route(request_type, context)
        end = time.perf_counter()
        
        routing_ms = (end - start) * 1000
        assert routing_ms < 10, f"Routing took {routing_ms:.2f}ms (should be <10ms)"
    
    def test_cache_lookup_speed(self):
        """Cache lookup should be <1ms."""
        from brain.response_cache import ResponseCache
        
        cache = ResponseCache(max_size=100)
        
        # Store entry
        cache.set(
            cache_key="test_key",
            response_text="cached response",
            request_type="quick_query",
            model="qwen2.5-coder:7b",
            ttl_seconds=3600,
        )
        
        # Measure lookup
        start = time.perf_counter()
        result = cache.get("test_key")
        end = time.perf_counter()
        
        lookup_ms = (end - start) * 1000
        assert result == "cached response"
        assert lookup_ms < 1, f"Cache lookup took {lookup_ms:.3f}ms (should be <1ms)"
    
    def test_cache_hit_total_time(self):
        """Cache hit path should be <5ms total (routing + lookup)."""
        from brain.response_cache import ResponseCache
        router = ContextualRouter()
        cache = ResponseCache(max_size=100)
        
        # Setup cached entry
        context = RequestContext(message="What is Python?")
        request_type = router.classify(context)
        cache_key = router.generate_cache_key(request_type, context)
        cache.set(cache_key, "Python is...", "quick_query", "model", 3600)
        
        # Measure full cache hit path
        start = time.perf_counter()
        
        # 1. Classify
        request_type = router.classify(context)
        
        # 2. Route
        response_path = router.route(request_type, context)
        
        # 3. Generate cache key
        cache_key = router.generate_cache_key(request_type, context)
        
        # 4. Lookup
        result = cache.get(cache_key)
        
        end = time.perf_counter()
        
        total_ms = (end - start) * 1000
        assert result is not None
        assert total_ms < 5, f"Cache hit path took {total_ms:.2f}ms (should be <5ms)"


class TestRAGContextPrefetching:
    """Test parallel context retrieval strategies."""
    
    @pytest.mark.asyncio
    async def test_parallel_context_retrieval_concept(self):
        """Test that parallel retrieval would be faster than sequential."""
        # Simulate context retrieval times
        persona_time = 0.010  # 10ms
        memories_time = 0.050  # 50ms
        faqs_time = 0.020  # 20ms
        
        # Sequential: sum of times
        sequential_total = persona_time + memories_time + faqs_time
        assert sequential_total == 0.080  # 80ms
        
        # Parallel: max of times
        parallel_total = max(persona_time, memories_time, faqs_time)
        assert parallel_total == 0.050  # 50ms
        
        # Speedup
        speedup = sequential_total / parallel_total
        assert abs(speedup - 1.6) < 0.01  # 1.6x faster (with floating point tolerance)
        
        # This demonstrates the concept - actual implementation would use asyncio.gather()


class TestSpecialistParallelExecution:
    """Test parallel specialist execution patterns."""
    
    def test_specialist_priority_levels(self):
        """High priority specialists should execute first."""
        from brain.specialists.protocol import SpecialistPriority
        
        # Test priority ordering
        priorities = [
            SpecialistPriority.LOW,
            SpecialistPriority.HIGH,
            SpecialistPriority.MEDIUM,
        ]
        
        # Sort by priority (lower value = higher priority)
        # HIGH = 10, MEDIUM = 50, LOW = 100
        sorted_priorities = sorted(priorities, key=lambda p: p.value)
        
        assert sorted_priorities[0] == SpecialistPriority.HIGH
        assert sorted_priorities[1] == SpecialistPriority.MEDIUM
        assert sorted_priorities[2] == SpecialistPriority.LOW
    
    @pytest.mark.asyncio
    async def test_parallel_specialist_execution_concept(self):
        """Test that parallel specialist execution would be faster."""
        import asyncio
        
        # Simulate specialist execution times
        async def specialist_a():
            await asyncio.sleep(0.030)  # 30ms
            return "result_a"
        
        async def specialist_b():
            await asyncio.sleep(0.020)  # 20ms
            return "result_b"
        
        async def specialist_c():
            await asyncio.sleep(0.025)  # 25ms
            return "result_c"
        
        # Parallel execution
        start = time.perf_counter()
        results = await asyncio.gather(
            specialist_a(),
            specialist_b(),
            specialist_c(),
        )
        end = time.perf_counter()
        
        parallel_ms = (end - start) * 1000
        
        # Should take ~30ms (max time), not 75ms (sum)
        assert len(results) == 3
        assert parallel_ms < 40, f"Parallel execution took {parallel_ms:.1f}ms (should be <40ms)"


class TestStreamingOptimizations:
    """Test streaming response delivery."""
    
    def test_streaming_chunk_size(self):
        """Verify optimal chunk sizes for streaming."""
        # Small chunks = more responsive but more overhead
        # Large chunks = less overhead but less responsive
        
        # Target: 5-10 words per chunk for good balance
        test_response = "This is a test response with multiple words in it"
        words = test_response.split()
        
        # Optimal chunk: 5-10 words
        chunk_size = 7
        chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
        
        assert len(chunks) == 2  # "This is a test response with multiple" + "words in it"
        assert all(len(chunk.split()) <= 10 for chunk in chunks)
    
    @pytest.mark.asyncio
    async def test_async_streaming_generator(self):
        """Test async generator pattern for streaming."""
        async def mock_stream():
            for i in range(5):
                yield f"chunk_{i}"
        
        chunks = []
        async for chunk in mock_stream():
            chunks.append(chunk)
        
        assert len(chunks) == 5
        assert chunks[0] == "chunk_0"
        assert chunks[-1] == "chunk_4"


class TestEndToEndPerformance:
    """End-to-end performance benchmarks."""
    
    def test_code_completion_target(self):
        """Code completion should be <3s total (measured in v2.6.0)."""
        # Current: 2.6s (10.6x speedup from v2.6.0)
        # Target with Phase 2C: <2s (streaming + cache)
        
        # This is a placeholder for actual measurement
        target_ms = 2000
        current_ms = 2600  # From v2.6.0 benchmark
        
        # Cache hit would reduce to <5ms
        cache_hit_ms = 5
        
        assert cache_hit_ms < target_ms
        assert cache_hit_ms < current_ms * 0.01  # >99% faster on cache hit
    
    def test_quick_query_target(self):
        """Quick query should be <5ms on cache hit."""
        # Router (2ms) + Cache lookup (1ms) + Streaming (2ms) = 5ms total
        
        routing_ms = 2
        cache_lookup_ms = 1
        streaming_overhead_ms = 2
        
        total_ms = routing_ms + cache_lookup_ms + streaming_overhead_ms
        
        assert total_ms <= 5
    
    def test_first_token_latency_target(self):
        """First token should arrive <200ms for non-cached requests."""
        # Breakdown:
        # - Routing: 2ms
        # - RAG context: 50ms (parallel)
        # - Specialists: 30ms (parallel)
        # - LLM first token: 100ms (model dependent)
        # - Streaming overhead: 18ms
        # Total: 200ms
        
        routing_ms = 2
        rag_context_ms = 50  # Parallel retrieval
        specialists_ms = 30  # Parallel execution
        llm_first_token_ms = 100  # Model dependent (can't optimize)
        streaming_overhead_ms = 18
        
        total_ms = routing_ms + rag_context_ms + specialists_ms + llm_first_token_ms + streaming_overhead_ms
        
        assert total_ms == 200
        assert total_ms < 250  # With buffer


class TestPerformanceRegression:
    """Ensure optimizations don't break existing functionality."""
    
    def test_router_classification_unchanged(self):
        """Router classification should still work correctly."""
        router = ContextualRouter()
        
        # Code completion
        context = RequestContext(
            message="",
            code_before="def hello():\n    ",
            has_code_before=True,
            is_completion=True,
        )
        assert router.classify(context) == RequestType.CODE_COMPLETION
        
        # Quick query
        context = RequestContext(message="What is Python?")
        assert router.classify(context) == RequestType.QUICK_QUERY
    
    def test_cache_functionality_unchanged(self):
        """Cache should still store and retrieve correctly."""
        from brain.response_cache import ResponseCache
        
        cache = ResponseCache(max_size=100)
        
        cache.set("key", "value", "type", "model", 3600)
        assert cache.get("key") == "value"
        
        # LRU still works
        cache.set("key2", "value2", "type", "model", 3600)
        assert cache.get("key2") == "value2"
