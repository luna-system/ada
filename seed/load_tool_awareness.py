#!/usr/bin/env python3
"""Load synthetic tool awareness memories into ChromaDB.

This seeds Ada's memory with examples of tool usage, teaching her
about her own capabilities through the Tier 2 (Instinctive/Memory) pathway.
"""
import json
import os
import sys
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from brain.rag_store import RagStore
from datetime import datetime, timezone


def load_synthetic_memories():
    """Load synthetic tool usage memories."""
    print("Loading synthetic tool usage memories...")
    
    # Create RagStore instance with Ollama URL from environment
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    print(f"Using Ollama at: {ollama_url}")
    store = RagStore(collection_name="conversations", ollama_base_url=ollama_url)
    
    memories_file = Path(__file__).parent / "tool_usage_memories.json"
    with open(memories_file) as f:
        data = json.load(f)
    
    count = 0
    for item in data["synthetic_memories"]:
        # Add to memories using upsert_memory
        store.upsert_memory(
            text=item["content"],
            scope=item["metadata"].get("scope", "system"),
            importance=int(item["metadata"].get("importance", 0.5) * 5),  # Convert 0-1 to 1-5
            tags=item["metadata"].get("tags", []),
            timestamp=item["metadata"].get("timestamp"),
            source="synthetic"
        )
        count += 1
        print(f"  ✓ Added: {item['content'][:60]}...")
    
    print(f"✅ Loaded {count} synthetic memories")


def load_tool_awareness_faqs():
    """Load tool awareness FAQs."""
    print("\nLoading tool awareness FAQs...")
    
    # Create RagStore instance for FAQs with Ollama URL from environment
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    store = RagStore(collection_name="conversations", ollama_base_url=ollama_url)
    
    faqs_file = Path(__file__).parent / "tool_awareness_faqs.json"
    with open(faqs_file) as f:
        data = json.load(f)
    
    count = 0
    for item in data["faqs"]:
        # FAQs are stored as documents with type="faq"
        content = f"Q: {item['question']}\nA: {item['answer']}"
        
        # Build extra metadata for the FAQ
        extra_meta = {
            "category": item["metadata"].get("category", "general"),
            "question": item["question"]
        }
        
        store.upsert_doc(
            text=content,
            type="faq",
            scope="global",
            importance=int(item["metadata"].get("importance", 0.5) * 5),
            tags=item["metadata"].get("tags", []),
            source="synthetic",
            extra_meta=extra_meta
        )
        count += 1
        print(f"  ✓ Added: {item['question']}")
    
    print(f"✅ Loaded {count} tool awareness FAQs")


def verify_loading():
    """Verify memories were loaded correctly."""
    print("\nVerifying memories...")
    
    # Create RagStore with Ollama URL from environment
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    store = RagStore(collection_name="conversations", ollama_base_url=ollama_url)
    
    # Test memory retrieval
    results = store.retrieve_memories(
        query="How do I look up code?",
        k=3
    )
    
    if results:
        print(f"✅ Memory retrieval working ({len(results)} results)")
        print(f"   Sample: {results[0][0][:80]}...")
    else:
        print("❌ No memories found!")
        return False
    
    # Test FAQ retrieval  
    results = store.retrieve_faqs(
        query="What tools do I have?",
        k=3
    )
    
    if results:
        print(f"✅ FAQ retrieval working ({len(results)} results)")
        print(f"   Sample: {results[0][0][:80]}...")
    else:
        print("❌ No FAQs found!")
        return False
    
    return True


if __name__ == "__main__":
    print("🧠 Loading Tool Awareness Synthetic Memories\n")
    print("=" * 60)
    
    try:
        load_synthetic_memories()
        load_tool_awareness_faqs()
        
        print("\n" + "=" * 60)
        if verify_loading():
            print("\n🎉 All synthetic memories loaded successfully!")
        else:
            print("\n❌ Verification failed")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
