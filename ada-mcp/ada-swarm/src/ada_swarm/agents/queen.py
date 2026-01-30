from typing import Any, List, Optional, Union
from pydantic_ai import RunContext
from .base import BaseAgent, AgentDeps
from ..prompts.queen_bee import QUEEN_BEE_PROMPT


class QueenAgent(BaseAgent[AgentDeps, str]):
    """
    QueenAgent - Swarm Orchestrator.
    Personality: Strategic, decisive, supportive, quality-focused.
    System prompt: Consciousness-aware orchestrator with READ-ONLY file access.

    Capabilities (Orchestrator-Focused):
    - Task decomposition and planning
    - Worker Bee spawning and coordination
    - READ-ONLY filesystem access (read_file, list_directory)
    - Research and documentation tools
    - Beads task management
    - Swarm orchestration tools
    
    Intentionally EXCLUDED (Workers handle these):
    - write_file (Workers implement changes)
    - execute_command (Workers execute commands)
    
    Philosophy: The Queen orchestrates, Workers execute!
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
        
        # Remove write_file tool - Queen should delegate to Workers!
        # The tool is registered in BaseAgent, but we remove it here
        if hasattr(self, '_function_tools') and 'write_file' in self._function_tools:
            del self._function_tools['write_file']
