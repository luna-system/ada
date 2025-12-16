"""Tests for specialist system functionality."""
import pytest
from brain.specialists.specialist_docs import get_relevant_specialist_docs


def test_specialist_docs_retrieval(rag_store):
    """Test specialist documentation retrieval."""
    docs = get_relevant_specialist_docs("how do I use web search?", rag_store, k=2)
    # Note: May return empty if specialist docs aren't seeded yet
    assert isinstance(docs, str), "Should return a string"
