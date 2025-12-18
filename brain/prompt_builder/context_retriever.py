"""Context retrieval from RAG store and configuration.

@ai-indexable: core-refactor
@ai-purpose: Retrieves context data from various sources (RAG, filesystem, config)
@ai-dependencies: brain.rag_store, brain.config, brain.memory_decay
@ai-enhanced: v2.1 - Memory decay weighting applied to memories
@ai-enhanced: v2.2 - Neuromorphic importance scoring and gradient detail levels
"""
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import logging
from datetime import datetime, timezone
from dateutil import parser

from brain.rag_store import RagStore
from brain import config
from brain.memory_decay import MemoryDecayWeighter

logger = logging.getLogger(__name__)


class ContextRetriever:
    """Retrieves context from RAG store and configuration files.
    
    This class handles all data retrieval operations needed for prompt building,
    separating retrieval logic from formatting and assembly.
    """

    def __init__(self, rag_store_instance=None, config_instance=None, cache=None):
        """Initialize the context retriever.
        
        Args:
            rag_store_instance: Optional RAG store instance (for testing)
            config_instance: Optional config (for testing)
            cache: Optional MultiTimescaleCache instance
        """
        # Create RagStore instance if not provided
        self.rag_store = rag_store_instance or RagStore(collection_name="conversations")
        self.config = config_instance or config
        self.cache = cache
        
        # Initialize memory decay weighter if enabled
        self.decay_weighter = None
        if hasattr(self.config, 'MEMORY_DECAY_ENABLED') and self.config.MEMORY_DECAY_ENABLED:
            time_scale = getattr(self.config, 'MEMORY_DECAY_TIME_SCALE_HOURS', 100.0)
            self.decay_weighter = MemoryDecayWeighter(time_scale_hours=time_scale)
            logger.info(f"Memory decay enabled (time_scale={time_scale}hr)")
        
        # Gradient thresholds (configurable via config)
        self.thresholds = {
            'full': getattr(self.config, 'GRADIENT_THRESHOLD_FULL', 0.75),
            'chunks': getattr(self.config, 'GRADIENT_THRESHOLD_CHUNKS', 0.50),
            'summary': getattr(self.config, 'GRADIENT_THRESHOLD_SUMMARY', 0.20)
        }
        
        # Signal weights for importance calculation (configurable)
        self.signal_weights = {
            'decay': getattr(self.config, 'IMPORTANCE_WEIGHT_DECAY', 0.4),
            'surprise': getattr(self.config, 'IMPORTANCE_WEIGHT_SURPRISE', 0.3),
            'relevance': getattr(self.config, 'IMPORTANCE_WEIGHT_RELEVANCE', 0.2),
            'habituation': getattr(self.config, 'IMPORTANCE_WEIGHT_HABITUATION', 0.1)
        }

    def get_persona(self) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Retrieve persona content from RAG store (with caching).
        
        Returns:
            (text, metadata) tuple or None if not found
        """
        # Try cache first if enabled
        if self.cache is not None:
            cached = self.cache.get("persona")
            if cached is not None:
                logger.debug("Persona cache hit")
                # Cache stores tuple as string, need to reconstruct
                # For Phase 1, we store just the text and reconstruct metadata
                return (cached, {})
        
        # Cache miss - query RAG
        try:
            result = self.rag_store.load_persona_block()
            
            # Cache the result if caching is enabled
            if self.cache is not None and result is not None:
                text, metadata = result
                # Estimate token count (rough: 1 token ≈ 4 chars)
                token_count = len(text) // 4
                self.cache.set(
                    "persona",
                    text,
                    ttl_seconds=self.config.CACHE_PERSONA_TTL,
                    token_count=token_count
                )
                logger.debug(f"Cached persona ({token_count} tokens)")
            
            return result
        except Exception as e:
            logger.error(f"Error reading persona: {e}")
            return None

    def get_memories(
        self, 
        query: str, 
        k: int = 5, 
        entity: Optional[str] = None
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Retrieve relevant memories from RAG store with decay weighting.
        
        Args:
            query: Search query for semantic similarity
            k: Maximum number of memories to return
            entity: Optional entity scope filter
            
        Returns:
            List of (text, metadata) tuples, sorted by decay-adjusted relevance
        """
        try:
            # Get more results if decay is enabled (will re-sort and trim)
            fetch_k = k * 2 if self.decay_weighter else k
            memories = self.rag_store.retrieve_memories(query=query, k=fetch_k, entity=entity)
            
            # Apply decay weighting if enabled
            if self.decay_weighter and memories:
                # Convert to format expected by decay weighter
                memory_dicts = []
                for text, metadata in memories:
                    memory_dicts.append({
                        'content': text,
                        'metadata': metadata,
                        'distance': metadata.get('distance', 0.5)
                    })
                
                # Apply decay and re-sort
                from brain.memory_decay import apply_decay_to_memories
                weighted = apply_decay_to_memories(memory_dicts, self.decay_weighter)
                
                # Convert back to (text, metadata) format and take top k
                memories = [
                    (m['content'], m['metadata'])
                    for m in weighted[:k]
                ]
                
                logger.debug(f"Applied decay weighting to {len(memories)} memories")
            
            return memories
        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            return []

    def get_faqs(
        self, 
        query: str, 
        k: int = 3
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Retrieve relevant FAQs from RAG store.
        
        Args:
            query: Search query for semantic similarity
            k: Maximum number of FAQs to return
            
        Returns:
            List of (text, metadata) tuples
        """
        try:
            return self.rag_store.retrieve_faqs(query=query, k=k)
        except Exception as e:
            logger.error(f"Error retrieving FAQs: {e}")
            return []

    def get_turns(
        self, 
        query: str,
        k: int = 5,
        conversation_id: Optional[str] = None
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Retrieve conversation turns.
        
        Args:
            query: Search query for semantic similarity  
            k: Maximum number of turns to return
            conversation_id: Optional conversation ID filter
            
        Returns:
            List of (text, metadata) tuples
        """
        if not conversation_id:
            return []
        
        try:
            return self.rag_store.retrieve_turns(
                query=query,
                k=k,
                conversation_id=conversation_id
            )
        except Exception as e:
            logger.error(f"Error retrieving conversation turns: {e}")
            return []
    
    def get_summaries(
        self,
        conversation_id: str,
        k: int = 3
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Retrieve conversation summaries.
        
        Args:
            conversation_id: Conversation ID to retrieve summaries for
            k: Maximum number of summaries to return
            
        Returns:
            List of (text, metadata) tuples
        """
        try:
            return self.rag_store.retrieve_summaries(
                conversation_id=conversation_id,
                k=k
            )
        except Exception as e:
            logger.error(f"Error retrieving summaries: {e}")
            return []
    
    def calculate_importance(self, turn: Dict[str, Any], query: str) -> float:
        """Calculate multi-signal importance score for a conversation turn.
        
        Combines signals from:
        - Temporal decay (how old is it?)
        - Prediction error (how surprising/novel?)
        - Semantic relevance (how related to current query?)
        - Context habituation (how repetitive?)
        
        Args:
            turn: Turn dict with 'timestamp', 'content', 'metadata'
            query: Current query for relevance calculation
            
        Returns:
            Importance score between 0.0 and 1.0
        """
        # Parse timestamp (default to very recent if missing)
        try:
            if 'timestamp' in turn:
                turn_time = parser.isoparse(turn['timestamp'])
            else:
                # Missing timestamp - assume recent
                turn_time = datetime.now(timezone.utc)
        except Exception as e:
            logger.warning(f"Invalid timestamp in turn: {e}")
            turn_time = datetime.now(timezone.utc)
        
        # Calculate age in hours
        now = datetime.now(timezone.utc)
        age_hours = max(0, (now - turn_time).total_seconds() / 3600)
        
        # Signal 1: Temporal decay (raw decay factor, not final weight)
        import math
        if self.decay_weighter:
            # Use temperature-modulated decay time scale
            importance_hint = turn.get('metadata', {}).get('importance', 0.5)
            strength = self.decay_weighter.time_scale_hours * (1.0 + importance_hint)
            decay_score = math.exp(-age_hours / strength)
        else:
            # Simple exponential decay if weighter not available
            decay_score = math.exp(-age_hours / 100.0)
        
        # Signal 2: Prediction error (surprise/novelty)
        metadata = turn.get('metadata', {})
        surprise_score = metadata.get('prediction_error', 0.5)
        
        # Signal 3: Semantic relevance (simple text similarity for now)
        # TODO: Phase 2 - Replace with proper embedding similarity
        content = turn.get('content', '')
        
        # Empty content gets zero relevance
        if not content.strip():
            relevance_score = 0.0
        elif not query:
            relevance_score = 0.0
        else:
            # Simple keyword overlap as proxy (Phase 1)
            query_words = set(query.lower().split())
            content_words = set(content.lower().split())
            if query_words:
                overlap = len(query_words & content_words) / len(query_words)
                relevance_score = min(1.0, overlap * 2)  # Scale up a bit
            else:
                relevance_score = 0.0
        
        # Signal 4: Habituation penalty (inverted - high habituation = low importance)
        habituation_score = metadata.get('habituation_score', 0.0)
        novelty_score = 1.0 - habituation_score  # Invert
        
        # Weighted combination
        importance = (
            self.signal_weights['decay'] * decay_score +
            self.signal_weights['surprise'] * surprise_score +
            self.signal_weights['relevance'] * relevance_score +
            self.signal_weights['habituation'] * novelty_score
        )
        
        # Penalty for empty content (it has no semantic value)
        content = turn.get('content', '')
        if not content.strip():
            importance *= 0.1  # Heavy penalty for empty turns
        
        # Clamp to [0, 1]
        importance = max(0.0, min(1.0, importance))
        
        return importance
    
    def get_detail_level(self, importance: float) -> str:
        """Determine gradient detail level based on importance score.
        
        Args:
            importance: Score between 0.0 and 1.0
            
        Returns:
            One of: 'FULL', 'CHUNKS', 'SUMMARY', 'DROPPED'
        """
        if importance >= self.thresholds['full']:
            return 'FULL'
        elif importance >= self.thresholds['chunks']:
            return 'CHUNKS'
        elif importance >= self.thresholds['summary']:
            return 'SUMMARY'
        else:
            return 'DROPPED'
    
    def set_thresholds(self, thresholds: Dict[str, float]) -> None:
        """Update gradient thresholds.
        
        Args:
            thresholds: Dict with 'full', 'chunks', 'summary' keys
        """
        self.thresholds.update(thresholds)
        logger.info(f"Updated gradient thresholds: {self.thresholds}")
    
    def set_signal_weights(self, weights: Dict[str, float]) -> None:
        """Update importance signal weights.
        
        Args:
            weights: Dict with 'decay', 'surprise', 'relevance', 'habituation' keys
        """
        self.signal_weights.update(weights)
        logger.info(f"Updated signal weights: {self.signal_weights}")
