"""Semantic chunking - group related memories to reduce redundancy.

Biological inspiration: Human memory consolidation groups related information
into semantic clusters, retrieving representative "gist" rather than every
individual memory. This reduces cognitive load while preserving meaning.

Key concepts:
- **Similarity clustering:** Group memories by embedding distance
- **Chunk representatives:** Select best example from each cluster
- **Redundancy reduction:** ~20-30% token savings by deduplication
"""
# @ai-indexable: core-utility
# @ai-purpose: Semantic clustering of memories to reduce redundancy
# @ai-dependencies: numpy (optional for faster computation)

from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class MemoryChunk:
    """A semantic cluster of related memories."""
    representative: Tuple[str, Dict]  # (content, metadata) of best example
    members: List[Tuple[str, Dict]]  # All memories in this chunk
    centroid_distance: float  # Average distance within chunk
    size: int  # Number of memories
    
    def get_content(self) -> str:
        """Get representative content (most important/recent)."""
        return self.representative[0]
    
    def get_metadata(self) -> Dict:
        """Get representative metadata."""
        return self.representative[1]
    
    def format_summary(self) -> str:
        """Format chunk with member count."""
        if self.size == 1:
            return self.representative[0]
        return f"{self.representative[0]} (+{self.size - 1} similar)"


class SemanticChunker:
    """Group related memories into semantic chunks.
    
    Uses embedding distances to cluster similar memories, then selects
    the most important/recent representative from each cluster.
    
    Example:
        chunker = SemanticChunker(
            similarity_threshold=0.3,
            min_chunk_size=2
        )
        
        # Memories with distances from vector search
        memories = [
            ("Python is fast", {"importance": 4, "distance": 0.1}),
            ("Python has good performance", {"importance": 3, "distance": 0.15}),
            ("JavaScript async is tricky", {"importance": 5, "distance": 0.8}),
        ]
        
        chunks = chunker.chunk_memories(memories)
        # Result: 2 chunks (Python group, JavaScript singleton)
        
    Biological analogy:
        Similar to how humans remember "the gist" of multiple related
        experiences rather than every individual instance.
    """
    
    def __init__(
        self,
        similarity_threshold: float = 0.3,
        min_chunk_size: int = 2,
        max_chunk_size: int = 10
    ):
        """Initialize semantic chunker.
        
        Args:
            similarity_threshold: Distance threshold for grouping (0.0-1.0)
                                 Lower = stricter grouping
            min_chunk_size: Minimum memories to form a chunk (default: 2)
            max_chunk_size: Maximum memories per chunk (prevents huge clusters)
        """
        self.similarity_threshold = similarity_threshold
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
    
    def chunk_memories(
        self,
        memories: List[Tuple[str, Dict]]
    ) -> List[MemoryChunk]:
        """Group memories into semantic chunks.
        
        Args:
            memories: List of (content, metadata) tuples
                     metadata should include 'distance' if available
        
        Returns:
            List of MemoryChunk objects, one per cluster
        """
        if not memories:
            return []
        
        # Extract distances for clustering
        memory_dists: List[Tuple[int, float]] = []  # (index, distance)
        for i, (_, metadata) in enumerate(memories):
            dist = metadata.get('distance', 0.5)
            memory_dists.append((i, dist))
        
        # Sort by distance (similar memories cluster together)
        memory_dists.sort(key=lambda x: x[1])
        
        # Greedy clustering: group memories within threshold distance
        chunks: List[List[int]] = []  # List of index lists
        current_chunk: List[int] = []
        last_dist = -1.0
        
        for idx, dist in memory_dists:
            # Start new chunk if distance gap > threshold or chunk too large
            if (current_chunk and 
                (abs(dist - last_dist) > self.similarity_threshold or
                 len(current_chunk) >= self.max_chunk_size)):
                if len(current_chunk) >= self.min_chunk_size:
                    chunks.append(current_chunk)
                else:
                    # Chunk too small, add as singletons
                    for i in current_chunk:
                        chunks.append([i])
                current_chunk = []
            
            current_chunk.append(idx)
            last_dist = dist
        
        # Handle final chunk
        if current_chunk:
            if len(current_chunk) >= self.min_chunk_size:
                chunks.append(current_chunk)
            else:
                for i in current_chunk:
                    chunks.append([i])
        
        # Create MemoryChunk objects
        result: List[MemoryChunk] = []
        for chunk_indices in chunks:
            chunk_memories = [memories[i] for i in chunk_indices]
            
            # Select representative: highest importance, then most recent
            rep = self._select_representative(chunk_memories)
            
            # Calculate average distance within chunk
            distances = [memories[i][1].get('distance', 0.5) for i in chunk_indices]
            avg_dist = sum(distances) / len(distances) if distances else 0.5
            
            result.append(MemoryChunk(
                representative=rep,
                members=chunk_memories,
                centroid_distance=avg_dist,
                size=len(chunk_memories)
            ))
        
        return result
    
    def _select_representative(
        self,
        memories: List[Tuple[str, Dict]]
    ) -> Tuple[str, Dict]:
        """Select best representative from a group of memories.
        
        Criteria:
        1. Highest importance
        2. Most recent (tie-breaker)
        3. First in list (final tie-breaker)
        
        Args:
            memories: List of (content, metadata) tuples
        
        Returns:
            Best (content, metadata) tuple
        """
        if not memories:
            return ("", {})
        
        if len(memories) == 1:
            return memories[0]
        
        # Score: importance (0-5) + recency (0-1) * 0.5
        def score(memory: Tuple[str, Dict]) -> float:
            _, metadata = memory
            importance = metadata.get('importance', 3)
            
            # Recency from timestamp (simplified: use distance as proxy)
            # Lower distance often correlates with more recent queries
            distance = metadata.get('distance', 0.5)
            recency_boost = (1.0 - min(distance, 1.0)) * 0.5
            
            return float(importance) + recency_boost
        
        return max(memories, key=score)
    
    def collapse_chunks(
        self,
        chunks: List[MemoryChunk],
        max_tokens: int = 8000,
        token_counter=None
    ) -> List[Tuple[str, Dict]]:
        """Convert chunks back to memory list, respecting token budget.
        
        Args:
            chunks: List of memory chunks
            max_tokens: Maximum token budget
            token_counter: Optional token counting function
        
        Returns:
            List of (content, metadata) tuples for prompt assembly
        """
        if token_counter is None:
            # Simple heuristic: ~4 chars per token
            token_counter = lambda text: len(text) // 4
        
        result: List[Tuple[str, Dict]] = []
        tokens_used = 0
        
        for chunk in chunks:
            content = chunk.format_summary()
            tokens = token_counter(content)
            
            if tokens_used + tokens > max_tokens:
                break  # Budget exceeded
            
            result.append((content, chunk.get_metadata()))
            tokens_used += tokens
        
        return result


def apply_chunking_to_memories(
    memories: List[Tuple[str, Dict]],
    chunker: Optional[SemanticChunker] = None
) -> List[Tuple[str, Dict]]:
    """Apply semantic chunking to memory list (convenience function).
    
    Args:
        memories: List of (content, metadata) tuples
        chunker: Optional SemanticChunker instance (creates default if None)
    
    Returns:
        Chunked memory list with redundancy reduced
    """
    if chunker is None:
        chunker = SemanticChunker()
    
    chunks = chunker.chunk_memories(memories)
    return chunker.collapse_chunks(chunks)
