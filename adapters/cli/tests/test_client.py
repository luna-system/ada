"""Tests for Ada CLI client."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from ada_cli.client import AdaClient, AdaBrainConnectionError, AdaBrainResponseError


@pytest.mark.asyncio
async def test_client_initialization():
    """Test client can be initialized."""
    client = AdaClient(base_url="http://localhost:7000")
    assert client.base_url == "http://localhost:7000"
    assert client.timeout == 120.0


@pytest.mark.asyncio
async def test_client_context_manager():
    """Test client works as context manager."""
    async with AdaClient() as client:
        assert client._client is not None
    
    # Client should be closed after context exit
    assert client._client is None


@pytest.mark.asyncio
async def test_health_check_success(httpx_mock):
    """Test successful health check."""
    httpx_mock.add_response(
        method="GET",
        url="http://localhost:7000/v1/healthz",
        json={"status": "healthy", "services": {}}
    )
    
    async with AdaClient() as client:
        health = await client.health()
        assert health["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_check_connection_error(httpx_mock):
    """Test health check with connection error."""
    httpx_mock.add_exception(Exception("Connection refused"))
    
    async with AdaClient() as client:
        with pytest.raises(AdaBrainConnectionError):
            await client.health()


@pytest.mark.asyncio
async def test_chat_stream(httpx_mock):
    """Test streaming chat."""
    # Mock SSE response
    sse_data = "data: Hello\ndata: World\ndata: [DONE]\n"
    httpx_mock.add_response(
        method="POST",
        url="http://localhost:7000/v1/chat/stream",
        text=sse_data
    )
    
    async with AdaClient() as client:
        chunks = []
        async for chunk in client.chat_stream("test"):
            chunks.append(chunk)
        
        assert chunks == ["Hello", "World"]


@pytest.mark.asyncio
async def test_chat_complete(httpx_mock):
    """Test non-streaming chat."""
    sse_data = "data: Hello\ndata:  \ndata: World\ndata: [DONE]\n"
    httpx_mock.add_response(
        method="POST",
        url="http://localhost:7000/v1/chat/stream",
        text=sse_data
    )
    
    async with AdaClient() as client:
        response = await client.chat("test")
        assert response == "Hello World"
