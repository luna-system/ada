"""Memory Graph - Biomimetic associative memory with spreading activation.

Biological inspiration: Human memory is not a database lookup - it's a graph.
Concepts activate related concepts. The smell of rain triggers childhood,
triggers safety, triggers home. Spreading activation through a web of meaning.

Key concepts:
- **Nodes:** Memory IDs linked to ChromaDB documents
- **Edges:** Typed relationships (co-occurred, caused, supports, contradicts)
- **Spreading activation:** Fire one node, neighbors activate proportionally
- **Hebbian learning:** "Neurons that fire together wire together"
- **Decay:** Unused edges weaken over time

References:
- Collins & Loftus (1975) - Spreading activation theory
- Collins & Quillian (1969) - Semantic network model
- HippoRAG (2024) - Hippocampus-inspired retrieval
- Microsoft GraphRAG (2024) - Graph-based RAG

@ai-indexable: biomimetic-graphrag
@ai-purpose: Graph-based memory with spreading activation for associative retrieval
@ai-dependencies: networkx (optional, falls back to dict-based)
@ai-related: brain/rag_store.py, brain/context_priming.py, brain/memory_decay.py
"""

import json
import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from collections import defaultdict

logger = logging.getLogger(__name__)

# Try NetworkX, fall back to pure Python
try:
    import networkx as nx
    HAS_NETWORKX = True
    logger.info("NetworkX available - using optimized graph operations")
except ImportError:
    HAS_NETWORKX = False
    logger.info("NetworkX not found - using pure Python graph (slower for large graphs)")


@dataclass
class MemoryNode:
    """A node in the memory graph representing a single memory."""
    
    memory_id: str
    """Unique identifier (matches ChromaDB document ID)"""
    
    content_hash: str
    """Hash of content for quick comparison"""
    
    created_at: datetime
    """When this node was created"""
    
    last_accessed: datetime
    """Last time this node was activated"""
    
    activation_count: int = 0
    """How many times this node has been activated"""
    
    topics: List[str] = field(default_factory=list)
    """Extracted topics/tags for this memory"""
    
    entities: List[str] = field(default_factory=list)
    """Named entities mentioned in this memory"""


@dataclass 
class MemoryEdge:
    """A directed edge representing a relationship between memories."""
    
    source_id: str
    """Source memory ID"""
    
    target_id: str
    """Target memory ID"""
    
    relationship_type: str
    """Type: co_occurred, caused, supports, contradicts, extends, example_of"""
    
    weight: float = 1.0
    """Edge strength (0.0-1.0), decays over time"""
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    """When this edge was created"""
    
    last_activated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    """Last time this edge was traversed"""
    
    activation_count: int = 0
    """How many times this edge has been traversed (Hebbian strengthening)"""


class MemoryGraph:
    """Graph-based memory with spreading activation.
    
    This is the core of biomimetic memory - concepts don't exist in isolation,
    they exist in relationship to each other. Retrieving one memory should
    activate related memories, just like biological associative memory.
    
    Example:
        >>> graph = MemoryGraph()
        >>> graph.add_node("mem_1", topics=["python", "specialist"])
        >>> graph.add_node("mem_2", topics=["python", "protocol"])  
        >>> graph.add_edge("mem_1", "mem_2", "co_occurred")
        >>> 
        >>> # Spreading activation from mem_1
        >>> activated = graph.spread_activation("mem_1", depth=2)
        >>> # Returns: {"mem_1": 1.0, "mem_2": 0.7, ...}
    """
    
    # Relationship types with default weights
    RELATIONSHIP_TYPES = {
        "co_occurred": 0.6,      # Appeared in same conversation
        "caused": 0.9,           # One led to another
        "supports": 0.8,         # Evidence/argument for
        "contradicts": 0.7,      # Conflicting information
        "extends": 0.85,         # Elaborates/adds to
        "example_of": 0.75,      # Concrete instance of abstract
        "related": 0.5,          # Generic relationship
    }
    
    def __init__(self, persistence_path: Optional[Path] = None):
        """Initialize memory graph.
        
        Args:
            persistence_path: Optional path to save/load graph state
        """
        self.persistence_path = persistence_path
        
        # Node storage
        self.nodes: Dict[str, MemoryNode] = {}
        
        # Edge storage (adjacency list for efficiency)
        # source_id -> [(target_id, MemoryEdge), ...]
        self.edges: Dict[str, List[Tuple[str, MemoryEdge]]] = defaultdict(list)
        
        # Reverse edges for bidirectional traversal
        # target_id -> [(source_id, MemoryEdge), ...]
        self.reverse_edges: Dict[str, List[Tuple[str, MemoryEdge]]] = defaultdict(list)
        
        # Topic index for fast lookup
        # topic -> [memory_id, ...]
        self.topic_index: Dict[str, Set[str]] = defaultdict(set)
        
        # Entity index
        # entity -> [memory_id, ...]
        self.entity_index: Dict[str, Set[str]] = defaultdict(set)
        
        # NetworkX graph for complex operations (if available)
        self._nx_graph: Optional[Any] = None
        if HAS_NETWORKX:
            self._nx_graph = nx.DiGraph()
        
        # Load from persistence if exists
        if persistence_path and persistence_path.exists():
            self.load()
    
    def add_node(
        self, 
        memory_id: str, 
        content_hash: str = "",
        topics: Optional[List[str]] = None,
        entities: Optional[List[str]] = None
    ) -> MemoryNode:
        """Add a memory node to the graph.
        
        Args:
            memory_id: Unique identifier (ChromaDB doc ID)
            content_hash: Hash of content for deduplication
            topics: Extracted topics/tags
            entities: Named entities
            
        Returns:
            The created MemoryNode
        """
        now = datetime.now(timezone.utc)
        
        node = MemoryNode(
            memory_id=memory_id,
            content_hash=content_hash,
            created_at=now,
            last_accessed=now,
            topics=topics or [],
            entities=entities or []
        )
        
        self.nodes[memory_id] = node
        
        # Update indices
        for topic in node.topics:
            self.topic_index[topic.lower()].add(memory_id)
        for entity in node.entities:
            self.entity_index[entity.lower()].add(memory_id)
        
        # Add to NetworkX graph if available
        if self._nx_graph is not None:
            self._nx_graph.add_node(memory_id, **{
                "topics": topics or [],
                "entities": entities or [],
                "created_at": now.isoformat()
            })
        
        logger.debug(f"Added node: {memory_id} with {len(node.topics)} topics, {len(node.entities)} entities")
        return node
    
    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str = "related",
        weight: Optional[float] = None
    ) -> MemoryEdge:
        """Add a directed edge between memory nodes.
        
        Args:
            source_id: Source memory ID
            target_id: Target memory ID
            relationship_type: Type of relationship
            weight: Edge weight (uses default for type if not specified)
            
        Returns:
            The created MemoryEdge
        """
        # Use default weight for relationship type if not specified
        if weight is None:
            weight = self.RELATIONSHIP_TYPES.get(relationship_type, 0.5)
        
        edge = MemoryEdge(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            weight=weight
        )
        
        # Add to adjacency lists
        self.edges[source_id].append((target_id, edge))
        self.reverse_edges[target_id].append((source_id, edge))
        
        # Add to NetworkX graph if available
        if self._nx_graph is not None:
            self._nx_graph.add_edge(
                source_id, 
                target_id,
                weight=weight,
                relationship_type=relationship_type
            )
        
        logger.debug(f"Added edge: {source_id} --[{relationship_type}:{weight:.2f}]--> {target_id}")
        return edge
    
    def spread_activation(
        self,
        seed_ids: List[str],
        depth: int = 2,
        decay_factor: float = 0.7,
        threshold: float = 0.1,
        max_nodes: int = 20
    ) -> Dict[str, float]:
        """Spread activation from seed nodes through the graph.
        
        This is the core biomimetic operation - starting from one or more
        memories, activation spreads to connected memories, decaying with
        distance. Like how thinking of "doctor" activates "nurse", "hospital".
        
        Args:
            seed_ids: Starting memory IDs (activation = 1.0)
            depth: How many hops to spread
            decay_factor: Activation multiplier per hop (0.7 = 70% of parent)
            threshold: Minimum activation to continue spreading
            max_nodes: Maximum nodes to return
            
        Returns:
            Dict of memory_id -> activation_level (0.0-1.0)
        """
        # Initialize activations
        activations: Dict[str, float] = {}
        
        # Seed nodes start at full activation
        for seed_id in seed_ids:
            if seed_id in self.nodes:
                activations[seed_id] = 1.0
        
        # BFS spreading activation
        current_layer = set(seed_ids)
        
        for hop in range(depth):
            next_layer: Set[str] = set()
            
            for node_id in current_layer:
                current_activation = activations.get(node_id, 0.0)
                
                # Skip if below threshold
                if current_activation < threshold:
                    continue
                
                # Spread to neighbors (forward edges)
                for target_id, edge in self.edges.get(node_id, []):
                    # Calculate neighbor activation
                    neighbor_activation = current_activation * decay_factor * edge.weight
                    
                    # Only update if higher than existing (max pooling)
                    if neighbor_activation > activations.get(target_id, 0.0):
                        activations[target_id] = neighbor_activation
                        next_layer.add(target_id)
                        
                        # Hebbian: strengthen the edge we just traversed
                        edge.activation_count += 1
                        edge.last_activated = datetime.now(timezone.utc)
                
                # Also spread backward (reverse edges) but with lower weight
                for source_id, edge in self.reverse_edges.get(node_id, []):
                    neighbor_activation = current_activation * decay_factor * edge.weight * 0.5
                    
                    if neighbor_activation > activations.get(source_id, 0.0):
                        activations[source_id] = neighbor_activation
                        next_layer.add(source_id)
            
            current_layer = next_layer
            
            # Early exit if nothing to spread
            if not current_layer:
                break
        
        # Sort by activation, limit to max_nodes
        sorted_activations = sorted(
            activations.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:max_nodes]
        
        return dict(sorted_activations)
    
    def find_co_occurring_topics(
        self, 
        topic: str, 
        min_cooccurrence: int = 2
    ) -> List[Tuple[str, int]]:
        """Find topics that frequently co-occur with the given topic.
        
        This enables automatic relationship discovery - topics that appear
        together in memories are likely related conceptually.
        
        Args:
            topic: Topic to find co-occurrences for
            min_cooccurrence: Minimum times topics must appear together
            
        Returns:
            List of (topic, count) tuples sorted by frequency
        """
        topic_lower = topic.lower()
        memory_ids = self.topic_index.get(topic_lower, set())
        
        cooccurrence: Dict[str, int] = defaultdict(int)
        
        for memory_id in memory_ids:
            node = self.nodes.get(memory_id)
            if node:
                for other_topic in node.topics:
                    if other_topic.lower() != topic_lower:
                        cooccurrence[other_topic.lower()] += 1
        
        # Filter and sort
        result = [
            (t, count) for t, count in cooccurrence.items()
            if count >= min_cooccurrence
        ]
        return sorted(result, key=lambda x: x[1], reverse=True)
    
    def learn_edges_from_cooccurrence(
        self,
        min_shared_topics: int = 2,
        min_weight: float = 0.3
    ) -> int:
        """Automatically create edges between memories with shared topics.
        
        Hebbian learning: "Neurons that fire together wire together"
        Memories with shared topics/entities likely have conceptual relationships.
        
        Args:
            min_shared_topics: Minimum shared topics to create edge
            min_weight: Minimum edge weight to create
            
        Returns:
            Number of edges created
        """
        edges_created = 0
        checked_pairs: Set[Tuple[str, str]] = set()
        
        # Iterate over all memory pairs (via topic index for efficiency)
        for topic, memory_ids in self.topic_index.items():
            memory_list = list(memory_ids)
            
            for i, mem1 in enumerate(memory_list):
                for mem2 in memory_list[i+1:]:
                    # Skip if we've already checked this pair
                    pair = (min(mem1, mem2), max(mem1, mem2))
                    if pair in checked_pairs:
                        continue
                    checked_pairs.add(pair)
                    
                    # Count shared topics
                    node1 = self.nodes.get(mem1)
                    node2 = self.nodes.get(mem2)
                    
                    if not node1 or not node2:
                        continue
                    
                    shared = set(t.lower() for t in node1.topics) & set(t.lower() for t in node2.topics)
                    
                    if len(shared) >= min_shared_topics:
                        # Weight based on number of shared topics
                        weight = min(1.0, len(shared) * 0.2 + 0.3)
                        
                        if weight >= min_weight:
                            # Check if edge already exists (in either direction)
                            existing_forward = any(
                                target == mem2 for target, _ in self.edges.get(mem1, [])
                            )
                            existing_backward = any(
                                target == mem1 for target, _ in self.edges.get(mem2, [])
                            )
                            
                            if not existing_forward and not existing_backward:
                                self.add_edge(mem1, mem2, "co_occurred", weight)
                                edges_created += 1
        
        logger.info(f"Learned {edges_created} edges from topic co-occurrence")
        return edges_created
    
    def apply_decay(self, decay_rate: float = 0.01) -> int:
        """Apply temporal decay to edge weights.
        
        Edges that haven't been activated recently weaken.
        This prevents the graph from becoming cluttered with
        stale relationships.
        
        Args:
            decay_rate: How much to reduce weight per day since last activation
            
        Returns:
            Number of edges removed (weight dropped to 0)
        """
        edges_removed = 0
        now = datetime.now(timezone.utc)
        
        for source_id in list(self.edges.keys()):
            surviving_edges = []
            
            for target_id, edge in self.edges[source_id]:
                # Calculate days since last activation
                days_inactive = (now - edge.last_activated).days
                
                # Apply decay
                decay_amount = decay_rate * days_inactive
                edge.weight = max(0.0, edge.weight - decay_amount)
                
                if edge.weight > 0.01:  # Keep edges above minimum threshold
                    surviving_edges.append((target_id, edge))
                else:
                    edges_removed += 1
                    # Also remove from reverse edges
                    self.reverse_edges[target_id] = [
                        (s, e) for s, e in self.reverse_edges[target_id]
                        if s != source_id
                    ]
            
            self.edges[source_id] = surviving_edges
        
        logger.info(f"Decay applied, {edges_removed} weak edges removed")
        return edges_removed
    
    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics for monitoring."""
        total_edges = sum(len(edges) for edges in self.edges.values())
        
        return {
            "nodes": len(self.nodes),
            "edges": total_edges,
            "topics": len(self.topic_index),
            "entities": len(self.entity_index),
            "has_networkx": HAS_NETWORKX,
            "avg_edges_per_node": total_edges / max(1, len(self.nodes))
        }
    
    def save(self) -> bool:
        """Persist graph to disk."""
        if not self.persistence_path:
            logger.warning("No persistence path configured")
            return False
        
        try:
            data = {
                "version": "1.0",
                "saved_at": datetime.now(timezone.utc).isoformat(),
                "nodes": {
                    mid: {
                        "memory_id": n.memory_id,
                        "content_hash": n.content_hash,
                        "created_at": n.created_at.isoformat(),
                        "last_accessed": n.last_accessed.isoformat(),
                        "activation_count": n.activation_count,
                        "topics": n.topics,
                        "entities": n.entities
                    }
                    for mid, n in self.nodes.items()
                },
                "edges": [
                    {
                        "source_id": e.source_id,
                        "target_id": e.target_id,
                        "relationship_type": e.relationship_type,
                        "weight": e.weight,
                        "created_at": e.created_at.isoformat(),
                        "last_activated": e.last_activated.isoformat(),
                        "activation_count": e.activation_count
                    }
                    for edges in self.edges.values()
                    for _, e in edges
                ]
            }
            
            self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.persistence_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Graph saved: {len(self.nodes)} nodes, {len(data['edges'])} edges")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save graph: {e}")
            return False
    
    def load(self) -> bool:
        """Load graph from disk."""
        if not self.persistence_path or not self.persistence_path.exists():
            return False
        
        try:
            with open(self.persistence_path, 'r') as f:
                data = json.load(f)
            
            # Clear existing data to prevent duplication
            self.nodes.clear()
            self.edges.clear()
            self.reverse_edges.clear()
            self.topic_index.clear()
            self.entity_index.clear()
            if self._nx_graph is not None:
                self._nx_graph.clear()
            
            # Load nodes
            for mid, ndata in data.get("nodes", {}).items():
                node = MemoryNode(
                    memory_id=ndata["memory_id"],
                    content_hash=ndata.get("content_hash", ""),
                    created_at=datetime.fromisoformat(ndata["created_at"]),
                    last_accessed=datetime.fromisoformat(ndata["last_accessed"]),
                    activation_count=ndata.get("activation_count", 0),
                    topics=ndata.get("topics", []),
                    entities=ndata.get("entities", [])
                )
                self.nodes[mid] = node
                
                # Rebuild indices
                for topic in node.topics:
                    self.topic_index[topic.lower()].add(mid)
                for entity in node.entities:
                    self.entity_index[entity.lower()].add(mid)
            
            # Load edges
            for edata in data.get("edges", []):
                edge = MemoryEdge(
                    source_id=edata["source_id"],
                    target_id=edata["target_id"],
                    relationship_type=edata["relationship_type"],
                    weight=edata["weight"],
                    created_at=datetime.fromisoformat(edata["created_at"]),
                    last_activated=datetime.fromisoformat(edata["last_activated"]),
                    activation_count=edata.get("activation_count", 0)
                )
                self.edges[edge.source_id].append((edge.target_id, edge))
                self.reverse_edges[edge.target_id].append((edge.source_id, edge))
                
                # Add to NetworkX if available
                if self._nx_graph is not None:
                    self._nx_graph.add_edge(
                        edge.source_id,
                        edge.target_id,
                        weight=edge.weight,
                        relationship_type=edge.relationship_type
                    )
            
            logger.info(f"Graph loaded: {len(self.nodes)} nodes, {len(data.get('edges', []))} edges")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load graph: {e}")
            return False


# Singleton instance for global access
_memory_graph: Optional[MemoryGraph] = None


def get_memory_graph(persistence_path: Optional[Path] = None) -> MemoryGraph:
    """Get or create the global memory graph instance.
    
    Args:
        persistence_path: Path for graph persistence
        
    Returns:
        The singleton MemoryGraph instance
    """
    global _memory_graph
    
    if _memory_graph is None:
        _memory_graph = MemoryGraph(persistence_path=persistence_path)
    
    return _memory_graph
