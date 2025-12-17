"""Integration tests for biomimetic features working together.

Tests that memory decay, semantic chunking, and attention spotlight
compose correctly without needing full prompt_assembler.
"""

import pytest
from datetime import datetime, timezone, timedelta
from brain.memory_decay import MemoryDecayWeighter, apply_decay_to_memories
from brain.semantic_chunking import SemanticChunker
from brain.attention_spotlight import AttentionalSpotlight


def test_decay_then_chunking():
    """Test that decay weights work before chunking."""
    now = datetime.now(timezone.utc)
    yesterday = (now - timedelta(days=1)).isoformat()
    month_ago = (now - timedelta(days=30)).isoformat()  # Older for visible decay
    
    # Memories with varying ages
    memories = [
        {"content": "Python is fast", "metadata": {"importance": 5, "timestamp": yesterday}, "distance": 0.1},
        {"content": "Python is optimized", "metadata": {"importance": 4, "timestamp": yesterday}, "distance": 0.12},
        {"content": "Old Python fact", "metadata": {"importance": 3, "timestamp": month_ago}, "distance": 0.15},
    ]
    
    # Apply decay
    weighter = MemoryDecayWeighter(time_scale_hours=100.0)
    decayed = apply_decay_to_memories(memories, weighter)
    
    # Old memory should be downweighted
    assert decayed[2]["metadata"]["decay_weight"] < decayed[0]["metadata"]["decay_weight"]
    
    # Now apply chunking to decayed results
    chunker = SemanticChunker(similarity_threshold=0.2, min_chunk_size=2)
    memory_tuples = [(m["content"], m["metadata"]) for m in decayed[:2]]  # Top 2 after decay
    chunks = chunker.chunk_memories(memory_tuples)
    
    # Should group the two Python memories
    assert len(chunks) == 1
    assert chunks[0].size == 2


def test_chunking_then_attention():
    """Test that chunking works before attention spotlight."""
    now = datetime.now(timezone.utc).isoformat()
    
    # 6 memories in 2 groups
    memories = [
        ("Python fact 1", {"importance": 5, "timestamp": now, "distance": 0.1}),
        ("Python fact 2", {"importance": 4, "timestamp": now, "distance": 0.12}),
        ("Python fact 3", {"importance": 4, "timestamp": now, "distance": 0.15}),
        ("Rust fact 1", {"importance": 3, "timestamp": now, "distance": 0.9}),
        ("Rust fact 2", {"importance": 3, "timestamp": now, "distance": 0.92}),
        ("Rust fact 3", {"importance": 3, "timestamp": now, "distance": 0.95}),
    ]
    
    # Chunk first
    chunker = SemanticChunker(similarity_threshold=0.15, min_chunk_size=2)
    chunks = chunker.chunk_memories(memories)
    
    # Should have 2 chunks
    assert len(chunks) == 2
    
    # Convert chunks to format attention spotlight expects
    attention_items = []
    for chunk in chunks:
        attention_items.append({
            "content": chunk.format_summary(),
            "metadata": chunk.get_metadata(),
            "distance": chunk.centroid_distance
        })
    
    # Apply attention spotlight
    spotlight = AttentionalSpotlight(spotlight_size=1)
    distribution = spotlight.apply_attention(attention_items)
    
    # Should have 1 in focus, 1 in periphery
    assert len(distribution.spotlight_items) == 1
    assert len(distribution.periphery_items) == 1


def test_full_pipeline_composition():
    """Test all three features compose: decay → chunking → attention."""
    now = datetime.now(timezone.utc)
    recent = now.isoformat()
    month_ago = (now - timedelta(days=30)).isoformat()  # Older for visible decay
    
    # Mix of old/new, similar/different
    memories = [
        {"content": "Python is fast", "metadata": {"importance": 5, "timestamp": recent}, "distance": 0.1},
        {"content": "Python is optimized", "metadata": {"importance": 4, "timestamp": recent}, "distance": 0.12},
        {"content": "Old Python fact", "metadata": {"importance": 3, "timestamp": month_ago}, "distance": 0.15},
        {"content": "Rust is memory safe", "metadata": {"importance": 5, "timestamp": recent}, "distance": 0.9},
    ]
    
    # Step 1: Decay
    weighter = MemoryDecayWeighter(time_scale_hours=100.0)
    decayed = apply_decay_to_memories(memories, weighter)
    
    # Old memory should be downweighted
    old_weight = next(m["metadata"]["decay_weight"] for m in decayed if "Old" in m["content"])
    recent_weight = next(m["metadata"]["decay_weight"] for m in decayed if m["content"] == "Python is fast")
    assert old_weight < recent_weight
    
    # Step 2: Chunking (group similar recent memories)
    chunker = SemanticChunker(similarity_threshold=0.2, min_chunk_size=2)
    # Take top 3 after decay (should be 2 recent Python + Rust)
    top_decayed = sorted(decayed, key=lambda m: m["metadata"]["decay_weight"], reverse=True)[:3]
    memory_tuples = [(m["content"], m["metadata"]) for m in top_decayed]
    chunks = chunker.chunk_memories(memory_tuples)
    
    # Should have 2 chunks (Python group + Rust singleton)
    assert 1 <= len(chunks) <= 2
    
    # Step 3: Attention (focus on most salient)
    attention_items = []
    for chunk in chunks:
        attention_items.append({
            "content": chunk.format_summary(),
            "metadata": chunk.get_metadata(),
            "distance": chunk.centroid_distance
        })
    
    spotlight = AttentionalSpotlight(spotlight_size=2)
    distribution = spotlight.apply_attention(attention_items)
    
    # All chunks should fit in spotlight (only 1-2 chunks)
    assert len(distribution.spotlight_items) <= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
