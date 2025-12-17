"""Context habituation - reduce weight of repeated, unchanged context.

Biological inspiration: Humans habituate to repeated stimuli (stop noticing
background noise, familiar sights). This saves cognitive resources by
reducing attention to predictable, unchanging information.

Dishabituation occurs when stimulus changes (novelty detection).
"""
# @ai-indexable: core-utility
# @ai-purpose: Track repeated context and reduce priority via habituation
# @ai-dependencies: hashlib, datetime

import hashlib
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional


@dataclass
class HabituationState:
    """Track habituation state for a context item."""
    content_hash: str
    first_seen: datetime
    last_seen: datetime
    repetition_count: int
    
    def age_seconds(self) -> float:
        """Time since first seen."""
        return (datetime.now(timezone.utc) - self.first_seen).total_seconds()
    
    def time_since_last_seconds(self) -> float:
        """Time since last seen."""
        return (datetime.now(timezone.utc) - self.last_seen).total_seconds()


class ContextHabituation:
    """Track and manage context habituation.
    
    Key concepts:
    - **Habituation threshold**: After N repetitions, reduce weight
    - **Habituation weight**: Multiplier for habituated items (0.0-1.0)
    - **Dishabituation**: Changed content resets counter (novelty detection)
    - **Decay**: Old habituation states expire (prevents infinite memory)
    
    Example:
        hab = ContextHabituation(threshold=3, habituated_weight=0.1)
        
        # First few times: full weight
        weight = hab.get_weight("persona", persona_text)  # 1.0
        weight = hab.get_weight("persona", persona_text)  # 1.0
        weight = hab.get_weight("persona", persona_text)  # 1.0
        
        # After threshold: reduced weight
        weight = hab.get_weight("persona", persona_text)  # 0.1 (habituated!)
        
        # If content changes: reset
        weight = hab.get_weight("persona", new_persona_text)  # 1.0 (dishabituation!)
    """
    
    def __init__(
        self,
        threshold: int = 3,
        habituated_weight: float = 0.1,
        decay_hours: float = 24.0
    ):
        """Initialize habituation tracker.
        
        Args:
            threshold: Number of repetitions before habituation kicks in
            habituated_weight: Weight multiplier for habituated items (0.0-1.0)
                              0.0 = skip entirely, 0.1 = "peripheral awareness"
            decay_hours: Hours before old habituation state expires
        """
        self.threshold = threshold
        self.habituated_weight = habituated_weight
        self.decay_hours = decay_hours
        self.states: dict[str, HabituationState] = {}
    
    def _hash_content(self, content: str) -> str:
        """Create content hash for comparison."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _cleanup_expired(self):
        """Remove old habituation states to prevent unbounded growth."""
        now = datetime.now(timezone.utc)
        expired_keys = []
        
        for key, state in self.states.items():
            hours_since_last = (now - state.last_seen).total_seconds() / 3600
            if hours_since_last > self.decay_hours:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.states[key]
    
    def get_weight(self, context_key: str, content: str) -> float:
        """Get weight multiplier for context item.
        
        Args:
            context_key: Unique identifier for context type
                         (e.g., "persona", "faq", "system_notices")
            content: The actual content to check
        
        Returns:
            Weight multiplier (1.0 = full weight, <1.0 = habituated)
        """
        # Periodic cleanup
        if len(self.states) > 100:  # Cleanup threshold
            self._cleanup_expired()
        
        content_hash = self._hash_content(content)
        now = datetime.now(timezone.utc)
        
        if context_key not in self.states:
            # First time seeing this key
            self.states[context_key] = HabituationState(
                content_hash=content_hash,
                first_seen=now,
                last_seen=now,
                repetition_count=1
            )
            return 1.0  # Full weight
        
        state = self.states[context_key]
        
        if state.content_hash != content_hash:
            # Content changed! Dishabituation (reset)
            self.states[context_key] = HabituationState(
                content_hash=content_hash,
                first_seen=now,
                last_seen=now,
                repetition_count=1
            )
            return 1.0  # Full weight for novel content
        
        # Content unchanged, increment repetition count
        state.last_seen = now
        state.repetition_count += 1
        
        # Check if habituated
        if state.repetition_count >= self.threshold:
            return self.habituated_weight  # Reduced weight
        
        return 1.0  # Still below threshold, full weight
    
    def force_reset(self, context_key: str):
        """Force reset habituation for a key (manual dishabituation).
        
        Useful when you know content should be fresh (e.g., user requested
        persona change).
        """
        if context_key in self.states:
            del self.states[context_key]
    
    def get_state(self, context_key: str) -> Optional[HabituationState]:
        """Get current habituation state for debugging."""
        return self.states.get(context_key)
    
    def get_stats(self) -> dict:
        """Get habituation statistics for monitoring.
        
        Returns:
            Dict with habituation metrics
        """
        total_states = len(self.states)
        habituated_count = sum(
            1 for s in self.states.values()
            if s.repetition_count >= self.threshold
        )
        
        return {
            'total_tracked': total_states,
            'habituated_count': habituated_count,
            'threshold': self.threshold,
            'habituated_weight': self.habituated_weight,
            'decay_hours': self.decay_hours
        }
    
    def should_include(self, context_key: str, content: str) -> bool:
        """Check if context should be included at all.
        
        Convenience method for binary include/exclude decisions.
        
        Returns:
            True if weight > 0, False otherwise
        """
        weight = self.get_weight(context_key, content)
        return weight > 0.0
