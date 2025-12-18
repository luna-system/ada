"""Tests for prediction error detection (Phase 3 biomimetic features)."""

import pytest
from brain.prediction_error import (
    PredictionErrorDetector,
    UncertaintyType,
    UncertaintySignal,
    PredictionError
)


class TestPredictionErrorDetector:
    """Test prediction error detection system."""
    
    def test_initialization(self):
        """Test detector initialization."""
        detector = PredictionErrorDetector()
        
        assert detector.enabled
        assert detector.uncertainty_threshold == 0.7
        assert detector.min_signals_for_error == 2
        assert len(detector.detected_signals) == 0
    
    def test_explicit_uncertainty_detection(self):
        """Test detection of explicit uncertainty statements."""
        detector = PredictionErrorDetector(min_signals_for_error=1)
        
        # Test various explicit uncertainty patterns
        test_cases = [
            "I'm not sure about that",
            "I don't know the answer",
            "I don't have information about this",
            "I would need to know more",
            "Unfortunately, I can't help with that",
        ]
        
        for text in test_cases:
            detector.reset()
            error = detector.process_chunk(text)
            
            # Should detect explicit uncertainty
            assert len(detector.detected_signals) > 0
            assert detector.detected_signals[0].type == UncertaintyType.EXPLICIT_UNCERTAINTY
            assert detector.detected_signals[0].confidence == 1.0
    
    def test_hedging_detection(self):
        """Test detection of hedging language."""
        detector = PredictionErrorDetector(min_signals_for_error=1)
        
        # Multiple hedge words should trigger
        text = "This might possibly be the case, perhaps it could work, maybe."
        error = detector.process_chunk(text)
        
        # Should detect hedging
        signals = [s for s in detector.detected_signals if s.type == UncertaintyType.HEDGING]
        assert len(signals) > 0
    
    def test_information_request_detection(self):
        """Test detection of information requests."""
        detector = PredictionErrorDetector(min_signals_for_error=1)
        
        text = "Could you provide more details about this topic?"
        error = detector.process_chunk(text)
        
        # Should detect information request
        assert len(detector.detected_signals) > 0
        assert any(s.type == UncertaintyType.INFORMATION_REQUEST for s in detector.detected_signals)
    
    def test_thinking_marker_detection(self):
        """Test detection of thinking/reasoning markers."""
        detector = PredictionErrorDetector(min_signals_for_error=1)
        
        test_cases = [
            "[thinking] about the problem",
            "<think>Let me consider this</think>",
            "<reasoning>This requires thought</reasoning>",
            "Let me think about that for a moment",
        ]
        
        for text in test_cases:
            detector.reset()
            error = detector.process_chunk(text)
            
            # Should detect thinking marker
            assert any(s.type == UncertaintyType.THINKING_MARKER for s in detector.detected_signals)
    
    def test_repetition_detection(self):
        """Test detection of repetitive content."""
        detector = PredictionErrorDetector(min_signals_for_error=1)
        
        # Repeated sentence
        text = "This is a sentence. This is a sentence. Different content here."
        error = detector.process_chunk(text)
        
        # Should detect repetition
        assert any(s.type == UncertaintyType.REPETITION for s in detector.detected_signals)
    
    def test_no_false_positives(self):
        """Test confident responses don't trigger false positives."""
        detector = PredictionErrorDetector(min_signals_for_error=2)
        
        # Confident, certain response
        text = "The answer is clearly X because of Y. This is well-documented."
        error = detector.process_chunk(text)
        
        # Should not detect prediction error
        assert error is None or error.confidence < 0.7
    
    def test_multiple_signals_build_error(self):
        """Test multiple uncertainty signals trigger prediction error."""
        detector = PredictionErrorDetector(min_signals_for_error=2)
        
        # First chunk - one signal
        error1 = detector.process_chunk("I'm not sure about this. ")
        assert error1 is None  # Not enough signals yet
        
        # Second chunk - second signal
        error2 = detector.process_chunk("I would need more information.")
        
        # Should now trigger prediction error
        assert error2 is not None
        assert len(error2.uncertainty_signals) >= 2
    
    def test_confidence_calculation(self):
        """Test prediction error confidence calculation."""
        detector = PredictionErrorDetector(min_signals_for_error=1)
        
        # High confidence explicit statement
        text = "I'm not sure and I don't know the answer."
        error = detector.process_chunk(text)
        
        assert error is not None
        assert error.confidence > 0.8  # Should be high confidence
    
    def test_dominant_type_detection(self):
        """Test dominant uncertainty type is correctly identified."""
        detector = PredictionErrorDetector(min_signals_for_error=1)
        
        # Multiple explicit uncertainty signals
        text = "I'm not sure. I don't know. I lack information."
        error = detector.process_chunk(text)
        
        assert error is not None
        assert error.error_type == UncertaintyType.EXPLICIT_UNCERTAINTY
    
    def test_topic_extraction(self):
        """Test suggested topics are extracted from text."""
        detector = PredictionErrorDetector(min_signals_for_error=1)
        
        text = "I'm not sure about Python FastAPI and ChromaDB integration."
        error = detector.process_chunk(text)
        
        assert error is not None
        # Should extract capitalized words as topics
        assert any('Python' in topic or 'FastAPI' in topic or 'ChromaDB' in topic
                   for topic in error.suggested_topics)
    
    def test_immediate_action_flag(self):
        """Test immediate action flag for urgent errors."""
        detector = PredictionErrorDetector(min_signals_for_error=1)
        
        # Explicit uncertainty should trigger immediate action
        text = "I don't have information about this topic."
        error = detector.process_chunk(text)
        
        assert error is not None
        assert error.requires_immediate_action
    
    def test_disabled_detector(self):
        """Test detector can be disabled."""
        detector = PredictionErrorDetector(enabled=False)
        
        text = "I'm not sure about anything."
        error = detector.process_chunk(text)
        
        # Should not detect anything when disabled
        assert error is None
        assert len(detector.detected_signals) == 0
    
    def test_reset_clears_state(self):
        """Test reset clears detector state."""
        detector = PredictionErrorDetector()
        
        # Accumulate some state
        detector.process_chunk("I'm not sure. ")
        detector.process_chunk("I don't know.")
        
        assert len(detector.accumulated_text) > 0
        assert len(detector.detected_signals) > 0
        
        # Reset
        detector.reset()
        
        assert len(detector.accumulated_text) == 0
        assert len(detector.detected_signals) == 0
    
    def test_stats_tracking(self):
        """Test statistics tracking."""
        detector = PredictionErrorDetector()
        
        detector.process_chunk("I'm not sure. Maybe this could work.")
        
        stats = detector.get_stats()
        
        assert 'total_signals' in stats
        assert 'signal_types' in stats
        assert 'text_length' in stats
        assert 'enabled' in stats
        
        assert stats['total_signals'] > 0
        assert stats['text_length'] > 0
    
    def test_uncertainty_threshold_filtering(self):
        """Test uncertainty threshold filters low-confidence signals."""
        detector = PredictionErrorDetector(
            uncertainty_threshold=0.9,  # Very high threshold
            min_signals_for_error=1
        )
        
        # Hedging has lower confidence (0.7)
        text = "Maybe possibly perhaps this might work."
        error = detector.process_chunk(text)
        
        # Should still build error but may adjust confidence
        if error:
            # All signals should meet some minimum bar
            assert all(s.confidence > 0.0 for s in error.uncertainty_signals)
    
    def test_streaming_chunk_processing(self):
        """Test processing multiple streaming chunks."""
        detector = PredictionErrorDetector(min_signals_for_error=2)
        
        # Simulate streaming response
        chunks = [
            "Let me think about ",
            "this question. I'm ",
            "not entirely sure, ",
            "but I would need ",
            "more context to answer."
        ]
        
        error = None
        for chunk in chunks:
            result = detector.process_chunk(chunk)
            if result:
                error = result
                break
        
        # Should eventually detect error
        assert error is not None
        assert len(error.uncertainty_signals) >= 2
    
    def test_uncertainty_signal_dataclass(self):
        """Test UncertaintySignal dataclass."""
        signal = UncertaintySignal(
            type=UncertaintyType.EXPLICIT_UNCERTAINTY,
            text_snippet="I'm not sure",
            confidence=1.0,
            suggested_context="more information needed",
            position=42
        )
        
        assert signal.type == UncertaintyType.EXPLICIT_UNCERTAINTY
        assert signal.text_snippet == "I'm not sure"
        assert signal.confidence == 1.0
        assert signal.suggested_context == "more information needed"
        assert signal.position == 42
    
    def test_prediction_error_dataclass(self):
        """Test PredictionError dataclass."""
        signals = [
            UncertaintySignal(
                type=UncertaintyType.EXPLICIT_UNCERTAINTY,
                text_snippet="I don't know",
                confidence=1.0
            )
        ]
        
        error = PredictionError(
            uncertainty_signals=signals,
            error_type=UncertaintyType.EXPLICIT_UNCERTAINTY,
            confidence=0.95,
            suggested_topics=["Python", "FastAPI"],
            requires_immediate_action=True
        )
        
        assert len(error.uncertainty_signals) == 1
        assert error.error_type == UncertaintyType.EXPLICIT_UNCERTAINTY
        assert error.confidence == 0.95
        assert "Python" in error.suggested_topics
        assert error.requires_immediate_action
