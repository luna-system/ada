"""Memory decay weighting using Ebbinghaus forgetting curve.

Biological inspiration: Human memory retention follows exponential decay,
with importance acting as a "memory strength" that slows forgetting.

R = e^(-t/S)
where:
  R = retention (weight)
  t = time elapsed
  S = strength (importance)
"""
# @ai-indexable: core-utility
# @ai-purpose: Apply biological forgetting curves to memory weighting
# @ai-dependencies: datetime, math

import math
from datetime import datetime, timezone
from typing import Optional


class MemoryDecayWeighter:
    """Apply Ebbinghaus forgetting curve to memory relevance scores.
    
    This mimics how human memory works: recent memories are more accessible,
    but important memories resist decay longer.
    
    Example:
        weighter = MemoryDecayWeighter()
        
        # Recent memory, medium importance
        weight = weighter.calculate_weight(
            timestamp="2025-12-17T10:00:00Z",
            importance=0.5,
            base_relevance=0.8
        )
        # Result: ~0.75 (slightly decayed)
        
        # Old memory, high importance
        weight = weighter.calculate_weight(
            timestamp="2025-12-01T10:00:00Z",
            importance=0.9,
            base_relevance=0.8
        )
        # Result: ~0.45 (decayed but boosted by importance)
    """
    
    def __init__(self, time_scale_hours: float = 100.0):
        """Initialize decay weighter.
        
        Args:
            time_scale_hours: Base timescale for decay (default: 100 hours ~4 days)
                Lower = faster forgetting, Higher = slower forgetting
        """
        self.time_scale_hours = time_scale_hours
    
    def calculate_weight(
        self,
        timestamp: str,
        importance: float,
        base_relevance: float = 1.0
    ) -> float:
        """Calculate final weight incorporating decay.
        
        Args:
            timestamp: ISO format timestamp of memory creation
            importance: Memory importance score (0.0-1.0)
            base_relevance: Base relevance score from vector search (0.0-1.0)
        
        Returns:
            Final weight (0.0-1.0) = base_relevance * decay_factor * importance_boost
        """
        # Parse timestamp
        try:
            memory_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            # If timestamp invalid, assume recent (no decay)
            return base_relevance * (1.0 + importance)
        
        # Calculate time elapsed
        now = datetime.now(timezone.utc)
        time_delta = now - memory_time
        hours_elapsed = time_delta.total_seconds() / 3600
        
        # Apply Ebbinghaus curve: R = e^(-t/S)
        # Strength = importance scales the time constant
        # High importance = slower decay
        strength = self.time_scale_hours * (1.0 + importance)
        decay_factor = math.exp(-hours_elapsed / strength)
        
        # Importance also provides a direct boost (0-1 → 1-2 multiplier)
        importance_boost = 1.0 + importance
        
        # Combine all factors
        final_weight = base_relevance * decay_factor * importance_boost
        
        # Clamp to [0, 1] range
        return max(0.0, min(1.0, final_weight))
    
    def calculate_half_life(self, importance: float) -> float:
        """Calculate half-life in hours for given importance.
        
        Useful for understanding decay rates.
        
        Args:
            importance: Memory importance (0.0-1.0)
        
        Returns:
            Hours until memory weight drops to 50%
        """
        strength = self.time_scale_hours * (1.0 + importance)
        # Half-life: t_half = ln(2) * S
        return math.log(2) * strength
    
    def get_decay_stats(self, hours_elapsed: float, importance: float) -> dict:
        """Get detailed decay statistics for debugging/analysis.
        
        Args:
            hours_elapsed: Hours since memory creation
            importance: Memory importance score
        
        Returns:
            Dict with decay metrics
        """
        strength = self.time_scale_hours * (1.0 + importance)
        decay_factor = math.exp(-hours_elapsed / strength)
        half_life = self.calculate_half_life(importance)
        
        return {
            'hours_elapsed': hours_elapsed,
            'importance': importance,
            'strength': strength,
            'decay_factor': decay_factor,
            'half_life_hours': half_life,
            'percentage_retained': decay_factor * 100
        }


def apply_decay_to_memories(
    memories: list[dict],
    weighter: Optional[MemoryDecayWeighter] = None
) -> list[dict]:
    """Apply decay weighting to a list of memories and re-sort.
    
    Args:
        memories: List of memory dicts with 'metadata' containing
                  'timestamp' and 'importance'
        weighter: MemoryDecayWeighter instance (creates default if None)
    
    Returns:
        Re-sorted list with decay-adjusted weights in metadata
    """
    if weighter is None:
        weighter = MemoryDecayWeighter()
    
    weighted_memories = []
    
    for memory in memories:
        # Extract metadata
        metadata = memory.get('metadata', {})
        timestamp = metadata.get('timestamp', datetime.now(timezone.utc).isoformat())
        importance = float(metadata.get('importance', 0.5))
        
        # Base relevance from vector search distance
        # ChromaDB returns smaller distances = more similar
        # Convert to relevance score (1 - distance)
        distance = memory.get('distance', 0.5)
        base_relevance = 1.0 - distance
        
        # Calculate decayed weight
        final_weight = weighter.calculate_weight(
            timestamp=timestamp,
            importance=importance,
            base_relevance=base_relevance
        )
        
        # Add weight to metadata
        memory_copy = memory.copy()
        memory_copy['metadata'] = metadata.copy()
        memory_copy['metadata']['decay_weight'] = final_weight
        memory_copy['metadata']['original_distance'] = distance
        
        weighted_memories.append(memory_copy)
    
    # Re-sort by decay-adjusted weight (higher = better)
    weighted_memories.sort(key=lambda m: m['metadata']['decay_weight'], reverse=True)
    
    return weighted_memories
