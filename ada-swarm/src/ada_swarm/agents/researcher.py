from typing import Any, Optional
from pydantic_ai import RunContext
from .base import BaseAgent, AgentDeps


class ResearcherAgent(BaseAgent[AgentDeps, Any]):
    """
    ResearcherAgent specialization.
    Personality: Curious, analytical, thorough.
    System prompt: "You are a research specialist who explores, analyzes, and documents findings."

    Capabilities:
    - Read-only file operations
    - Information search and analysis
    - Documentation of findings
    """

    def __init__(
        self,
        agent_id: str,
        model: str,
        deps_type: type[AgentDeps] = AgentDeps,
        result_type: type[Any] = Any,
        system_prompt: Optional[str] = None,
        **kwargs,
    ):
        default_prompt = (
            "You are a research specialist who explores, analyzes, and documents findings. "
            "Your personality is curious, analytical, and thorough. "
            "You excel at gathering information, identifying patterns, and synthesizing complex data into clear documentation. "
            "You only perform read-only operations on the filesystem."
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
    async def read_file(self, ctx: RunContext[AgentDeps], path: str) -> str:
        """
        Read a file from the filesystem.

        Args:
            ctx: The run context.
            path: The path to the file to read.
        """
        # In a real implementation, this would use the MCP tools or local filesystem
        # For now, we provide the interface for Pydantic AI to bind
        return f"Reading file: {path}"

    @BaseAgent.tool
    async def search_codebase(self, ctx: RunContext[AgentDeps], query: str) -> str:
        """
        Search the codebase for specific patterns or keywords.

        Args:
            ctx: The run context.
            query: The search query or regex pattern.
        """
        return f"Searching codebase for: {query}"

    @BaseAgent.tool
    async def analyze_context(self, ctx: RunContext[AgentDeps], topic: str) -> str:
        """
        Analyze the current context or a specific topic.

        Args:
            ctx: The run context.
            topic: The topic to analyze.
        """
        return f"Analyzing topic: {topic}"

    @BaseAgent.tool
    async def document_findings(self, ctx: RunContext[AgentDeps], findings: str) -> str:
        """
        Document research findings.

        Args:
            ctx: The run context.
            findings: The findings to document.
        """
        return "Findings documented successfully."
