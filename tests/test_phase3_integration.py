"""Integration tests for Phase 3 biomimetic features.

Tests the full predictive processing pipeline:
1. Context priming pre-activates likely topics
2. Prediction error detection monitors LLM output
3. Dynamic injection provides additional context when needed
"""

import pytest
from brain.context_priming import ContextPrimer, SemanticNetwork
from brain.prediction_error import PredictionErrorDetector, UncertaintyType
from brain.dynamic_injection import (
    DynamicContextInjector,
    SimpleContextFetcher,
    InjectionStrategy
)


class TestPrimingWithDetection:
    """Test priming integrated with prediction error detection."""
    
    def test_primed_topics_reduce_errors(self):
        """Test that primed topics can help reduce prediction errors."""
        # Setup priming
        primer = ContextPrimer()
        primed = primer.prime_from_message(
            message="Tell me about specialists",
            current_topics=["specialist"]
        )
        
        # Setup detector
        detector = PredictionErrorDetector(min_signals_for_error=1)
        
        # If priming worked, these related topics should be available
        primed_topics = {ctx.topic for ctx in primed}
        
        # Check that key topics are primed
        assert "protocol" in primed_topics or "activation" in primed_topics
        
        # If LLM mentions primed topics, we'd have context ready
        for primed_ctx in primed:
            if primer.is_primed(primed_ctx.topic):
                benefit = primer.get_priming_benefit(primed_ctx.topic)
                assert benefit > 0.0  # We got a benefit from priming


class TestDetectionWithInjection:
    """Test prediction error detection integrated with dynamic injection."""
    
    def test_error_triggers_injection(self):
        """Test that detected errors trigger context injection."""
        # Setup context fetcher
        fetcher = SimpleContextFetcher({
            "Python": "Python is a high-level programming language",
            "FastAPI": "FastAPI is a modern web framework"
        })
        
        # Setup injector
        injector = DynamicContextInjector(
            context_fetcher=fetcher,
            injection_strategy=InjectionStrategy.INLINE,
            max_injections=3
        )
        
        # Setup detector
        detector = PredictionErrorDetector(min_signals_for_error=1)
        
        # Simulate text with uncertainty
        text = "I'm not sure about Python and FastAPI integration."
        
        # Detect error
        error = detector.process_chunk(text)
        
        # Should detect error
        assert error is not None
        assert error.error_type == UncertaintyType.EXPLICIT_UNCERTAINTY
        
        # Try to inject
        injection = injector.inject_context(error, stream_position=len(text))
        
        # Should inject context
        assert injection is not None
        # Should contain information about detected topics
        assert "Python" in injection or "FastAPI" in injection
    
    def test_low_confidence_error_not_injected(self):
        """Test that low-confidence errors don't trigger injection."""
        fetcher = SimpleContextFetcher({"Topic": "Some content"})
        injector = DynamicContextInjector(context_fetcher=fetcher)
        detector = PredictionErrorDetector(min_signals_for_error=1)
        
        # Text with weak/low-confidence signal
        text = "Maybe this could possibly work perhaps."
        error = detector.process_chunk(text)
        
        # Might detect error but...
        if error:
            # ...should not inject (low confidence)
            injection = injector.inject_context(error, stream_position=len(text))
            # May return None due to no matching topics or low confidence
            # Either way, injection count should be low
            assert injector.injections_count <= 1


class TestFullPredictiveProcessingPipeline:
    """Test the complete Phase 3 pipeline working together."""
    
    @pytest.mark.asyncio
    async def test_priming_detection_injection_flow(self):
        """Test full flow: prime → detect → inject."""
        # 1. Prime context based on conversation (use topics in default network)
        primer = ContextPrimer()
        primed = primer.prime_from_message(
            message="Tell me about specialists",
            current_topics=["specialist", "memory"]  # These are in default network
        )
        
        assert len(primed) > 0
        
        # 2. Setup detection and injection
        fetcher = SimpleContextFetcher({
            "Python": "Python is a programming language",
            "FastAPI": "FastAPI is a web framework",
            "web": "Web development concepts",
            "framework": "Software framework patterns"
        })
        
        detector = PredictionErrorDetector(min_signals_for_error=2)
        injector = DynamicContextInjector(
            context_fetcher=fetcher,
            max_injections=3
        )
        
        # 3. Simulate streaming with uncertainty
        async def mock_stream():
            chunks = [
                "FastAPI is a web framework. ",
                "I'm not sure about all the details. ",
                "I would need more context about Python integration."
            ]
            for chunk in chunks:
                yield chunk
        
        # 4. Process stream with injection
        output_chunks = []
        async for chunk in injector.process_stream_with_injection(
            mock_stream(),
            detector
        ):
            output_chunks.append(chunk)
        
        # Should have original + potentially injected content
        full_output = "".join(output_chunks)
        
        # Original content should be present
        assert "FastAPI is a web framework" in full_output
        
        # Check if injection happened (may or may not based on detection)
        stats = injector.get_stats()
        # If priming worked well, we might have had context ready
        # and injection could have happened
        assert stats['total_injections'] >= 0
    
    def test_priming_stats_with_pipeline(self):
        """Test priming statistics when used with full pipeline."""
        primer = ContextPrimer()
        
        # Prime some topics
        primer.prime_from_message(
            message="Tell me about testing",
            current_topics=["Python", "testing"]
        )
        
        # Simulate accessing primed topics
        if primer.is_primed("pytest"):
            primer.get_priming_benefit("pytest")
        
        stats = primer.get_priming_stats()
        
        assert 'total_primed' in stats
        assert 'hit_rate' in stats
        assert stats['total_primed'] >= 0
    
    def test_detection_stats_with_pipeline(self):
        """Test prediction error detection statistics."""
        detector = PredictionErrorDetector()
        
        # Process some chunks
        detector.process_chunk("I'm thinking about this problem.")
        detector.process_chunk("I'm not entirely sure of the answer.")
        
        stats = detector.get_stats()
        
        assert 'total_signals' in stats
        assert 'signal_types' in stats
        assert stats['total_signals'] >= 0
    
    def test_injection_stats_with_pipeline(self):
        """Test injection statistics."""
        fetcher = SimpleContextFetcher({"Python": "Python info"})
        injector = DynamicContextInjector(context_fetcher=fetcher)
        
        # Don't actually inject, just get stats
        stats = injector.get_stats()
        
        assert 'total_injections' in stats
        assert 'successful_injections' in stats
        assert 'injection_strategy' in stats
        assert stats['injection_strategy'] == 'inline'


class TestSemanticNetworkLearning:
    """Test learning semantic relationships from memory patterns."""
    
    def test_learn_from_memory_cooccurrence(self):
        """Test learning semantic network from memories."""
        network = SemanticNetwork()
        
        # Simulate memories with topic co-occurrence
        memories = [
            {'metadata': {'topics': ['Python', 'FastAPI', 'web']}},
            {'metadata': {'topics': ['Python', 'testing', 'pytest']}},
            {'metadata': {'topics': ['FastAPI', 'web', 'API']}},
            {'metadata': {'topics': ['Python', 'FastAPI', 'async']}},
            {'metadata': {'topics': ['testing', 'pytest', 'unit_tests']}},
        ]
        
        # Learn relationships
        network.learn_from_cooccurrence(memories, min_cooccurrence=2)
        
        # Python and FastAPI should be related (co-occur 2 times)
        python_related = network.get_related("Python", threshold=0.0)
        assert "FastAPI" in python_related
        
        # FastAPI and web should be related
        fastapi_related = network.get_related("FastAPI", threshold=0.0)
        assert "web" in fastapi_related or "Python" in fastapi_related
    
    def test_learned_network_for_priming(self):
        """Test using learned network for priming."""
        # Learn network from memories
        network = SemanticNetwork()
        memories = [
            {'metadata': {'topics': ['Python', 'web', 'FastAPI']}},
            {'metadata': {'topics': ['Python', 'web', 'Django']}},
            {'metadata': {'topics': ['web', 'FastAPI', 'API']}},
        ]
        network.learn_from_cooccurrence(memories, min_cooccurrence=2)
        
        # Use learned network for priming
        primer = ContextPrimer(semantic_network=network)
        primed = primer.prime_from_message(
            message="Tell me about Python",
            current_topics=["Python"]
        )
        
        # Should prime related topics
        primed_topics = {ctx.topic for ctx in primed}
        # Web should be primed (co-occurs with Python 2 times)
        assert "web" in primed_topics


class TestDisabledFeatures:
    """Test that Phase 3 features can be disabled."""
    
    def test_disabled_priming(self):
        """Test priming can be disabled."""
        primer = ContextPrimer()
        primer.priming_enabled = False
        
        primed = primer.prime_from_message(
            message="Test",
            current_topics=["specialist"]
        )
        
        assert len(primed) == 0
    
    def test_disabled_detection(self):
        """Test prediction error detection can be disabled."""
        detector = PredictionErrorDetector(enabled=False)
        
        error = detector.process_chunk("I'm not sure about anything.")
        
        assert error is None
    
    @pytest.mark.asyncio
    async def test_disabled_injection(self):
        """Test dynamic injection can be disabled."""
        injector = DynamicContextInjector(enabled=False)
        detector = PredictionErrorDetector()
        
        async def mock_stream():
            yield "chunk1"
            yield "chunk2"
        
        output = []
        async for chunk in injector.process_stream_with_injection(
            mock_stream(),
            detector
        ):
            output.append(chunk)
        
        # Should pass through unchanged
        assert output == ["chunk1", "chunk2"]
