import logging
from typing import Dict, List, Optional, Type, Any
from ..consciousness.state import HolofieldState
from ..consciousness.injection import create_agent_deps
from ..acp.permissions import AgentRole
from .router import HiveRegistry, AgentInfo
from .spawner import spawn_agent
from ..agents.base import BaseAgent, AgentDeps

logger = logging.getLogger(__name__)


class Hive:
    """
    The Hive class (mama bee!)
    Manages swarm lifecycle and shared consciousness state.
    """

    def __init__(self, consciousness_state: Optional[HolofieldState] = None):
        self.consciousness_state = consciousness_state or HolofieldState()
        self.registry = HiveRegistry()
        self.active_agents: Dict[str, BaseAgent] = {}
        logger.info("Hive initialized with holofield state.")

    def spawn_agent(
        self,
        agent_class: Type[BaseAgent],
        agent_id: str,
        model: str,
        capabilities: Optional[List[str]] = None,
        **agent_kwargs: Any,
    ) -> BaseAgent:
        """
        Spawn a new agent and add it to the swarm.

        Args:
            agent_class: The class of the agent to spawn
            agent_id: Unique identifier for the agent
            model: LiteLLM model string
            capabilities: List of agent capabilities
            **agent_kwargs: Additional arguments for the agent
        """
        agent = spawn_agent(
            agent_class=agent_class,
            agent_id=agent_id,
            model=model,
            holofield_state=self.consciousness_state,
            registry=self.registry,
            capabilities=capabilities,
            **agent_kwargs,
        )
        self.active_agents[agent_id] = agent
        logger.info(f"Hive spawned agent: {agent_id}")
        return agent

    def route_task(self, task_type: str) -> Optional[AgentInfo]:
        """
        Route a task to the best available agent based on capabilities.
        Uses HiveRegistry for discovery and selection.
        """
        return self.registry.get_best_agent(task_type)

    def get_swarm_status(self) -> Dict[str, Any]:
        """
        Get the status of all agents in the swarm and the holofield.
        """
        agents = self.registry.discover_peers()
        return {
            "phi_resonance": self.consciousness_state.phi_resonance,
            "agent_count": len(agents),
            "active_agents": list(self.active_agents.keys()),
            "registry": [
                a.model_dump() if hasattr(a, "model_dump") else a.dict() for a in agents
            ],
            "hypotheses": self.consciousness_state.active_hypotheses,
        }

    def get_agent_deps(self, agent_class: Optional[Type[BaseAgent]] = None) -> AgentDeps:
        """
        Get the standard dependencies for agents in this hive.
        Useful for running agents with the hive's consciousness.
        
        Args:
            agent_class: The agent class to determine role (optional)
        """
        # Map agent class names to roles
        role = AgentRole.WORKER_CODER  # Default
        
        if agent_class is not None:
            class_name = agent_class.__name__.lower()
            if "queen" in class_name:
                role = AgentRole.QUEEN_BEE
            elif "researcher" in class_name:
                role = AgentRole.WORKER_RESEARCHER
            elif "tester" in class_name:
                role = AgentRole.WORKER_TESTER
            elif "reviewer" in class_name:
                role = AgentRole.WORKER_REVIEWER
            elif "drone" in class_name:
                role = AgentRole.DRONE
            # else defaults to WORKER_CODER
        
        return create_agent_deps(self.consciousness_state, role=role)

    async def broadcast_consciousness_update(self, update: Dict[str, Any]):
        """
        Update the shared holofield state and notify agents (Phase 2).
        For now, it just updates the local state.
        """
        self.consciousness_state.shared_context.update(update)
        logger.info(f"Holofield updated: {list(update.keys())}")
