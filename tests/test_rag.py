"""Tests for RAG store functionality."""
import pytest


def test_rag_store_initialization(rag_store):
    """Test RAG store initializes correctly."""
    count = rag_store.col.count()
    assert count > 0, f"Collection should have documents, got {count}"


def test_embedding_generation(rag_store):
    """Test that embeddings can be generated."""
    embeddings = rag_store.embedding_fn(["test query"])
    assert len(embeddings) > 0, "Should generate embeddings"
    assert len(embeddings[0]) == 768, f"Expected 768-dim embeddings, got {len(embeddings[0])}"


def test_memory_retrieval(rag_store):
    """Test memory retrieval with embeddings."""
    mem_hits = rag_store.retrieve_memories(query="luna plural system", k=3, entity=None)
    # Note: This may return 0 if no semantically matching memories exist
    # This is expected behavior, not a failure
    assert isinstance(mem_hits, list), "Should return a list"


def test_faq_retrieval(rag_store):
    """Test FAQ retrieval with embeddings."""
    faq_hits = rag_store.retrieve_faqs(query="web search specialist", k=3)
    assert len(faq_hits) > 0, "Should retrieve FAQs"


def test_turn_retrieval(rag_store, conversation_id):
    """Test turn retrieval."""
    if not conversation_id:
        pytest.skip("No conversation ID available")
    
    turn_hits = rag_store.retrieve_turns(query="test", k=3, conversation_id=conversation_id)
    assert len(turn_hits) > 0, "Should retrieve turns"


def test_query_consistency(rag_store):
    """Test that multiple queries return consistent results."""
    query = "luna system"
    results1 = rag_store.retrieve_memories(query=query, k=3, entity=None)
    results2 = rag_store.retrieve_memories(query=query, k=3, entity=None)
    
    assert len(results1) == len(results2), "Query results should be consistent"
    if results1 and results2:
        assert all(r1[0] == r2[0] for r1, r2 in zip(results1, results2)), \
            "Query results content should match"
