"""Prediction error detection - monitor LLM output for uncertainty.

Based on biological predictive processing: brains constantly predict sensory input
and only process prediction errors (when predictions fail). This saves energy by
not wasting processing on expected/redundant information.

For Ada: Monitor LLM output for uncertainty markers that indicate the model
needs additional context (prediction error → fetch more context).

@ai-indexable: biomimetic-phase3
@ai-purpose: Detect when LLM needs additional context mid-generation
@ai-dependencies: None (pure Python, regex-based)
@ai-related: brain/llm.py, brain/prompt_builder/prompt_assembler.py
"""

import logging
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set
from enum import Enum

logger = logging.getLogger(__name__)


class UncertaintyType(Enum):
    """Types of uncertainty signals in LLM output."""
    
    EXPLICIT_UNCERTAINTY = "explicit"  # "I'm not sure", "I don't know"
    HEDGING = "hedging"  # "might", "perhaps", "possibly"
    INFORMATION_REQUEST = "request"  # "I would need to know"
    THINKING_MARKER = "thinking"  # "[thinking]", <reasoning> tags
    REPETITION = "repetition"  # Repeating same content
    INCOMPLETE = "incomplete"  # Trailing off, unfinished sentences


@dataclass
class UncertaintySignal:
    """Detected uncertainty in LLM output."""
    
    type: UncertaintyType
    """Type of uncertainty detected"""
    
    text_snippet: str
    """The text that triggered detection"""
    
    confidence: float
    """Confidence this is real uncertainty (0.0-1.0)"""
    
    suggested_context: Optional[str] = None
    """What additional context might help"""
    
    position: int = 0
    """Character position in stream where detected"""


@dataclass
class PredictionError:
    """A detected prediction error requiring additional context."""
    
    uncertainty_signals: List[UncertaintySignal]
    """All uncertainty signals that contributed to this error"""
    
    error_type: UncertaintyType
    """Dominant type of uncertainty"""
    
    confidence: float
    """Confidence this is a real prediction error (0.0-1.0)"""
    
    suggested_topics: List[str] = field(default_factory=list)
    """Topics that might resolve the error"""
    
    requires_immediate_action: bool = False
    """Whether context injection should happen immediately"""


class PredictionErrorDetector:
    """Detect prediction errors in LLM output stream.
    
    Monitors streaming LLM output for uncertainty signals that indicate
    the model needs additional context to generate a good response.
    """
    
    # Uncertainty patterns (compiled regex)
    EXPLICIT_PATTERNS = [
        re.compile(r"I(?:'m| am) not sure", re.IGNORECASE),
        re.compile(r"I (?:don't|do not) (?:know|have)", re.IGNORECASE),
        re.compile(r"I (?:don't|do not) have (?:information|context|details)", re.IGNORECASE),
        re.compile(r"I would need (?:to know|more|additional)", re.IGNORECASE),
        re.compile(r"I lack (?:information|context|details)", re.IGNORECASE),
        re.compile(r"(?:Unfortunately|Sorry),? I (?:can't|cannot)", re.IGNORECASE),
    ]
    
    HEDGING_PATTERNS = [
        re.compile(r"\b(?:might|may|could|possibly|perhaps|maybe)\b", re.IGNORECASE),
        re.compile(r"\b(?:it seems|it appears|likely)\b", re.IGNORECASE),
        re.compile(r"\b(?:probably|potentially|presumably)\b", re.IGNORECASE),
    ]
    
    REQUEST_PATTERNS = [
        re.compile(r"(?:could you|can you) (?:provide|tell|give|share)", re.IGNORECASE),
        re.compile(r"(?:what|which) (?:about|regarding)", re.IGNORECASE),
        re.compile(r"I would need to (?:check|verify|look up)", re.IGNORECASE),
    ]
    
    THINKING_PATTERNS = [
        re.compile(r"\[thinking\]", re.IGNORECASE),
        re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL),
        re.compile(r"<reasoning>.*?</reasoning>", re.IGNORECASE | re.DOTALL),
        re.compile(r"let me think", re.IGNORECASE),
    ]
    
    def __init__(
        self,
        uncertainty_threshold: float = 0.7,
        min_signals_for_error: int = 2,
        enabled: bool = True
    ):
        """Initialize prediction error detector.
        
        Args:
            uncertainty_threshold: Minimum confidence to report uncertainty
            min_signals_for_error: Minimum signals to declare prediction error
            enabled: Whether detection is enabled
        """
        self.uncertainty_threshold = uncertainty_threshold
        self.min_signals_for_error = min_signals_for_error
        self.enabled = enabled
        
        # State tracking
        self.accumulated_text = ""
        self.detected_signals: List[UncertaintySignal] = []
        self.last_chunk_text = ""
    
    def process_chunk(self, chunk: str) -> Optional[PredictionError]:
        """Process a streaming chunk and detect prediction errors.
        
        Args:
            chunk: New text chunk from LLM stream
        
        Returns:
            PredictionError if detected, None otherwise
        """
        if not self.enabled:
            return None
        
        # Accumulate text
        self.accumulated_text += chunk
        self.last_chunk_text = chunk
        
        # Detect signals in accumulated text (to catch patterns split across chunks)
        # But only add new unique signals
        current_signal_texts = {s.text_snippet for s in self.detected_signals}
        new_signals = self._detect_signals(self.accumulated_text, position=len(self.accumulated_text))
        
        # Filter out duplicates
        unique_new_signals = [
            s for s in new_signals
            if s.text_snippet not in current_signal_texts
        ]
        self.detected_signals.extend(unique_new_signals)
        
        # Check if we have a prediction error
        if len(self.detected_signals) >= self.min_signals_for_error:
            return self._build_prediction_error()
        
        return None
    
    def _detect_signals(self, text: str, position: int) -> List[UncertaintySignal]:
        """Detect uncertainty signals in text chunk."""
        signals = []
        
        # Check explicit uncertainty
        for pattern in self.EXPLICIT_PATTERNS:
            match = pattern.search(text)
            if match:
                signals.append(UncertaintySignal(
                    type=UncertaintyType.EXPLICIT_UNCERTAINTY,
                    text_snippet=match.group(0),
                    confidence=1.0,  # High confidence - explicit statement
                    position=position
                ))
        
        # Check hedging (lower confidence)
        hedge_count = 0
        for pattern in self.HEDGING_PATTERNS:
            hedge_count += len(pattern.findall(text))
        
        if hedge_count >= 3:  # Multiple hedges indicate uncertainty
            signals.append(UncertaintySignal(
                type=UncertaintyType.HEDGING,
                text_snippet=f"{hedge_count} hedge words detected",
                confidence=0.7,  # Medium confidence
                position=position
            ))
        
        # Check information requests
        for pattern in self.REQUEST_PATTERNS:
            match = pattern.search(text)
            if match:
                signals.append(UncertaintySignal(
                    type=UncertaintyType.INFORMATION_REQUEST,
                    text_snippet=match.group(0),
                    confidence=0.9,
                    position=position
                ))
        
        # Check thinking markers (model is uncertain)
        for pattern in self.THINKING_PATTERNS:
            match = pattern.search(text)
            if match:
                signals.append(UncertaintySignal(
                    type=UncertaintyType.THINKING_MARKER,
                    text_snippet=match.group(0),
                    confidence=0.8,
                    position=position
                ))
        
        # Check for repetition (suggests lack of information)
        if self._detect_repetition(text):
            signals.append(UncertaintySignal(
                type=UncertaintyType.REPETITION,
                text_snippet="Repeated content detected",
                confidence=0.6,
                position=position
            ))
        
        return signals
    
    def _detect_repetition(self, text: str) -> bool:
        """Detect if text is repeating (sign of uncertainty)."""
        # Simple repetition detection: split into sentences and check duplicates
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
        
        if len(sentences) < 2:
            return False
        
        # Check if any sentence appears multiple times
        seen = set()
        for sentence in sentences:
            if sentence in seen:
                return True
            seen.add(sentence)
        
        return False
    
    def _build_prediction_error(self) -> PredictionError:
        """Build prediction error from accumulated signals."""
        # Filter by confidence threshold
        high_conf_signals = [
            s for s in self.detected_signals
            if s.confidence >= self.uncertainty_threshold
        ]
        
        if not high_conf_signals:
            # Use all signals if none meet threshold
            high_conf_signals = self.detected_signals
        
        # Determine dominant type
        type_counts = {}
        for signal in high_conf_signals:
            type_counts[signal.type] = type_counts.get(signal.type, 0) + 1
        
        dominant_type = max(type_counts.keys(), key=lambda t: type_counts[t])
        
        # Calculate overall confidence
        avg_confidence = sum(s.confidence for s in high_conf_signals) / len(high_conf_signals)
        
        # Suggest topics based on accumulated text
        suggested_topics = self._extract_topics(self.accumulated_text)
        
        # Determine if immediate action needed
        immediate = any(
            s.type == UncertaintyType.EXPLICIT_UNCERTAINTY
            for s in high_conf_signals
        )
        
        return PredictionError(
            uncertainty_signals=high_conf_signals,
            error_type=dominant_type,
            confidence=avg_confidence,
            suggested_topics=suggested_topics,
            requires_immediate_action=immediate
        )
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics that might need additional context.
        
        Simple keyword extraction - looks for capitalized words, technical terms.
        """
        # Find capitalized words (potential topics)
        words = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b', text)
        
        # Remove common words
        stopwords = {'The', 'This', 'That', 'These', 'Those', 'I', 'You', 'We', 'They'}
        topics = [w for w in words if w not in stopwords]
        
        # Deduplicate and limit
        unique_topics = list(dict.fromkeys(topics))[:5]
        
        return unique_topics
    
    def reset(self):
        """Reset detector state (e.g., at start of new response)."""
        self.accumulated_text = ""
        self.detected_signals.clear()
        self.last_chunk_text = ""
    
    def get_stats(self) -> Dict:
        """Get detection statistics."""
        signal_counts = {}
        for signal in self.detected_signals:
            signal_counts[signal.type.value] = signal_counts.get(signal.type.value, 0) + 1
        
        return {
            'total_signals': len(self.detected_signals),
            'signal_types': signal_counts,
            'text_length': len(self.accumulated_text),
            'enabled': self.enabled
        }
