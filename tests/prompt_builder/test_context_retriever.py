"""Tests for ContextRetriever component.

Demonstrates improved testing patterns:
- Parametrized tests to reduce duplication
- Shared fixtures from conftest.py
- Focused test methods
- Clear test organization
"""
import pytest
from unittest.mock import patch
from brain.prompt_builder.context_retriever import ContextRetriever


class TestContextRetrieverInitialization:
    """Test retriever initialization and basic structure."""

    def test_initialization(self, patched_context_retriever):
        """Test that ContextRetriever initializes correctly."""
        retriever = patched_context_retriever()
        
        assert retriever is not None
        assert hasattr(retriever, 'get_persona')
        assert hasattr(retriever, 'get_memories')
        assert hasattr(retriever, 'get_faqs')
        assert hasattr(retriever, 'get_turns')
        assert hasattr(retriever, 'get_summaries')


class TestPersonaRetrieval:
    """Test persona loading from RAG store."""

    def test_get_persona_success(self, patched_context_retriever, mock_rag_store):
        """Test retrieving persona from RAG store."""
        retriever = patched_context_retriever()
        result = retriever.get_persona()
        
        assert result is not None
        text, metadata = result
        assert text == "I am Ada, a helpful AI assistant."
        assert metadata["version"] == "1.0"
        mock_rag_store.load_persona_block.assert_called_once()

    def test_get_persona_not_found(self, patched_context_retriever, mock_rag_store):
        """Test graceful handling when persona doesn't exist."""
        mock_rag_store.load_persona_block.return_value = None
        
        retriever = patched_context_retriever()
        result = retriever.get_persona()
        
        assert result is None


class TestRAGRetrieval:
    """Test RAG data retrieval methods.
    
    Uses parametrization to test similar methods with different inputs.
    """

    @pytest.mark.parametrize("method_name,kwargs,expected_call,expected_len", [
        # Memories
        (
            "get_memories",
            {"query": "Python testing", "k": 5},
            {"query": "Python testing", "k": 5, "entity": None},
            2
        ),
        # Memories with entity
        (
            "get_memories",
            {"query": "Python testing", "k": 5, "entity": "project-x"},
            {"query": "Python testing", "k": 5, "entity": "project-x"},
            2
        ),
        # FAQs
        (
            "get_faqs",
            {"query": "testing", "k": 3},
            {"query": "testing", "k": 3},
            2
        ),
        # Turns
        (
            "get_turns",
            {"query": "test", "k": 5, "conversation_id": "conv123"},
            {"query": "test", "k": 5, "conversation_id": "conv123"},
            2
        ),
        # Summaries
        (
            "get_summaries",
            {"conversation_id": "conv123", "k": 3},
            {"conversation_id": "conv123", "k": 3},
            1
        ),
    ])
    def test_retrieval_methods(
        self,
        patched_context_retriever,
        mock_rag_store,
        method_name,
        kwargs,
        expected_call,
        expected_len
    ):
        """Test RAG retrieval methods with various parameters."""
        retriever = patched_context_retriever()
        
        # Call the method
        method = getattr(retriever, method_name)
        result = method(**kwargs)
        
        # Verify result length
        assert len(result) == expected_len
        
        # Verify correct RAG store method was called
        rag_method_name = method_name.replace("get_", "retrieve_")
        if method_name == "get_summaries":
            rag_method_name = "retrieve_summaries"
        
        rag_method = getattr(mock_rag_store, rag_method_name)
        rag_method.assert_called_once_with(**expected_call)

    def test_get_memories_returns_tuples(self, patched_context_retriever):
        """Test that memories return (text, metadata) tuples."""
        retriever = patched_context_retriever()
        memories = retriever.get_memories(query="test", k=5)
        
        assert len(memories) == 2
        text, metadata = memories[0]
        assert isinstance(text, str)
        assert isinstance(metadata, dict)
        assert text == "Memory 1 about Python"
        assert metadata["importance"] == 5

    def test_get_faqs_returns_tuples(self, patched_context_retriever):
        """Test that FAQs return (text, metadata) tuples."""
        retriever = patched_context_retriever()
        faqs = retriever.get_faqs(query="test", k=3)
        
        assert len(faqs) == 2
        text, metadata = faqs[0]
        assert isinstance(text, str)
        assert isinstance(metadata, dict)
        assert text == "FAQ 1: How to test?"
        assert metadata["topic"] == "testing"


class TestEmptyResults:
    """Test handling of empty/missing data."""

    @pytest.mark.parametrize("method_name,kwargs", [
        ("get_memories", {"query": "nonexistent", "k": 5}),
        ("get_faqs", {"query": "nonexistent", "k": 3}),
        ("get_turns", {"query": "test", "k": 5, "conversation_id": "conv123"}),
    ])
    def test_empty_results(
        self,
        patched_context_retriever,
        mock_rag_store,
        method_name,
        kwargs
    ):
        """Test graceful handling of empty results."""
        # Mock empty results
        rag_method_name = method_name.replace("get_", "retrieve_")
        rag_method = getattr(mock_rag_store, rag_method_name)
        rag_method.return_value = []
        
        retriever = patched_context_retriever()
        method = getattr(retriever, method_name)
        result = method(**kwargs)
        
        assert result == []

    def test_get_turns_no_conversation_id(
        self,
        patched_context_retriever,
        mock_rag_store
    ):
        """Test that turns returns empty list without conversation_id."""
        retriever = patched_context_retriever()
        turns = retriever.get_turns(query="test", k=5, conversation_id=None)
        
        assert turns == []
        mock_rag_store.retrieve_turns.assert_not_called()
