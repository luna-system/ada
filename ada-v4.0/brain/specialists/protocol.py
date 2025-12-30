"""
Specialist Protocol - MCP-inspired interface for extensible AI capabilities.

Defines standard interfaces for specialist modules (OCR, vision, media, etc.)
that can augment the main LLM with specialized processing capabilities.
"""
from typing import Protocol, Any, Optional, runtime_checkable
from dataclasses import dataclass, field
from enum import Enum


class SpecialistPriority(Enum):
    """Priority for context injection order (lower = earlier in prompt)"""
    CRITICAL = 0    # System notices, identity
    HIGH = 10       # OCR/Vision results (user-provided context)
    MEDIUM = 50     # Media, external data
    LOW = 100       # Supplementary info


@dataclass
class SpecialistCapability:
    """
    Defines what a specialist can do.
    Inspired by MCP Tool schema but simplified for monolithic architecture.
    """
    name: str  # Unique identifier (e.g., "ocr", "vision", "media")
    description: str  # Human-readable description
    version: str = "1.0.0"
    
    # Input/output schemas (JSON Schema format for future validation)
    input_schema: dict = field(default_factory=dict)
    output_schema: dict = field(default_factory=dict)
    
    # Context injection configuration
    context_priority: SpecialistPriority = SpecialistPriority.MEDIUM
    context_icon: str = "🔧"  # Emoji for prompt formatting
    
    # Runtime metadata
    tags: list[str] = field(default_factory=list)
    enabled: bool = True


@dataclass
class SpecialistResult:
    """
    Standardized output format for specialist processing.
    All specialists return this structure for consistent handling.
    """
    success: bool
    specialist_name: str
    
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
class Specialist(Protocol):
    """
    Protocol (interface) that all specialists must implement.
    
    This is a Python Protocol (PEP 544) - structural typing, not inheritance.
    Any class with these methods is considered a Specialist.
    """
    
    @property
    def capability(self) -> SpecialistCapability:
        """Declare specialist capabilities and metadata"""
        ...
    
    async def process(self, **kwargs) -> SpecialistResult:
        """
        Execute specialist logic.
        
        Args:
            **kwargs: Specialist-specific parameters
            
        Returns:
            SpecialistResult with context_text for prompt injection
        """
        ...
    
    def should_activate(self, request_context: dict) -> bool:
        """
        Determine if this specialist should process the current request.
        
        Args:
            request_context: Dict containing request metadata
                - prompt: user prompt text
                - conversation_id: current conversation
                - entity: optional entity filter
                - ocr_context: OCR data if present
                - media: media data if present
                - etc.
        
        Returns:
            True if specialist should be invoked for this request
        """
        ...


class BaseSpecialist:
    """
    Optional base class providing common utilities.
    Specialists can inherit this or implement Protocol directly.
    """
    
    def __init__(self, capability: SpecialistCapability):
        self._capability = capability
    
    @property
    def capability(self) -> SpecialistCapability:
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
    
    def error_result(self, error_msg: str, error_code: Optional[str] = None) -> SpecialistResult:
        """Helper to create error results"""
        return SpecialistResult(
            success=False,
            specialist_name=self._capability.name,
            error=error_msg,
            error_code=error_code
        )
    
    def success_result(self, context_text: str, data: dict, metadata: Optional[dict] = None) -> SpecialistResult:
        """Helper to create success results"""
        return SpecialistResult(
            success=True,
            specialist_name=self._capability.name,
            context_text=context_text,
            data=data,
            metadata=metadata or {}
        )
