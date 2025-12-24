"""State tracking for recursive reasoning loops.

Tracks where Ada is in the reasoning process: which phase, what tools have been
called, how close to convergence, and the semantic identity being preserved.

This is Ada's "working memory" during recursive reasoning.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime


class ReasoningPhase(Enum):
    """Phases of recursive reasoning.
    
    Reasoning follows a natural progression:
    - UNDERSTANDING: Gathering information about the problem
    - PLANNING: Figuring out what to do
    - IMPLEMENTING: Making changes or providing solution
    - VERIFYING: Checking the work
    """
    UNDERSTANDING = "understanding"
    PLANNING = "planning"
    IMPLEMENTING = "implementing"
    VERIFYING = "verifying"


@dataclass
class ToolCall:
    """Record of a tool invocation during reasoning."""
    tool_name: str
    params: Dict[str, Any]
    result: Optional[Any] = None
    importance: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time_ms: float = 0.0
    
    # Tool transparency fields (Phase 3 - Tool Transparency)
    cache_hit: bool = False
    detail_level: Optional[str] = None  # "full", "chunks", "summary", "dropped"
    signals: Optional[Dict[str, float]] = None  # {"surprise": 0.8, "relevance": 0.6, ...}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "tool_name": self.tool_name,
            "params": self.params,
            "result": str(self.result) if self.result else None,
            "importance": self.importance,
            "timestamp": self.timestamp.isoformat(),
            "execution_time_ms": self.execution_time_ms,
            # Include transparency fields
            "cache_hit": self.cache_hit,
            "detail_level": self.detail_level,
            "signals": self.signals or {},
        }


@dataclass
class ReasoningState:
    """Tracks Ada's state during recursive reasoning.
    
    This is the "mind" of Ada as she thinks through a problem:
    - Where is she in the process? (phase)
    - What has she learned? (tools_called)
    - How much context is she using? (context_size)
    - How close to a solution? (convergence_score)
    - What's the core identity? (semantic_identity)
    
    Example:
        state = ReasoningState(
            user_request="Refactor auth to JWT",
            phase=ReasoningPhase.UNDERSTANDING
        )
        
        # After first tool call
        state.add_tool_call(ToolCall(
            tool_name="ada_search",
            params={"query": "authentication"},
            result=["auth.ts", "middleware/auth.js"],
            importance=0.85
        ))
        
        # Check convergence
        if state.should_continue():
            # Keep reasoning
            ...
    """
    
    # Core tracking
    user_request: str
    phase: ReasoningPhase = ReasoningPhase.UNDERSTANDING
    iteration: int = 0
    max_iterations: int = 10
    
    # Tool tracking
    tools_called: List[ToolCall] = field(default_factory=list)
    
    # Context management
    context_size: int = 0  # Current token count
    context_budget: int = 28000  # Max tokens for dynamic context (23.5k + buffer)
    importance_threshold: float = 0.50  # Minimum importance to include in context
    
    # Convergence tracking
    convergence_score: float = 0.0  # 0-1, how close to solution
    has_solution: bool = False
    reasoning_history: List[str] = field(default_factory=list)  # LLM thoughts
    
    # Panic switch - Ada can bail early on critical errors
    error_bailout: bool = False
    error_bailout_reason: str = ""
    
    # Semantic identity (for quantum isomorphism)
    semantic_identity: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.now)
    last_update: datetime = field(default_factory=datetime.now)
    
    def add_tool_call(self, tool_call: ToolCall) -> None:
        """Record a tool invocation."""
        self.tools_called.append(tool_call)
        self.iteration += 1
        self.last_update = datetime.now()
    
    def add_thought(self, thought: str) -> None:
        """Record an LLM reasoning step."""
        self.reasoning_history.append(thought)
        self.last_update = datetime.now()
    
    def update_convergence(self, score: float) -> None:
        """Update how close we are to a solution (0-1)."""
        self.convergence_score = score
        if score >= 0.95:
            self.has_solution = True
        self.last_update = datetime.now()
    
    def should_continue(self) -> bool:
        """Should we continue reasoning or stop?"""
        # Stop if we have a solution
        if self.has_solution:
            return False
        
        # Stop if we hit max iterations
        if self.iteration >= self.max_iterations:
            return False
        
        # Stop if panic switch activated (error bailout)
        if self.error_bailout:
            return False
        
        # Continue otherwise
        return True
    
    def is_looping(self) -> bool:
        """Detect if we're stuck in a reasoning loop.
        
        Heuristic: If we've called the same tool with similar params
        multiple times recently, we're probably looping.
        """
        if len(self.tools_called) < 3:
            return False
        
        # Check last 3 tool calls
        recent_calls = self.tools_called[-3:]
        tool_names = [call.tool_name for call in recent_calls]
        
        # All same tool?
        if len(set(tool_names)) == 1:
            # Probably looping
            return True
        
        return False
    
    def advance_phase(self) -> None:
        """Move to next reasoning phase."""
        phases = list(ReasoningPhase)
        current_idx = phases.index(self.phase)
        
        if current_idx < len(phases) - 1:
            self.phase = phases[current_idx + 1]
            self.last_update = datetime.now()
    
    def elapsed_time_ms(self) -> float:
        """How long has this reasoning loop been running?"""
        delta = datetime.now() - self.started_at
        return delta.total_seconds() * 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict for API responses."""
        return {
            "user_request": self.user_request,
            "phase": self.phase.value,
            "iteration": self.iteration,
            "max_iterations": self.max_iterations,
            "tools_called": [call.to_dict() for call in self.tools_called],
            "context_size": self.context_size,
            "context_budget": self.context_budget,
            "importance_threshold": self.importance_threshold,
            "convergence_score": self.convergence_score,
            "has_solution": self.has_solution,
            "elapsed_time_ms": self.elapsed_time_ms(),
            "is_looping": self.is_looping(),
        }
