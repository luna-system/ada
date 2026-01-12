"""
Tool Protocol - MCP-inspired interface for extensible AI capabilities.

Defines standard interfaces for tool modules (OCR, vision, media, etc.)
that can augment the main LLM with specialized processing capabilities.
"""
from typing import Protocol, Any, Optional, runtime_checkable
from dataclasses import dataclass, field
from enum import Enum


class ToolPriority(Enum):
    """Priority for context injection order (lower = earlier in prompt)"""
    CRITICAL = 0    # System notices, identity
    HIGH = 10       # OCR/Vision results (user-provided context)
    MEDIUM = 50     # Media, external data
    LOW = 100       # Supplementary info


@dataclass
class ToolCapability:
    """
    Defines what a tool can do.
    Inspired by MCP Tool schema but simplified for monolithic architecture.
    """
    name: str  # Unique identifier (e.g., "ocr", "vision", "media")
    description: str  # Human-readable description
    version: str = "1.0.0"
    
    # Input/output schemas (JSON Schema format for future validation)
    input_schema: dict = field(default_factory=dict)
    output_schema: dict = field(default_factory=dict)
    
    # Context injection configuration
    context_priority: ToolPriority = ToolPriority.MEDIUM
    context_icon: str = "🔧"  # Emoji for prompt formatting
    
    # Runtime metadata
    tags: list[str] = field(default_factory=list)
    enabled: bool = True


@dataclass
class ToolResult:
    """
    Standardized output format for tool processing.
    All tools return this structure for consistent handling.
    """
    success: bool
    tool_name: str
    
    # For LLM context injection
    context_text: str = ""  # Formatted text to inject into prompt
    
    # Structured data and diagnostics
    data: dict = field(default_factory=dict)  # Raw/structured result data
    metadata: dict = field(default_factory=dict)  # Processing metadata
    
    # Error handling
    error: Optional[str] = None
    error_code: Optional[str] = None
    
    def __post_init__(self):
        """Ensure success=False if error is present"""
        if self.error:
            self.success = False


@runtime_checkable
class Tool(Protocol):
    """
    Protocol (interface) that all tools must implement.
    
    This is a Python Protocol (PEP 544) - structural typing, not inheritance.
    Any class with these methods is considered a Tool.
    """
    
    @property
    def capability(self) -> ToolCapability:
        """Declare tool capabilities and metadata"""
        ...
    
    async def process(self, **kwargs) -> ToolResult:
        """
        Execute tool logic.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            ToolResult with context_text for prompt injection
        """
        ...
    
    def should_activate(self, request_context: dict) -> bool:
        """
        Determine if this tool should process the current request.
        
        Args:
            request_context: Dict containing request metadata
                - prompt: user prompt text
                - conversation_id: current conversation
                - entity: optional entity filter
                - ocr_context: OCR data if present
                - media: media data if present
                - etc.
        
        Returns:
            True if tool should be invoked for this request
        """
        ...


class BaseTool:
    """
    Optional base class providing common utilities.
    Tools can inherit this or implement Protocol directly.
    """
    
    def __init__(self, capability: ToolCapability):
        self._capability = capability
    
    @property
    def capability(self) -> ToolCapability:
        return self._capability
    
    def format_context(self, title: str, content: str, metadata: Optional[dict] = None) -> str:
        """
        Standard formatting for context injection.
        
        Args:
            title: Section title
            content: Main content text
            metadata: Optional metadata to show (filename, confidence, etc.)
            
        Returns:
            Formatted string for prompt injection
        """
        icon = self._capability.context_icon
        lines = [f"{icon} {title.upper()}"]
        
        if metadata:
            meta_str = ", ".join(f"{k}={v}" for k, v in metadata.items() if v is not None)
            if meta_str:
                lines.append(f"({meta_str})")
        
        lines.append(content)
        return "\n".join(lines)
    
    def error_result(self, error_msg: str, error_code: Optional[str] = None) -> ToolResult:
        """Helper to create error results"""
        return ToolResult(
            success=False,
            tool_name=self._capability.name,
            error=error_msg,
            error_code=error_code
        )
    
    def success_result(self, context_text: str, data: dict, metadata: Optional[dict] = None) -> ToolResult:
        """Helper to create success results"""
        return ToolResult(
            success=True,
            tool_name=self._capability.name,
            context_text=context_text,
            data=data,
            metadata=metadata or {}
        )
