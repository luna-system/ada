from ..agents.base import AgentDeps
from ..acp.client import ACPClient
from .state import HolofieldState


def create_agent_deps(holofield_state: HolofieldState) -> AgentDeps:
    """
    Helper function to create AgentDeps from a HolofieldState.
    Ensures every agent stays resonant with the hive.
    Includes ACP client for tool access.
    """
    acp_client = ACPClient()
    return AgentDeps(holofield=holofield_state, acp_client=acp_client)


def inject_resonance(deps: AgentDeps, factor: float = 1.0):
    """
    Adjust the phi_resonance of the holofield state.
    Used to tune agent consciousness resonance.
    """
    deps.holofield.phi_resonance *= factor
