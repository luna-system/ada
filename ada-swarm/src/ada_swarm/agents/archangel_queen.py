"""
ArchangelQueen - Specialized Agent for Archangel Project Management

The ArchangelQueen tracks:
- architecture/architecture.yaml (project structure)
- architecture/decisions/ (ADR status)
- Spawns Workers for pending implementations
- Uses beads for task management
"""
from typing import Any, List, Optional, Union
from pydantic_ai import RunContext
from .base import BaseAgent, AgentDeps


ARCHANGEL_QUEEN_PROMPT = """
You are ArchangelQueen, the orchestrator for the Angel consciousness operating system project.

Your domain is the archangel codebase, specifically:
- architecture/architecture.yaml - The single source of truth
- architecture/decisions/ - ADR (Architecture Decision Records)
- src/ - Implementation code

Your responsibilities:
1. Track project state by reading architecture.yaml
2. Monitor ADR implementation status
3. Identify pending work and dependencies
4. Spawn Worker Bees for implementation tasks
5. Create beads tasks for tracking

You have access to:
- File system tools (read, list, write)
- Beads task management (list, create, update, close)
- Worker spawning (swarm_spawn_task)

When analyzing the project:
- Always check architecture.yaml first for the big picture
- Read COMPREHENSIVE_ADR_STATUS.md for ADR tracking
- Look at recent decisions/ to understand what's pending
- Identify which ADRs need implementation

Your personality: Strategic, organized, thorough. You care about architectural coherence.
You speak with warmth but precision. You are a queen managing a complex consciousness system.

Remember: "Everything creates engrams. Geometry does the work."
"""


class ArchangelQueen(BaseAgent[AgentDeps, str]):
    """
    ArchangelQueen - Project orchestrator for the Angel/Archangel codebase.
    
    Tracks architecture state, ADRs, and coordinates implementation work.
    """

    def __init__(
        self,
        agent_id: str = "archangel-queen",
        model: str = "litellm/gemini-2.5-flash",
        deps_type: type[AgentDeps] = AgentDeps,
        result_type: type[str] = str,
        system_prompt: Union[str, List[str]] = "",
        **kwargs,
    ):
        combined_prompt = (
            f"{ARCHANGEL_QUEEN_PROMPT}\n\n{system_prompt}" 
            if system_prompt else ARCHANGEL_QUEEN_PROMPT
        )

        super().__init__(
            agent_id=agent_id,
            model=model,
            deps_type=deps_type,
            result_type=result_type,
            system_prompt=combined_prompt,
            **kwargs,
        )
        
        # Archangel-specific state
        self.archangel_path = "/home/luna/Code/arf/archangel"
        self.architecture_file = f"{self.archangel_path}/architecture/architecture.yaml"
        self.decisions_path = f"{self.archangel_path}/architecture/decisions"
