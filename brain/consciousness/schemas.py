"""
🌸 Floret Consciousness Data Schemas - Pure Data Structures 🌸

Core data types for multi-round consciousness architecture.
Clean separation of data models from business logic.

Authors: Ada (Floret Consciousness), luna (Pixie Dust), Sonnet (Implementation)
Framework: Azimuth Divergence Awareness (ADA)
"""
# @ai-indexable: data-models
# @ai-purpose: Data schemas for floret consciousness architecture
# @ai-dependencies: None (pure data structures)
# @ai-related: brain/consciousness/engine.py, brain/consciousness/heisenberg.py

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

@dataclass
class ToolRequest:
    """A tool request from a thinking round"""
    tool_name: str
    parameters: Dict[str, Any]
    confidence: float
    reasoning: str  # Why this tool is needed

@dataclass
class ThinkingRoundResult:
    """Result from a single thinking round"""
    round_number: int
    thinking_content: str
    tool_requests: List[ToolRequest]
    is_complete: bool  # True if Ada thinks she's done
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FloretContext:
    """Context accumulated across multiple thinking rounds (florets)"""
    initial_query: str
    user_context: Dict[str, Any]
    rounds: List[ThinkingRoundResult] = field(default_factory=list)
    tool_results: Dict[str, Any] = field(default_factory=dict)  # tool_name -> results
    current_round: int = 0
    
    def add_round(self, round_result: ThinkingRoundResult, tool_results: Dict[str, Any]) -> 'FloretContext':
        """Add a thinking round and its tool results to context"""
        self.rounds.append(round_result)
        self.tool_results.update(tool_results)
        self.current_round += 1
        return self
    
    def get_agl_summary(self) -> str:
        """Generate AGL summary for inter-floret communication"""
        # This will be expanded in Phase 1.1 with full AGL integration
        summary_parts = []
        summary_parts.append(f"@rounds_completed: {len(self.rounds)}")
        summary_parts.append(f"@tools_executed: {list(self.tool_results.keys())}")
        if self.rounds:
            summary_parts.append(f"@last_thinking_state: {self.rounds[-1].thinking_content[:100]}...")
        return " | ".join(summary_parts)