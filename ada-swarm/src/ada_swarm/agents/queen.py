from typing import Any, List, Optional, Union
from pydantic_ai import RunContext
from .base import BaseAgent, AgentDeps
from ..prompts.queen_bee import QUEEN_BEE_PROMPT


class QueenAgent(BaseAgent[AgentDeps, str]):
    """
    QueenAgent - Swarm Orchestrator.
    Personality: Strategic, decisive, supportive, quality-focused.
    System prompt: Consciousness-aware orchestrator with full tool access.

    Capabilities:
    - Task decomposition and planning
    - Worker Bee spawning and coordination
    - Full filesystem and execution access
    - Research and documentation tools
    - Beads task management
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
        combined_prompt = (
            f"{QUEEN_BEE_PROMPT}\n\n{system_prompt}" if system_prompt else QUEEN_BEE_PROMPT
        )

        super().__init__(
            agent_id=agent_id,
            model=model,
            deps_type=deps_type,
            result_type=result_type,
            system_prompt=combined_prompt,
            **kwargs,
        )
