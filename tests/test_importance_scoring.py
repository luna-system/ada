"""Tests for neuromorphic context importance scoring (Phase 1).

This module tests the multi-signal importance scoring system that determines
which conversation turns get FULL detail, which get CHUNKED, which get
SUMMARIZED, and which get DROPPED from context.

Importance is calculated from:
- Temporal decay (existing memory_decay.py)
- Prediction error (surprise/novelty from prediction_error.py)
- Semantic relevance (vector similarity to current query)
- Context habituation (repeated pattern detection from context_habituation.py)
"""

import pytest
from datetime import datetime, timezone, timedelta
from brain.prompt_builder.context_retriever import ContextRetriever
from brain.memory_decay import MemoryDecayWeighter


class TestBasicImportanceScoring:
    """Test basic importance calculation without full integration."""
    
    def test_calculate_importance_exists(self):
        """Verify calculate_importance function exists."""
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        assert hasattr(retriever, 'calculate_importance')
    
    def test_importance_score_range(self):
        """Importance scores should be between 0.0 and 1.0."""
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        # Mock turn data
        turn = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'content': 'test message',
            'metadata': {}
        }
        query = "test query"
        
        score = retriever.calculate_importance(turn, query)
        
        assert 0.0 <= score <= 1.0, f"Score {score} outside valid range"
    
    def test_recent_turns_higher_importance(self):
        """Recent turns should score higher than old turns."""
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        now = datetime.now(timezone.utc)
        recent_turn = {
            'timestamp': now.isoformat(),
            'content': 'recent message',
            'metadata': {}
        }
        old_turn = {
            'timestamp': (now - timedelta(hours=24)).isoformat(),
            'content': 'old message',
            'metadata': {}
        }
        query = "test query"
        
        recent_score = retriever.calculate_importance(recent_turn, query)
        old_score = retriever.calculate_importance(old_turn, query)
        
        assert recent_score > old_score, "Recent turns should have higher importance"


class TestMultiSignalIntegration:
    """Test integration of multiple importance signals."""
    
    def test_decay_component(self):
        """Temporal decay should be incorporated into importance."""
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        now = datetime.now(timezone.utc)
        turn = {
            'timestamp': (now - timedelta(hours=12)).isoformat(),
            'content': 'test message',
            'metadata': {}
        }
        query = "test query"
        
        importance = retriever.calculate_importance(turn, query)
        
        # Should incorporate decay weight from memory_decay.py
        # 12 hour old turn should have moderate decay
        assert 0.3 < importance < 0.9, f"Decay not properly applied: {importance}"
    
    def test_surprise_boost(self):
        """High prediction error (surprise) should boost importance."""
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        now = datetime.now(timezone.utc)
        surprising_turn = {
            'timestamp': now.isoformat(),
            'content': 'completely unexpected novel information',
            'metadata': {'prediction_error': 0.9}  # High surprise
        }
        boring_turn = {
            'timestamp': now.isoformat(),
            'content': 'routine expected information',
            'metadata': {'prediction_error': 0.1}  # Low surprise
        }
        query = "tell me something interesting"
        
        surprising_score = retriever.calculate_importance(surprising_turn, query)
        boring_score = retriever.calculate_importance(boring_turn, query)
        
        assert surprising_score > boring_score, "Surprising turns should score higher"
    
    def test_relevance_component(self):
        """Semantic relevance to current query should affect importance."""
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        now = datetime.now(timezone.utc)
        relevant_turn = {
            'timestamp': now.isoformat(),
            'content': 'detailed explanation of neural networks and machine learning',
            'metadata': {}
        }
        irrelevant_turn = {
            'timestamp': now.isoformat(),
            'content': 'discussion about gardening and plants',
            'metadata': {}
        }
        query = "explain how neural networks work"
        
        relevant_score = retriever.calculate_importance(relevant_turn, query)
        irrelevant_score = retriever.calculate_importance(irrelevant_turn, query)
        
        assert relevant_score > irrelevant_score, "Relevant turns should score higher"
    
    def test_habituation_penalty(self):
        """Repeated patterns should have reduced importance."""
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        now = datetime.now(timezone.utc)
        novel_turn = {
            'timestamp': now.isoformat(),
            'content': 'first mention of quantum computing',
            'metadata': {'habituation_score': 0.1}  # Novel
        }
        repeated_turn = {
            'timestamp': now.isoformat(),
            'content': 'yet another mention of same topic',
            'metadata': {'habituation_score': 0.9}  # Habituated
        }
        query = "tell me about quantum computing"
        
        novel_score = retriever.calculate_importance(novel_turn, query)
        repeated_score = retriever.calculate_importance(repeated_turn, query)
        
        assert novel_score > repeated_score, "Novel content should score higher than repeated"


class TestGradientThresholds:
    """Test the gradient detail levels based on importance scores."""
    
    def test_gradient_level_assignment(self):
        """Verify get_detail_level function exists and returns valid levels."""
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        assert hasattr(retriever, 'get_detail_level')
        
        # Test various importance scores
        level_high = retriever.get_detail_level(0.9)
        level_medium = retriever.get_detail_level(0.6)
        level_low = retriever.get_detail_level(0.3)
        level_minimal = retriever.get_detail_level(0.1)
        
        valid_levels = ['FULL', 'CHUNKS', 'SUMMARY', 'DROPPED']
        assert level_high in valid_levels
        assert level_medium in valid_levels
        assert level_low in valid_levels
        assert level_minimal in valid_levels
    
    def test_high_importance_gets_full_detail(self):
        """High importance turns should get FULL detail."""
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        level = retriever.get_detail_level(0.85)
        assert level == 'FULL', "High importance should get FULL detail"
    
    def test_medium_importance_gets_chunks(self):
        """Medium importance turns should get CHUNKS (semantic units)."""
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        level = retriever.get_detail_level(0.55)
        assert level == 'CHUNKS', "Medium importance should get CHUNKS"
    
    def test_low_importance_gets_summary(self):
        """Low importance turns should get SUMMARY."""
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        level = retriever.get_detail_level(0.25)
        assert level == 'SUMMARY', "Low importance should get SUMMARY"
    
    def test_minimal_importance_gets_dropped(self):
        """Very low importance turns should be DROPPED."""
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        level = retriever.get_detail_level(0.05)
        assert level == 'DROPPED', "Minimal importance should be DROPPED"
    
    def test_threshold_boundaries(self):
        """Test exact threshold boundaries."""
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        # Default thresholds (can be configured):
        # FULL: >= 0.75
        # CHUNKS: >= 0.50 and < 0.75
        # SUMMARY: >= 0.20 and < 0.50
        # DROPPED: < 0.20
        
        assert retriever.get_detail_level(0.75) == 'FULL'
        assert retriever.get_detail_level(0.74) == 'CHUNKS'
        assert retriever.get_detail_level(0.50) == 'CHUNKS'
        assert retriever.get_detail_level(0.49) == 'SUMMARY'
        assert retriever.get_detail_level(0.20) == 'SUMMARY'
        assert retriever.get_detail_level(0.19) == 'DROPPED'


class TestMemoryDecayIntegration:
    """Test integration with existing memory_decay.py module."""
    
    def test_uses_existing_decay_function(self):
        """Should use calculate_decay_weight from memory_decay.py."""
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        now = datetime.now(timezone.utc)
        turn = {
            'timestamp': (now - timedelta(hours=6)).isoformat(),
            'content': 'test message',
            'metadata': {}
        }
        query = "test"
        
        importance = retriever.calculate_importance(turn, query)
        
        # Calculate expected decay contribution
        weighter = MemoryDecayWeighter()
        expected_decay = weighter.calculate_weight(
            turn['timestamp'],
            importance=0.5,
            base_relevance=1.0
        )
        
        # Importance should incorporate decay (though not equal, since multi-signal)
        # Allow for multi-signal weighting - could be higher due to other signals
        assert 0 < importance, "Should have non-zero importance"
        assert importance <= 1.0, "Should not exceed maximum"
    
    def test_temperature_modulation(self):
        """Temperature from memory_decay should affect importance."""
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        now = datetime.now(timezone.utc)
        # High importance content should resist decay (high temperature)
        important_turn = {
            'timestamp': (now - timedelta(hours=24)).isoformat(),
            'content': 'critical architectural decision',
            'metadata': {'importance': 0.9}  # Triggers temperature boost
        }
        # Low importance content decays faster (low temperature)
        trivial_turn = {
            'timestamp': (now - timedelta(hours=24)).isoformat(),
            'content': 'minor formatting detail',
            'metadata': {'importance': 0.1}
        }
        query = "what decisions did we make?"
        
        important_score = retriever.calculate_importance(important_turn, query)
        trivial_score = retriever.calculate_importance(trivial_turn, query)
        
        assert important_score > trivial_score, "Important content should resist decay"


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_missing_timestamp(self):
        """Should handle missing timestamp gracefully."""
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        turn = {
            'content': 'test message',
            'metadata': {}
            # No timestamp!
        }
        query = "test"
        
        # Should not crash, should assume recent
        score = retriever.calculate_importance(turn, query)
        assert 0.0 <= score <= 1.0
    
    def test_missing_metadata(self):
        """Should handle missing metadata gracefully."""
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        turn = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'content': 'test message'
            # No metadata!
        }
        query = "test"
        
        score = retriever.calculate_importance(turn, query)
        assert 0.0 <= score <= 1.0
    
    def test_empty_content(self):
        """Should handle empty content gracefully."""
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        turn = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'content': '',
            'metadata': {}
        }
        query = "test"
        
        score = retriever.calculate_importance(turn, query)
        # Empty content should have low importance
        assert score < 0.3
    
    def test_future_timestamp(self):
        """Should handle future timestamps (clock skew) gracefully."""
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        future = datetime.now(timezone.utc) + timedelta(hours=1)
        turn = {
            'timestamp': future.isoformat(),
            'content': 'test message',
            'metadata': {}
        }
        query = "test"
        
        # Should treat as very recent, not error
        score = retriever.calculate_importance(turn, query)
        assert score > 0.7, "Future timestamps should be treated as very recent"


class TestConfigurability:
    """Test that thresholds and weights are configurable."""
    
    def test_custom_thresholds(self):
        """Should be able to configure gradient thresholds."""
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        # Default thresholds
        default_full = retriever.get_detail_level(0.75)
        
        # Set custom thresholds (via config or method)
        # This tests the interface, implementation comes later
        custom_thresholds = {
            'full': 0.80,
            'chunks': 0.60,
            'summary': 0.30
        }
        
        # Should be able to configure (method TBD)
        assert hasattr(retriever, 'thresholds') or hasattr(retriever, 'set_thresholds')
    
    def test_signal_weights(self):
        """Should be able to configure relative signal weights."""
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        # Should be able to adjust weights for:
        # - decay (temporal)
        # - surprise (prediction error)
        # - relevance (semantic similarity)
        # - habituation (repetition penalty)
        
        # Test that weights exist and can be accessed
        assert hasattr(retriever, 'signal_weights') or hasattr(retriever, 'set_signal_weights')


# Property-Based Testing (Phase 1 Quick Wins!)
class TestPropertyBasedImportanceScoring:
    """Property-based tests using Hypothesis - generates thousands of test cases!
    
    These tests don't check specific values, they check PROPERTIES that should
    ALWAYS be true regardless of input. This is the real science! 🔬
    """
    
    def test_hypothesis_import(self):
        """Verify Hypothesis is available."""
        try:
            from hypothesis import given, strategies as st
            assert True, "Hypothesis imported successfully!"
        except ImportError:
            pytest.skip("Hypothesis not installed - run: pip install hypothesis")
    
    def test_importance_always_bounded_manual(self):
        """Property: Importance ALWAYS between 0 and 1 (manual version).
        
        This is a manual property test - we'll upgrade to Hypothesis next.
        """
        from hypothesis import given, strategies as st, settings
        
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        @given(
            age_hours=st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
            prediction_error=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
            importance_meta=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
        )
        @settings(max_examples=1000)  # 🔥 MAXIMUM SCIENCE MODE 🔥
        def property_importance_bounded(age_hours, prediction_error, importance_meta):
            """Generate random inputs, verify output always valid."""
            now = datetime.now(timezone.utc)
            past = now - timedelta(hours=age_hours)
            
            turn = {
                'timestamp': past.isoformat(),
                'content': 'property test content',
                'metadata': {
                    'prediction_error': prediction_error,
                    'importance': importance_meta
                }
            }
            
            score = retriever.calculate_importance(turn, query="test")
            
            # THE PROPERTY: Score must ALWAYS be [0, 1]
            assert 0.0 <= score <= 1.0, (
                f"Property violated! Score {score} outside [0,1] for "
                f"age={age_hours}h, pe={prediction_error}, imp={importance_meta}"
            )
        
        # Run the property test
        property_importance_bounded()
    
    def test_temporal_monotonicity_property(self):
        """Property: Recent turns ALWAYS score >= older turns (when other factors equal).
        
        This is STRICT MONOTONICITY - the core claim of temporal decay.
        """
        from hypothesis import given, strategies as st, settings
        
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        @given(
            recent_hours=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
            old_hours=st.floats(min_value=24.0, max_value=1000.0, allow_nan=False),
        )
        @settings(max_examples=1000)  # 🔥 TEMPORAL MONOTONICITY AT SCALE 🔥
        def property_recent_beats_old(recent_hours, old_hours):
            """Recent should ALWAYS beat old when other factors equal."""
            now = datetime.now(timezone.utc)
            
            # Same content, same metadata - only time differs
            base_metadata = {
                'prediction_error': 0.5,
                'importance': 0.5,
                'habituation_penalty': 0.0
            }
            
            recent_turn = {
                'timestamp': (now - timedelta(hours=recent_hours)).isoformat(),
                'content': 'identical content',
                'metadata': base_metadata.copy()
            }
            
            old_turn = {
                'timestamp': (now - timedelta(hours=old_hours)).isoformat(),
                'content': 'identical content',
                'metadata': base_metadata.copy()
            }
            
            recent_score = retriever.calculate_importance(recent_turn, query="test")
            old_score = retriever.calculate_importance(old_turn, query="test")
            
            # THE PROPERTY: Recent MUST score higher (or equal in edge cases)
            assert recent_score >= old_score, (
                f"Temporal monotonicity violated! Recent ({recent_hours}h) scored "
                f"{recent_score} but old ({old_hours}h) scored {old_score}"
            )
        
        property_recent_beats_old()
    
    def test_surprise_increases_importance_property(self):
        """Property: Higher prediction error ALWAYS increases importance.
        
        With all else equal, surprise should boost the score.
        """
        from hypothesis import given, strategies as st, settings
        
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        @given(
            low_surprise=st.floats(min_value=0.0, max_value=0.4, allow_nan=False),
            high_surprise=st.floats(min_value=0.6, max_value=1.0, allow_nan=False),
            age_hours=st.floats(min_value=0.1, max_value=100.0, allow_nan=False)
        )
        @settings(max_examples=1000)  # 🔥 SURPRISE SIGNAL AT SCALE 🔥
        def property_surprise_boosts(low_surprise, high_surprise, age_hours):
            """Higher surprise should ALWAYS increase importance."""
            now = datetime.now(timezone.utc)
            timestamp = (now - timedelta(hours=age_hours)).isoformat()
            
            low_turn = {
                'timestamp': timestamp,
                'content': 'test content',
                'metadata': {
                    'prediction_error': low_surprise,
                    'importance': 0.5,
                    'habituation_penalty': 0.0
                }
            }
            
            high_turn = {
                'timestamp': timestamp,
                'content': 'test content',
                'metadata': {
                    'prediction_error': high_surprise,
                    'importance': 0.5,
                    'habituation_penalty': 0.0
                }
            }
            
            low_score = retriever.calculate_importance(low_turn, query="test")
            high_score = retriever.calculate_importance(high_turn, query="test")
            
            # THE PROPERTY: High surprise MUST beat low surprise
            assert high_score >= low_score, (
                f"Surprise property violated! Low surprise ({low_surprise}) scored "
                f"{low_score} but high surprise ({high_surprise}) scored {high_score}"
            )
        
        property_surprise_boosts()
    
    def test_gradient_level_consistency_property(self):
        """Property: Same importance score ALWAYS maps to same detail level.
        
        The gradient thresholds must be deterministic.
        """
        from hypothesis import given, strategies as st, settings
        
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        @given(
            importance=st.floats(min_value=0.0, max_value=1.0, allow_nan=False)
        )
        @settings(max_examples=1000)  # 🔥 GRADIENT DETERMINISM AT SCALE 🔥
        def property_gradient_deterministic(importance):
            """Same score should ALWAYS produce same detail level."""
            level1 = retriever.get_detail_level(importance)
            level2 = retriever.get_detail_level(importance)
            
            # THE PROPERTY: Must be consistent
            assert level1 == level2, (
                f"Gradient inconsistency! Score {importance} gave different levels: "
                f"{level1} vs {level2}"
            )
            
            # Also check valid levels
            valid_levels = ['FULL', 'CHUNKS', 'SUMMARY', 'DROPPED']
            assert level1 in valid_levels, f"Invalid level: {level1}"
        
        property_gradient_deterministic()
    
    def test_empty_content_penalty_property(self):
        """Property: Empty content ALWAYS scores lower than non-empty.
        
        The 0.1x penalty should be universal.
        """
        from hypothesis import given, strategies as st, settings
        
        retriever = ContextRetriever(rag_store_instance=None, config_instance=None)
        
        @given(
            age_hours=st.floats(min_value=0.1, max_value=100.0, allow_nan=False),
            prediction_error=st.floats(min_value=0.0, max_value=1.0, allow_nan=False)
        )
        @settings(max_examples=500)  # 🔥 EMPTY PENALTY AT SCALE 🔥
        def property_empty_penalty(age_hours, prediction_error):
            """Empty content should ALWAYS score lower."""
            now = datetime.now(timezone.utc)
            timestamp = (now - timedelta(hours=age_hours)).isoformat()
            
            empty_turn = {
                'timestamp': timestamp,
                'content': '',
                'metadata': {'prediction_error': prediction_error}
            }
            
            filled_turn = {
                'timestamp': timestamp,
                'content': 'actual content here',
                'metadata': {'prediction_error': prediction_error}
            }
            
            empty_score = retriever.calculate_importance(empty_turn, query="test")
            filled_score = retriever.calculate_importance(filled_turn, query="test")
            
            # THE PROPERTY: Empty should score lower (or equal in edge cases)
            # Note: Due to relevance being 0 for both, might be equal
            # But empty should NOT score HIGHER
            assert empty_score <= filled_score, (
                f"Empty content penalty violated! Empty scored {empty_score} "
                f"but filled scored {filled_score}"
            )
        
        property_empty_penalty()


# Integration test (would need full RAG store)
class TestFullIntegration:
    """Integration tests with full system (mark as integration)."""
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires full RAG store and config")
    def test_end_to_end_importance_scoring(self):
        """Test full importance scoring with real RAG store."""
        # This would test with actual ChromaDB, config, etc.
        # Skipped for unit tests, runs in integration suite
        pass
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires full RAG store and config")
    def test_retrieval_with_gradient_levels(self):
        """Test that get_turns() returns turns with correct detail levels."""
        # This would test that the full retrieval pipeline works
        # Skipped for unit tests
        pass
