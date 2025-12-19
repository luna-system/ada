"""HTTP client for Ada's brain API - shared implementation.

This module provides the core AdaClient class used by all Python adapters.
It handles both streaming and non-streaming interactions with Ada's brain.
"""

import json
import logging
from typing import AsyncIterator

import httpx

from .exceptions import AdaBrainConnectionError, AdaBrainResponseError

logger = logging.getLogger(__name__)


class AdaClient:
    """Async HTTP client for Ada's brain REST API.
    
    This client provides a clean interface for interacting with Ada's brain,
    supporting both streaming (real-time) and non-streaming (complete response)
    modes.
    
    The client can be used as an async context manager for automatic cleanup:
        >>> async with AdaClient() as client:
        ...     response = await client.chat("Hello!")
    
    Or manually managed:
        >>> client = AdaClient()
        >>> response = await client.chat("Hello!")
        >>> await client.close()
    
    Attributes:
        base_url: Base URL for Ada's brain API
        timeout: Request timeout in seconds
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: float = 120.0
    ):
        """Initialize Ada client.
        
        Args:
            base_url: Base URL for Ada's brain API (default: http://localhost:8000)
            timeout: Request timeout in seconds (default: 120.0)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None
    
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
        conversation_id: str = "default",
        include_thinking: bool = False,
        model: str | None = None
    ) -> AsyncIterator[str]:
        """Stream chat response chunks from Ada's brain.
        
        This method yields response chunks as they arrive via Server-Sent Events,
        allowing for real-time display of Ada's thinking and response.
        
        Args:
            message: User's message/prompt
            conversation_id: Unique conversation identifier for context
            include_thinking: Whether to include <think> tags in output
            model: Optional model override (e.g., 'qwen2.5-coder:7b' for code completion)
            
        Yields:
            Response text chunks as they arrive
            
        Raises:
            AdaBrainConnectionError: If unable to connect to brain
            AdaBrainResponseError: If brain returns an error response
            
        Example:
            >>> async for chunk in client.chat_stream("What's 2+2?"):
            ...     print(chunk, end="", flush=True)
        """
        url = f"{self.base_url}/v1/chat/stream"
        payload = {
            "prompt": message,
            "conversation_id": conversation_id,
            "stream": True
        }
        
        # Add model override if specified
        if model:
            payload["model"] = model
        
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
                        f"Brain returned {response.status_code}: {error_text.decode()}",
                        status_code=response.status_code
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
                                    # Skip thinking chunks
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
        conversation_id: str = "default",
        include_thinking: bool = False,
        model: str | None = None
    ) -> str:
        """Get complete chat response from Ada's brain (non-streaming).
        
        This method collects all response chunks and returns the complete text.
        Useful for adapters that can't display incremental updates (like Matrix).
        
        Args:
            message: User's message/prompt
            conversation_id: Unique conversation identifier for context
            include_thinking: Whether to include <think> tags in output
            model: Optional model override (e.g., 'qwen2.5-coder:7b' for code completion)
            
        Returns:
            Complete response text
            
        Raises:
            AdaBrainConnectionError: If unable to connect to brain
            AdaBrainResponseError: If brain returns an error response
            
        Example:
            >>> response = await client.chat("Explain quantum computing")
            >>> print(response)
        """
        chunks = []
        async for chunk in self.chat_stream(message, conversation_id, include_thinking, model):
            chunks.append(chunk)
        return "".join(chunks)
    
    async def search_memories(
        self,
        query: str,
        limit: int = 5,
        scope: str = "user"
    ) -> list[dict]:
        """Search Ada's memory store.
        
        Args:
            query: Search query text
            limit: Maximum number of results
            scope: Memory scope to search (user, conversation, etc.)
            
        Returns:
            List of memory documents matching the query
            
        Raises:
            AdaBrainConnectionError: If unable to connect to brain
            AdaBrainResponseError: If brain returns an error
        """
        url = f"{self.base_url}/v1/memory/search"
        payload = {
            "query": query,
            "limit": limit,
            "scope": scope
        }
        
        client = self._get_client()
        
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError as e:
            raise AdaBrainConnectionError(
                f"Unable to connect to Ada's brain: {e}"
            ) from e
        except httpx.HTTPStatusError as e:
            raise AdaBrainResponseError(
                f"Memory search failed: {e}",
                status_code=e.response.status_code
            ) from e
        except httpx.HTTPError as e:
            raise AdaBrainConnectionError(
                f"HTTP error during memory search: {e}"
            ) from e
    
    async def add_memory(
        self,
        content: str,
        importance: float = 0.5,
        scope: str = "user",
        memory_type: str = "note"
    ) -> dict:
        """Add a memory to Ada's store.
        
        Args:
            content: Memory content text
            importance: Importance score (0.0-1.0)
            scope: Memory scope (user, conversation, etc.)
            memory_type: Type of memory (note, fact, preference, etc.)
            
        Returns:
            Created memory document
            
        Raises:
            AdaBrainConnectionError: If unable to connect to brain
            AdaBrainResponseError: If brain returns an error
        """
        url = f"{self.base_url}/v1/memory"
        payload = {
            "content": content,
            "metadata": {
                "type": memory_type,
                "importance": importance,
                "scope": scope
            }
        }
        
        client = self._get_client()
        
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError as e:
            raise AdaBrainConnectionError(
                f"Unable to connect to Ada's brain: {e}"
            ) from e
        except httpx.HTTPStatusError as e:
            raise AdaBrainResponseError(
                f"Memory creation failed: {e}",
                status_code=e.response.status_code
            ) from e
        except httpx.HTTPError as e:
            raise AdaBrainConnectionError(
                f"HTTP error during memory creation: {e}"
            ) from e
    
    async def health(self) -> dict:
        """Check Ada's brain health status.
        
        Returns:
            Health status dictionary with service statuses:
            - brain: Brain service status
            - ollama: LLM service status  
            - chroma: Vector database status
            
        Raises:
            AdaBrainConnectionError: If unable to connect to brain
            
        Example:
            >>> health = await client.health()
            >>> if health["brain"]["status"] == "healthy":
            ...     print("Ada is ready!")
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
        """Close the HTTP client and cleanup resources.
        
        This should be called when you're done using the client to
        properly close connections and free resources.
        """
        if self._client is not None:
            await self._client.aclose()
            self._client = None
