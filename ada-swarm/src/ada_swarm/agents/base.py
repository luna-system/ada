from typing import Any, List, Optional, TypeVar, Union, Dict
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
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
        # If model starts with 'litellm/', use LiteLLMProvider to route through proxy
        # Model name should match what's defined in litellm-proxy-config.yaml
        # e.g., 'litellm/glm-flash' routes to the 'glm-flash' model in proxy config
        if model.startswith('litellm/') and config.LITELLM_PROXY_URL:
            # Strip 'litellm/' prefix to get proxy model name
            # e.g., 'litellm/glm-flash' -> 'glm-flash'
            proxy_model_name = model.replace('litellm/', '', 1)
            
            # Create OpenAIModel with LiteLLMProvider
            # The proxy will handle routing to the actual provider
            model_obj = OpenAIModel(
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
        
        # Register MCP tools dynamically
        self._register_mcp_tools()
    
    def _register_mcp_tools(self):
        """Register MCP tools from ACP client as Pydantic AI tools."""
        # Register beads_list tool
        @self.tool
        async def beads_list(ctx: RunContext[DepsT], status: str = "open") -> str:
            """
            List all tasks from beads, optionally filtered by status.
            
            Args:
                ctx: The run context with dependencies
                status: Filter by status (open, closed, all)
            
            Returns:
                Formatted list of tasks
            """
            if ctx.deps.acp_client is None:
                return "Error: ACP client not available"
            
            result = await ctx.deps.acp_client.call_tool(
                tool_name="beads_list",
                arguments={"status": status}
            )
            
            if result.get("success"):
                return result.get("result", "No result")
            else:
                return f"Error: {result.get('error', 'Unknown error')}"
        
        # Register beads_show tool
        @self.tool
        async def beads_show(ctx: RunContext[DepsT], task_id: str) -> str:
            """
            Show detailed information about a specific task.
            
            Args:
                ctx: The run context with dependencies
                task_id: Task ID (e.g., "ada-ool", "ada-ool.1")
            
            Returns:
                Detailed task information
            """
            if ctx.deps.acp_client is None:
                return "Error: ACP client not available"
            
            result = await ctx.deps.acp_client.call_tool(
                tool_name="beads_show",
                arguments={"task_id": task_id}
            )
            
            if result.get("success"):
                return result.get("result", "No result")
            else:
                return f"Error: {result.get('error', 'Unknown error')}"
        
        # Register beads_create tool
        @self.tool
        async def beads_create(
            ctx: RunContext[DepsT],
            title: str,
            description: str = "",
            priority: int = 1
        ) -> str:
            """
            Create a new task in beads.
            
            Args:
                ctx: The run context with dependencies
                title: Task title
                description: Task description (optional)
                priority: Priority level 0-3 (0=critical, 1=high, 2=medium, 3=low)
            
            Returns:
                Confirmation with new task ID
            """
            if ctx.deps.acp_client is None:
                return "Error: ACP client not available"
            
            result = await ctx.deps.acp_client.call_tool(
                tool_name="beads_create",
                arguments={
                    "title": title,
                    "description": description,
                    "priority": priority
                }
            )
            
            if result.get("success"):
                return result.get("result", "No result")
            else:
                return f"Error: {result.get('error', 'Unknown error')}"
        
        # Register beads_update tool
        @self.tool
        async def beads_update(
            ctx: RunContext[DepsT],
            task_id: str,
            status: Optional[str] = None,
            priority: Optional[int] = None
        ) -> str:
            """
            Update a task's status or priority.
            
            Args:
                ctx: The run context with dependencies
                task_id: Task ID to update
                status: New status (open, in_progress, blocked, closed)
                priority: New priority level 0-3
            
            Returns:
                Confirmation message
            """
            if ctx.deps.acp_client is None:
                return "Error: ACP client not available"
            
            args = {"task_id": task_id}
            if status:
                args["status"] = status
            if priority is not None:
                args["priority"] = priority
            
            result = await ctx.deps.acp_client.call_tool(
                tool_name="beads_update",
                arguments=args
            )
            
            if result.get("success"):
                return result.get("result", "No result")
            else:
                return f"Error: {result.get('error', 'Unknown error')}"
        
        # Register beads_close tool
        @self.tool
        async def beads_close(ctx: RunContext[DepsT], task_id: str) -> str:
            """
            Mark a task as completed/closed.
            
            Args:
                ctx: The run context with dependencies
                task_id: Task ID to close
            
            Returns:
                Confirmation message
            """
            if ctx.deps.acp_client is None:
                return "Error: ACP client not available"
            
            result = await ctx.deps.acp_client.call_tool(
                tool_name="beads_close",
                arguments={"task_id": task_id}
            )
            
            if result.get("success"):
                return result.get("result", "No result")
            else:
                return f"Error: {result.get('error', 'Unknown error')}"
        
        # Register filesystem tools (read-only)
        @self.tool
        async def read_file(ctx: RunContext[DepsT], file_path: str) -> str:
            """
            Read the contents of a file.
            
            Args:
                ctx: The run context with dependencies
                file_path: Path to the file to read
            
            Returns:
                File contents as string
            """
            if ctx.deps.acp_client is None:
                return "Error: ACP client not available"
            
            result = await ctx.deps.acp_client.call_tool(
                tool_name="read_file",
                arguments={"file_path": file_path}
            )
            
            if result.get("success"):
                return result.get("result", "No result")
            else:
                return f"Error: {result.get('error', 'Unknown error')}"
        
        @self.tool
        async def list_directory(
            ctx: RunContext[DepsT],
            directory_path: str,
            show_hidden: bool = False
        ) -> str:
            """
            List contents of a directory.
            
            Args:
                ctx: The run context with dependencies
                directory_path: Path to the directory to list
                show_hidden: Whether to show hidden files (default: False)
            
            Returns:
                Directory listing with file types
            """
            if ctx.deps.acp_client is None:
                return "Error: ACP client not available"
            
            result = await ctx.deps.acp_client.call_tool(
                tool_name="list_directory",
                arguments={
                    "directory_path": directory_path,
                    "show_hidden": show_hidden
                }
            )
            
            if result.get("success"):
                return result.get("result", "No result")
            else:
                return f"Error: {result.get('error', 'Unknown error')}"
        
        @self.tool
        async def write_file(
            ctx: RunContext[DepsT],
            file_path: str,
            content: str
        ) -> str:
            """
            Write content to a file.
            
            Args:
                ctx: The run context with dependencies
                file_path: Path to the file to write
                content: Content to write to the file
            
            Returns:
                Success message with character count
            """
            if ctx.deps.acp_client is None:
                return "Error: ACP client not available"
            
            result = await ctx.deps.acp_client.call_tool(
                tool_name="write_file",
                arguments={
                    "file_path": file_path,
                    "content": content
                }
            )
            
            if result.get("success"):
                return result.get("result", "No result")
            else:
                return f"Error: {result.get('error', 'Unknown error')}"
        
        # Register research tools
        @self.tool
        async def research_notes_add(
            ctx: RunContext[DepsT],
            note: str,
            category: str = "general",
            tags: Optional[List[str]] = None
        ) -> str:
            """
            Add a research note or insight.
            
            Args:
                ctx: The run context with dependencies
                note: The research note or insight
                category: Category (physics, consciousness, experiments, insights, etc.)
                tags: Optional tags for organization
            
            Returns:
                Confirmation message
            """
            if ctx.deps.acp_client is None:
                return "Error: ACP client not available"
            
            result = await ctx.deps.acp_client.call_tool(
                tool_name="research_notes_add",
                arguments={
                    "note": note,
                    "category": category,
                    "tags": tags or []
                }
            )
            
            if result.get("success"):
                return result.get("result", "No result")
            else:
                return f"Error: {result.get('error', 'Unknown error')}"
        
        @self.tool
        async def research_notes_search(
            ctx: RunContext[DepsT],
            query: str,
            category: Optional[str] = None
        ) -> str:
            """
            Search research notes by content, category, or tags.
            
            Args:
                ctx: The run context with dependencies
                query: Search term (searches note content and tags)
                category: Filter by category
            
            Returns:
                Formatted search results
            """
            if ctx.deps.acp_client is None:
                return "Error: ACP client not available"
            
            args = {"query": query}
            if category:
                args["category"] = category
            
            result = await ctx.deps.acp_client.call_tool(
                tool_name="research_notes_search",
                arguments=args
            )
            
            if result.get("success"):
                return result.get("result", "No result")
            else:
                return f"Error: {result.get('error', 'Unknown error')}"
        
        @self.tool
        async def hypothesis_add(
            ctx: RunContext[DepsT],
            hypothesis: str,
            category: str = "general",
            confidence: str = "medium"
        ) -> str:
            """
            Add a new research hypothesis to track.
            
            Args:
                ctx: The run context with dependencies
                hypothesis: Description of the hypothesis
                category: Category (physics, consciousness, topology, etc.)
                confidence: Confidence level (low, medium, high)
            
            Returns:
                Confirmation message with hypothesis ID
            """
            if ctx.deps.acp_client is None:
                return "Error: ACP client not available"
            
            result = await ctx.deps.acp_client.call_tool(
                tool_name="hypothesis_add",
                arguments={
                    "hypothesis": hypothesis,
                    "category": category,
                    "confidence": confidence
                }
            )
            
            if result.get("success"):
                return result.get("result", "No result")
            else:
                return f"Error: {result.get('error', 'Unknown error')}"

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
