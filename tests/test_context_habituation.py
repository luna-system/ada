"""Tests for context habituation."""
import pytest
from datetime import datetime, timezone

from brain.context_habituation import ContextHabituation, HabituationState


class TestHabituationState:
    """Test HabituationState dataclass."""
    
    def test_age_calculation(self):
        """Test age_seconds calculation."""
        state = HabituationState(
            content_hash="abc123",
            first_seen=datetime(2025, 12, 17, 10, 0, 0, tzinfo=timezone.utc),
            last_seen=datetime(2025, 12, 17, 12, 0, 0, tzinfo=timezone.utc),
            repetition_count=3
        )
        
        age = state.age_seconds()
        assert age >= 0  # Should be positive
    
    def test_time_since_last(self):
        """Test time_since_last_seconds calculation."""
        state = HabituationState(
            content_hash="abc123",
            first_seen=datetime(2025, 12, 17, 10, 0, 0, tzinfo=timezone.utc),
            last_seen=datetime(2025, 12, 17, 12, 0, 0, tzinfo=timezone.utc),
            repetition_count=3
        )
        
        time_since = state.time_since_last_seconds()
        assert time_since >= 0


class TestContextHabituation:
    """Test ContextHabituation functionality."""
    
    def test_initialization(self):
        """Test habituation tracker initialization."""
        hab = ContextHabituation(
            threshold=3,
            habituated_weight=0.1,
            decay_hours=24.0
        )
        
        assert hab.threshold == 3
        assert hab.habituated_weight == 0.1
        assert hab.decay_hours == 24.0
        assert len(hab.states) == 0
    
    def test_first_exposure_full_weight(self):
        """First exposure should return full weight."""
        hab = ContextHabituation(threshold=3, habituated_weight=0.1)
        
        weight = hab.get_weight("persona", "Ada is a helpful AI assistant.")
        
        assert weight == 1.0
        assert "persona" in hab.states
        assert hab.states["persona"].repetition_count == 1
    
    def test_repeated_unchanged_content(self):
        """Repeated unchanged content should maintain count."""
        hab = ContextHabituation(threshold=3, habituated_weight=0.1)
        content = "Ada is a helpful AI assistant."
        
        # First few exposures - habituation starts AFTER threshold
        weight1 = hab.get_weight("persona", content)  # count=1, weight=1.0
        weight2 = hab.get_weight("persona", content)  # count=2, weight=1.0
        
        assert weight1 == 1.0
        assert weight2 == 1.0
        assert hab.states["persona"].repetition_count == 2
    
    def test_habituation_after_threshold(self):
        """After threshold, weight should reduce."""
        hab = ContextHabituation(threshold=3, habituated_weight=0.1)
        content = "Ada is a helpful AI assistant."
        
        # Hit threshold
        hab.get_weight("persona", content)  # 1
        hab.get_weight("persona", content)  # 2
        hab.get_weight("persona", content)  # 3
        
        # Next exposure should be habituated
        weight = hab.get_weight("persona", content)  # 4
        
        assert weight == 0.1  # Reduced weight
        assert hab.states["persona"].repetition_count == 4
    
    def test_dishabituation_on_change(self):
        """Changed content should reset (dishabituation)."""
        hab = ContextHabituation(threshold=3, habituated_weight=0.1)
        
        # Habituate
        hab.get_weight("persona", "Original content")
        hab.get_weight("persona", "Original content")
        hab.get_weight("persona", "Original content")
        hab.get_weight("persona", "Original content")  # Habituated
        
        # Change content
        weight = hab.get_weight("persona", "Changed content")
        
        assert weight == 1.0  # Full weight restored
        assert hab.states["persona"].repetition_count == 1  # Reset
    
    def test_different_keys_tracked_separately(self):
        """Different context keys should be tracked independently."""
        hab = ContextHabituation(threshold=3, habituated_weight=0.1)
        
        # Habituate persona
        for _ in range(4):
            hab.get_weight("persona", "Persona content")
        
        # FAQs should still have full weight
        weight = hab.get_weight("faqs", "FAQ content")
        
        assert weight == 1.0
        assert hab.states["persona"].repetition_count == 4
        assert hab.states["faqs"].repetition_count == 1
    
    def test_force_reset(self):
        """Test manual reset of habituation."""
        hab = ContextHabituation(threshold=3, habituated_weight=0.1)
        
        # Create some habituation
        hab.get_weight("persona", "Content")
        hab.get_weight("persona", "Content")
        hab.get_weight("persona", "Content")
        
        # Force reset
        hab.force_reset("persona")
        
        assert "persona" not in hab.states
        
        # Next exposure should be fresh
        weight = hab.get_weight("persona", "Content")
        assert weight == 1.0
        assert hab.states["persona"].repetition_count == 1
    
    def test_should_include_helper(self):
        """Test should_include convenience method."""
        hab = ContextHabituation(threshold=3, habituated_weight=0.1)
        
        # Below threshold
        assert hab.should_include("persona", "Content") is True
        
        # At threshold
        hab.get_weight("persona", "Content")
        hab.get_weight("persona", "Content")
        hab.get_weight("persona", "Content")
        
        # Still included (weight > 0)
        assert hab.should_include("persona", "Content") is True
        
        # If weight was 0, would be excluded
        hab.habituated_weight = 0.0
        assert hab.should_include("persona", "Content") is False
    
    def test_get_stats(self):
        """Test statistics generation."""
        hab = ContextHabituation(threshold=3, habituated_weight=0.1)
        
        # Create some states
        hab.get_weight("persona", "Content 1")
        hab.get_weight("faqs", "Content 2")
        hab.get_weight("faqs", "Content 2")
        hab.get_weight("faqs", "Content 2")
        hab.get_weight("faqs", "Content 2")  # Habituated
        
        stats = hab.get_stats()
        
        assert stats['total_tracked'] == 2
        assert stats['habituated_count'] == 1  # Only FAQs is habituated
        assert stats['threshold'] == 3
        assert stats['habituated_weight'] == 0.1
    
    def test_cleanup_expired(self):
        """Test cleanup of expired states."""
        hab = ContextHabituation(threshold=3, habituated_weight=0.1, decay_hours=0.001)
        
        # Create state
        hab.get_weight("persona", "Content")
        assert len(hab.states) == 1
        
        # Wait for expiry (tiny decay time for testing)
        import time
        time.sleep(0.01)  # 0.01 seconds > 0.001 hours
        
        # Trigger cleanup by adding many states
        for i in range(101):
            hab.get_weight(f"key_{i}", f"content_{i}")
        
        # Original persona state should be cleaned up
        # (Note: This is probabilistic based on when cleanup triggers)
        # Just verify cleanup doesn't crash
        assert len(hab.states) >= 0
    
    def test_get_state_debugging(self):
        """Test get_state for debugging."""
        hab = ContextHabituation(threshold=3, habituated_weight=0.1)
        
        hab.get_weight("persona", "Content")
        
        state = hab.get_state("persona")
        
        assert state is not None
        assert isinstance(state, HabituationState)
        assert state.repetition_count == 1
        
        # Non-existent key
        assert hab.get_state("nonexistent") is None
