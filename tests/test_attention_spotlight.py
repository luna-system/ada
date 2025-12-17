"""Tests for attentional spotlight."""
import pytest
from datetime import datetime, timezone, timedelta

from brain.attention_spotlight import (
    AttentionalSpotlight,
    AttentionItem,
    AttentionDistribution
)


class TestAttentionItem:
    """Test AttentionItem dataclass."""
    
    def test_format_detailed(self):
        """Test detailed formatting."""
        item = AttentionItem(
            content="This is a detailed memory about Python.",
            salience_score=0.8,
            metadata={'importance': 0.7}
        )
        
        detailed = item.format_detailed()
        assert detailed == "This is a detailed memory about Python."
    
    def test_format_summary_short(self):
        """Test summary formatting for short content."""
        item = AttentionItem(
            content="Short memory.",
            salience_score=0.5,
            metadata={}
        )
        
        summary = item.format_summary()
        assert summary == "Short memory."
    
    def test_format_summary_long(self):
        """Test summary formatting for long content."""
        long_content = "A" * 150  # 150 chars
        item = AttentionItem(
            content=long_content,
            salience_score=0.3,
            metadata={}
        )
        
        summary = item.format_summary()
        assert len(summary) <= 103  # 100 + "..."
        assert summary.endswith("...")


class TestAttentionalSpotlight:
    """Test AttentionalSpotlight functionality."""
    
    def test_initialization(self):
        """Test spotlight initialization."""
        spotlight = AttentionalSpotlight(
            spotlight_budget=4000,
            periphery_budget=8000,
            spotlight_size=4
        )
        
        assert spotlight.spotlight_budget == 4000
        assert spotlight.periphery_budget == 8000
        assert spotlight.spotlight_size == 4
        
        # Weights should sum to 1.0
        total_weight = (
            spotlight.recency_weight +
            spotlight.importance_weight +
            spotlight.relevance_weight
        )
        assert abs(total_weight - 1.0) < 0.01
    
    def test_calculate_salience_recent_important(self):
        """Recent + important should have high salience."""
        spotlight = AttentionalSpotlight()
        
        salience = spotlight.calculate_salience(
            content="Test content",
            metadata={
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'importance': 0.9
            },
            distance=0.1  # Low distance = high relevance
        )
        
        assert salience > 0.7  # Should be high
    
    def test_calculate_salience_old_unimportant(self):
        """Old + unimportant should have low salience."""
        spotlight = AttentionalSpotlight()
        
        old_timestamp = (datetime.now(timezone.utc) - timedelta(hours=200)).isoformat()
        
        salience = spotlight.calculate_salience(
            content="Test content",
            metadata={
                'timestamp': old_timestamp,
                'importance': 0.1
            },
            distance=0.8  # High distance = low relevance
        )
        
        assert salience < 0.3  # Should be low
    
    def test_apply_attention_spotlight_size(self):
        """Test spotlight size limit."""
        spotlight = AttentionalSpotlight(spotlight_size=3)
        
        items = [
            {
                'content': f"Memory {i}",
                'metadata': {'importance': 0.5 + (i * 0.1)},
                'distance': 0.2
            }
            for i in range(10)
        ]
        
        distribution = spotlight.apply_attention(items)
        
        assert len(distribution.spotlight_items) == 3
        assert len(distribution.periphery_items) == 7
    
    def test_apply_attention_salience_ordering(self):
        """Test that highest salience items go to spotlight."""
        spotlight = AttentionalSpotlight(spotlight_size=2)
        
        now = datetime.now(timezone.utc)
        
        items = [
            {
                'content': "Old unimportant",
                'metadata': {
                    'timestamp': (now - timedelta(hours=200)).isoformat(),
                    'importance': 0.1
                },
                'distance': 0.8
            },
            {
                'content': "Recent important",
                'metadata': {
                    'timestamp': now.isoformat(),
                    'importance': 0.9
                },
                'distance': 0.1
            },
            {
                'content': "Medium",
                'metadata': {
                    'timestamp': (now - timedelta(hours=50)).isoformat(),
                    'importance': 0.5
                },
                'distance': 0.5
            }
        ]
        
        distribution = spotlight.apply_attention(items)
        
        # Recent important should be in spotlight
        spotlight_contents = [item.content for item in distribution.spotlight_items]
        assert "Recent important" in spotlight_contents
        
        # Old unimportant should be in periphery
        periphery_contents = [item.content for item in distribution.periphery_items]
        assert "Old unimportant" in periphery_contents
    
    def test_apply_attention_token_counting(self):
        """Test token counting in distribution."""
        spotlight = AttentionalSpotlight(spotlight_size=2)
        
        items = [
            {'content': "A" * 100, 'metadata': {'importance': 0.9}, 'distance': 0.1},
            {'content': "B" * 100, 'metadata': {'importance': 0.8}, 'distance': 0.2},
            {'content': "C" * 100, 'metadata': {'importance': 0.3}, 'distance': 0.7}
        ]
        
        distribution = spotlight.apply_attention(items)
        
        # Should have token counts
        assert distribution.spotlight_tokens > 0
        assert distribution.periphery_tokens > 0
        assert distribution.total_tokens == (
            distribution.spotlight_tokens + distribution.periphery_tokens
        )
    
    def test_format_context(self):
        """Test formatted context output."""
        spotlight = AttentionalSpotlight(spotlight_size=1)
        
        items = [
            {'content': "Focus item", 'metadata': {'importance': 0.9}, 'distance': 0.1},
            {'content': "Peripheral item", 'metadata': {'importance': 0.3}, 'distance': 0.7}
        ]
        
        distribution = spotlight.apply_attention(items)
        formatted = distribution.format_context()
        
        # Should have sections
        assert "## Focus (High Priority)" in formatted
        assert "## Peripheral Awareness (Summaries)" in formatted
        
        # Focus item should be detailed
        assert "Focus item" in formatted
        
        # Peripheral should be summarized (starts with dash)
        assert "- Peripheral item" in formatted
    
    def test_get_stats(self):
        """Test statistics generation."""
        spotlight = AttentionalSpotlight(spotlight_size=2)
        
        items = [
            {'content': f"Item {i}", 'metadata': {'importance': 0.5}, 'distance': 0.5}
            for i in range(5)
        ]
        
        distribution = spotlight.apply_attention(items)
        stats = spotlight.get_stats(distribution)
        
        assert stats['spotlight_count'] == 2
        assert stats['periphery_count'] == 3
        assert stats['total_items'] == 5
        assert 'spotlight_tokens' in stats
        assert 'periphery_tokens' in stats
        assert 'avg_salience_spotlight' in stats
        assert 'avg_salience_periphery' in stats
    
    def test_periphery_compression_saves_tokens(self):
        """Test that periphery uses fewer tokens than full detail."""
        spotlight = AttentionalSpotlight(spotlight_size=0)  # All periphery
        
        long_content = "This is a very long memory. " * 50  # ~1400 chars
        
        items = [
            {'content': long_content, 'metadata': {'importance': 0.5}, 'distance': 0.5}
        ]
        
        distribution = spotlight.apply_attention(items)
        
        # Periphery should be much shorter
        full_tokens = len(long_content) // 4
        periphery_tokens = distribution.periphery_tokens
        
        assert periphery_tokens < full_tokens * 0.2  # Should save >80%
