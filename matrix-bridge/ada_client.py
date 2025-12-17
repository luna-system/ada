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
            "prompt": message,  # Brain API expects "prompt" not "message"
            "conversation_id": room_id if room_id else user_id,  # Use room ID for context
            "stream": True
        }
        
        # Conversation history not needed - brain handles it via conversation_id
        logger.info(f"Sending to brain: {payload}")
        
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
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Error from Ada brain: {e.response.status_code} {e.response.reason_phrase}")
            logger.error(f"Request payload was: {payload}")
            yield "Sorry, I encountered an error connecting to my brain. Please try again later."
        except httpx.HTTPError as e:
            logger.error(f"Error communicating with Ada brain: {e}")
            logger.error(f"Request payload was: {payload}")
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
            Complete response text (parsed from streaming JSON chunks)
        """
        import json
        response_parts = []
        async for chunk in self.chat_stream(message, user_id, room_id, conversation_history):
            try:
                data = json.loads(chunk)
                if data.get("type") == "token":
                    response_parts.append(data.get("content", ""))
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse chunk: {chunk}")
        return "".join(response_parts)
    
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
