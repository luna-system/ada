from fastapi import FastAPI, HTTPException, Request
from ada_swarm.a2a.protocol import A2AMessage
import logging
from typing import Callable, Awaitable, Dict, Any
import uvicorn

logger = logging.getLogger(__name__)


class A2AServer:
    """
    FastAPI server for receiving A2A messages.
    Each agent runs an instance of this server.
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.app = FastAPI(title=f"Ada A2A Server - {agent_id}")
        self.handlers: Dict[str, Callable[[A2AMessage], Awaitable[Any]]] = {}

        self._setup_routes()

    def _setup_routes(self):
        @self.app.post("/message")
        async def receive_message(message: A2AMessage):
            if message.to_agent != self.agent_id:
                logger.warning(
                    f"Received message for {message.to_agent} but I am {self.agent_id}"
                )
                # We still process it if it reached us, but log a warning

            logger.info(
                f"[{self.agent_id}] Received {message.message_type} from {message.from_agent}"
            )

            # Call registered handler if any
            handler = self.handlers.get(message.message_type)
            if handler:
                try:
                    result = await handler(message)
                    return {
                        "status": "success",
                        "message_id": message.id,
                        "result": result,
                    }
                except Exception as e:
                    logger.error(f"Error in message handler: {e}")
                    raise HTTPException(status_code=500, detail=str(e))

            return {"status": "received", "message_id": message.id}

        @self.app.get("/health")
        async def health():
            return {"status": "ok", "agent_id": self.agent_id}

    def register_handler(
        self, message_type: str, handler: Callable[[A2AMessage], Awaitable[Any]]
    ):
        """Register a handler for a specific message type"""
        self.handlers[message_type] = handler

    def run(self, host: str = "0.0.0.0", port: int = 0):
        """Start the server. If port is 0, a random port will be chosen."""
        uvicorn.run(self.app, host=host, port=port)
