"""HTTP client for Ada's brain API.

This client follows the standard adapter contract pattern established by
the CLI reference implementation.
"""

import logging
from typing import AsyncIterator

import httpx

from config import Config

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
                    if response.status_code != 200:
                        error_text = await response.aread()
                        raise AdaBrainResponseError(
                            f"Brain returned {response.status_code}: {error_text.decode()}"
                        )
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            chunk = line[6:]  # Remove "data: " prefix
                            if chunk and chunk != "[DONE]":
                                yield chunk
        
        except httpx.ConnectError as e:
            logger.error(f"Unable to connect to Ada brain at {self.base_url}: {e}")
            raise AdaBrainConnectionError(
                f"Unable to connect to Ada's brain at {self.base_url}: {e}"
            ) from e
        except httpx.HTTPError as e:
            logger.error(f"HTTP error communicating with Ada brain: {e}")
            raise AdaBrainConnectionError(
                f"HTTP error communicating with Ada's brain: {e}"
            ) from e
    
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
                logg(self) -> dict:
        """
        Check Ada's brain health status.
        
        Returns:
            Health status dictionary with service statuses
            
        Raises:
            AdaBrainConnectionError: If unable to connect to brain
        """
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/v1/healthz")
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError as e:
            raise AdaBrainConnectionError(
                f"Unable to connect to Ada's brain at {self.base_url}: {e}"
            ) from e
        except httpx.HTTPError as e:
            raise AdaBrainConnectionError(
                f"HTTP error communicating with Ada's brain: {e}"
            ) from response.status_code == 200
        except Exception as e:
            logger.error(f"Brain healthcheck failed: {e}")
            return False
