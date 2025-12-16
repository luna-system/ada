"""Integration tests for Ada MCP Server.

These tests verify end-to-end behavior with a mock Ada Brain server.
"""

import pytest
import httpx
from unittest.mock import AsyncMock, patch
import json

from ada_mcp.ada_client import AdaClient
from ada_mcp.tools import handle_tool_call


class MockAdaBrain:
    """Mock Ada Brain HTTP server for testing."""
    
    def __init__(self):
        self.health_response = {
            "ok": True,
            "service": "brain",
            "python": "3.13.0",
            "persona": {"loaded": True},
            "chroma": {"ok": True},
        }
        self.chat_responses = []
        self.memories = []
    
    def add_chat_response(self, response: str, conversation_id: str = None):
        """Add a chat response to the queue."""
        self.chat_responses.append({
            "response": response,
            "conversation_id": conversation_id or "test-conv",
        })
    
    def add_memory(self, memory: dict):
        """Add a memory to the store."""
        self.memories.append(memory)


@pytest.fixture
async def mock_brain():
    """Fixture for mock Ada Brain."""
    brain = MockAdaBrain()
    
    # Set up default responses
    brain.add_chat_response("Hello! I'm Ada, your AI assistant.")
    brain.add_memory({
        "id": "mem-1",
        "content": "Ada is an AI framework for personal assistants",
        "type": "fact",
        "metadata": {"source": "system"},
    })
    
    return brain


@pytest.fixture
async def ada_client_with_mock(mock_brain):
    """Ada client with mocked HTTP responses."""
    client = AdaClient("http://mock:8000")
    
    # Mock health endpoint
    async def mock_get(url, **kwargs):
        response = AsyncMock()
        response.raise_for_status = lambda: None
        
        if "/health" in url:
            response.json = AsyncMock(return_value=mock_brain.health_response)
        elif "/memories/search" in url:
            query = kwargs.get("params", {}).get("query", "")
            # Simple search: match query in content
            matches = [
                m for m in mock_brain.memories
                if query.lower() in m["content"].lower()
            ]
            response.json = AsyncMock(return_value={"memories": matches})
        
        return response
    
    # Mock post endpoints
    async def mock_post(url, **kwargs):
        response = AsyncMock()
        response.raise_for_status = lambda: None
        
        if "/chat" in url:
            if mock_brain.chat_responses:
                response.json = AsyncMock(return_value=mock_brain.chat_responses.pop(0))
            else:
                response.json = AsyncMock(return_value={
                    "response": "Default response",
                    "conversation_id": "test-conv",
                })
        elif "/memories" in url:
            payload = kwargs.get("json", {})
            new_memory = {
                "id": f"mem-{len(mock_brain.memories) + 1}",
                **payload,
            }
            mock_brain.memories.append(new_memory)
            response.json = AsyncMock(return_value=new_memory)
        
        return response
    
    client.client.get = mock_get
    client.client.post = mock_post
    
    yield client
    
    await client.close()


@pytest.mark.asyncio
async def test_full_conversation_flow(ada_client_with_mock, mock_brain):
    """Test a full conversation flow."""
    # Clear default responses and add our own
    mock_brain.chat_responses.clear()
    
    # First message
    mock_brain.add_chat_response(
        "Hello! How can I help you today?",
        "conv-123",
    )
    
    result1 = await handle_tool_call(
        "ada_chat",
        {"message": "Hello Ada"},
        ada_client_with_mock,
    )
    
    assert "Hello! How can I help you today?" in result1[0].text
    
    # Follow-up message
    mock_brain.add_chat_response(
        "I can help you with coding, research, and more!",
        "conv-123",
    )
    
    result2 = await handle_tool_call(
        "ada_chat",
        {"message": "What can you do?", "conversation_id": "conv-123"},
        ada_client_with_mock,
    )
    
    assert "coding, research" in result2[0].text


@pytest.mark.asyncio
async def test_memory_workflow(ada_client_with_mock, mock_brain):
    """Test adding and searching memories."""
    # Add a memory
    add_result = await handle_tool_call(
        "ada_add_memory",
        {
            "content": "Python is the best language for MCP servers",
            "type": "opinion",
            "importance": 0.7,
        },
        ada_client_with_mock,
    )
    
    assert "mem-" in add_result[0].text
    
    # Search for it
    search_result = await handle_tool_call(
        "ada_search_memory",
        {"query": "Python"},
        ada_client_with_mock,
    )
    
    assert "Python is the best language" in search_result[0].text


@pytest.mark.asyncio
async def test_health_check_integration(ada_client_with_mock):
    """Test health check returns full system status."""
    result = await handle_tool_call(
        "ada_health",
        {},
        ada_client_with_mock,
    )
    
    text = result[0].text
    assert "✓ Ada Brain is healthy" in text
    assert "Python: 3.13.0" in text
    assert "Persona loaded: True" in text
    assert "ChromaDB: ✓" in text


@pytest.mark.asyncio
async def test_memory_search_with_no_matches(ada_client_with_mock):
    """Test memory search when nothing matches."""
    result = await handle_tool_call(
        "ada_search_memory",
        {"query": "nonexistent topic that definitely does not exist"},
        ada_client_with_mock,
    )
    
    assert "No matching memories found" in result[0].text


@pytest.mark.asyncio
async def test_multiple_memories_search(ada_client_with_mock, mock_brain):
    """Test searching returns multiple memories."""
    # Add several memories about AI
    for i in range(3):
        mock_brain.add_memory({
            "id": f"ai-mem-{i}",
            "content": f"AI fact number {i}: Machine learning is powerful",
            "type": "fact",
        })
    
    result = await handle_tool_call(
        "ada_search_memory",
        {"query": "AI"},
        ada_client_with_mock,
    )
    
    text = result[0].text
    assert "Found" in text
    assert "AI fact number" in text


@pytest.mark.asyncio
async def test_error_handling_unhealthy_brain(ada_client_with_mock, mock_brain):
    """Test handling when Ada Brain is unhealthy."""
    mock_brain.health_response = {
        "ok": False,
        "service": "brain",
        "error": "Database connection failed",
    }
    
    result = await handle_tool_call(
        "ada_health",
        {},
        ada_client_with_mock,
    )
    
    assert "✗ Ada Brain is not healthy" in result[0].text
