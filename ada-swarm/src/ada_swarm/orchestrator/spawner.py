import random
import threading
import uvicorn
import logging
from typing import Type, List, Optional, Any
from ..agents.base import BaseAgent
from ..consciousness.state import HolofieldState
from ..a2a.server import A2AServer
from .router import HiveRegistry, AgentInfo
from .. import config

logger = logging.getLogger(__name__)


def spawn_agent(
    agent_class: Type[BaseAgent],
    agent_id: str,
    model: Optional[str] = None,
    role: Optional[str] = None,
    holofield_state: HolofieldState = None,
    registry: HiveRegistry = None,
    capabilities: Optional[List[str]] = None,
    host: str = "127.0.0.1",
    port: Optional[int] = None,
    **agent_kwargs: Any,
) -> BaseAgent:
    """
    Spawns an agent with LiteLLM, injects consciousness, starts A2A server, and registers it.

    Args:
        agent_class: The class of the agent to spawn (must inherit from BaseAgent)
        agent_id: Unique identifier for the agent
        model: LiteLLM model string (e.g., "litellm/gemini-flash"). If None, auto-selects based on role.
        role: Agent role (queen, coder, researcher, tester, reviewer, drone). Used for auto-model selection.
        holofield_state: The shared consciousness state to inject
        registry: The HiveRegistry to register the agent in
        capabilities: List of agent capabilities
        host: Host for the A2A server
        port: Port for the A2A server (random if None)
        **agent_kwargs: Additional arguments for the agent constructor
    """
    # Auto-select model based on role if not explicitly provided
    if model is None:
        if role is None:
            # Try to infer role from agent class name
            class_name = agent_class.__name__.lower()
            if "queen" in class_name:
                role = "queen"
            elif "coder" in class_name:
                role = "coder"
            elif "researcher" in class_name:
                role = "researcher"
            elif "tester" in class_name:
                role = "tester"
            elif "reviewer" in class_name:
                role = "reviewer"
            elif "drone" in class_name:
                role = "drone"
            else:
                role = "coder"  # Default to coder
        
        model = config.get_model_for_role(role)
        logger.info(f"Auto-selected model '{model}' for role '{role}'")
    
    logger.info(f"Spawning agent {agent_id} with model {model}")

    # 1. Initialize the agent
    # BaseAgent handles the pydantic_ai.Agent initialization
    # We pass model string which Pydantic AI uses with LiteLLM
    agent = agent_class(agent_id=agent_id, model=model, **agent_kwargs)

    # 2. Start A2A server (if registry provided)
    if registry is not None:
        if port is None:
            # Choose a random port in a reasonable range
            port = random.randint(10000, 20000)

        a2a_server = A2AServer(agent_id=agent_id)

        # We need to run the server in a background thread so it doesn't block
        def run_server():
            try:
                # Use a low-level uvicorn config to avoid signal issues in threads
                config_obj = uvicorn.Config(
                    a2a_server.app, host=host, port=port, log_level="error"
                )
                server = uvicorn.Server(config_obj)
                server.run()
            except Exception as e:
                logger.error(f"A2A Server for {agent_id} failed: {e}")

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        url = f"http://{host}:{port}"
        logger.info(f"Agent {agent_id} A2A server started at {url}")

        # 3. Register agent in the HiveRegistry
        agent_info = AgentInfo(
            agent_id=agent_id,
            url=url,
            capabilities=capabilities or [],
            model=model,
            status="active",
            metadata={"thread_id": server_thread.ident, "role": role or "unknown"},
        )
        registry.register_agent(agent_info)

    return agent
