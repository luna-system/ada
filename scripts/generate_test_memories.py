#!/usr/bin/env python3
"""Generate realistic test memory data for Ada.

This script creates diverse memory documents for testing biomimetic features:
- Temporal distribution (recent to old)
- Importance variation (0.0 - 1.0)
- Semantic clustering (related topics)
- Entity scoping (user-specific, global)

Usage:
    python scripts/generate_test_memories.py --count 100 --output data/test_memories.json
    python scripts/generate_test_memories.py --load  # Load directly into ChromaDB
"""
import argparse
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any
import sys

# Memory templates organized by topic clusters
MEMORY_TEMPLATES = {
    "python_programming": [
        "Python list comprehensions are more efficient than loops for simple transformations",
        "Use f-strings for string formatting in Python 3.6+",
        "Type hints improve code readability and catch bugs early",
        "Dataclasses reduce boilerplate for simple data containers",
        "The walrus operator := allows assignment in expressions",
        "Use pathlib.Path instead of os.path for cleaner file operations",
        "Context managers (with statement) ensure proper resource cleanup",
        "asyncio enables concurrent I/O without threading complexity",
    ],
    "web_development": [
        "RESTful APIs use HTTP methods semantically (GET, POST, PUT, DELETE)",
        "Server-Sent Events (SSE) provide efficient one-way streaming",
        "CORS headers control cross-origin resource sharing",
        "HTTP caching with ETag and Last-Modified reduces server load",
        "WebSockets enable bidirectional real-time communication",
        "Progressive enhancement ensures baseline functionality for all users",
        "Content Security Policy headers prevent XSS attacks",
        "Service workers enable offline-first web applications",
    ],
    "machine_learning": [
        "Embeddings map semantic similarity to geometric distance",
        "Vector databases enable fast similarity search at scale",
        "Temperature controls randomness in LLM generation",
        "Attention mechanisms let models focus on relevant context",
        "RAG combines retrieval with generation for grounded responses",
        "Fine-tuning adapts pre-trained models to specific tasks",
        "Quantization reduces model size with minimal quality loss",
        "Prompt engineering guides model behavior without training",
    ],
    "open_source": [
        "Copyleft licenses require derivatives to be open source",
        "Permissive licenses allow proprietary use of code",
        "Semantic versioning communicates breaking changes clearly",
        "Conventional commits enable automated changelog generation",
        "GitHub Actions automate CI/CD workflows",
        "Documentation is a feature, not an afterthought",
        "Open source thrives on welcoming contributor communities",
        "DIY culture empowers everyone to build and share",
    ],
    "music_tech": [
        "ListenBrainz provides open music listening data",
        "MusicBrainz is the Wikipedia of music metadata",
        "FLAC provides lossless audio compression",
        "Sample rate determines audio frequency range captured",
        "Bit depth affects dynamic range and noise floor",
        "Metadata tags organize music libraries effectively",
        "Scrobbling tracks listening history automatically",
        "Open audio formats preserve user freedom",
    ],
    "unix_philosophy": [
        "Do one thing and do it well",
        "Compose small tools into powerful pipelines",
        "Text streams are universal interfaces",
        "Design for extensibility, not prediction",
        "Store data in flat text files when possible",
        "Silence is golden - only output what matters",
        "Make errors clear and actionable",
        "Everything is a file (or should act like one)",
    ],
}

def generate_memories(count: int, days_range: int = 90) -> List[Dict[str, Any]]:
    """Generate test memories with realistic variation.
    
    Args:
        count: Number of memories to generate
        days_range: Spread memories over this many days
        
    Returns:
        List of memory documents with content, metadata, timestamps
    """
    memories = []
    now = datetime.now(timezone.utc)
    
    # Flatten templates
    all_topics = list(MEMORY_TEMPLATES.keys())
    all_templates = [
        (topic, template)
        for topic, templates in MEMORY_TEMPLATES.items()
        for template in templates
    ]
    
    for i in range(count):
        # Select random template
        topic, content = random.choice(all_templates)
        
        # Generate timestamp with bias toward recent
        # Exponential distribution: more recent memories
        days_ago = random.expovariate(0.1) * days_range
        days_ago = min(days_ago, days_range)  # Cap at range
        timestamp = now - timedelta(days=days_ago)
        
        # Importance: Normal distribution centered at 0.5
        # Clamped to [0.0, 1.0]
        importance = random.gauss(0.5, 0.2)
        importance = max(0.0, min(1.0, importance))
        
        # Entity scope: 80% user-specific, 20% global
        scope = "user" if random.random() < 0.8 else "global"
        entity = "test_user" if scope == "user" else None
        
        memory = {
            "content": content,
            "metadata": {
                "type": "memory",
                "timestamp": timestamp.isoformat(),
                "importance": importance,
                "scope": scope,
                "topic": topic,
                "source": "test_generator",
            }
        }
        
        if entity:
            memory["metadata"]["entity"] = entity
        
        memories.append(memory)
    
    return memories


def save_memories(memories: List[Dict[str, Any]], output_path: Path):
    """Save memories to JSON file.
    
    Args:
        memories: List of memory documents
        output_path: Path to output JSON file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with output_path.open('w') as f:
        json.dump(memories, f, indent=2, default=str)
    
    print(f"✅ Saved {len(memories)} memories to {output_path}")


def load_memories_to_chroma(memories: List[Dict[str, Any]]):
    """Load memories directly into ChromaDB.
    
    Args:
        memories: List of memory documents
    """
    try:
        from brain.rag_store import RagStore
        from brain.config import CHROMA_MODE, DATA_DIR
        
        rag = RagStore()
        
        for memory in memories:
            content = memory["content"]
            metadata = memory["metadata"]
            
            rag.upsert_doc(
                text=content,
                type=metadata.get("type", "memory"),
                scope=metadata.get("scope", "user"),
                entity=metadata.get("entity"),
                topic=metadata.get("topic"),
                timestamp=metadata.get("timestamp"),
                importance=metadata.get("importance", 0.5),
                source=metadata.get("source", "test_generator")
            )
        
        print(f"✅ Loaded {len(memories)} memories into ChromaDB")
        
    except Exception as e:
        print(f"❌ Error loading to ChromaDB: {e}")
        print("Make sure ChromaDB is running and accessible")
        sys.exit(1)


def print_summary(memories: List[Dict[str, Any]]):
    """Print statistical summary of generated memories.
    
    Args:
        memories: List of memory documents
    """
    topics = {}
    importances = []
    timestamps = []
    
    for memory in memories:
        topic = memory["metadata"].get("topic", "unknown")
        topics[topic] = topics.get(topic, 0) + 1
        importances.append(memory["metadata"].get("importance", 0.5))
        timestamps.append(datetime.fromisoformat(memory["metadata"]["timestamp"]))
    
    print("\n📊 Memory Statistics:")
    print(f"  Total: {len(memories)}")
    print(f"  Topics: {len(topics)}")
    for topic, count in sorted(topics.items(), key=lambda x: -x[1]):
        print(f"    - {topic}: {count}")
    
    print(f"\n  Importance:")
    print(f"    - Mean: {sum(importances) / len(importances):.2f}")
    print(f"    - Min: {min(importances):.2f}")
    print(f"    - Max: {max(importances):.2f}")
    
    oldest = min(timestamps)
    newest = max(timestamps)
    span = (newest - oldest).days
    print(f"\n  Time span:")
    print(f"    - Oldest: {oldest.strftime('%Y-%m-%d')}")
    print(f"    - Newest: {newest.strftime('%Y-%m-%d')}")
    print(f"    - Span: {span} days")


def main():
    parser = argparse.ArgumentParser(
        description="Generate realistic test memory data for Ada"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of memories to generate (default: 100)"
    )
    parser.add_argument(
        "--days-range",
        type=int,
        default=90,
        help="Spread memories over this many days (default: 90)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/test_memories.json"),
        help="Output JSON file path (default: data/test_memories.json)"
    )
    parser.add_argument(
        "--load",
        action="store_true",
        help="Load memories directly into ChromaDB instead of saving to file"
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducible generation"
    )
    
    args = parser.parse_args()
    
    if args.seed is not None:
        random.seed(args.seed)
        print(f"🎲 Using random seed: {args.seed}")
    
    print(f"🧠 Generating {args.count} test memories...")
    memories = generate_memories(args.count, args.days_range)
    
    print_summary(memories)
    
    if args.load:
        print("\n📥 Loading into ChromaDB...")
        load_memories_to_chroma(memories)
    else:
        print(f"\n💾 Saving to {args.output}...")
        save_memories(memories, args.output)
        print("\n💡 To load into ChromaDB:")
        print(f"   python scripts/generate_test_memories.py --load")


if __name__ == "__main__":
    main()
