"""Context priming system - predictively load likely-needed context.

Based on biological priming: exposure to a stimulus influences response to
later stimuli. Semantic networks pre-activate related concepts.

Example: Seeing "doctor" primes "nurse," "hospital," "medicine"
Application: Discussing "specialist" primes "protocol," "activation," "codebase"

@ai-indexable: biomimetic-phase3
@ai-purpose: Predictive context loading based on conversation trajectory
@ai-dependencies: None (pure Python)
@ai-related: brain/rag_store.py, brain/prompt_builder/context_retriever.py
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class PrimingContext:
    """Context that has been pre-activated for fast access."""
    
    topic: str
    """The primed topic/concept"""
    
    related_topics: List[str]
    """Topics semantically related to this one"""
    
    priming_strength: float
    """How strongly primed (0.0-1.0, based on semantic distance)"""
    
    primed_at: datetime
    """When this context was primed"""
    
    accessed: bool = False
    """Whether this primed context was actually used"""


@dataclass
class SemanticNetwork:
    """Map of concept relationships for priming.
    
    Can be learned from co-occurrence in memories or hand-crafted.
    """
    
    relationships: Dict[str, List[Tuple[str, float]]] = field(default_factory=dict)
    """topic -> [(related_topic, strength), ...]"""
    
    def get_related(self, topic: str, threshold: float = 0.5) -> List[str]:
        """Get related topics above strength threshold."""
        if topic not in self.relationships:
            return []
        
        return [
            related for related, strength in self.relationships[topic]
            if strength >= threshold
        ]
    
    def add_relationship(self, topic1: str, topic2: str, strength: float):
        """Add bidirectional relationship between topics."""
        if topic1 not in self.relationships:
            self.relationships[topic1] = []
        if topic2 not in self.relationships:
            self.relationships[topic2] = []
        
        # Add bidirectional
        self.relationships[topic1].append((topic2, strength))
        self.relationships[topic2].append((topic1, strength))
    
    def learn_from_cooccurrence(self, memories: List[Dict], min_cooccurrence: int = 3):
        """Learn relationships from memory co-occurrence patterns.
        
        Args:
            memories: List of memory documents with 'topics' metadata
            min_cooccurrence: Minimum times topics must co-occur
        """
        # Track co-occurrence counts
        cooccurrence = defaultdict(lambda: defaultdict(int))
        topic_counts = defaultdict(int)
        
        for memory in memories:
            topics = memory.get('metadata', {}).get('topics', [])
            
            # Count individual topics
            for topic in topics:
                topic_counts[topic] += 1
            
            # Count co-occurrences (pairs)
            for i, topic1 in enumerate(topics):
                for topic2 in topics[i+1:]:
                    cooccurrence[topic1][topic2] += 1
                    cooccurrence[topic2][topic1] += 1
        
        # Convert counts to relationship strengths
        for topic1, related in cooccurrence.items():
            for topic2, count in related.items():
                if count >= min_cooccurrence:
                    # Strength based on how often they co-occur vs individual frequency
                    # Pointwise Mutual Information (PMI) inspired
                    total_memories = len(memories)
                    p_topic1 = topic_counts[topic1] / total_memories
                    p_topic2 = topic_counts[topic2] / total_memories
                    p_together = count / total_memories
                    
                    # Avoid division by zero
                    if p_topic1 * p_topic2 > 0:
                        strength = min(1.0, p_together / (p_topic1 * p_topic2))
                        self.add_relationship(topic1, topic2, strength)
    
    @classmethod
    def load_default(cls) -> "SemanticNetwork":
        """Load hand-crafted default semantic network for Ada concepts."""
        network = cls()
        
        # Core Ada concepts
        network.add_relationship("specialist", "protocol", 0.9)
        network.add_relationship("specialist", "activation", 0.9)
        network.add_relationship("specialist", "codebase", 0.8)
        network.add_relationship("protocol", "interface", 0.8)
        network.add_relationship("protocol", "baseclass", 0.7)
        
        # Memory/RAG concepts
        network.add_relationship("memory", "rag", 0.9)
        network.add_relationship("memory", "chroma", 0.8)
        network.add_relationship("memory", "vector", 0.8)
        network.add_relationship("rag", "embedding", 0.9)
        network.add_relationship("rag", "search", 0.8)
        
        # Biomimetic concepts
        network.add_relationship("biomimetic", "attention", 0.9)
        network.add_relationship("biomimetic", "decay", 0.9)
        network.add_relationship("biomimetic", "chunking", 0.9)
        network.add_relationship("attention", "salience", 0.8)
        network.add_relationship("attention", "spotlight", 0.8)
        
        # Architecture concepts
        network.add_relationship("architecture", "fastapi", 0.8)
        network.add_relationship("architecture", "docker", 0.7)
        network.add_relationship("architecture", "compose", 0.7)
        network.add_relationship("fastapi", "endpoint", 0.9)
        network.add_relationship("fastapi", "route", 0.8)
        
        return network


class ContextPrimer:
    """Pre-activate likely context based on conversation trajectory.
    
    Biological inspiration: Semantic networks in human cognition where
    related concepts pre-activate each other, making them faster to access.
    """
    
    def __init__(self, semantic_network: Optional[SemanticNetwork] = None):
        """Initialize context primer.
        
        Args:
            semantic_network: Optional custom semantic network
        """
        self.network = semantic_network or SemanticNetwork.load_default()
        self.primed_contexts: Dict[str, PrimingContext] = {}
        self.priming_enabled = True
    
    def prime_from_message(self, message: str, current_topics: List[str]) -> List[PrimingContext]:
        """Prime context based on message and current conversation topics.
        
        Args:
            message: User's message
            current_topics: Topics active in current conversation
        
        Returns:
            List of primed contexts
        """
        if not self.priming_enabled:
            return []
        
        primed = []
        primed_topics = set()
        
        # Prime based on current topics
        for topic in current_topics:
            related = self.network.get_related(topic)
            
            for related_topic in related:
                if related_topic not in primed_topics:
                    # Calculate priming strength (decreases with semantic distance)
                    strength = self._calculate_priming_strength(topic, related_topic)
                    
                    context = PrimingContext(
                        topic=related_topic,
                        related_topics=[topic],
                        priming_strength=strength,
                        primed_at=datetime.now(timezone.utc)
                    )
                    
                    primed.append(context)
                    primed_topics.add(related_topic)
                    self.primed_contexts[related_topic] = context
        
        logger.info(f"Primed {len(primed)} contexts from {len(current_topics)} active topics")
        return primed
    
    def _calculate_priming_strength(self, source_topic: str, target_topic: str) -> float:
        """Calculate priming strength between topics."""
        # Get strength from semantic network
        for related, strength in self.network.relationships.get(source_topic, []):
            if related == target_topic:
                return strength
        
        return 0.5  # Default moderate strength
    
    def is_primed(self, topic: str) -> bool:
        """Check if a topic has been primed."""
        return topic in self.primed_contexts
    
    def get_priming_benefit(self, topic: str) -> float:
        """Get priming benefit for a topic (for metrics tracking).
        
        Returns:
            Priming strength if primed, 0.0 if not primed
        """
        if topic in self.primed_contexts:
            context = self.primed_contexts[topic]
            context.accessed = True
            return context.priming_strength
        return 0.0
    
    def get_priming_stats(self) -> Dict:
        """Get priming statistics for monitoring."""
        total = len(self.primed_contexts)
        accessed = sum(1 for ctx in self.primed_contexts.values() if ctx.accessed)
        
        if total == 0:
            hit_rate = 0.0
        else:
            hit_rate = accessed / total
        
        return {
            'total_primed': total,
            'accessed': accessed,
            'hit_rate': hit_rate,
            'priming_enabled': self.priming_enabled
        }
    
    def clear_priming(self):
        """Clear all primed contexts (e.g., at end of conversation)."""
        self.primed_contexts.clear()
