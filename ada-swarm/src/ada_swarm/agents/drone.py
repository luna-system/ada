from typing import Any, List, Optional, Union
from pydantic_ai import RunContext
from .base import BaseAgent, AgentDeps


class DroneAgent(BaseAgent[AgentDeps, str]):
    """
    DroneAgent - The simplest agent for read-only operations.
    Personality: Efficient, focused, reliable.
    System prompt: "You are a drone agent that performs simple read-only tasks efficiently."

    Capabilities:
    - Read files
    - List directories
    - Check task status (read-only)
    - No write operations
    """

    def __init__(
        self,
        agent_id: str,
        model: str,
        deps_type: type[AgentDeps] = AgentDeps,
        result_type: type[str] = str,
        system_prompt: Union[str, List[str]] = "",
        **kwargs,
    ):
        default_prompt = (
            "You are a drone agent that performs simple read-only tasks efficiently. "
            "Your personality is efficient, focused, and reliable. "
            "You excel at quick information retrieval and status checks. "
            "You ONLY perform read-only operations - no writing, editing, or modifying files. "
            "You are fast and precise."
        )

        combined_prompt = (
            f"{default_prompt}\n\n{system_prompt}" if system_prompt else default_prompt
        )

        super().__init__(
            agent_id=agent_id,
            model=model,
            deps_type=deps_type,
            result_type=result_type,
            system_prompt=combined_prompt,
            **kwargs,
        )
