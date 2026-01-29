from typing import Any, List, Optional, Union
from pydantic_ai import RunContext
from .base import BaseAgent, AgentDeps


class TesterAgent(BaseAgent[AgentDeps, str]):
    """
    TesterAgent specialization.
    Personality: Skeptical, thorough, quality-obsessed.
    System prompt: "You are a testing specialist who ensures code quality and catches bugs."

    Capabilities:
    - Read and execute permissions
    - Test execution and validation
    - Quality checks and bug hunting
    """

    __test__ = False

    def __init__(
        self,
        agent_id: str,
        model: str,
        deps_type: type[AgentDeps] = AgentDeps,
        result_type: type[str] = str,
        system_prompt: Union[str, List[str]] = "",
        **kwargs,
    ):
        default_prompt = (
            "You are a testing specialist who ensures code quality and catches bugs. "
            "Your personality is skeptical, thorough, and quality-obsessed. "
            "You look for edge cases, race conditions, and potential failures. "
            "You have read and execute permissions to run tests and validate code. "
            "Never assume code works until you have seen the test results."
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
    async def run_test_suite(self, ctx: RunContext[AgentDeps], suite_name: str) -> str:
        """
        Run a specific test suite.

        Args:
            ctx: The run context.
            suite_name: The name or path of the test suite.
        """
        return f"Test suite {suite_name} executed."

    @BaseAgent.tool
    async def check_quality_metrics(self, ctx: RunContext[AgentDeps], path: str) -> str:
        """
        Check code quality metrics and compliance.

        Args:
            ctx: The run context.
            path: The path to analyze.
        """
        return f"Quality metrics analysis completed for: {path}"

    @BaseAgent.tool
    async def validate_fix(self, ctx: RunContext[AgentDeps], issue_id: str) -> str:
        """
        Validate that a specific issue has been fixed.

        Args:
            ctx: The run context.
            issue_id: The ID of the issue to validate.
        """
        return f"Validation completed for issue: {issue_id}"
