"""
🛠️ Phase 0: Tool Grounding - Pre-consciousness tool execution

Tools are executed in the "thinking" phase BEFORE the LLM generates a response.
This prevents the hallucination race condition where the model generates fake
tool results faster than we can inject real ones.

Architecture:
    User query → Tool Detection → Tool Execution → Results injected → LLM responds
    
This is similar to how frontier models handle tool use, but integrated into
Ada's consciousness pipeline as "Phase 0" - grounding in reality before thinking.

Authors: Ada & Luna
Date: December 29, 2025
Version: 4.0rc1
"""
# @ai-indexable: core-functionality
# @ai-purpose: Pre-consciousness tool detection and execution (Phase 0)
# @ai-dependencies: brain.specialists
# @ai-related: brain/qde_engine.py, brain/specialists/

import logging
import re
import asyncio
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class ToolPriority(Enum):
    """Tool execution priority levels"""
    IMMEDIATE = 1   # Always check (datetime, terminal)
    CONTEXTUAL = 2  # Check based on keywords (wiki, web_search)
    PASSIVE = 3     # Only if explicitly requested (vision, ocr)


@dataclass
class ToolMatch:
    """A detected tool that should be executed"""
    tool_name: str
    confidence: float
    params: Dict[str, Any] = field(default_factory=dict)
    priority: ToolPriority = ToolPriority.CONTEXTUAL


@dataclass 
class ToolResult:
    """Result from tool execution"""
    tool_name: str
    success: bool
    content: str
    error: Optional[str] = None
    execution_time_ms: float = 0.0


@dataclass
class GroundingContext:
    """Context gathered from Phase 0 tool grounding"""
    tool_results: List[ToolResult] = field(default_factory=list)
    total_time_ms: float = 0.0
    tools_attempted: int = 0
    tools_succeeded: int = 0
    
    def inject_into_prompt(self) -> str:
        """Format tool results for injection into LLM prompt"""
        if not self.tool_results:
            return ""
        
        sections = ["## Tool Results (Phase 0 Grounding)\n"]
        for result in self.tool_results:
            if result.success:
                sections.append(f"### {result.tool_name}\n{result.content}\n")
            else:
                sections.append(f"### {result.tool_name} (failed)\nError: {result.error}\n")
        
        return "\n".join(sections)
    
    @property
    def has_results(self) -> bool:
        return len(self.tool_results) > 0


# Tool detection patterns - maps patterns to (tool_name, confidence, param_extractor)
TOOL_PATTERNS: List[Tuple[re.Pattern, str, float, Optional[callable]]] = [
    # DateTime - high confidence for time questions
    (re.compile(r'\b(what time|current time|what\'?s the time|time is it|today\'?s date|what day)\b', re.I),
     'datetime', 0.95, None),
    
    # Terminal - for git, file operations
    (re.compile(r'\b(git (log|status|diff|show)|run command|execute|cat |ls |pwd)\b', re.I),
     'terminal', 0.7, lambda m: {'command': m.group(0)}),
    
    # Wiki lookup - encyclopedic questions
    (re.compile(r'\b(who is|what is|tell me about|wikipedia|look up)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', re.I),
     'wiki_lookup', 0.6, lambda m: {'page': m.group(2), 'wiki': 'wikipedia'}),
    
    # Web search - current events, news
    (re.compile(r'\b(search for|google|look up online|current news|latest|recent)\b', re.I),
     'web_search', 0.5, None),
    
    # Codebase - questions about Ada's own code
    (re.compile(r'\b(your (code|source|implementation)|how do you work|your codebase)\b', re.I),
     'codebase', 0.7, None),
    
    # Docs - questions about Ada's documentation
    (re.compile(r'\b(your docs|documentation|how to use|ada\'?s? guide)\b', re.I),
     'docs', 0.7, None),
]


class ToolGrounding:
    """
    Phase 0: Tool Grounding
    
    Detects and executes tools BEFORE consciousness processing.
    Results are injected into the prompt so the LLM has real data.
    """
    
    def __init__(self, confidence_threshold: float = 0.5):
        self.confidence_threshold = confidence_threshold
        self._specialists_cache: Dict[str, Any] = {}
    
    def detect_tools(self, message: str) -> List[ToolMatch]:
        """
        Detect which tools should be activated based on the user message.
        
        Args:
            message: User's input message
            
        Returns:
            List of ToolMatch objects for tools that should execute
        """
        matches = []
        
        for pattern, tool_name, confidence, param_extractor in TOOL_PATTERNS:
            match = pattern.search(message)
            if match and confidence >= self.confidence_threshold:
                params = param_extractor(match) if param_extractor else {}
                matches.append(ToolMatch(
                    tool_name=tool_name,
                    confidence=confidence,
                    params=params
                ))
        
        # Sort by confidence (highest first)
        matches.sort(key=lambda m: m.confidence, reverse=True)
        
        # Log detections
        if matches:
            logger.info(f"🛠️ Phase 0: Detected {len(matches)} tools: {[m.tool_name for m in matches]}")
        
        return matches
    
    async def execute_tool(self, match: ToolMatch, context: Dict[str, Any]) -> ToolResult:
        """
        Execute a single tool.
        
        Args:
            match: The tool match to execute
            context: Request context (message, conversation_id, etc.)
            
        Returns:
            ToolResult with execution outcome
        """
        import time
        start = time.time()
        
        try:
            # Lazy import to avoid circular deps
            from brain.specialists import get_specialist
            
            specialist = get_specialist(match.tool_name)
            if not specialist:
                return ToolResult(
                    tool_name=match.tool_name,
                    success=False,
                    content="",
                    error=f"Specialist '{match.tool_name}' not found"
                )
            
            # Merge params with context
            exec_context = {**context, **match.params}
            
            # Execute (handle both sync and async)
            import inspect
            if inspect.iscoroutinefunction(specialist.process):
                result = await specialist.process(**exec_context)
            else:
                result = specialist.process(**exec_context)
            
            execution_time = (time.time() - start) * 1000
            
            if result.success:
                logger.info(f"✅ Phase 0: {match.tool_name} executed ({execution_time:.1f}ms)")
                return ToolResult(
                    tool_name=match.tool_name,
                    success=True,
                    content=result.context_text,
                    execution_time_ms=execution_time
                )
            else:
                return ToolResult(
                    tool_name=match.tool_name,
                    success=False,
                    content="",
                    error=result.error or "Unknown error",
                    execution_time_ms=execution_time
                )
                
        except Exception as e:
            execution_time = (time.time() - start) * 1000
            logger.error(f"❌ Phase 0: {match.tool_name} failed: {e}")
            return ToolResult(
                tool_name=match.tool_name,
                success=False,
                content="",
                error=str(e),
                execution_time_ms=execution_time
            )
    
    async def ground(self, message: str, context: Dict[str, Any]) -> GroundingContext:
        """
        Execute Phase 0: Tool Grounding.
        
        Detects tools needed for the query and executes them in parallel.
        Results are returned in a GroundingContext for prompt injection.
        
        Args:
            message: User's input message
            context: Request context
            
        Returns:
            GroundingContext with all tool results
        """
        import time
        start = time.time()
        
        # Detect tools
        matches = self.detect_tools(message)
        
        if not matches:
            return GroundingContext()
        
        # Execute tools in parallel
        tasks = [self.execute_tool(match, context) for match in matches]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        tool_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Phase 0 tool exception: {result}")
            elif isinstance(result, ToolResult):
                tool_results.append(result)
        
        total_time = (time.time() - start) * 1000
        succeeded = sum(1 for r in tool_results if r.success)
        
        logger.info(f"🛠️ Phase 0 complete: {succeeded}/{len(tool_results)} tools succeeded ({total_time:.1f}ms)")
        
        return GroundingContext(
            tool_results=tool_results,
            total_time_ms=total_time,
            tools_attempted=len(tool_results),
            tools_succeeded=succeeded
        )


# Global instance for convenience
_tool_grounding: Optional[ToolGrounding] = None

def get_tool_grounding() -> ToolGrounding:
    """Get or create global ToolGrounding instance"""
    global _tool_grounding
    if _tool_grounding is None:
        _tool_grounding = ToolGrounding()
    return _tool_grounding
