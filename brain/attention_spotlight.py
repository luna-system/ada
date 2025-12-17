"""Attentional spotlight - focus + periphery like human attention.

Biological inspiration: Humans can hold ~4 items in sharp focus (attentional
spotlight) with remaining context in peripheral awareness. This saves cognitive
resources by providing full detail only where needed.

Key concepts:
- **Spotlight:** ~4 most salient items, full detail, high token budget
- **Periphery:** Remaining items, compressed summaries, lower token budget
- **Salience:** Recency + importance + relevance combined score
"""
# @ai-indexable: core-utility
# @ai-purpose: Attention-based context prioritization (focus + periphery)
# @ai-dependencies: datetime

from datetime import datetime, timezone
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class AttentionItem:
    """Context item with attention metadata."""
    content: str
    salience_score: float  # 0.0-1.0, higher = more salient
    metadata: dict
    
    def format_detailed(self) -> str:
        """Full detail for spotlight items."""
        return self.content
    
    def format_summary(self) -> str:
        """Compressed summary for peripheral items."""
        # Extract first sentence or first 100 chars
        lines = self.content.split('\n')
        first_line = lines[0] if lines else self.content
        
        if len(first_line) > 100:
            return first_line[:97] + "..."
        return first_line


@dataclass
class AttentionDistribution:
    """Result of attention-based context assembly."""
    spotlight_items: List[AttentionItem]  # In focus
    periphery_items: List[AttentionItem]  # Peripheral awareness
    spotlight_tokens: int
    periphery_tokens: int
    total_tokens: int
    
    def format_context(self) -> str:
        """Format as prompt-ready context."""
        parts = []
        
        if self.spotlight_items:
            parts.append("## Focus (High Priority)")
            for item in self.spotlight_items:
                parts.append(item.format_detailed())
        
        if self.periphery_items:
            parts.append("\n## Peripheral Awareness (Summaries)")
            for item in self.periphery_items:
                parts.append(f"- {item.format_summary()}")
        
        return "\n".join(parts)


class AttentionalSpotlight:
    """Mimic human attentional focus: spotlight + periphery.
    
    Distributes token budget between high-detail focus and compressed periphery,
    mimicking how humans allocate attention.
    
    Example:
        spotlight = AttentionalSpotlight(
            spotlight_budget=4000,
            periphery_budget=8000,
            spotlight_size=4
        )
        
        # Calculate salience and distribute attention
        distribution = spotlight.apply_attention(memories)
        
        # Top 4 items get full detail (~4K tokens)
        # Rest get compressed summaries (~8K tokens)
        context = distribution.format_context()
    """
    
    def __init__(
        self,
        spotlight_budget: int = 4000,
        periphery_budget: int = 8000,
        spotlight_size: int = 4,
        recency_weight: float = 0.4,
        importance_weight: float = 0.3,
        relevance_weight: float = 0.3
    ):
        """Initialize attention spotlight.
        
        Args:
            spotlight_budget: Token budget for detailed focus items
            periphery_budget: Token budget for compressed peripheral items
            spotlight_size: Number of items in spotlight (default: 4, Miller's Law)
            recency_weight: Weight for recency in salience (0.0-1.0)
            importance_weight: Weight for importance in salience (0.0-1.0)
            relevance_weight: Weight for relevance in salience (0.0-1.0)
        """
        self.spotlight_budget = spotlight_budget
        self.periphery_budget = periphery_budget
        self.spotlight_size = spotlight_size
        
        # Salience weights (should sum to 1.0)
        total = recency_weight + importance_weight + relevance_weight
        self.recency_weight = recency_weight / total
        self.importance_weight = importance_weight / total
        self.relevance_weight = relevance_weight / total
    
    def calculate_salience(
        self,
        content: str,
        metadata: dict,
        distance: float = 0.5
    ) -> float:
        """Calculate salience score for a context item.
        
        Salience = weighted combination of:
        - Recency (how recent is it?)
        - Importance (how important did we mark it?)
        - Relevance (how relevant to current query?)
        
        Args:
            content: The context content
            metadata: Metadata dict with timestamp, importance
            distance: Vector search distance (lower = more relevant)
        
        Returns:
            Salience score (0.0-1.0), higher = more salient
        """
        # Recency score (decay over time)
        timestamp_str = metadata.get('timestamp', datetime.now(timezone.utc).isoformat())
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            hours_ago = (datetime.now(timezone.utc) - timestamp).total_seconds() / 3600
            # Decay over ~100 hours
            recency_score = max(0.0, 1.0 - (hours_ago / 100.0))
        except (ValueError, AttributeError):
            recency_score = 0.5  # Default if timestamp invalid
        
        # Importance score (direct from metadata)
        importance_score = float(metadata.get('importance', 0.5))
        
        # Relevance score (from vector search distance)
        # Lower distance = higher relevance
        relevance_score = 1.0 - min(1.0, distance)
        
        # Weighted combination
        salience = (
            self.recency_weight * recency_score +
            self.importance_weight * importance_score +
            self.relevance_weight * relevance_score
        )
        
        return max(0.0, min(1.0, salience))
    
    def apply_attention(
        self,
        items: List[Dict],
        token_counter=None
    ) -> AttentionDistribution:
        """Apply attentional spotlight to context items.
        
        Args:
            items: List of context dicts with 'content', 'metadata', 'distance'
            token_counter: Optional callable to count tokens (defaults to simple heuristic)
        
        Returns:
            AttentionDistribution with spotlight and periphery items
        """
        if token_counter is None:
            # Simple heuristic: ~4 chars per token
            token_counter = lambda text: len(text) // 4
        
        # Calculate salience for all items
        attention_items = []
        for item in items:
            salience = self.calculate_salience(
                content=item.get('content', ''),
                metadata=item.get('metadata', {}),
                distance=item.get('distance', 0.5)
            )
            
            attention_items.append(AttentionItem(
                content=item.get('content', ''),
                salience_score=salience,
                metadata=item.get('metadata', {})
            ))
        
        # Sort by salience (highest first)
        attention_items.sort(key=lambda x: x.salience_score, reverse=True)
        
        # Split into spotlight and periphery
        spotlight_items = attention_items[:self.spotlight_size]
        periphery_items = attention_items[self.spotlight_size:]
        
        # Count tokens
        spotlight_tokens = sum(token_counter(item.format_detailed()) for item in spotlight_items)
        periphery_tokens = sum(token_counter(item.format_summary()) for item in periphery_items)
        
        return AttentionDistribution(
            spotlight_items=spotlight_items,
            periphery_items=periphery_items,
            spotlight_tokens=spotlight_tokens,
            periphery_tokens=periphery_tokens,
            total_tokens=spotlight_tokens + periphery_tokens
        )
    
    def get_stats(self, distribution: AttentionDistribution) -> dict:
        """Get attention distribution statistics.
        
        Args:
            distribution: AttentionDistribution from apply_attention()
        
        Returns:
            Dict with attention metrics
        """
        spotlight_count = len(distribution.spotlight_items)
        periphery_count = len(distribution.periphery_items)
        total_count = spotlight_count + periphery_count
        
        avg_salience_spotlight = (
            sum(item.salience_score for item in distribution.spotlight_items) / spotlight_count
            if spotlight_count > 0 else 0.0
        )
        
        avg_salience_periphery = (
            sum(item.salience_score for item in distribution.periphery_items) / periphery_count
            if periphery_count > 0 else 0.0
        )
        
        return {
            'spotlight_count': spotlight_count,
            'periphery_count': periphery_count,
            'total_items': total_count,
            'spotlight_tokens': distribution.spotlight_tokens,
            'periphery_tokens': distribution.periphery_tokens,
            'total_tokens': distribution.total_tokens,
            'avg_salience_spotlight': avg_salience_spotlight,
            'avg_salience_periphery': avg_salience_periphery,
            'spotlight_budget': self.spotlight_budget,
            'periphery_budget': self.periphery_budget,
            'within_budget': (
                distribution.spotlight_tokens <= self.spotlight_budget and
                distribution.periphery_tokens <= self.periphery_budget
            )
        }
