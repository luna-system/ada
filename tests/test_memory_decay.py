"""Tests for memory decay weighting (Ebbinghaus curve)."""
import pytest
from datetime import datetime, timezone, timedelta
import math

from brain.memory_decay import MemoryDecayWeighter, apply_decay_to_memories


class TestMemoryDecayWeighter:
    """Test Ebbinghaus forgetting curve implementation."""
    
    def test_initialization(self):
        """Test weighter initialization."""
        weighter = MemoryDecayWeighter(time_scale_hours=100.0)
        assert weighter.time_scale_hours == 100.0
    
    def test_recent_memory_high_weight(self):
        """Recent memories should have high weight."""
        weighter = MemoryDecayWeighter()
        
        # Memory from 1 hour ago
        timestamp = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        weight = weighter.calculate_weight(
            timestamp=timestamp,
            importance=0.5,
            base_relevance=0.8
        )
        
        # Should be close to base relevance
        assert weight > 0.7
        assert weight <= 1.0
    
    def test_old_memory_decayed_weight(self):
        """Old memories should have lower weight."""
        weighter = MemoryDecayWeighter(time_scale_hours=100.0)
        
        # Memory from 200 hours ago (2x time scale)
        timestamp = (datetime.now(timezone.utc) - timedelta(hours=200)).isoformat()
        weight = weighter.calculate_weight(
            timestamp=timestamp,
            importance=0.5,
            base_relevance=0.8
        )
        
        # Should be significantly decayed
        assert weight < 0.5
    
    def test_importance_slows_decay(self):
        """Important memories should decay slower."""
        weighter = MemoryDecayWeighter(time_scale_hours=100.0)
        timestamp = (datetime.now(timezone.utc) - timedelta(hours=150)).isoformat()
        
        # Low importance
        weight_low = weighter.calculate_weight(
            timestamp=timestamp,
            importance=0.1,
            base_relevance=0.8
        )
        
        # High importance
        weight_high = weighter.calculate_weight(
            timestamp=timestamp,
            importance=0.9,
            base_relevance=0.8
        )
        
        # High importance should have higher weight
        assert weight_high > weight_low
    
    def test_half_life_calculation(self):
        """Test half-life calculation."""
        weighter = MemoryDecayWeighter(time_scale_hours=100.0)
        
        # Low importance
        half_life_low = weighter.calculate_half_life(importance=0.1)
        
        # High importance
        half_life_high = weighter.calculate_half_life(importance=0.9)
        
        # High importance = longer half-life
        assert half_life_high > half_life_low
        
        # Should be ln(2) * strength
        expected = math.log(2) * 100.0 * (1.0 + 0.1)
        assert abs(half_life_low - expected) < 0.1
    
    def test_invalid_timestamp_defaults_recent(self):
        """Invalid timestamp should default to recent (no decay)."""
        weighter = MemoryDecayWeighter()
        
        weight = weighter.calculate_weight(
            timestamp="invalid",
            importance=0.5,
            base_relevance=0.8
        )
        
        # Should be close to base * importance boost
        assert weight > 0.8
    
    def test_decay_stats(self):
        """Test decay statistics generation."""
        weighter = MemoryDecayWeighter(time_scale_hours=100.0)
        
        stats = weighter.get_decay_stats(hours_elapsed=100.0, importance=0.5)
        
        assert 'hours_elapsed' in stats
        assert 'importance' in stats
        assert 'decay_factor' in stats
        assert 'half_life_hours' in stats
        assert 'percentage_retained' in stats
        
        # At time scale with importance boost, should be ~51% retained (e^(-100/150))
        # Strength = time_scale * (1 + importance) = 100 * 1.5 = 150
        assert 45 < stats['percentage_retained'] < 55
    
    def test_weight_clamped_to_valid_range(self):
        """Weight should be clamped to [0, 1]."""
        weighter = MemoryDecayWeighter()
        
        # Very recent + very important (might exceed 1.0)
        timestamp = datetime.now(timezone.utc).isoformat()
        weight = weighter.calculate_weight(
            timestamp=timestamp,
            importance=1.0,
            base_relevance=1.0
        )
        
        assert 0.0 <= weight <= 1.0


class TestApplyDecayToMemories:
    """Test apply_decay_to_memories helper function."""
    
    def test_apply_decay_to_memory_list(self):
        """Test applying decay to list of memories."""
        now = datetime.now(timezone.utc)
        
        memories = [
            {
                'content': 'Old unimportant memory',
                'metadata': {
                    'timestamp': (now - timedelta(hours=200)).isoformat(),
                    'importance': 0.1
                },
                'distance': 0.2  # Low distance = high relevance
            },
            {
                'content': 'Recent important memory',
                'metadata': {
                    'timestamp': (now - timedelta(hours=1)).isoformat(),
                    'importance': 0.9
                },
                'distance': 0.5  # Higher distance = lower relevance
            }
        ]
        
        weighter = MemoryDecayWeighter(time_scale_hours=100.0)
        weighted = apply_decay_to_memories(memories, weighter)
        
        # Should be re-sorted with decay weights
        assert len(weighted) == 2
        assert 'decay_weight' in weighted[0]['metadata']
        
        # Recent important memory should be first despite higher distance
        assert weighted[0]['content'] == 'Recent important memory'
    
    def test_creates_default_weighter(self):
        """Test that default weighter is created if None."""
        memories = [
            {
                'content': 'Test memory',
                'metadata': {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'importance': 0.5
                },
                'distance': 0.3
            }
        ]
        
        weighted = apply_decay_to_memories(memories, weighter=None)
        
        assert len(weighted) == 1
        assert 'decay_weight' in weighted[0]['metadata']
    
    def test_handles_missing_metadata(self):
        """Test graceful handling of missing metadata."""
        memories = [
            {
                'content': 'Memory with minimal metadata',
                'metadata': {},  # No timestamp or importance
                'distance': 0.3
            }
        ]
        
        weighted = apply_decay_to_memories(memories)
        
        # Should not crash
        assert len(weighted) == 1
        assert 'decay_weight' in weighted[0]['metadata']
