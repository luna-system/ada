"""Simplified Ada client for MCP server - async HTTP client for Ada's brain."""

import json
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class AdaBrainError(Exception):
    """Base exception for Ada brain errors."""
    pass


class AdaBrainConnectionError(AdaBrainError):
    """Exception for connection errors to Ada's brain."""
    pass


class AdaBrainResponseError(AdaBrainError):
    """Exception for error responses from Ada's brain."""
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class AdaClient:
    """Async HTTP client for Ada's brain REST API.
    
    Simplified version for MCP server - handles non-streaming requests only.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 120.0):
        """Initialize Ada client.
        
        Args:
            base_url: Base URL for Ada's brain API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
    
    async def chat(self, message: str, conversation_id: str | None = None) -> str:
        """Send a chat message to Ada and get the complete response.
        
        Args:
            message: User's message
            conversation_id: Optional conversation ID for context
            
        Returns:
            Ada's complete response text
            
        Raises:
            AdaBrainConnectionError: If unable to connect
            AdaBrainResponseError: If brain returns an error
        """
        url = f"{self.base_url}/v1/chat/stream"
        payload = {
            "prompt": message,
            "conversation_id": conversation_id or "default",
            "stream": True
        }
        
        try:
            # Use streaming endpoint but collect all chunks
            response_text = ""
            async with self._client.stream(
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
                        chunk = line[6:]
                        
                        if chunk == "[DONE]":
                            break
                        
                        if chunk:
                            try:
                                data = json.loads(chunk)
                                content = data.get("content", "")
                                
                                # Filter out thinking tags
                                if "<think>" not in content and "</think>" not in content:
                                    response_text += content
                            except json.JSONDecodeError:
                                response_text += chunk
            
            return response_text
            
        except httpx.ConnectError as e:
            raise AdaBrainConnectionError(
                f"Unable to connect to Ada's brain at {self.base_url}: {e}"
            ) from e
        except httpx.HTTPError as e:
            raise AdaBrainConnectionError(
                f"HTTP error communicating with Ada's brain: {e}"
            ) from e
    
    async def search_memories(
        self,
        query: str,
        scope: str | None = None,
        type: str | None = None
    ) -> list[dict[str, Any]]:
        """Search Ada's memory store.
        
        Args:
            query: Search query
            scope: Optional scope filter
            type: Optional type filter
            
        Returns:
            List of matching memory documents
        """
        url = f"{self.base_url}/v1/memories/search"
        params = {"q": query}
        if scope:
            params["scope"] = scope
        if type:
            params["type"] = type
        
        try:
            response = await self._client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("memories", [])
        except httpx.ConnectError as e:
            raise AdaBrainConnectionError(
                f"Unable to connect to Ada's brain at {self.base_url}: {e}"
            ) from e
        except httpx.HTTPError as e:
            raise AdaBrainConnectionError(
                f"HTTP error communicating with Ada's brain: {e}"
            ) from e
    
    async def add_memory(
        self,
        content: str,
        type: str = "note",
        importance: float = 0.5,
        scope: str = "user"
    ) -> dict[str, Any]:
        """Add a memory to Ada's store.
        
        Args:
            content: Memory content
            type: Memory type
            importance: Importance score (0.0-1.0)
            scope: Memory scope
            
        Returns:
            Created memory document
        """
        url = f"{self.base_url}/v1/memories"
        payload = {
            "content": content,
            "type": type,
            "importance": importance,
            "scope": scope
        }
        
        try:
            response = await self._client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError as e:
            raise AdaBrainConnectionError(
                f"Unable to connect to Ada's brain at {self.base_url}: {e}"
            ) from e
        except httpx.HTTPError as e:
            raise AdaBrainConnectionError(
                f"HTTP error communicating with Ada's brain: {e}"
            ) from e
    
    async def health(self) -> dict[str, Any]:
        """Check Ada brain health status.
        
        Returns:
            Health check response
        """
        url = f"{self.base_url}/v1/healthz"
        
        try:
            response = await self._client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError as e:
            raise AdaBrainConnectionError(
                f"Unable to connect to Ada's brain at {self.base_url}: {e}"
            ) from e
        except httpx.HTTPError as e:
            raise AdaBrainConnectionError(
                f"HTTP error communicating with Ada's brain: {e}"
            ) from e
