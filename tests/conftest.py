"""Pytest configuration and shared fixtures."""
import pytest
from brain.rag_store import RagStore
from brain import config


@pytest.fixture(scope="session")
def rag_store():
    """Shared RagStore instance for all tests."""
    return RagStore(
        persist_dir="/data/chroma",
        collection_name="conversations",
        ollama_base_url=config.OLLAMA_BASE_URL,
        embed_model=config.EMBED_MODEL
    )


@pytest.fixture(scope="session")
def conversation_id(rag_store):
    """Get a valid conversation ID from the database."""
    all_turns = rag_store.col.get(where={"type": "turn"}, limit=1, include=["metadatas"])
    if all_turns.get("metadatas"):
        return all_turns["metadatas"][0].get("conversation_id")
    return None
