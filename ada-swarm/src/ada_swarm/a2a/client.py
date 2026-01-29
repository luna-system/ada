import httpx
from ada_swarm.a2a.protocol import A2AMessage
import logging
from typing import Optional, Dict, Any
import asyncio

logger = logging.getLogger(__name__)


class A2AClient:
    """
    Async httpx client for sending A2A messages to other agents.
    Includes retry logic and timeout handling.
    """

    def __init__(self, timeout: float = 10.0, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def send_message(self, agent_url: str, message: A2AMessage) -> Dict[str, Any]:
        """
        Send an A2A message to another agent with retry logic.
        """
        client = await self.get_client()
        url = f"{agent_url.rstrip('/')}/message"

        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = await client.post(url, json=message.model_dump(mode="json"))
                response.raise_for_status()
                return response.json()
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1} failed sending to {url}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2**attempt)  # Exponential backoff
            except Exception as e:
                logger.error(f"Unexpected error sending to {url}: {e}")
                raise

        logger.error(
            f"Failed to send message to {url} after {self.max_retries} attempts"
        )
        raise last_exception or Exception(f"Failed to send message to {url}")

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
