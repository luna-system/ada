"""HTTP client for Ada's brain API."""

import logging
from typing import AsyncIterator

import httpx

from config import Config

logger = logging.getLogger(__name__)


class AdaBrainClient:
    """Client for communicating with Ada's brain API."""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.ada_brain_url
        self.stream_endpoint = config.ada_stream_endpoint
        self.timeout = config.ada_timeout
        
    async def chat_stream(
        self,
        message: str,
        user_id: str,
        room_id: str | None = None,
        conversation_history: list[dict] | None = None
    ) -> AsyncIterator[str]:
        """
        Stream chat response from Ada's brain.
        
        Args:
            message: User's message
            user_id: Matrix user ID
            room_id: Matrix room ID (optional)
            conversation_history: Recent messages for context
            
        Yields:
            Response chunks as they arrive
        """
        url = f"{self.base_url}{self.stream_endpoint}"
        
        payload = {
            "message": message,
            "user_id": user_id,
            "stream": True
        }
        
        # Add room context if available
        if room_id:
            payload["room_id"] = room_id
        
        # Add conversation history if available
        if conversation_history:
            payload["conversation_history"] = conversation_history
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    url,
                    json=payload,
                    headers={"Accept": "text/event-stream"}
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            chunk = line[6:]  # Remove "data: " prefix
                            if chunk and chunk != "[DONE]":
                                yield chunk
        
        except httpx.HTTPError as e:
            logger.error(f"Error communicating with Ada brain: {e}")
            yield "Sorry, I encountered an error connecting to my brain. Please try again later."
        except Exception as e:
            logger.error(f"Unexpected error in chat stream: {e}", exc_info=True)
            yield "Sorry, I encountered an unexpected error. Please try again later."
    
    async def chat(
        self,
        message: str,
        user_id: str,
        room_id: str | None = None,
        conversation_history: list[dict] | None = None
    ) -> str:
        """
        Get complete chat response (non-streaming).
        
        Args:
            message: User's message
            user_id: Matrix user ID
            room_id: Matrix room ID (optional)
            conversation_history: Recent messages for context
            
        Returns:
            Complete response text
        """
        chunks = []
        async for chunk in self.chat_stream(message, user_id, room_id, conversation_history):
            chunks.append(chunk)
        return "".join(chunks)
    
    async def healthcheck(self) -> bool:
        """
        Check if Ada's brain is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/v1/healthz")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Brain healthcheck failed: {e}")
            return False
