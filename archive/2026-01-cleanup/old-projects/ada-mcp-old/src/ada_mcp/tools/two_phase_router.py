"""
Two-Phase Router - Intelligent Query Routing

Phase 1: Determine if tool is needed
  - Tool-only queries: execute tool, return result
  - Tool + reasoning: execute tool, then feed to LLM
  - Chat-only: no tool needed

Phase 2: If needed, invoke LLM with tool metadata in context

This enables:
✅ Fast responses for simple queries (no LLM needed)
✅ Reasoned responses for complex queries (tool + LLM)
✅ Pure chat when no tools needed
✅ Metadata-informed LLM decisions
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple, Any
import re


class QueryIntent(Enum):
    """Detected intent of the query."""
    
    TOOL_ONLY = "tool_only"           # "introspect"
    TOOL_AND_REASONING = "tool_and_reasoning"  # "introspect and suggest"
    CHAT_ONLY = "chat_only"           # "tell me a story"


# Patterns that indicate tool + reasoning needed
REASONING_PATTERNS = [
    r"and\s+(suggest|recommend|find|identify|propose)",  # "and suggest"
    r"and\s+(explain|describe|analyze|evaluate)",        # "and explain"
    r"then\s+(do|make|create)",                           # "then create"
    r"(help me|show me|tell me).*?(by|using|with)",      # "help me by using"
    r"what.*?(would|should|can)\s+you.*?do",            # "what could you do with"
]

# Patterns that indicate a tool is involved
TOOL_PATTERNS = [
    r"\b(introspect|analyze|find|search|check|examine)",
    r"\b(read|look at|see|check).*?(file|architecture|doc|context)",
    r"\b(your|the)\s+(architecture|context|memory|tools|files)",
    r"what\s+(file|doc|memory).*?(do|are)",
    r"show.*?(file|memory|context)",
    r"context\.md|codebase-map|files\s+do\s+you",
]

# Patterns that are pure chat (no tools)
CHAT_PATTERNS = [
    r"^(tell|story|joke|imagine|create|write|compose)\b",  # Start with these
    r"\b(hello|hi|hey|goodbye|thanks|how are you)\b",
    r"^how are you",
    r"^what.*?think.*?(about|of)",
    r"^opinion.*?(on|about)",
]


def should_use_tool(query: str) -> bool:
    """Determine if query should invoke a tool."""
    query_lower = query.lower().strip()
    
    # Check chat patterns first (highest confidence)
    for pattern in CHAT_PATTERNS:
        if re.search(pattern, query_lower):
            return False
    
    # Check tool patterns
    for pattern in TOOL_PATTERNS:
        if re.search(pattern, query_lower):
            return True
    
    # Default: no tool needed
    return False


def extract_tool_request(query: str) -> Tuple[str, Optional[str]]:
    """
    Extract tool name and optional reasoning request.
    
    Returns:
        Tuple of (tool_name, reasoning_prompt)
    """
    query_lower = query.lower()
    
    # Detect tool type (prioritize by specificity)
    if "introspect" in query_lower:
        tool = "introspection"
    elif "analyze" in query_lower or "evaluate" in query_lower:
        tool = "analysis"
    elif "search" in query_lower or "find" in query_lower:
        tool = "search"
    else:
        tool = "general"
    
    # Extract reasoning request
    reasoning = None
    
    # Pattern: "tool and/then [reasoning]"
    match = re.search(r"(?:and|then)\s+(.+?)(?:\?|$)", query_lower)
    if match:
        reasoning = match.group(1).strip()
    
    # Pattern: "tool [reason by/for/using] [phrase]"
    match = re.search(r"(?:to|for|by)\s+(.+?)(?:\?|$)", query_lower)
    if match and reasoning is None:
        reasoning = match.group(1).strip()
    
    return tool, reasoning


@dataclass
class RouterDecision:
    """Decision made by the router."""
    
    phase: str                    # "tool_only", "tool_and_reasoning", "chat_only"
    needs_tool: bool             # Should invoke tool?
    needs_llm: bool              # Should invoke LLM?
    tool_name: Optional[str]     # Which tool to invoke
    reasoning_prompt: Optional[str]  # Additional context for LLM


class TwoPhaseRouter:
    """Route queries through one or two phases."""
    
    def classify_query(self, query: str) -> str:
        """
        Classify query intent.
        
        Returns:
            "tool_only", "tool_and_reasoning", or "chat_only"
        """
        query_lower = query.lower()
        
        # Does it need a tool?
        if not should_use_tool(query):
            return "chat_only"
        
        # Does it need reasoning on top of tool result?
        for pattern in REASONING_PATTERNS:
            if re.search(pattern, query_lower):
                return "tool_and_reasoning"
        
        # Just tool, no reasoning
        return "tool_only"
    
    def should_invoke_tool(self, query_or_phase: str) -> bool:
        """Should we invoke a tool?"""
        if query_or_phase in ("tool_only", "tool_and_reasoning"):
            return True
        return should_use_tool(query_or_phase)
    
    def should_invoke_llm(self, query_or_phase: str) -> bool:
        """Should we invoke the LLM?"""
        # Tool-only doesn't need LLM (just return tool result)
        if query_or_phase == "tool_only":
            return False
        
        # Chat-only and tool-and-reasoning use LLM
        if query_or_phase in ("chat_only", "tool_and_reasoning"):
            return True
        
        # For raw query strings, check if it needs reasoning
        if should_use_tool(query_or_phase):
            phase = self.classify_query(query_or_phase)
            return phase != "tool_only"
        
        return True
    
    def should_inject_metadata_to_llm(self, metadata: dict, query: str) -> bool:
        """
        Should we inject tool metadata into LLM context?
        
        Yes if:
        - Query has reasoning keywords
        - Metadata contains relevant info
        """
        query_lower = query.lower()
        
        # Check for reasoning keywords or follow-up requests
        reasoning_keywords = [
            "suggest", "recommend", "explain", "analyze", "evaluate",
            "find", "identify", "propose", "what would", "how could",
            "highest", "easiest", "best", "improve"
        ]
        
        for keyword in reasoning_keywords:
            if keyword in query_lower:
                return True
        
        # Also check the regex patterns
        for pattern in REASONING_PATTERNS:
            if re.search(pattern, query_lower):
                return True
        
        return False
    
    def format_metadata_for_llm(self, metadata: dict, query: str) -> str:
        """Format metadata as context for LLM prompt."""
        files = metadata.get("filesAccessed", [])
        actions = metadata.get("actionsTaken", [])
        duration = metadata.get("durationMs", 0)
        
        context = f"""
Tool Execution Context:
- Tool: {metadata.get('toolName', 'unknown')}
- Files Accessed: {', '.join(files) if files else 'none'}
- Actions Performed: {len(actions)} actions
- Execution Time: {duration}ms

User Query: {query}

Please use the above context to provide a thoughtful response.
"""
        return context.strip()
    
    def make_decision(self, query: str) -> RouterDecision:
        """
        Make complete routing decision for a query.
        
        Returns:
            RouterDecision with phase, needs_tool, needs_llm, etc.
        """
        phase = self.classify_query(query)
        tool_name, reasoning = extract_tool_request(query)
        
        return RouterDecision(
            phase=phase,
            needs_tool=self.should_invoke_tool(phase),
            needs_llm=self.should_invoke_llm(phase),
            tool_name=tool_name if self.should_invoke_tool(phase) else None,
            reasoning_prompt=reasoning,
        )
