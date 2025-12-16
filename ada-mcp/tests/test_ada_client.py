"""Tests for Ada HTTP client."""

import pytest
import httpx
from unittest.mock import AsyncMock, patch

from ada_mcp.ada_client import AdaClient


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.AsyncClient."""
    with patch("ada_mcp.ada_client.httpx.AsyncClient") as mock:
        yield mock


@pytest.mark.asyncio
async def test_health_check_success():
    """Test successful health check."""
    client = AdaClient("http://test:8000")
    
    # Mock the response
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={
        "ok": True,
        "service": "brain",
        "python": "3.13.0",
    })
    mock_response.raise_for_status = lambda: None
    
    client.client.get = AsyncMock(return_value=mock_response)
    
    result = await client.health()
    
    assert result["ok"] is True
    assert result["service"] == "brain"
    client.client.get.assert_called_once_with("http://test:8000/health")
    
    await client.close()


@pytest.mark.asyncio
async def test_chat_non_streaming():
    """Test non-streaming chat."""
    client = AdaClient("http://test:8000")
    
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={
        "response": "Hello! How can I help?",
        "conversation_id": "test-123",
    })
    mock_response.raise_for_status = lambda: None
    
    client.client.post = AsyncMock(return_value=mock_response)
    
    result = await client.chat("Hello", conversation_id="test-123")
    
    assert result["response"] == "Hello! How can I help?"
    assert result["conversation_id"] == "test-123"
    
    # Verify the call
    call_args = client.client.post.call_args
    assert call_args[0][0] == "http://test:8000/chat"
    assert call_args[1]["json"]["input"] == "Hello"
    assert call_args[1]["json"]["conversation_id"] == "test-123"
    
    await client.close()


@pytest.mark.asyncio
async def test_chat_streaming():
    """Test streaming chat."""
    client = AdaClient("http://test:8000")
    
    mock_response = AsyncMock()
    mock_response.raise_for_status = lambda: None
    
    client.client.post = AsyncMock(return_value=mock_response)
    
    result = await client.chat("Hello", stream=True)
    
    assert result == mock_response
    
    # Verify streaming endpoint was used
    call_args = client.client.post.call_args
    assert call_args[0][0] == "http://test:8000/chat/stream"
    assert call_args[1]["headers"]["Accept"] == "text/event-stream"
    
    await client.close()


@pytest.mark.asyncio
async def test_search_memories():
    """Test memory search."""
    client = AdaClient("http://test:8000")
    
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={
        "memories": [
            {"id": "mem-1", "content": "Test memory 1"},
            {"id": "mem-2", "content": "Test memory 2"},
        ]
    })
    mock_response.raise_for_status = lambda: None
    
    client.client.get = AsyncMock(return_value=mock_response)
    
    result = await client.search_memories("test query", scope="user", type="note")
    
    assert len(result) == 2
    assert result[0]["content"] == "Test memory 1"
    
    # Verify params
    call_args = client.client.get.call_args
    assert call_args[1]["params"]["query"] == "test query"
    assert call_args[1]["params"]["scope"] == "user"
    assert call_args[1]["params"]["type"] == "note"
    
    await client.close()


@pytest.mark.asyncio
async def test_add_memory():
    """Test adding a memory."""
    client = AdaClient("http://test:8000")
    
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={
        "id": "mem-123",
        "content": "Test memory",
        "type": "note",
        "importance": 0.7,
    })
    mock_response.raise_for_status = lambda: None
    
    client.client.post = AsyncMock(return_value=mock_response)
    
    result = await client.add_memory(
        "Test memory",
        type="note",
        importance=0.7,
        scope="user",
    )
    
    assert result["id"] == "mem-123"
    assert result["content"] == "Test memory"
    
    # Verify payload
    call_args = client.client.post.call_args
    payload = call_args[1]["json"]
    assert payload["content"] == "Test memory"
    assert payload["type"] == "note"
    assert payload["importance"] == 0.7
    assert payload["scope"] == "user"
    
    await client.close()


@pytest.mark.asyncio
async def test_base_url_stripping():
    """Test that trailing slashes are stripped from base URL."""
    client = AdaClient("http://test:8000/")
    assert client.base_url == "http://test:8000"
    
    client2 = AdaClient("http://test:8000")
    assert client2.base_url == "http://test:8000"
    
    await client.close()
    await client2.close()


@pytest.mark.asyncio
async def test_http_error_handling():
    """Test that HTTP errors are raised."""
    client = AdaClient("http://test:8000")
    
    # Create a proper mock that raises on raise_for_status()
    mock_response = AsyncMock()
    
    def raise_error():
        raise httpx.HTTPStatusError(
            "500 Server Error",
            request=AsyncMock(),
            response=AsyncMock(),
        )
    
    mock_response.raise_for_status = raise_error
    
    client.client.get = AsyncMock(return_value=mock_response)
    
    with pytest.raises(httpx.HTTPStatusError):
        await client.health()
    
    await client.close()
