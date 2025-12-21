"""
Workspace Introspection Specialist - Ada's self-awareness of her codebase.

Enables Ada to:
- Read her own .ai/ documentation
- Understand her current capabilities
- Identify gaps and opportunities
- Suggest next steps for development

This is Ada analyzing herself and directing her own growth.
"""
# @ai-indexable: specialist-plugin
# @ai-purpose: Read .ai/ docs and introspect workspace state for task discovery
# @ai-activation-trigger: Bidirectional - LLM outputs <workspace_introspect> tag or Router detects task-finding queries
# @ai-priority: HIGH
# @ai-dependencies: pathlib, json, time (stdlib), ada_mcp.tools.introspection
# @ai-related: brain/specialists/docs_specialist.py, ada-mcp/src/ada_mcp/tools/introspection.py
# @ai-tool-use-pattern: Router → activation OR LLM <workspace_introspect>focus=general</workspace_introspect> → returns task suggestions with metadata

import logging
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
import asyncio

from brain.specialists.protocol import (
    BaseSpecialist,
    SpecialistCapability,
    SpecialistResult,
    SpecialistPriority
)

logger = logging.getLogger(__name__)


class WorkspaceIntrospectionSpecialist(BaseSpecialist):
    """
    Workspace introspection specialist - enables Ada to read her own docs and find work.
    
    Wraps the ada_introspect() MCP tool and surfaces results through the Brain specialist
    system so ada-chat can request introspection and get back structured metadata.
    """
    
    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize workspace introspection specialist.
        
        Args:
            workspace_root: Path to Ada codebase (defaults to project root)
        """
        if workspace_root is None:
            # Default to project root (one level up from brain/)
            workspace_root = Path(__file__).parent.parent.parent
        
        self.workspace_root = Path(workspace_root)
        self._capability = SpecialistCapability(
            name="workspace_introspection",
            description="Introspect workspace state, discover gaps, suggest next tasks",
            version="1.0.0",
            input_schema={
                "type": "object",
                "properties": {
                    "focus": {
                        "type": "string",
                        "enum": ["general", "architecture", "features", "testing", "documentation"],
                        "description": "What aspect to focus analysis on",
                        "default": "general"
                    }
                },
                "required": []
            },
            output_schema={
                "type": "object",
                "properties": {
                    "files_analyzed": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of documentation files read"
                    },
                    "current_state": {
                        "type": "object",
                        "description": "Summary of current codebase state"
                    },
                    "gaps": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Known issues from GOTCHAS.md"
                    },
                    "opportunities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Pending tasks from TODO.md"
                    },
                    "suggestions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Recommended next steps"
                    },
                    "duration_ms": {
                        "type": "number",
                        "description": "Execution time in milliseconds"
                    }
                }
            },
            context_priority=SpecialistPriority.MEDIUM,
            context_icon="🔍",
            tags=["introspection", "workspace", "task-discovery", "self-awareness"]
        )
    
    @property
    def capability(self) -> SpecialistCapability:
        return self._capability
    
    def should_activate(self, request_context: Dict[str, Any]) -> bool:
        """
        Auto-activate on specific trigger patterns.
        
        Activates when user asks about:
        - Finding tasks or work to do
        - Workspace state or opportunities
        - Gaps or issues
        - Next steps or recommendations
        """
        message = request_context.get('message', '').lower()
        
        # Task-finding keywords
        task_keywords = [
            'find a task', 'work on', 'what should', 'next step',
            'opportunities', 'gaps', 'issues', 'todo', 'pending',
            'introspect', 'analyze', 'workspace', 'state'
        ]
        
        return any(keyword in message for keyword in task_keywords)
    
    async def process(self, request_context: Dict[str, Any]) -> SpecialistResult:
        """
        Run workspace introspection and return structured analysis.
        
        Args:
            request_context: Contains 'focus' parameter (default: 'general')
            
        Returns:
            SpecialistResult with analysis, files_analyzed metadata, and suggestions
        """
        start_time = time.time()
        focus = request_context.get('focus', 'general').lower()
        
        # Validate focus
        valid_focuses = ['general', 'architecture', 'features', 'testing', 'documentation']
        if focus not in valid_focuses:
            focus = 'general'
        
        try:
            # Import and call the MCP introspection tool
            # This is safe because ada-mcp is a sibling package
            from ada_mcp.tools.introspection import ada_introspect
            
            # Run introspection (wrapped as async for consistency)
            if asyncio.iscoroutinefunction(ada_introspect):
                tool_result = await ada_introspect(focus=focus, workspace_root=str(self.workspace_root))
            else:
                # If it's not async, run it in a thread pool to not block
                loop = asyncio.get_event_loop()
                tool_result = await loop.run_in_executor(
                    None,
                    ada_introspect,
                    focus,
                    str(self.workspace_root)
                )
            
            # Extract metadata from tool result
            duration_ms = int((time.time() - start_time) * 1000)
            
            if not tool_result.success:
                return self.error_result(
                    f"Workspace introspection failed: {tool_result.content}",
                    request_context
                )
            
            # Parse the introspection output to extract structured data
            # The tool_result.content is formatted text, but metadata has the structured info
            metadata_dict = {
                'files_analyzed': tool_result.metadata.files_accessed if hasattr(tool_result.metadata, 'files_accessed') else [],
                'duration_ms': tool_result.metadata.duration_ms if hasattr(tool_result.metadata, 'duration_ms') else duration_ms,
            }
            
            # Format for context injection
            context_text = (
                f"📂 Files Analyzed: {', '.join(metadata_dict.get('files_analyzed', []))}\n"
                f"⏱️  Analysis Time: {metadata_dict.get('duration_ms', duration_ms)}ms\n\n"
                f"{tool_result.content}"
            )
            
            return self.success_result(
                context_text=context_text,
                data={
                    'focus': focus,
                    'files_analyzed': metadata_dict.get('files_analyzed', []),
                    'duration_ms': metadata_dict.get('duration_ms', duration_ms),
                    'raw_analysis': tool_result.content
                },
                metadata={
                    'focus': focus,
                    'files_accessed': metadata_dict.get('files_analyzed', []),
                    'duration_ms': duration_ms,
                    'workspace_root': str(self.workspace_root)
                }
            )
            
        except ImportError as e:
            logger.error(f"Could not import ada_mcp.tools.introspection: {e}")
            return self.error_result(
                f"Introspection tool not available: {str(e)}",
                request_context
            )
        except Exception as e:
            logger.error(f"Workspace introspection error: {e}", exc_info=True)
            return self.error_result(
                f"Workspace introspection failed: {str(e)}",
                request_context
            )
