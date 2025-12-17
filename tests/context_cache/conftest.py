"""Shared fixtures for context cache tests."""
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock


@pytest.fixture
def mock_config():
    """Mock configuration with cache settings."""
    config = Mock()
    config.CACHE_PERSONA_TTL = 86400  # 24 hours
    config.CACHE_FAQ_TTL = 86400
    config.CACHE_MEMORY_TTL = 300  # 5 minutes
    config.CACHE_CONVERSATION_TTL = 3600  # 1 hour
    config.CACHE_MAX_ENTRIES = 1000
    config.CACHE_CLEANUP_INTERVAL = 300
    return config


@pytest.fixture
def mock_rag_store():
    """Mock RAG store that returns predictable data."""
    store = Mock()
    
    # Persona returns (text, metadata) tuple
    persona_text = "You are Ada, a helpful AI assistant.\nYou value privacy and run locally."
    store.load_persona_block = Mock(return_value=(persona_text, {"source": "persona.md"}))
    
    return store


@pytest.fixture
def sample_persona_text():
    """Sample persona text for testing."""
    return "You are Ada, a helpful AI assistant.\nYou value privacy and run locally."


@pytest.fixture
def current_time():
    """Fixed timestamp for testing."""
    return datetime(2025, 12, 17, 12, 0, 0, tzinfo=timezone.utc)
