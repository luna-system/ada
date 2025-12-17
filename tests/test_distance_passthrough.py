"""Test that distance scores pass through from ChromaDB to attention spotlight."""

import pytest
import os
from unittest.mock import Mock, patch
from brain.rag_store import RagStore


def test_retrieve_memories_includes_distances():
    """Test that retrieve_memories captures and includes distance scores in metadata."""
    # Mock ChromaDB collection
    mock_col = Mock()
    mock_result = {
        "documents": [["memory1", "memory2", "memory3"]],
        "metadatas": [[
            {"type": "memory", "importance": 5, "timestamp": "2025-01-01T00:00:00Z"},
            {"type": "memory", "importance": 3, "timestamp": "2025-01-02T00:00:00Z"},
            {"type": "memory", "importance": 4, "timestamp": "2025-01-03T00:00:00Z"},
        ]],
        "distances": [[0.1, 0.3, 0.5]]  # ChromaDB returns similarity distances
    }
    mock_col.query.return_value = mock_result
    
    # Create RagStore instance with mocked collection (skip ChromaDB init)
    with patch('chromadb.PersistentClient'):
        with patch.dict(os.environ, {'CHROMA_URL': ''}, clear=False):
            rag_store = RagStore()
            rag_store.col = mock_col
            rag_store.use_http = False
    
    # Retrieve memories
    results = rag_store.retrieve_memories(query="test query", k=3)
    
    # Verify distances are in metadata
    assert len(results) == 3
    distances_found = []
    for i, (text, metadata) in enumerate(results):
        assert "distance" in metadata, f"Memory {i} missing distance"
        assert isinstance(metadata["distance"], (int, float)), "Distance should be numeric"
        assert 0.0 <= metadata["distance"] <= 2.0, "Distance should be in reasonable range"
        distances_found.append(metadata["distance"])
        
    # Verify we got all 3 distances (order may vary due to reranking)
    assert set(distances_found) == {0.1, 0.3, 0.5}, "All distances should be present"


def test_retrieve_memories_handles_missing_distances():
    """Test graceful handling when ChromaDB doesn't return distances."""
    mock_col = Mock()
    mock_result = {
        "documents": [["memory1"]],
        "metadatas": [[{"type": "memory", "importance": 3}]],
        # No distances key
    }
    mock_col.query.return_value = mock_result
    
    # Create RagStore with mocked collection
    with patch('chromadb.PersistentClient'):
        with patch.dict(os.environ, {'CHROMA_URL': ''}, clear=False):
            rag_store = RagStore()
            rag_store.col = mock_col
            rag_store.use_http = False
    
    # Should not crash
    results = rag_store.retrieve_memories(query="test", k=1)
    assert len(results) == 1
    # Distance should not be added if not present
    # (context_retriever will default to 0.5)


def test_distance_used_in_attention_spotlight():
    """Integration test: distance flows through to attention spotlight."""
    from brain.attention_spotlight import AttentionalSpotlight
    
    # Simulate memories with distances (as they'd come from context_retriever)
    # Format: apply_attention expects List[Dict] with 'content', 'metadata', 'distance'
    items = [
        {
            "content": "High relevance memory",
            "metadata": {"importance": 5, "timestamp": "2025-12-17T00:00:00Z"},
            "distance": 0.1  # Closest = most relevant
        },
        {
            "content": "Medium relevance memory",
            "metadata": {"importance": 3, "timestamp": "2025-12-17T00:00:00Z"},
            "distance": 0.5
        },
        {
            "content": "Low relevance memory",
            "metadata": {"importance": 2, "timestamp": "2025-12-17T00:00:00Z"},
            "distance": 0.9  # Farthest = least relevant
        },
    ]
    
    # Apply attention spotlight
    spotlight = AttentionalSpotlight(
        spotlight_size=2,
        spotlight_budget=4000,
        periphery_budget=8000
    )
    distribution = spotlight.apply_attention(items)
    
    # Verify spotlight has 2 items
    assert len(distribution.spotlight_items) == 2
    # Items should be sorted by salience (importance + recency + distance-based relevance)
    assert distribution.spotlight_items[0].salience_score >= distribution.spotlight_items[1].salience_score
    
    # Distance=0.1 memory (high relevance) should beat distance=0.9 (low relevance)
    spotlight_contents = [item.content for item in distribution.spotlight_items]
    assert any("High relevance" in content for content in spotlight_contents), \
        f"Closest memory should be in spotlight, got: {spotlight_contents}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
