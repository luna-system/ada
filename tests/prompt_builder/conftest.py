"""Shared fixtures for prompt_builder tests."""
import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_rag_store():
    """Mock RAG store with standard test data.
    
    Provides consistent mock data across all prompt_builder tests.
    Can be overridden in individual tests by setting return_value.
    """
    store = Mock()
    
    # Memories
    store.retrieve_memories.return_value = [
        ("Memory 1 about Python", {"importance": 5, "scope": "global"}),
        ("Memory 2 about testing", {"importance": 3, "scope": "user"})
    ]
    
    # FAQs
    store.retrieve_faqs.return_value = [
        ("FAQ 1: How to test?", {"topic": "testing"}),
        ("FAQ 2: What is TDD?", {"topic": "methodology"})
    ]
    
    # Conversation turns
    store.retrieve_turns.return_value = [
        ("Hello", {"role": "user", "timestamp": "2025-12-17T00:00:00Z"}),
        ("Hi there!", {"role": "assistant", "timestamp": "2025-12-17T00:00:01Z"})
    ]
    
    # Summaries
    store.retrieve_summaries.return_value = [
        ("Summary of conversation", {"conversation_id": "conv123"})
    ]
    
    # Persona
    store.load_persona_block.return_value = (
        "I am Ada, a helpful AI assistant.",
        {"version": "1.0"}
    )
    
    return store


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    config = Mock()
    config.PERSONA_PATH = "/tmp/persona.md"
    config.SYSTEM_PROMPT = "You are a helpful assistant."
    config.PERSONA_MAX_CHARS = 5000
    return config


@pytest.fixture
def patched_context_retriever(mock_rag_store, mock_config):
    """ContextRetriever with patched dependencies.
    
    Returns a function that creates a retriever with mocked dependencies.
    Use this when you need to customize mock behavior per test.
    """
    def _create_retriever():
        with patch('brain.prompt_builder.context_retriever.rag_store', mock_rag_store):
            with patch('brain.prompt_builder.context_retriever.config', mock_config):
                from brain.prompt_builder.context_retriever import ContextRetriever
                return ContextRetriever()
    return _create_retriever
