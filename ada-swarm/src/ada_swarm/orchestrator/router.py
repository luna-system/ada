from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import threading
import logging

logger = logging.getLogger(__name__)


class AgentInfo(BaseModel):
    """Information about an agent in the swarm"""

    agent_id: str
    url: str
    capabilities: List[str] = Field(default_factory=list)
    model: Optional[str] = None
    status: str = "active"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HiveRegistry:
    """
    Registry mapping agent_id -> URL and capabilities.
    Thread-safe operations for agent discovery.
    """

    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}
        self._lock = threading.Lock()

    def register_agent(self, agent_info: AgentInfo):
        """Register or update an agent in the registry"""
        with self._lock:
            self.agents[agent_info.agent_id] = agent_info
            logger.info(f"Registered agent: {agent_info.agent_id} at {agent_info.url}")

    def unregister_agent(self, agent_id: str):
        """Remove an agent from the registry"""
        with self._lock:
            if agent_id in self.agents:
                del self.agents[agent_id]
                logger.info(f"Unregistered agent: {agent_id}")

    def discover_peers(self, capability: Optional[str] = None) -> List[AgentInfo]:
        """Find agents, optionally filtered by capability"""
        with self._lock:
            if capability:
                return [
                    info
                    for info in self.agents.values()
                    if capability in info.capabilities
                ]
            return list(self.agents.values())

    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get information about a specific agent"""
        with self._lock:
            return self.agents.get(agent_id)

    def get_best_agent(self, task_type: str) -> Optional[AgentInfo]:
        """
        Select the best agent for a task.
        Uses φ-weighted selection to choose among capable agents.
        """
        peers = self.discover_peers(task_type)
        if not peers:
            return None

        if len(peers) == 1:
            return peers[0]

        # φ-weighted selection (simplified for MVP)
        # We use the golden ratio to pick an index that is "resonant"
        # In a real implementation, this would involve performance metrics
        phi = (1 + 5**0.5) / 2
        index = int((len(peers) * phi) % len(peers))

        selected = peers[index]
        logger.info(f"φ-selected agent {selected.agent_id} for task {task_type}")
        return selected

    def list_agents(self) -> List[str]:
        """List all registered agent IDs"""
        with self._lock:
            return list(self.agents.keys())
