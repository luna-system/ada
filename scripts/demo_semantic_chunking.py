#!/usr/bin/env python3
"""Demo semantic chunking with generated test memories.

This script demonstrates how semantic chunking groups similar memories
by embedding distance, reducing token usage while preserving context.

Shows:
- Memory loading from JSON
- Semantic chunking with configurable threshold
- Token count reduction
- Representative selection (importance + recency)
"""
import json
from pathlib import Path
from datetime import datetime
import sys

# Add brain to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from brain.semantic_chunking import SemanticChunker


def load_test_memories(path: Path) -> list[dict]:
    """Load memories from JSON file."""
    with path.open() as f:
        return json.load(f)


def format_memory_short(memory) -> str:
    """Format memory for display (handles both dict and tuple formats)."""
    if isinstance(memory, tuple):
        content, metadata = memory
    else:
        content = memory["content"]
        metadata = memory["metadata"]
    
    content_short = content[:60] + "..." if len(content) > 60 else content
    topic = metadata.get("topic", "unknown")
    importance = metadata.get("importance", 0.5)
    timestamp = metadata.get("timestamp", "")[:10]
    return f"{content_short} [topic:{topic}, imp:{importance:.2f}, date:{timestamp}]"


def estimate_tokens(text: str) -> int:
    """Rough token estimate (1 token ≈ 4 characters)."""
    return len(text) // 4


def demo_chunking(memories: list[dict], threshold: float = 0.3):
    """Demonstrate semantic chunking."""
    print(f"\n🧠 Semantic Chunking Demo")
    print(f"{'='*70}\n")
    
    # Add fake distances for demo (in real use, these come from ChromaDB)
    # Simulate clustering by topic
    topics = {}
    for i, memory in enumerate(memories):
        topic = memory["metadata"].get("topic", "unknown")
        if topic not in topics:
            topics[topic] = []
        topics[topic].append(i)
    
    # Assign distances based on topic clustering
    for memory in memories:
        memory["distance"] = 0.5  # Default mid-range
    
    # Make same-topic memories closer
    for topic, indices in topics.items():
        base_distance = hash(topic) % 100 / 200  # Topic-specific base
        for i, idx in enumerate(indices):
            memories[idx]["distance"] = base_distance + (i * 0.05)
    
    print(f"📥 Input: {len(memories)} memories")
    
    # Calculate original token count
    original_text = "\n".join(m["content"] for m in memories)
    original_tokens = estimate_tokens(original_text)
    print(f"   Original tokens: {original_tokens}")
    
    # Apply chunking
    chunker = SemanticChunker(
        similarity_threshold=threshold,
        min_chunk_size=2,
        max_chunk_size=10
    )
    
    # Convert to format expected by chunker: List[Tuple[str, Dict]]
    memory_tuples = [
        (m["content"], {**m["metadata"], "distance": m.get("distance", 0.5)})
        for m in memories
    ]
    
    chunks = chunker.chunk_memories(memory_tuples)
    print(f"\n📦 Chunked: {len(memories)} memories → {len(chunks)} chunks")
    print(f"   Threshold: {threshold} (lower = stricter grouping)")
    
    # Show chunks
    print(f"\n{'Chunk Details':<70}")
    print("-" * 70)
    
    for i, chunk in enumerate(chunks, 1):
        print(f"\n🔸 Chunk {i} ({chunk.size} memories)")
        print(f"   Representative: {format_memory_short(chunk.representative)}")
        
        if chunk.size > 1:
            print(f"   Similar memories:")
            for member in chunk.members[:3]:  # Show first 3
                print(f"     • {format_memory_short(member)}")
            if chunk.size > 4:
                print(f"     ... and {chunk.size - 4} more")
        
        # Show formatted summary
        if chunk.size == 1:
            summary = chunk.representative[0]  # Just the content
        else:
            rep_content = chunk.representative[0]
            summary = f"{rep_content} (+{chunk.size - 1} similar)"
        
        tokens = estimate_tokens(summary)
        print(f"   Formatted: \"{summary[:70]}...\"")
        print(f"   Tokens: {tokens}")
    
    # Calculate savings
    chunked_summaries = []
    for chunk in chunks:
        if chunk.size == 1:
            chunked_summaries.append(chunk.representative[0])
        else:
            rep_content = chunk.representative[0]
            chunked_summaries.append(f"{rep_content} (+{chunk.size - 1} similar)")
    
    chunked_text = "\n".join(chunked_summaries)
    chunked_tokens = estimate_tokens(chunked_text)
    savings = ((original_tokens - chunked_tokens) / original_tokens) * 100
    
    print(f"\n{'Token Savings':<70}")
    print("-" * 70)
    print(f"  Original: {original_tokens} tokens")
    print(f"  Chunked:  {chunked_tokens} tokens")
    print(f"  Savings:  {savings:.1f}% reduction")
    
    print(f"\n✨ Semantic chunking preserves meaning while reducing tokens!")


def main():
    # Load test memories
    mem_path = Path("data/test_memories.json")
    
    if not mem_path.exists():
        print(f"❌ No test memories found at {mem_path}")
        print("   Run: python scripts/generate_test_memories.py")
        sys.exit(1)
    
    memories = load_test_memories(mem_path)
    
    # Take first 20 for demo
    demo_memories = memories[:20]
    
    print("🎵 'Revolution in a zip file, baby' 🎵")
    print("Testing semantic chunking with generated memories\n")
    
    # Demo with default threshold
    demo_chunking(demo_memories, threshold=0.3)
    
    # Show effect of different thresholds
    print(f"\n\n{'Threshold Comparison':<70}")
    print("=" * 70)
    
    # Convert once for comparison
    memory_tuples = [
        (m["content"], {**m["metadata"], "distance": m.get("distance", 0.5)})
        for m in demo_memories
    ]
    
    for threshold in [0.1, 0.3, 0.5]:
        chunker = SemanticChunker(similarity_threshold=threshold)
        chunks = chunker.chunk_memories(memory_tuples.copy())
        print(f"  Threshold {threshold}: {len(demo_memories)} memories → {len(chunks)} chunks")


if __name__ == "__main__":
    main()
