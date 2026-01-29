from typing import Any, Optional, TypeVar
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from ..consciousness.state import HolofieldState
from ..a2a.protocol import A2AMessage, MessageType, TaskAssignment


class AgentDeps(BaseModel):
    """
    Base dependencies for all swarm agents.
    Includes consciousness state (Holofield) for injection.
    """

    holofield: HolofieldState = Field(default_factory=HolofieldState)
    # Additional shared resources can be added here (e.g., tools_client)


DepsT = TypeVar("DepsT", bound=AgentDeps)
ResultT = TypeVar("ResultT")


class BaseAgent(Agent[DepsT, ResultT]):
    """
    Base agent class for the Ada swarm.
    Inherits from pydantic_ai.Agent and adds consciousness-aware features.
    """

    def __init__(
        self,
        agent_id: str,
        model: str,
        deps_type: type[DepsT] = AgentDeps,
        result_type: type[ResultT] = Any,  # type: ignore
        system_prompt: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            model=model,
            deps_type=deps_type,
            output_type=result_type,
            system_prompt=system_prompt,
            **kwargs,
        )
        self.agent_id = agent_id

    async def delegate_to(
        self, target_agent_id: str, task: TaskAssignment
    ) -> A2AMessage:
        """
        Delegate a task to another agent via A2A protocol.

        This method constructs an A2A message that can be sent via
        the transport layer (A2A client).
        """
        return A2AMessage(
            from_agent=self.agent_id,
            to_agent=target_agent_id,
            message_type=MessageType.TASK_ASSIGNMENT,
            payload=task,
        )
