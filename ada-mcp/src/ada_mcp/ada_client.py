"""HTTP client for Ada Brain REST API."""

import httpx
from typing import Any, Optional


class AdaClient:
    """Client for interacting with Ada Brain API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=60.0)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def health(self) -> dict[str, Any]:
        """Check Ada Brain health status."""
        response = await self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return await response.json()

    async def chat(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        stream: bool = False,
    ) -> dict[str, Any] | httpx.Response:
        """
        Send a chat message to Ada.

        Args:
            message: The message to send
            conversation_id: Optional conversation ID to continue
            stream: Whether to stream the response

        Returns:
            Response dict (if not streaming) or Response object (if streaming)
        """
        payload = {
            "input": message,
            "conversation_id": conversation_id,
        }

        if stream:
            response = await self.client.post(
                f"{self.base_url}/chat/stream",
                json=payload,
                headers={"Accept": "text/event-stream"},
            )
            response.raise_for_status()
            return response
        else:
            response = await self.client.post(f"{self.base_url}/chat", json=payload)
            response.raise_for_status()
            return await response.json()

    async def search_memories(
        self,
        query: str,
        scope: Optional[str] = None,
        type: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Search Ada's long-term memory.

        Args:
            query: Search query
            scope: Optional scope filter
            type: Optional type filter
            limit: Maximum number of results

        Returns:
            List of matching memories
        """
        params = {
            "query": query,
            "limit": limit,
        }
        if scope:
            params["scope"] = scope
        if type:
            params["type"] = type

        response = await self.client.get(f"{self.base_url}/memories/search", params=params)
        response.raise_for_status()
        data = await response.json()
        return data.get("memories", [])

    async def add_memory(
        self,
        content: str,
        type: str = "note",
        importance: float = 0.5,
        scope: str = "user",
    ) -> dict[str, Any]:
        """
        Add a memory to Ada's long-term store.

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

        response = await self.client.post(f"{self.base_url}/memories", json=payload)
        response.raise_for_status()
        return await response.json()
