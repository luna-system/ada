"""Tests for MCP tool handlers."""

import pytest
from unittest.mock import AsyncMock

from ada_mcp.tools import handle_tool_call, TOOLS
from ada_mcp.ada_client import AdaClient


@pytest.fixture
def mock_ada_client():
    """Mock Ada client."""
    client = AsyncMock(spec=AdaClient)
    return client


@pytest.mark.asyncio
async def test_ada_chat_tool(mock_ada_client):
    """Test ada_chat tool."""
    mock_ada_client.chat.return_value = {
        "response": "Hello! I'm Ada.",
        "conversation_id": "conv-123",
    }
    
    result = await handle_tool_call(
        "ada_chat",
        {"message": "Hello"},
        mock_ada_client,
    )
    
    assert len(result) == 1
    assert result[0].type == "text"
    assert "Hello! I'm Ada." in result[0].text
    
    mock_ada_client.chat.assert_called_once_with("Hello", None)


@pytest.mark.asyncio
async def test_ada_chat_with_conversation_id(mock_ada_client):
    """Test ada_chat with conversation ID."""
    mock_ada_client.chat.return_value = {
        "response": "Continuing our conversation.",
        "conversation_id": "conv-123",
    }
    
    result = await handle_tool_call(
        "ada_chat",
        {"message": "Continue", "conversation_id": "conv-123"},
        mock_ada_client,
    )
    
    assert len(result) == 1
    mock_ada_client.chat.assert_called_once_with("Continue", "conv-123")


@pytest.mark.asyncio
async def test_ada_search_memory_with_results(mock_ada_client):
    """Test ada_search_memory with results."""
    mock_ada_client.search_memories.return_value = [
        {"content": "Memory 1", "metadata": {"type": "note"}},
        {"content": "Memory 2", "metadata": {"type": "fact"}},
    ]
    
    result = await handle_tool_call(
        "ada_search_memory",
        {"query": "test"},
        mock_ada_client,
    )
    
    assert len(result) == 1
    assert "Found 2 memories" in result[0].text
    assert "Memory 1" in result[0].text
    assert "Memory 2" in result[0].text


@pytest.mark.asyncio
async def test_ada_search_memory_no_results(mock_ada_client):
    """Test ada_search_memory with no results."""
    mock_ada_client.search_memories.return_value = []
    
    result = await handle_tool_call(
        "ada_search_memory",
        {"query": "nonexistent"},
        mock_ada_client,
    )
    
    assert len(result) == 1
    assert "No matching memories found" in result[0].text


@pytest.mark.asyncio
async def test_ada_search_memory_with_filters(mock_ada_client):
    """Test ada_search_memory with scope and type filters."""
    mock_ada_client.search_memories.return_value = []
    
    await handle_tool_call(
        "ada_search_memory",
        {"query": "test", "scope": "project", "type": "note"},
        mock_ada_client,
    )
    
    mock_ada_client.search_memories.assert_called_once_with(
        "test",
        scope="project",
        type="note",
    )


@pytest.mark.asyncio
async def test_ada_add_memory(mock_ada_client):
    """Test ada_add_memory tool."""
    mock_ada_client.add_memory.return_value = {
        "id": "mem-123",
        "content": "Test memory",
    }
    
    result = await handle_tool_call(
        "ada_add_memory",
        {"content": "Test memory"},
        mock_ada_client,
    )
    
    assert len(result) == 1
    assert "mem-123" in result[0].text
    
    # Verify defaults
    mock_ada_client.add_memory.assert_called_once_with(
        "Test memory",
        type="note",
        importance=0.5,
        scope="user",
    )


@pytest.mark.asyncio
async def test_ada_add_memory_with_options(mock_ada_client):
    """Test ada_add_memory with custom options."""
    mock_ada_client.add_memory.return_value = {"id": "mem-456"}
    
    await handle_tool_call(
        "ada_add_memory",
        {
            "content": "Important fact",
            "type": "fact",
            "importance": 0.9,
            "scope": "project",
        },
        mock_ada_client,
    )
    
    mock_ada_client.add_memory.assert_called_once_with(
        "Important fact",
        type="fact",
        importance=0.9,
        scope="project",
    )


@pytest.mark.asyncio
async def test_ada_health_healthy(mock_ada_client):
    """Test ada_health when system is healthy."""
    mock_ada_client.health.return_value = {
        "ok": True,
        "service": "brain",
        "python": "3.13.0",
        "persona": {"loaded": True},
        "chroma": {"ok": True},
    }
    
    result = await handle_tool_call("ada_health", {}, mock_ada_client)
    
    assert len(result) == 1
    assert "✓ Ada Brain is healthy" in result[0].text
    assert "Python: 3.13.0" in result[0].text
    assert "Persona loaded: True" in result[0].text
    assert "ChromaDB: ✓" in result[0].text


@pytest.mark.asyncio
async def test_ada_health_unhealthy(mock_ada_client):
    """Test ada_health when system is unhealthy."""
    mock_ada_client.health.return_value = {
        "ok": False,
        "service": "brain",
    }
    
    result = await handle_tool_call("ada_health", {}, mock_ada_client)
    
    assert len(result) == 1
    assert "✗ Ada Brain is not healthy" in result[0].text


@pytest.mark.asyncio
async def test_unknown_tool(mock_ada_client):
    """Test handling of unknown tool."""
    result = await handle_tool_call(
        "unknown_tool",
        {},
        mock_ada_client,
    )
    
    assert len(result) == 1
    assert "Unknown tool" in result[0].text


def test_tool_definitions():
    """Test that all tools are properly defined."""
    assert len(TOOLS) == 4
    
    tool_names = [tool.name for tool in TOOLS]
    assert "ada_chat" in tool_names
    assert "ada_search_memory" in tool_names
    assert "ada_add_memory" in tool_names
    assert "ada_health" in tool_names
    
    # Verify each tool has required schema
    for tool in TOOLS:
        assert tool.name
        assert tool.description
        assert tool.inputSchema
        assert tool.inputSchema["type"] == "object"
        assert "properties" in tool.inputSchema
