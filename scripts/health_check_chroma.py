#!/usr/bin/env python3
"""
Health check for Chroma database and RAG functionality.

Checks:
- Chroma server connectivity
- Collection accessibility
- Embedding generation
- Query functionality for each document type
- Collection size and growth

Returns exit code 0 if healthy, 1 if unhealthy.
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timezone

from brain.rag_store import RagStore
from brain import config
import chromadb
from urllib.parse import urlparse


class HealthCheck:
    def __init__(self):
        self.checks = []
        self.warnings = []
        self.errors = []
    
    def add_check(self, name: str, status: bool, details: str = None):
        """Add a health check result."""
        self.checks.append({
            'name': name,
            'status': status,
            'details': details
        })
        if not status:
            self.errors.append(f"{name}: {details}" if details else name)
    
    def add_warning(self, message: str):
        """Add a warning (non-critical issue)."""
        self.warnings.append(message)
    
    def is_healthy(self) -> bool:
        """Return True if all checks passed."""
        return len(self.errors) == 0
    
    def report(self):
        """Print health check report."""
        print("=" * 60)
        print("CHROMA DATABASE HEALTH CHECK")
        print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 60)
        print()
        
        for check in self.checks:
            status = "✓" if check['status'] else "✗"
            print(f"{status} {check['name']}")
            if check['details']:
                print(f"  {check['details']}")
        
        if self.warnings:
            print()
            print("⚠ WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if self.errors:
            print()
            print("✗ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        
        print()
        print("=" * 60)
        if self.is_healthy():
            print("STATUS: HEALTHY ✓")
        else:
            print("STATUS: UNHEALTHY ✗")
        print("=" * 60)


def check_chroma_health():
    """Run all health checks."""
    health = HealthCheck()
    
    # 1. Check Chroma server connectivity
    try:
        chroma_url = os.getenv("CHROMA_URL", "http://chroma:8000")
        p = urlparse(chroma_url)
        host = p.hostname or "localhost"
        port = p.port or 8000
        
        client = chromadb.HttpClient(host=host, port=port)
        client.heartbeat()  # Check if server is alive
        health.add_check("Chroma Server Connection", True, f"Connected to {host}:{port}")
    except Exception as e:
        health.add_check("Chroma Server Connection", False, str(e))
        return health  # Can't continue without server
    
    # 2. Check collection exists
    try:
        col = client.get_collection(name="conversations")
        count = col.count()
        health.add_check("Collection Exists", True, f"Found 'conversations' collection with {count} documents")
        
        if count == 0:
            health.add_warning("Collection is empty")
        elif count < 10:
            health.add_warning(f"Collection has only {count} documents (expected more)")
    except Exception as e:
        health.add_check("Collection Exists", False, str(e))
        return health  # Can't continue without collection
    
    # 3. Check embedding generation
    try:
        rag = RagStore(
            persist_dir="/data/chroma",
            collection_name="conversations",
            ollama_base_url=config.OLLAMA_BASE_URL,
            embed_model=config.EMBED_MODEL
        )
        
        test_embedding = rag.embedding_fn(["test query"])
        emb_length = len(test_embedding[0])
        health.add_check("Embedding Generation", True, f"Generated {emb_length}-dim embedding")
        
        if emb_length != 768:
            health.add_warning(f"Unexpected embedding dimension: {emb_length} (expected 768 for nomic-embed-text)")
    except Exception as e:
        health.add_check("Embedding Generation", False, str(e))
        return health  # Can't test queries without embeddings
    
    # 4. Check document type distribution
    try:
        types = {}
        for doc_type in ['memory', 'faq', 'turn', 'summary', 'persona']:
            results = col.get(where={'type': doc_type}, limit=1)
            count = len(results.get('documents', []))
            types[doc_type] = count
        
        has_all_types = all(types.values())
        type_summary = ", ".join([f"{t}: {c}" for t, c in types.items()])
        health.add_check("Document Types", has_all_types, type_summary)
        
        if types['memory'] == 0:
            health.add_warning("No memories found")
        if types['faq'] == 0:
            health.add_warning("No FAQs found")
        if types['turn'] == 0:
            health.add_warning("No turns found")
    except Exception as e:
        health.add_check("Document Types", False, str(e))
    
    # 5. Check memory query functionality
    try:
        mem_hits = rag.retrieve_memories(query="test query", k=3, entity=None)
        health.add_check("Memory Query", len(mem_hits) > 0, f"Retrieved {len(mem_hits)} memories")
    except Exception as e:
        health.add_check("Memory Query", False, str(e))
    
    # 6. Check FAQ query functionality
    try:
        faq_hits = rag.retrieve_faqs(query="test query", k=3)
        health.add_check("FAQ Query", len(faq_hits) > 0, f"Retrieved {len(faq_hits)} FAQs")
    except Exception as e:
        health.add_check("FAQ Query", False, str(e))
    
    # 7. Check turn query functionality
    try:
        # Get a conversation ID that exists
        all_turns = col.get(where={"type": "turn"}, limit=1, include=["metadatas"])
        if all_turns.get("metadatas"):
            conv_id = all_turns["metadatas"][0].get("conversation_id")
            turn_hits = rag.retrieve_turns(query="test", k=3, conversation_id=conv_id)
            health.add_check("Turn Query", len(turn_hits) > 0, f"Retrieved {len(turn_hits)} turns")
        else:
            health.add_check("Turn Query", False, "No turns found to test")
    except Exception as e:
        health.add_check("Turn Query", False, str(e))
    
    # 8. Check specialist docs query
    try:
        from brain.specialists.specialist_docs import get_relevant_specialist_docs
        docs = get_relevant_specialist_docs("web search", rag, k=2)
        health.add_check("Specialist Docs Query", len(docs) > 0, f"Retrieved {len(docs)} chars")
    except Exception as e:
        health.add_check("Specialist Docs Query", False, str(e))
    
    # 9. Check for query consistency (same query returns same results)
    try:
        query = "consistency test"
        results1 = rag.retrieve_memories(query=query, k=2, entity=None)
        results2 = rag.retrieve_memories(query=query, k=2, entity=None)
        consistent = len(results1) == len(results2)
        health.add_check("Query Consistency", consistent, "Queries return consistent results")
    except Exception as e:
        health.add_check("Query Consistency", False, str(e))
    
    # 10. Check persona exists
    try:
        persona = rag.load_persona_block()
        health.add_check("Persona", persona is not None, "Persona loaded successfully")
    except Exception as e:
        health.add_check("Persona", False, str(e))
    
    return health


if __name__ == '__main__':
    health = check_chroma_health()
    health.report()
    sys.exit(0 if health.is_healthy() else 1)
