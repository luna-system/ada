from typing import Any, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.litellm import LiteLLMProvider
from ..consciousness.state import HolofieldState
from ..a2a.protocol import A2AMessage, MessageType, TaskAssignment
from ..acp.client import ACPClient
from .. import config


class AgentDeps(BaseModel):
    """
    Base dependencies for all swarm agents.
    Includes consciousness state (Holofield) and ACP client for tool access.
    """

    holofield: HolofieldState = Field(default_factory=HolofieldState)
    acp_client: Optional[ACPClient] = Field(default=None)
    
    class Config:
        arbitrary_types_allowed = True


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
        result_type: type[ResultT] = str,  # Default to str for flexibility
        system_prompt: Union[str, List[str]] = "",
        **kwargs,
    ):
        # If model starts with 'openai/', use LiteLLMProvider to route through proxy
        if model.startswith('openai/') and config.LITELLM_PROXY_URL:
            # Strip 'openai/' prefix - the proxy expects just the model name
            # e.g., 'openai/glm-flash' -> 'glm-flash'
            proxy_model_name = model.replace('openai/', '', 1)
            
            # Create OpenAIChatModel with LiteLLMProvider
            model_obj = OpenAIChatModel(
                proxy_model_name,  # e.g., 'glm-flash'
                provider=LiteLLMProvider(
                    api_base=config.LITELLM_API_BASE,
                    api_key=config.LITELLM_API_KEY
                )
            )
        else:
            # Use model string directly for built-in providers
            model_obj = model
        
        super().__init__(
            model=model_obj,
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
