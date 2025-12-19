"""Tests for ContextRetriever component.

Tests the context retrieval logic separated from prompt building.
"""
import pytest
from unittest.mock import Mock, patch
from brain.prompt_builder.context_retriever import ContextRetriever


class TestContextRetriever:
    """Test suite for ContextRetriever."""

    @pytest.fixture
    def mock_rag_store(self):
        """Mock RAG store for testing."""
        store = Mock()
        store.retrieve_memories.return_value = [
            ("Memory 1 about Python", {"importance": 5}),
            ("Memory 2 about testing", {"importance": 3})
        ]
        store.retrieve_faqs.return_value = [
            ("FAQ 1: How to test?", {"topic": "testing"}),
            ("FAQ 2: What is TDD?", {"topic": "methodology"})
        ]
        store.retrieve_turns.return_value = [
            ("Hello", {"role": "user", "timestamp": "2025-12-17T00:00:00Z"}),
            ("Hi there!", {"role": "assistant", "timestamp": "2025-12-17T00:00:01Z"})
        ]
        store.retrieve_summaries.return_value = [
            ("Summary of conversation", {"conversation_id": "conv123"})
        ]
        store.load_persona_block.return_value = ("I am Ada, a helpful AI assistant.", {"version": "1.0"})
        return store

    @pytest.fixture
    def mock_config(self):
        """Mock config for testing."""
        config = Mock()
        config.PERSONA_PATH = "/tmp/persona.md"
        config.MEMORY_DECAY_ENABLED = False
        config.GRAPHRAG_ENABLED = False
        return config

    @pytest.fixture
    def retriever(self, mock_rag_store, mock_config):
        """Create ContextRetriever with mocks passed via constructor."""
        return ContextRetriever(
            rag_store_instance=mock_rag_store,
            config_instance=mock_config
        )

    def test_initialization(self, retriever):
        """Test that ContextRetriever initializes correctly."""
        assert retriever is not None
        assert hasattr(retriever, 'get_persona')
        assert hasattr(retriever, 'get_memories')
        assert hasattr(retriever, 'get_faqs')
        assert hasattr(retriever, 'get_turns')
        assert hasattr(retriever, 'get_summaries')

    def test_get_persona_success(self, retriever, mock_rag_store):
        """Test retrieving persona from RAG store."""
        result = retriever.get_persona()
        
        assert result is not None
        text, metadata = result
        assert text == "I am Ada, a helpful AI assistant."
        assert metadata["version"] == "1.0"
        mock_rag_store.load_persona_block.assert_called_once()

    def test_get_persona_not_found(self, retriever, mock_rag_store):
        """Test graceful handling when persona doesn't exist."""
        mock_rag_store.load_persona_block.return_value = None
        
        result = retriever.get_persona()
        
        assert result is None

    def test_get_memories(self, retriever, mock_rag_store):
        """Test retrieving memories from RAG store."""
        memories = retriever.get_memories(query="Python testing", k=5)
        
        assert len(memories) == 2
        text1, meta1 = memories[0]
        assert text1 == "Memory 1 about Python"
        assert meta1["importance"] == 5
        mock_rag_store.retrieve_memories.assert_called_once_with(
            query="Python testing",
            k=5,
            entity=None
        )

    def test_get_memories_with_entity(self, retriever, mock_rag_store):
        """Test retrieving memories with entity filter."""
        memories = retriever.get_memories(query="Python testing", k=5, entity="project-x")
        
        mock_rag_store.retrieve_memories.assert_called_once_with(
            query="Python testing",
            k=5,
            entity="project-x"
        )

    def test_get_memories_empty_result(self, retriever, mock_rag_store):
        """Test handling empty memories result."""
        mock_rag_store.retrieve_memories.return_value = []
        
        memories = retriever.get_memories(query="nonexistent", k=5)
        
        assert memories == []

    def test_get_faqs(self, retriever, mock_rag_store):
        """Test retrieving FAQs from RAG store."""
        faqs = retriever.get_faqs(query="testing", k=3)
        
        assert len(faqs) == 2
        text1, meta1 = faqs[0]
        assert text1 == "FAQ 1: How to test?"
        assert meta1["topic"] == "testing"
        mock_rag_store.retrieve_faqs.assert_called_once_with(
            query="testing",
            k=3
        )

    def test_get_turns(self, retriever, mock_rag_store):
        """Test retrieving conversation turns."""
        turns = retriever.get_turns(query="test", k=5, conversation_id="conv123")
        
        assert len(turns) == 2
        text1, meta1 = turns[0]
        assert text1 == "Hello"
        assert meta1["role"] == "user"
        mock_rag_store.retrieve_turns.assert_called_once_with(
            query="test",
            k=5,
            conversation_id="conv123"
        )

    def test_get_turns_no_conversation_id(self, retriever, mock_rag_store):
        """Test handling when no conversation_id provided."""
        turns = retriever.get_turns(query="test", k=5, conversation_id=None)
        
        assert turns == []
        mock_rag_store.retrieve_turns.assert_not_called()
    
    def test_get_summaries(self, retriever, mock_rag_store):
        """Test retrieving conversation summaries."""
        summaries = retriever.get_summaries(conversation_id="conv123", k=3)
        
        assert len(summaries) == 1
        text, meta = summaries[0]
        assert text == "Summary of conversation"
        mock_rag_store.retrieve_summaries.assert_called_once_with(
            conversation_id="conv123",
            k=3
        )
