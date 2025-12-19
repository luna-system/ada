"""Tests for brain/memory_graph.py - Biomimetic associative memory.

Tests the core GraphRAG functionality:
- Node and edge operations
- Spreading activation (the key biomimetic feature)
- Hebbian learning from co-occurrence
- Temporal decay
- Persistence

Run with: pytest tests/test_memory_graph.py -v --ignore=tests/conftest.py
"""

import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path
import tempfile
import json

from brain.memory_graph import (
    MemoryGraph,
    MemoryNode,
    MemoryEdge,
    get_memory_graph,
    HAS_NETWORKX
)


class TestMemoryNode:
    """Test MemoryNode dataclass."""
    
    def test_create_node(self):
        """Nodes can be created with required fields."""
        now = datetime.now(timezone.utc)
        node = MemoryNode(
            memory_id="test_001",
            content_hash="abc123",
            created_at=now,
            last_accessed=now,
            topics=["python", "testing"],
            entities=["Ada", "Luna"]
        )
        
        assert node.memory_id == "test_001"
        assert node.topics == ["python", "testing"]
        assert node.entities == ["Ada", "Luna"]
        assert node.activation_count == 0
    
    def test_node_defaults(self):
        """Nodes have sensible defaults."""
        now = datetime.now(timezone.utc)
        node = MemoryNode(
            memory_id="test_002",
            content_hash="def456",
            created_at=now,
            last_accessed=now
        )
        
        assert node.topics == []
        assert node.entities == []
        assert node.activation_count == 0


class TestMemoryEdge:
    """Test MemoryEdge dataclass."""
    
    def test_create_edge(self):
        """Edges can be created with relationship type."""
        edge = MemoryEdge(
            source_id="mem_1",
            target_id="mem_2",
            relationship_type="co_occurred",
            weight=0.8
        )
        
        assert edge.source_id == "mem_1"
        assert edge.target_id == "mem_2"
        assert edge.relationship_type == "co_occurred"
        assert edge.weight == 0.8
        assert edge.activation_count == 0
    
    def test_edge_defaults(self):
        """Edges have default weight and timestamps."""
        edge = MemoryEdge(
            source_id="mem_1",
            target_id="mem_2",
            relationship_type="related"
        )
        
        assert edge.weight == 1.0
        assert edge.created_at is not None
        assert edge.last_activated is not None


class TestMemoryGraph:
    """Test MemoryGraph core operations."""
    
    def test_create_empty_graph(self):
        """Empty graph can be created."""
        graph = MemoryGraph()
        
        assert len(graph.nodes) == 0
        assert graph.get_stats()["nodes"] == 0
        assert graph.get_stats()["edges"] == 0
    
    def test_add_node(self):
        """Nodes can be added to graph."""
        graph = MemoryGraph()
        
        node = graph.add_node(
            memory_id="test_001",
            content_hash="abc123",
            topics=["python", "specialist"],
            entities=["BaseSpecialist"]
        )
        
        assert node.memory_id == "test_001"
        assert "test_001" in graph.nodes
        assert graph.get_stats()["nodes"] == 1
    
    def test_topic_indexing(self):
        """Topics are indexed for fast lookup."""
        graph = MemoryGraph()
        
        graph.add_node("mem_1", topics=["python", "testing"])
        graph.add_node("mem_2", topics=["python", "debugging"])
        graph.add_node("mem_3", topics=["javascript"])
        
        # Case-insensitive lookup
        assert "mem_1" in graph.topic_index["python"]
        assert "mem_2" in graph.topic_index["python"]
        assert "mem_3" not in graph.topic_index["python"]
    
    def test_entity_indexing(self):
        """Entities are indexed for fast lookup."""
        graph = MemoryGraph()
        
        graph.add_node("mem_1", entities=["Ada", "Luna"])
        graph.add_node("mem_2", entities=["Ada", "Claude"])
        
        assert "mem_1" in graph.entity_index["ada"]
        assert "mem_2" in graph.entity_index["ada"]
        assert "mem_1" in graph.entity_index["luna"]
        assert "mem_1" not in graph.entity_index["claude"]
    
    def test_add_edge(self):
        """Edges can be added between nodes."""
        graph = MemoryGraph()
        
        graph.add_node("mem_1")
        graph.add_node("mem_2")
        edge = graph.add_edge("mem_1", "mem_2", "co_occurred", 0.7)
        
        assert edge.source_id == "mem_1"
        assert edge.target_id == "mem_2"
        assert edge.weight == 0.7
        assert graph.get_stats()["edges"] == 1
    
    def test_edge_default_weights(self):
        """Edges use default weights based on relationship type."""
        graph = MemoryGraph()
        
        graph.add_node("mem_1")
        graph.add_node("mem_2")
        graph.add_node("mem_3")
        
        edge1 = graph.add_edge("mem_1", "mem_2", "caused")
        edge2 = graph.add_edge("mem_1", "mem_3", "related")
        
        assert edge1.weight == 0.9  # "caused" default
        assert edge2.weight == 0.5  # "related" default


class TestSpreadingActivation:
    """Test the core biomimetic feature: spreading activation."""
    
    def test_single_seed_activation(self):
        """Activation spreads from a single seed node."""
        graph = MemoryGraph()
        
        # Create a simple chain: mem_1 -> mem_2 -> mem_3
        graph.add_node("mem_1")
        graph.add_node("mem_2")
        graph.add_node("mem_3")
        graph.add_edge("mem_1", "mem_2", "related", 1.0)
        graph.add_edge("mem_2", "mem_3", "related", 1.0)
        
        activations = graph.spread_activation(["mem_1"], depth=2, decay_factor=0.7)
        
        # Seed has full activation
        assert activations["mem_1"] == 1.0
        # First hop has decayed activation
        assert 0.65 < activations["mem_2"] < 0.75  # ~0.7
        # Second hop has more decay
        assert 0.45 < activations["mem_3"] < 0.55  # ~0.49
    
    def test_multiple_seed_activation(self):
        """Multiple seeds can activate the graph."""
        graph = MemoryGraph()
        
        graph.add_node("mem_1")
        graph.add_node("mem_2")
        graph.add_node("mem_3")
        graph.add_edge("mem_1", "mem_3", "related", 1.0)
        graph.add_edge("mem_2", "mem_3", "related", 1.0)
        
        activations = graph.spread_activation(["mem_1", "mem_2"], depth=1, decay_factor=0.7)
        
        assert activations["mem_1"] == 1.0
        assert activations["mem_2"] == 1.0
        # mem_3 receives activation from both seeds
        assert activations["mem_3"] == pytest.approx(0.7, rel=0.01)
    
    def test_activation_threshold(self):
        """Low activation doesn't spread further."""
        graph = MemoryGraph()
        
        # Long chain
        for i in range(5):
            graph.add_node(f"mem_{i}")
        for i in range(4):
            graph.add_edge(f"mem_{i}", f"mem_{i+1}", "related", 0.5)
        
        activations = graph.spread_activation(
            ["mem_0"], 
            depth=10, 
            decay_factor=0.5, 
            threshold=0.1
        )
        
        # Activation should peter out before reaching far nodes
        assert "mem_0" in activations
        assert "mem_1" in activations
        # Later nodes might not have enough activation
        assert activations.get("mem_4", 0) < 0.1
    
    def test_activation_max_nodes(self):
        """Activation respects max_nodes limit."""
        graph = MemoryGraph()
        
        # Create a hub with many spokes
        graph.add_node("hub")
        for i in range(50):
            graph.add_node(f"spoke_{i}")
            graph.add_edge("hub", f"spoke_{i}", "related", 0.8)
        
        activations = graph.spread_activation(["hub"], depth=1, max_nodes=10)
        
        assert len(activations) <= 10
    
    def test_hebbian_strengthening(self):
        """Traversed edges get activation count incremented."""
        graph = MemoryGraph()
        
        graph.add_node("mem_1")
        graph.add_node("mem_2")
        edge = graph.add_edge("mem_1", "mem_2", "related", 0.8)
        
        initial_count = edge.activation_count
        
        graph.spread_activation(["mem_1"], depth=1)
        
        # Edge should have been activated
        _, updated_edge = graph.edges["mem_1"][0]
        assert updated_edge.activation_count == initial_count + 1


class TestHebbianLearning:
    """Test automatic edge creation from co-occurrence."""
    
    def test_learn_from_shared_topics(self):
        """Edges created between memories with shared topics."""
        graph = MemoryGraph()
        
        graph.add_node("mem_1", topics=["python", "specialist", "protocol"])
        graph.add_node("mem_2", topics=["python", "specialist", "testing"])
        graph.add_node("mem_3", topics=["javascript", "frontend"])
        
        edges_created = graph.learn_edges_from_cooccurrence(min_shared_topics=2)
        
        # mem_1 and mem_2 share "python" and "specialist"
        assert edges_created >= 1
        
        # Verify edge exists (could be in either direction due to implementation)
        has_edge = any(
            target == "mem_2" for target, _ in graph.edges.get("mem_1", [])
        ) or any(
            target == "mem_1" for target, _ in graph.edges.get("mem_2", [])
        )
        assert has_edge
    
    def test_no_edges_for_unrelated(self):
        """No edges for memories without shared topics."""
        graph = MemoryGraph()
        
        graph.add_node("mem_1", topics=["python", "backend"])
        graph.add_node("mem_2", topics=["javascript", "frontend"])
        
        edges_created = graph.learn_edges_from_cooccurrence(min_shared_topics=2)
        
        assert edges_created == 0
    
    def test_cooccurrence_weight_scales(self):
        """More shared topics = higher weight."""
        graph = MemoryGraph()
        
        graph.add_node("mem_1", topics=["a", "b", "c", "d", "e"])
        graph.add_node("mem_2", topics=["a", "b", "c", "d", "e"])  # 5 shared
        graph.add_node("mem_3", topics=["a", "b", "f", "g", "h"])  # 2 shared
        
        graph.learn_edges_from_cooccurrence(min_shared_topics=2)
        
        # Find edges between mem_1 and mem_2 (either direction)
        edge_to_2 = next(
            (e for t, e in graph.edges.get("mem_1", []) if t == "mem_2"),
            None
        ) or next(
            (e for t, e in graph.edges.get("mem_2", []) if t == "mem_1"),
            None
        )
        
        # Find edges between mem_1 and mem_3 (either direction)
        edge_to_3 = next(
            (e for t, e in graph.edges.get("mem_1", []) if t == "mem_3"),
            None
        ) or next(
            (e for t, e in graph.edges.get("mem_3", []) if t == "mem_1"),
            None
        )
        
        assert edge_to_2 is not None
        assert edge_to_3 is not None
        # More shared topics = higher weight
        assert edge_to_2.weight > edge_to_3.weight


class TestTopicCooccurrence:
    """Test finding co-occurring topics."""
    
    def test_find_cooccurring_topics(self):
        """Topics that appear together are found."""
        graph = MemoryGraph()
        
        graph.add_node("mem_1", topics=["python", "specialist"])
        graph.add_node("mem_2", topics=["python", "specialist"])
        graph.add_node("mem_3", topics=["python", "protocol"])
        graph.add_node("mem_4", topics=["javascript"])
        
        cooccurring = graph.find_co_occurring_topics("python", min_cooccurrence=2)
        
        # "specialist" appears with "python" twice
        topics = [t for t, _ in cooccurring]
        assert "specialist" in topics
        # "protocol" only once
        assert "protocol" not in topics


class TestDecay:
    """Test temporal decay of edges."""
    
    def test_decay_reduces_weight(self):
        """Old edges lose weight."""
        graph = MemoryGraph()
        
        graph.add_node("mem_1")
        graph.add_node("mem_2")
        edge = graph.add_edge("mem_1", "mem_2", "related", 0.5)
        
        # Simulate edge being old
        edge.last_activated = datetime.now(timezone.utc) - timedelta(days=30)
        
        graph.apply_decay(decay_rate=0.01)  # 1% per day
        
        # Edge should have lost ~30% weight
        _, updated_edge = graph.edges["mem_1"][0]
        assert updated_edge.weight < 0.3  # 0.5 - 0.3 = 0.2
    
    def test_recent_edges_preserved(self):
        """Recently activated edges don't decay much."""
        graph = MemoryGraph()
        
        graph.add_node("mem_1")
        graph.add_node("mem_2")
        edge = graph.add_edge("mem_1", "mem_2", "related", 0.5)
        
        # Edge is fresh
        edge.last_activated = datetime.now(timezone.utc)
        
        graph.apply_decay(decay_rate=0.01)
        
        _, updated_edge = graph.edges["mem_1"][0]
        assert updated_edge.weight == pytest.approx(0.5, rel=0.01)
    
    def test_dead_edges_removed(self):
        """Edges that decay to 0 are removed."""
        graph = MemoryGraph()
        
        graph.add_node("mem_1")
        graph.add_node("mem_2")
        edge = graph.add_edge("mem_1", "mem_2", "related", 0.1)
        
        # Very old edge
        edge.last_activated = datetime.now(timezone.utc) - timedelta(days=100)
        
        removed = graph.apply_decay(decay_rate=0.01)
        
        assert removed >= 1
        assert len(graph.edges.get("mem_1", [])) == 0


class TestPersistence:
    """Test save/load functionality."""
    
    def test_save_and_load(self):
        """Graph can be saved and restored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_graph.json"
            
            # Create and populate graph
            graph1 = MemoryGraph(persistence_path=path)
            graph1.add_node("mem_1", topics=["python"])
            graph1.add_node("mem_2", topics=["testing"])
            graph1.add_edge("mem_1", "mem_2", "related", 0.8)
            graph1.save()
            
            # Load into new graph
            graph2 = MemoryGraph(persistence_path=path)
            graph2.load()
            
            assert len(graph2.nodes) == 2
            assert "mem_1" in graph2.nodes
            assert graph2.nodes["mem_1"].topics == ["python"]
            assert len(graph2.edges["mem_1"]) == 1
    
    def test_persistence_path_auto_load(self):
        """Graph auto-loads from persistence path if exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_graph.json"
            
            # Create initial graph
            graph1 = MemoryGraph(persistence_path=path)
            graph1.add_node("mem_1", topics=["python"])
            graph1.save()
            
            # New graph should auto-load
            graph2 = MemoryGraph(persistence_path=path)
            
            assert "mem_1" in graph2.nodes


class TestStats:
    """Test statistics and monitoring."""
    
    def test_stats_accuracy(self):
        """Stats reflect actual graph state."""
        graph = MemoryGraph()
        
        graph.add_node("mem_1", topics=["a", "b"])
        graph.add_node("mem_2", topics=["b", "c"])
        graph.add_node("mem_3", entities=["Ada"])
        graph.add_edge("mem_1", "mem_2", "related")
        graph.add_edge("mem_2", "mem_3", "caused")
        
        stats = graph.get_stats()
        
        assert stats["nodes"] == 3
        assert stats["edges"] == 2
        assert stats["topics"] == 3  # a, b, c
        assert stats["entities"] == 1  # Ada
        assert stats["has_networkx"] == HAS_NETWORKX


class TestNetworkXIntegration:
    """Test NetworkX integration if available."""
    
    @pytest.mark.skipif(not HAS_NETWORKX, reason="NetworkX not installed")
    def test_networkx_graph_synced(self):
        """NetworkX graph stays in sync with our data structures."""
        import networkx as nx
        
        graph = MemoryGraph()
        
        graph.add_node("mem_1", topics=["python"])
        graph.add_node("mem_2", topics=["testing"])
        graph.add_edge("mem_1", "mem_2", "related", 0.8)
        
        # Check NetworkX graph
        assert graph._nx_graph is not None
        assert graph._nx_graph.number_of_nodes() == 2
        assert graph._nx_graph.number_of_edges() == 1
        assert graph._nx_graph.has_edge("mem_1", "mem_2")
