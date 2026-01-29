from typing import Any, List, Optional, Union
from pydantic_ai import RunContext
from .base import BaseAgent, AgentDeps
from ..prompts.worker_reviewer import WORKER_REVIEWER_PROMPT


class ReviewerAgent(BaseAgent[AgentDeps, str]):
    """
    ReviewerAgent specialization.
    Personality: Thoughtful, helpful, standards-focused.
    System prompt: Code review specialist with AST-grep and UBS tools.

    Capabilities:
    - Code analysis with AST-grep
    - Bug scanning with UBS
    - Read-only filesystem access
    - Task management
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
            f"{WORKER_REVIEWER_PROMPT}\n\n{system_prompt}" if system_prompt else WORKER_REVIEWER_PROMPT
        )

        super().__init__(
            agent_id=agent_id,
            model=model,
            deps_type=deps_type,
            result_type=result_type,
            system_prompt=combined_prompt,
            **kwargs,
        )
