"""Tests for semantic chunking of memories."""

import pytest
from brain.semantic_chunking import (
    SemanticChunker,
    MemoryChunk,
    apply_chunking_to_memories
)


def test_semantic_chunker_init():
    """Test SemanticChunker initialization with custom parameters."""
    chunker = SemanticChunker(
        similarity_threshold=0.4,
        min_chunk_size=3,
        max_chunk_size=5
    )
    assert chunker.similarity_threshold == 0.4
    assert chunker.min_chunk_size == 3
    assert chunker.max_chunk_size == 5


def test_chunk_empty_memories():
    """Test chunking with empty input."""
    chunker = SemanticChunker()
    chunks = chunker.chunk_memories([])
    assert chunks == []


def test_chunk_single_memory():
    """Test chunking with single memory (should return 1 chunk)."""
    chunker = SemanticChunker(min_chunk_size=1)
    memories = [
        ("Single memory", {"importance": 3, "distance": 0.5})
    ]
    chunks = chunker.chunk_memories(memories)
    
    assert len(chunks) == 1
    assert chunks[0].size == 1
    assert chunks[0].representative[0] == "Single memory"


def test_chunk_similar_memories():
    """Test that similar memories (close distances) get grouped."""
    chunker = SemanticChunker(
        similarity_threshold=0.2,
        min_chunk_size=2
    )
    memories = [
        ("Python is fast", {"importance": 4, "distance": 0.1}),
        ("Python has good performance", {"importance": 3, "distance": 0.12}),
        ("Python is optimized", {"importance": 3, "distance": 0.15}),
        ("JavaScript async is tricky", {"importance": 5, "distance": 0.8}),
    ]
    chunks = chunker.chunk_memories(memories)
    
    # Should have 2 chunks: Python group + JavaScript singleton
    assert len(chunks) == 2
    
    # Python chunk should have 3 members
    python_chunk = next(c for c in chunks if c.size == 3)
    assert python_chunk.size == 3
    assert "Python" in python_chunk.representative[0]
    
    # JavaScript should be singleton
    js_chunk = next(c for c in chunks if c.size == 1)
    assert "JavaScript" in js_chunk.representative[0]


def test_chunk_representative_selection():
    """Test that highest importance memory becomes representative."""
    chunker = SemanticChunker(
        similarity_threshold=0.3,
        min_chunk_size=2
    )
    memories = [
        ("Low importance", {"importance": 2, "distance": 0.1}),
        ("High importance", {"importance": 5, "distance": 0.12}),
        ("Medium importance", {"importance": 3, "distance": 0.15}),
    ]
    chunks = chunker.chunk_memories(memories)
    
    assert len(chunks) == 1  # All similar, one chunk
    assert chunks[0].representative[0] == "High importance"
    assert chunks[0].representative[1]["importance"] == 5


def test_max_chunk_size_enforced():
    """Test that chunks don't exceed max_chunk_size."""
    chunker = SemanticChunker(
        similarity_threshold=0.5,  # Large threshold
        min_chunk_size=2,
        max_chunk_size=3
    )
    
    # 5 similar memories
    memories = [
        (f"Memory {i}", {"importance": 3, "distance": 0.1 + i*0.01})
        for i in range(5)
    ]
    chunks = chunker.chunk_memories(memories)
    
    # Should split into multiple chunks, none > 3
    for chunk in chunks:
        assert chunk.size <= 3


def test_min_chunk_size_enforced():
    """Test that small groups become singletons if below min_chunk_size."""
    chunker = SemanticChunker(
        similarity_threshold=0.1,  # Strict
        min_chunk_size=3
    )
    
    # 2 similar memories (below min)
    memories = [
        ("Memory 1", {"importance": 3, "distance": 0.1}),
        ("Memory 2", {"importance": 3, "distance": 0.11}),
        ("Memory 3", {"importance": 3, "distance": 0.9}),  # Dissimilar
    ]
    chunks = chunker.chunk_memories(memories)
    
    # Should be 3 singleton chunks (group too small)
    assert len(chunks) == 3
    assert all(c.size == 1 for c in chunks)


def test_memory_chunk_format_summary():
    """Test MemoryChunk summary formatting."""
    chunk = MemoryChunk(
        representative=("Main memory", {"importance": 5}),
        members=[
            ("Main memory", {"importance": 5}),
            ("Similar 1", {"importance": 3}),
            ("Similar 2", {"importance": 4}),
        ],
        centroid_distance=0.12,
        size=3
    )
    
    summary = chunk.format_summary()
    assert "Main memory" in summary
    assert "+2 similar" in summary  # 3 total - 1 representative


def test_memory_chunk_singleton_format():
    """Test MemoryChunk with single member (no +N suffix)."""
    chunk = MemoryChunk(
        representative=("Only memory", {"importance": 3}),
        members=[("Only memory", {"importance": 3})],
        centroid_distance=0.5,
        size=1
    )
    
    summary = chunk.format_summary()
    assert summary == "Only memory"
    assert "similar" not in summary


def test_collapse_chunks_respects_budget():
    """Test that collapse_chunks respects token budget."""
    chunker = SemanticChunker()
    chunks = [
        MemoryChunk(
            representative=(f"Memory {i}" * 100, {"importance": 3}),
            members=[(f"Memory {i}" * 100, {"importance": 3})],
            centroid_distance=0.1,
            size=1
        )
        for i in range(10)
    ]
    
    # Small budget should limit results
    result = chunker.collapse_chunks(chunks, max_tokens=100)
    assert len(result) < 10  # Can't fit all


def test_apply_chunking_convenience_function():
    """Test convenience function with default chunker."""
    memories = [
        ("Python is fast", {"importance": 4, "distance": 0.1}),
        ("Python is optimized", {"importance": 3, "distance": 0.12}),
        ("JavaScript is single-threaded", {"importance": 5, "distance": 0.9}),
    ]
    
    result = apply_chunking_to_memories(memories)
    
    # Should return chunked memories
    assert len(result) > 0
    assert all(isinstance(item, tuple) for item in result)
    assert all(len(item) == 2 for item in result)  # (content, metadata)


def test_chunking_preserves_metadata():
    """Test that chunking preserves metadata from representative."""
    chunker = SemanticChunker(min_chunk_size=2)
    memories = [
        ("Memory 1", {"importance": 5, "distance": 0.1, "custom": "value1"}),
        ("Memory 2", {"importance": 3, "distance": 0.12, "custom": "value2"}),
    ]
    
    chunks = chunker.chunk_memories(memories)
    assert len(chunks) == 1
    
    # Should preserve custom metadata from representative (importance=5)
    assert chunks[0].get_metadata()["custom"] == "value1"
    assert chunks[0].get_metadata()["importance"] == 5


def test_chunking_reduces_count():
    """Integration test: chunking reduces memory count."""
    chunker = SemanticChunker(
        similarity_threshold=0.15,  # Stricter threshold for distinct groups
        min_chunk_size=2
    )
    
    # 10 memories in 3 similarity groups with larger gaps
    memories = []
    for i in range(4):
        memories.append((f"Python fact {i}", {"importance": 3, "distance": 0.1 + i*0.02}))
    for i in range(3):
        memories.append((f"JavaScript fact {i}", {"importance": 3, "distance": 0.6 + i*0.02}))
    for i in range(3):
        memories.append((f"Rust fact {i}", {"importance": 3, "distance": 0.9 + i*0.02}))
    
    chunks = chunker.chunk_memories(memories)
    
    # Should have 3 chunks (one per group)
    assert len(chunks) == 3
    assert all(c.size >= 2 for c in chunks)  # Each group has min 2-4 members


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
