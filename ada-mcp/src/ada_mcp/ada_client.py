"""HTTP client for Ada's brain API - reference implementation.

This module provides a clean, async HTTP client for interacting with
Ada's brain. It will serve as the foundation for the shared ada-client
library in Phase 2.

Key patterns demonstrated:
- Async/await with httpx
- SSE (Server-Sent Events) stream parsing
- Error handling and retries
- Both streaming and complete response modes
"""

import json
import logging
from typing import AsyncIterator, Optional

import httpx

logger = logging.getLogger(__name__)


class AdaBrainError(Exception):
    """Base exception for Ada brain client errors."""
    pass


class AdaBrainConnectionError(AdaBrainError):
    """Raised when unable to connect to Ada's brain."""
    pass


class AdaBrainResponseError(AdaBrainError):
    """Raised when Ada's brain returns an error response."""
    pass


class AdaClient:
    """Async HTTP client for Ada's brain API.
    
    This client handles both streaming and non-streaming interactions
    with Ada's brain, using the standard REST API endpoints.
    
    Example:
        >>> async with AdaClient() as client:
        ...     response = await client.chat("Hello!")
        ...     print(response)
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:7000",
        timeout: float = 120.0
    ):
        """Initialize Ada client.
        
        Args:
            base_url: Base URL for Ada's brain API (default: http://localhost:7000)
            timeout: Request timeout in seconds (default: 120.0)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client
    
    async def chat_stream(
        self,
        message: str,
        conversation_id: str = "cli-default",
        include_thinking: bool = False
    ) -> AsyncIterator[str]:
        """Stream chat response chunks from Ada's brain.
        
        This method yields response chunks as they arrive, allowing for
        real-time display of Ada's thinking and response.
        
        Args:
            message: User's message/prompt
            conversation_id: Unique conversation identifier for context
            include_thinking: Whether to include <think> tags in output
            
        Yields:
            Response text chunks as they arrive
            
        Raises:
            AdaBrainConnectionError: If unable to connect to brain
            AdaBrainResponseError: If brain returns an error
        """
        url = f"{self.base_url}/v1/chat/stream"
        payload = {
            "prompt": message,
            "conversation_id": conversation_id,
            "stream": True
        }
        
        client = self._get_client()
        
        try:
            async with client.stream(
                "POST",
                url,
                json=payload,
                headers={"Accept": "text/event-stream"}
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise AdaBrainResponseError(
                        f"Brain returned {response.status_code}: {error_text.decode()}"
                    )
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        chunk = line[6:]  # Remove "data: " prefix
                        
                        if chunk == "[DONE]":
                            break
                        
                        if chunk:
                            # Parse JSON chunk
                            try:
                                data = json.loads(chunk)
                                content = data.get("content", "")
                                
                                # Filter thinking tags if requested
                                if not include_thinking and "<think>" in content:
                                    # Simple filtering - just skip thinking chunks
                                    continue
                                
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                # If not JSON, yield raw chunk
                                yield chunk
        
        except httpx.ConnectError as e:
            raise AdaBrainConnectionError(
                f"Unable to connect to Ada's brain at {self.base_url}: {e}"
            ) from e
        except httpx.HTTPError as e:
            raise AdaBrainConnectionError(
                f"HTTP error communicating with Ada's brain: {e}"
            ) from e
    
    async def chat(
        self,
        message: str,
        conversation_id: str = "cli-default",
        include_thinking: bool = False
    ) -> str:
        """Get complete chat response from Ada's brain (non-streaming).
        
        This method collects all chunks and returns the complete response,
        similar to how the Matrix bridge works.
        
        Args:
            message: User's message/prompt
            conversation_id: Unique conversation identifier for context
            include_thinking: Whether to include <think> tags in output
            
        Returns:
            Complete response text
            
        Raises:
            AdaBrainConnectionError: If unable to connect to brain
            AdaBrainResponseError: If brain returns an error
        """
        chunks = []
        async for chunk in self.chat_stream(message, conversation_id, include_thinking):
            chunks.append(chunk)
        return "".join(chunks)
    
    async def health(self) -> dict:
        """Check Ada's brain health status.
        
        Returns:
            Health status dictionary with service statuses
            
        Raises:
            AdaBrainConnectionError: If unable to connect to brain
        """
        url = f"{self.base_url}/v1/healthz"
        client = self._get_client()
        
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise AdaBrainConnectionError(
                f"Unable to check health: {e}"
            ) from e
    
    async def close(self):
        """Close the HTTP client and cleanup resources."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
    
    async def search_memories(
        self,
        query: str,
        scope: Optional[str] = None,
        type: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict]:
        """Search Ada's long-term memory.
        
        Args:
            query: Search query
            scope: Optional scope filter
            type: Optional type filter
            limit: Maximum number of results
            
        Returns:
            List of matching memories
        """
        params = {"query": query, "limit": limit}
        if scope:
            params["scope"] = scope
        if type:
            params["type"] = type
        
        client = self._get_client()
        response = await client.get(f"{self.base_url}/v1/memory", params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("memories", [])
    
    async def add_memory(
        self,
        content: str,
        type: str = "note",
        importance: float = 0.5,
        scope: str = "user",
    ) -> dict:
        """Add a memory to Ada's long-term store.
        
        Args:
            content: Memory content
            type: Memory type (default: "note")
            importance: Importance score 0.0-1.0 (default: 0.5)
            scope: Memory scope (default: "user")
            
        Returns:
            Created memory with ID
        """
        payload = {
            "content": content,
            "type": type,
            "importance": importance,
            "scope": scope,
        }
        
        client = self._get_client()
        response = await client.post(f"{self.base_url}/v1/memory", json=payload)
        response.raise_for_status()
        return response.json()
