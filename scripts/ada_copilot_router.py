#!/usr/bin/env python3
"""
Ada vs Copilot Task Router - Token Economics

Determines whether to route a task to Ada (free, slower) or Copilot (paid, faster)
based on estimated efficiency and token cost.

Philosophy:
- Ada is great at reasoning, memory lookup, context assembly
- Copilot is fast for quick fixes, explanations, one-shots
- Route based on task characteristics, not speed alone

The key insight: Copilot tokens cost money. Ada compute is "free" (local hardware).
If Ada can solve it adequately in <2 seconds, the economics favor Ada.
"""

import json
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class TaskComplexity(Enum):
    """Task complexity classification"""
    TRIVIAL = "trivial"        # "Hi!", "What's the weather?" - Ada wins (fast)
    SIMPLE = "simple"          # Factual lookup, definition - Ada wins (memory)
    MODERATE = "moderate"      # Needs code understanding - Copilot might win
    COMPLEX = "complex"        # Deep analysis - Copilot wins (fresh knowledge)
    REASONING = "reasoning"    # "Why?" questions - Ada wins (time-aware thinking)


class TaskCategory(Enum):
    """Task categories for routing logic"""
    MEMORY_LOOKUP = "memory_lookup"        # "What did we discuss?"
    PERSONA_QUERY = "persona_query"         # "What's my philosophy?"
    CODE_RETRIEVAL = "code_retrieval"       # "Show me function X"
    QUICK_FIX = "quick_fix"                 # "Fix this typo"
    EXPLANATION = "explanation"             # "Explain X"
    DEEP_ANALYSIS = "deep_analysis"         # "Why is this happening?"
    CREATIVE = "creative"                   # "Write me a poem"
    REASONING = "reasoning"                 # "Should we do X?"


@dataclass
class TaskProfile:
    """Characteristics of a task"""
    prompt: str
    category: TaskCategory
    complexity: TaskComplexity
    requires_fresh_context: bool  # Does task need current knowledge?
    uses_history: bool            # Does task benefit from conversation history?
    quality_critical: bool        # Is answer correctness critical?
    time_sensitive: bool          # Does user need immediate response?


@dataclass
class RoutingDecision:
    """Route decision with reasoning"""
    executor: str              # "ada" or "copilot"
    confidence: float          # 0.0-1.0
    estimated_latency_ms: int
    estimated_token_cost: float
    reasoning: str
    fallback: str             # If primary fails, try this


class TaskRouter:
    """Route tasks to Ada or Copilot based on efficiency"""
    
    # Task routing table: category → executor preferences
    ROUTING_TABLE = {
        TaskCategory.MEMORY_LOOKUP: ("ada", "copilot"),      # Ada's strength
        TaskCategory.PERSONA_QUERY: ("ada", "copilot"),      # Ada has loaded persona
        TaskCategory.CODE_RETRIEVAL: ("ada", "copilot"),     # Ada can search codebase
        TaskCategory.QUICK_FIX: ("copilot", "ada"),          # Copilot is faster
        TaskCategory.EXPLANATION: ("copilot", "ada"),        # Copilot has broad knowledge
        TaskCategory.DEEP_ANALYSIS: ("copilot", "ada"),      # Needs fresh context usually
        TaskCategory.CREATIVE: ("copilot", "ada"),           # Copilot's expertise
        TaskCategory.REASONING: ("ada", "copilot"),          # Ada can take time to think
    }
    
    # Latency characteristics (milliseconds)
    LATENCY = {
        "ada": {"ttft": 220, "per_token": 110},      # 220ms to first token, ~110ms per token after
        "copilot": {"ttft": 50, "per_token": 20},    # Copilot is much faster (estimated)
    }
    
    # Token cost (in cents per 1M tokens, typical Claude pricing)
    TOKEN_COST = {
        "copilot": 0.003,  # ~$3 per 1M tokens (rough estimate)
        "ada": 0.0,        # Local hardware, "free" but electricity is real cost
    }
    
    @staticmethod
    def classify_task(prompt: str) -> TaskProfile:
        """Classify a task based on its characteristics"""
        
        # Simple heuristics for classification
        prompt_lower = prompt.lower()
        
        # Determine category
        if any(x in prompt_lower for x in ["remember", "what did", "earlier", "last time", "you said"]):
            category = TaskCategory.MEMORY_LOOKUP
        elif any(x in prompt_lower for x in ["persona", "about you", "your philosophy", "your thoughts"]):
            category = TaskCategory.PERSONA_QUERY
        elif any(x in prompt_lower for x in ["show me", "find the", "where is", "function", "class", "def"]):
            category = TaskCategory.CODE_RETRIEVAL
        elif any(x in prompt_lower for x in ["fix", "typo", "error", "bug", "wrong"]):
            category = TaskCategory.QUICK_FIX
        elif any(x in prompt_lower for x in ["explain", "what is", "how does", "tell me about"]):
            category = TaskCategory.EXPLANATION
        elif any(x in prompt_lower for x in ["why", "analyze", "deep", "understand", "root cause"]):
            category = TaskCategory.DEEP_ANALYSIS
        elif any(x in prompt_lower for x in ["write", "poem", "story", "creative", "imagine"]):
            category = TaskCategory.CREATIVE
        elif any(x in prompt_lower for x in ["should we", "should i", "pros and cons", "think about"]):
            category = TaskCategory.REASONING
        else:
            category = TaskCategory.EXPLANATION  # Default
        
        # Determine complexity
        tokens_in_prompt = len(prompt.split())
        if tokens_in_prompt < 3:
            complexity = TaskComplexity.TRIVIAL
        elif tokens_in_prompt < 10:
            complexity = TaskComplexity.SIMPLE
        elif tokens_in_prompt < 30:
            complexity = TaskComplexity.MODERATE
        elif tokens_in_prompt < 100:
            complexity = TaskComplexity.COMPLEX
        else:
            complexity = TaskComplexity.REASONING
        
        # Determine characteristics
        requires_fresh = any(x in prompt_lower for x in ["today", "now", "current", "latest", "recent", "tomorrow"])
        uses_history = any(x in prompt_lower for x in ["earlier", "before", "last", "previous", "we discussed"])
        quality_critical = any(x in prompt_lower for x in ["important", "critical", "security", "production"])
        time_sensitive = any(x in prompt_lower for x in ["urgent", "asap", "quick", "now", "immediately"])
        
        return TaskProfile(
            prompt=prompt,
            category=category,
            complexity=complexity,
            requires_fresh_context=requires_fresh,
            uses_history=uses_history,
            quality_critical=quality_critical,
            time_sensitive=time_sensitive,
        )
    
    @staticmethod
    def estimate_tokens(prompt: str, category: TaskCategory) -> int:
        """Estimate response token count based on category"""
        # Rough heuristics
        base_tokens = len(prompt.split()) // 2  # Responses are roughly half prompt length
        
        category_multipliers = {
            TaskCategory.MEMORY_LOOKUP: 1.0,      # Short response
            TaskCategory.PERSONA_QUERY: 1.5,      # Moderate
            TaskCategory.CODE_RETRIEVAL: 2.0,     # Code is verbose
            TaskCategory.QUICK_FIX: 0.5,          # Very short
            TaskCategory.EXPLANATION: 2.5,        # Detailed
            TaskCategory.DEEP_ANALYSIS: 3.0,      # Very detailed
            TaskCategory.CREATIVE: 2.0,           # Variable
            TaskCategory.REASONING: 2.5,          # Thoughtful
        }
        
        return int(base_tokens * category_multipliers.get(category, 1.5))
    
    @classmethod
    def route(cls, prompt: str) -> RoutingDecision:
        """Make routing decision for a task"""
        
        profile = cls.classify_task(prompt)
        primary, fallback = cls.ROUTING_TABLE[profile.category]
        
        # Calculate metrics for primary executor
        est_tokens = cls.estimate_tokens(prompt, profile.category)
        latency = cls.LATENCY[primary]["ttft"] + (est_tokens * cls.LATENCY[primary]["per_token"])
        token_cost = est_tokens * (cls.TOKEN_COST[primary] / 1_000_000) * 100  # Convert to cents
        
        # Decision logic
        confidence = 0.9
        reasoning = f"Routing to {primary} - {profile.category.value} task"
        
        # Override for time-sensitive tasks
        if profile.time_sensitive and primary == "ada":
            primary, fallback = fallback, primary
            confidence = 0.7
            reasoning = f"Time-sensitive: prioritizing speed over efficiency"
        
        # Override if quality is critical
        if profile.quality_critical and primary == "ada":
            # Keep Ada but with lower confidence
            reasoning = f"Quality-critical: keeping {primary} but with reduced confidence"
            confidence = 0.6
        
        # Economics check: Is Ada's latency justified by token savings?
        if primary == "ada" and latency > 2000:  # Over 2 seconds
            # Check if Copilot would be significantly cheaper despite speed
            copilot_cost = est_tokens * (cls.TOKEN_COST["copilot"] / 1_000_000) * 100
            if copilot_cost > 0.01 and latency > 3000:  # If Copilot would cost money + wait is long
                primary, fallback = fallback, primary
                confidence = 0.5
                reasoning = f"Latency too high ({latency:.0f}ms) and cost savings marginal"
        
        return RoutingDecision(
            executor=primary,
            confidence=confidence,
            estimated_latency_ms=int(latency),
            estimated_token_cost=token_cost,
            reasoning=reasoning,
            fallback=fallback,
        )


def main():
    """Demonstrate routing logic"""
    
    test_prompts = [
        "Hi!",
        "What's your philosophy about privacy?",
        "Show me the retrieve_turns function",
        "Fix this typo: 'recieve' should be 'receive'",
        "Explain machine learning",
        "Why is the performance degrading?",
        "Write me a poem about code",
        "Should we switch to Rust?",
        "What did we discuss about the codebase specialist?",
        "I need a critical security fix ASAP",
    ]
    
    print("=" * 80)
    print("ADA ↔ COPILOT TASK ROUTER - TOKEN ECONOMICS")
    print("=" * 80)
    
    for prompt in test_prompts:
        decision = TaskRouter.route(prompt)
        
        print(f"\nPrompt: {prompt[:50]}...")
        print(f"  → Route to: {decision.executor.upper()}")
        print(f"  Confidence: {decision.confidence:.0%}")
        print(f"  Estimated latency: {decision.estimated_latency_ms}ms")
        print(f"  Token cost: ${decision.estimated_token_cost:.4f}")
        print(f"  Reasoning: {decision.reasoning}")
        print(f"  Fallback: {decision.fallback}")
    
    print("\n" + "=" * 80)
    print("ECONOMICS SUMMARY")
    print("=" * 80)
    
    ada_total_tokens = 0
    copilot_total_tokens = 0
    total_cost = 0
    
    for prompt in test_prompts:
        decision = TaskRouter.route(prompt)
        est_tokens = TaskRouter.estimate_tokens(prompt, TaskRouter.classify_task(prompt).category)
        
        if decision.executor == "ada":
            ada_total_tokens += est_tokens
        else:
            copilot_total_tokens += est_tokens
            total_cost += decision.estimated_token_cost
    
    print(f"Ada tokens handled: {ada_total_tokens}")
    print(f"Copilot tokens handled: {copilot_total_tokens}")
    print(f"Total Copilot cost: ${total_cost:.4f}")
    print(f"Tokens saved to local compute: {ada_total_tokens}")
    print(f"Efficiency: {ada_total_tokens / (ada_total_tokens + copilot_total_tokens):.0%} of work done locally (free)")


if __name__ == "__main__":
    main()
