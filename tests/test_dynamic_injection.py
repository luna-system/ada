"""Tests for dynamic context injection (Phase 3 biomimetic features)."""

import pytest
from brain.dynamic_injection import (
    DynamicContextInjector,
    SimpleContextFetcher,
    DynamicContext,
    InjectionStrategy,
    InjectionPoint
)
from brain.prediction_error import (
    PredictionError,
    UncertaintySignal,
    UncertaintyType,
    PredictionErrorDetector
)


class TestDynamicContext:
    """Test DynamicContext dataclass."""
    
    def test_dynamic_context_creation(self):
        """Test creating dynamic context."""
        context = DynamicContext(
            content="Python is a programming language",
            source="memory",
            relevance_score=0.9,
            priority=10
        )
        
        assert context.content == "Python is a programming language"
        assert context.source == "memory"
        assert context.relevance_score == 0.9
        assert context.priority == 10
        assert context.fetched_at is not None


class TestSimpleContextFetcher:
    """Test simple context fetcher."""
    
    def test_exact_match(self):
        """Test fetching context with exact topic match."""
        fetcher = SimpleContextFetcher({
            "Python": "Python is a high-level programming language",
            "FastAPI": "FastAPI is a modern web framework"
        })
        
        contexts = fetcher(["Python"])
        
        assert len(contexts) == 1
        assert "Python" in contexts[0].content
        assert contexts[0].relevance_score == 1.0
    
    def test_partial_match(self):
        """Test fetching context with partial topic match."""
        fetcher = SimpleContextFetcher({
            "python_basics": "Python is easy to learn"
        })
        
        contexts = fetcher(["Python"])  # Lowercase, partial match
        
        assert len(contexts) == 1
        assert contexts[0].relevance_score == 0.8
    
    def test_multiple_topics(self):
        """Test fetching context for multiple topics."""
        fetcher = SimpleContextFetcher({
            "Python": "Python info",
            "FastAPI": "FastAPI info",
            "Docker": "Docker info"
        })
        
        contexts = fetcher(["Python", "Docker"])
        
        assert len(contexts) == 2
        topics_fetched = [c.content for c in contexts]
        assert any("Python" in t for t in topics_fetched)
        assert any("Docker" in t for t in topics_fetched)
    
    def test_no_match(self):
        """Test fetching context when no topics match."""
        fetcher = SimpleContextFetcher({
            "Python": "Python info"
        })
        
        contexts = fetcher(["Unknown"])
        
        assert len(contexts) == 0


class TestDynamicContextInjector:
    """Test dynamic context injection system."""
    
    def test_initialization(self):
        """Test injector initialization."""
        injector = DynamicContextInjector()
        
        assert injector.enabled
        assert injector.max_injections == 3
        assert injector.injection_strategy == InjectionStrategy.INLINE
        assert injector.injections_count == 0
    
    def test_should_inject_immediate_action(self):
        """Test injection for errors requiring immediate action."""
        injector = DynamicContextInjector()
        
        error = PredictionError(
            uncertainty_signals=[],
            error_type=UncertaintyType.EXPLICIT_UNCERTAINTY,
            confidence=0.9,
            requires_immediate_action=True
        )
        
        assert injector.should_inject(error)
    
    def test_should_inject_high_confidence(self):
        """Test injection for high-confidence errors."""
        injector = DynamicContextInjector()
        
        error = PredictionError(
            uncertainty_signals=[],
            error_type=UncertaintyType.HEDGING,
            confidence=0.85,  # Above 0.8 threshold
            requires_immediate_action=False
        )
        
        assert injector.should_inject(error)
    
    def test_should_not_inject_low_confidence(self):
        """Test no injection for low-confidence errors."""
        injector = DynamicContextInjector()
        
        error = PredictionError(
            uncertainty_signals=[],
            error_type=UncertaintyType.HEDGING,
            confidence=0.5,  # Below threshold
            requires_immediate_action=False
        )
        
        assert not injector.should_inject(error)
    
    def test_should_not_inject_when_disabled(self):
        """Test injection disabled."""
        injector = DynamicContextInjector(enabled=False)
        
        error = PredictionError(
            uncertainty_signals=[],
            error_type=UncertaintyType.EXPLICIT_UNCERTAINTY,
            confidence=1.0,
            requires_immediate_action=True
        )
        
        assert not injector.should_inject(error)
    
    def test_max_injections_limit(self):
        """Test maximum injections limit."""
        injector = DynamicContextInjector(max_injections=2)
        
        error = PredictionError(
            uncertainty_signals=[],
            error_type=UncertaintyType.EXPLICIT_UNCERTAINTY,
            confidence=1.0,
            requires_immediate_action=True
        )
        
        # First two should inject
        assert injector.should_inject(error)
        injector.injections_count = 1
        assert injector.should_inject(error)
        
        # Third should not
        injector.injections_count = 2
        assert not injector.should_inject(error)
    
    def test_fetch_context(self):
        """Test fetching context for topics."""
        fetcher = SimpleContextFetcher({
            "Python": "Python programming language"
        })
        
        injector = DynamicContextInjector(context_fetcher=fetcher)
        
        contexts = injector.fetch_context(["Python"])
        
        assert len(contexts) == 1
        assert "Python" in contexts[0].content
    
    def test_format_injection_inline(self):
        """Test formatting context for inline injection."""
        injector = DynamicContextInjector(injection_strategy=InjectionStrategy.INLINE)
        
        contexts = [
            DynamicContext(
                content="Python is great",
                source="memory",
                relevance_score=0.9,
                priority=10
            ),
            DynamicContext(
                content="FastAPI is fast",
                source="memory",
                relevance_score=0.8,
                priority=5
            )
        ]
        
        injection = injector.format_injection(contexts)
        
        # Should have context markers
        assert "[Context: memory]" in injection
        # Should have content
        assert "Python is great" in injection
        assert "FastAPI is fast" in injection
        # Higher priority first
        assert injection.index("Python") < injection.index("FastAPI")
    
    def test_inject_context_success(self):
        """Test successful context injection."""
        fetcher = SimpleContextFetcher({
            "Python": "Python is a programming language"
        })
        
        injector = DynamicContextInjector(context_fetcher=fetcher)
        
        error = PredictionError(
            uncertainty_signals=[],
            error_type=UncertaintyType.EXPLICIT_UNCERTAINTY,
            confidence=0.9,
            suggested_topics=["Python"],
            requires_immediate_action=True
        )
        
        injection = injector.inject_context(error, stream_position=100)
        
        # Should return injection text
        assert injection is not None
        assert "Python" in injection
        
        # Should record injection point
        assert len(injector.injection_points) == 1
        assert injector.injection_points[0].stream_position == 100
        assert injector.injections_count == 1
    
    def test_inject_context_no_topics(self):
        """Test injection with no matching topics."""
        fetcher = SimpleContextFetcher({})
        
        injector = DynamicContextInjector(context_fetcher=fetcher)
        
        error = PredictionError(
            uncertainty_signals=[],
            error_type=UncertaintyType.EXPLICIT_UNCERTAINTY,
            confidence=0.9,
            suggested_topics=["Unknown"],
            requires_immediate_action=True
        )
        
        injection = injector.inject_context(error, stream_position=100)
        
        # Should return None (no context found)
        assert injection is None
        assert injector.injections_count == 0
    
    @pytest.mark.asyncio
    async def test_process_stream_with_injection(self):
        """Test processing stream with dynamic injection."""
        # Setup
        fetcher = SimpleContextFetcher({
            "Python": "Python is a programming language"
        })
        
        injector = DynamicContextInjector(context_fetcher=fetcher, max_injections=5)
        detector = PredictionErrorDetector(min_signals_for_error=1)
        
        # Simulate stream chunks
        async def mock_stream():
            chunks = [
                "Let me explain ",
                "Python. I'm not sure ",
                "about the details."
            ]
            for chunk in chunks:
                yield chunk
        
        # Process stream
        output_chunks = []
        async for chunk in injector.process_stream_with_injection(
            mock_stream(),
            detector
        ):
            output_chunks.append(chunk)
        
        # Should have original chunks plus potential injections
        assert len(output_chunks) >= 3
        
        # Should contain original content
        full_output = "".join(output_chunks)
        assert "Let me explain" in full_output
        assert "I'm not sure" in full_output
    
    @pytest.mark.asyncio
    async def test_process_stream_disabled(self):
        """Test stream processing when injection disabled."""
        injector = DynamicContextInjector(enabled=False)
        detector = PredictionErrorDetector()
        
        async def mock_stream():
            yield "chunk1"
            yield "chunk2"
        
        output_chunks = []
        async for chunk in injector.process_stream_with_injection(
            mock_stream(),
            detector
        ):
            output_chunks.append(chunk)
        
        # Should pass through unchanged
        assert output_chunks == ["chunk1", "chunk2"]
    
    def test_reset(self):
        """Test resetting injector state."""
        fetcher = SimpleContextFetcher({"Python": "Python info"})
        injector = DynamicContextInjector(context_fetcher=fetcher)
        
        # Inject something
        error = PredictionError(
            uncertainty_signals=[],
            error_type=UncertaintyType.EXPLICIT_UNCERTAINTY,
            confidence=0.9,
            suggested_topics=["Python"],
            requires_immediate_action=True
        )
        injector.inject_context(error, stream_position=100)
        
        assert injector.injections_count > 0
        assert len(injector.injection_points) > 0
        
        # Reset
        injector.reset()
        
        assert injector.injections_count == 0
        assert len(injector.injection_points) == 0
    
    def test_get_stats(self):
        """Test statistics tracking."""
        fetcher = SimpleContextFetcher({"Python": "Python info"})
        injector = DynamicContextInjector(
            context_fetcher=fetcher,
            injection_strategy=InjectionStrategy.INLINE,
            max_injections=5
        )
        
        # Inject something
        error = PredictionError(
            uncertainty_signals=[],
            error_type=UncertaintyType.EXPLICIT_UNCERTAINTY,
            confidence=0.9,
            suggested_topics=["Python"],
            requires_immediate_action=True
        )
        injector.inject_context(error, stream_position=100)
        
        stats = injector.get_stats()
        
        assert 'total_injections' in stats
        assert 'successful_injections' in stats
        assert 'injection_strategy' in stats
        assert 'max_injections' in stats
        assert 'enabled' in stats
        
        assert stats['total_injections'] == 1
        assert stats['injection_strategy'] == "inline"
        assert stats['max_injections'] == 5


class TestInjectionPoint:
    """Test InjectionPoint dataclass."""
    
    def test_injection_point_creation(self):
        """Test creating injection point."""
        error = PredictionError(
            uncertainty_signals=[],
            error_type=UncertaintyType.EXPLICIT_UNCERTAINTY,
            confidence=0.9
        )
        
        point = InjectionPoint(
            stream_position=100,
            trigger_error=error,
            injected_context="Additional context here",
            injection_strategy=InjectionStrategy.INLINE,
            success=True
        )
        
        assert point.stream_position == 100
        assert point.trigger_error == error
        assert "Additional context" in point.injected_context
        assert point.injection_strategy == InjectionStrategy.INLINE
        assert point.success
        assert point.timestamp is not None
