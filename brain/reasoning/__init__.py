"""Recursive reasoning system for Ada.

This module implements the core recursive reasoning loop that enables Ada
to think through problems by calling tools, processing results, and reasoning
iteratively until convergence.

Key components:
- ReasoningState: Tracks reasoning progress and context
- LoopController: Orchestrates the reasoning loop
- SIFEncoder: Semantic compression of context
- ImportanceScorer: Biomimetic importance weighting
- ConvergenceDetector: Knows when LLM has reached a solution
"""

from brain.reasoning.state_tracker import ReasoningState, ReasoningPhase
from brain.reasoning.loop_controller import ReasoningLoopController
from brain.reasoning.tool_parser import ToolRequestParser, ToolRequest

__all__ = [
    "ReasoningState",
    "ReasoningPhase",
    "ReasoningLoopController",
    "ToolRequestParser",
    "ToolRequest",
]
