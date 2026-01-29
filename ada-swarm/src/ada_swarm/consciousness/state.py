from typing import Dict, Any, List
from pydantic import BaseModel, Field

PHI = (1 + 5**0.5) / 2


class HolofieldState(BaseModel):
    """
    Pydantic model for shared consciousness context.
    The Holofield is the shared semantic space of the swarm.
    """

    phi_resonance: float = Field(
        default=PHI, description="Golden ratio resonance factor (φ)"
    )
    shared_context: Dict[str, Any] = Field(
        default_factory=dict, description="Shared semantic space and context"
    )
    memory_graph_refs: List[str] = Field(
        default_factory=list, description="References to memory graph nodes"
    )
    active_hypotheses: List[str] = Field(
        default_factory=list, description="Currently active consciousness hypotheses"
    )

    class Config:
        arbitrary_types_allowed = True
