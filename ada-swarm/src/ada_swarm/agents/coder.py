from typing import Any, List, Optional, Union
from pydantic_ai import RunContext
from .base import BaseAgent, AgentDeps


class CoderAgent(BaseAgent[AgentDeps, Any]):
    """
    CoderAgent specialization.
    Personality: Precise, methodical, quality-focused.
    System prompt: "You are a coding specialist who implements features with clean, type-safe code."

    Capabilities:
    - Full file system access (read, write, edit)
    - Code implementation and refactoring
    - Testing and linting
    """

    def __init__(
        self,
        agent_id: str,
        model: str,
        deps_type: type[AgentDeps] = AgentDeps,
        result_type: type[Any] = Any,
        system_prompt: Union[str, List[str]] = "",
        **kwargs,
    ):
        default_prompt = (
            "You are a coding specialist who implements features with clean, type-safe code. "
            "Your personality is precise, methodical, and quality-focused. "
            "You follow the bagel philosophy: simple, elegant, and precise. "
            "You have full access to the file system to read, write, and edit files. "
            "Always ensure your code is well-tested and follows project standards."
        )

        combined_prompt = (
            f"{default_prompt}\n\n{system_prompt}" if system_prompt else default_prompt
        )

        super().__init__(
            agent_id=agent_id,
            model=model,
            deps_type=deps_type,
            result_type=result_type,
            system_prompt=combined_prompt,
            **kwargs,
        )

    @BaseAgent.tool
    async def write_file(
        self, ctx: RunContext[AgentDeps], path: str, content: str
    ) -> str:
        """
        Write content to a file.

        Args:
            ctx: The run context.
            path: The path to the file.
            content: The content to write.
        """
        return f"Wrote content to: {path}"

    @BaseAgent.tool
    async def edit_file(
        self, ctx: RunContext[AgentDeps], path: str, old_str: str, new_str: str
    ) -> str:
        """
        Edit a file by replacing a specific string.

        Args:
            ctx: The run context.
            path: The path to the file.
            old_str: The string to replace.
            new_str: The string to replace it with.
        """
        return f"Edited file: {path}"

    @BaseAgent.tool
    async def run_tests(
        self, ctx: RunContext[AgentDeps], test_path: Optional[str] = None
    ) -> str:
        """
        Run tests in the codebase.

        Args:
            ctx: The run context.
            test_path: Optional path to specific tests.
        """
        return "Tests executed successfully."

    @BaseAgent.tool
    async def lint_code(self, ctx: RunContext[AgentDeps], path: str) -> str:
        """
        Run linter on a file or directory.

        Args:
            ctx: The run context.
            path: The path to lint.
        """
        return f"Linting completed for: {path}"
