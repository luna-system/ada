#!/usr/bin/env python3
"""
Contextual Malleability as Deployable Framework

Core Insight from v2.3.0 Research:
  Effect size 3.089: Context determines outcome effectiveness
  
Application to Routing:
  Don't ask "which is universally best?"
  Ask "which is best FOR THIS CONTEXT?"
  
This transforms routing from hardcoded decisions into context-driven logic.

Example:
  ❌ "Ada is slower, use Copilot" (universal, ignores context)
  ✅ "This task needs memory context Ada has, use Ada" (context-aware)
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Callable, Optional
from enum import Enum


class ExecutorRole(Enum):
    """Abstract role an executor can play"""
    MEMORY = "memory"          # Has loaded context/history
    FAST = "fast"              # Quick response
    CREATIVE = "creative"      # Novel solutions
    ANALYTICAL = "analytical"  # Logical reasoning
    CURRENT = "current"        # Fresh external knowledge
    SPECIALIZED = "specialized"  # Domain expertise


@dataclass
class ContextSignal:
    """A piece of context that affects routing decision"""
    name: str
    value: Any
    weight: float  # How much does this matter? (0.0-1.0)
    description: str
    
    def explain(self) -> str:
        return f"{self.name}: {self.value} (weight: {self.weight:.0%}) - {self.description}"


@dataclass
class ExecutorProfile:
    """What an executor is good at, in different contexts"""
    name: str
    roles: List[ExecutorRole]
    latency_ms: int
    cost_per_query: float
    
    def has_role(self, role: ExecutorRole) -> bool:
        return role in self.roles


class ContextualMalleabilityRouter:
    """
    Routes tasks to executors based on CONTEXT, not universal rules.
    
    Implements: "Same information, different context = very different effectiveness"
    From: v2.3.0 research, effect size 3.089
    
    Key insight: Don't hardcode routes. Score them contextually.
    """
    
    def __init__(self):
        self.executors: Dict[str, ExecutorProfile] = {}
        self.context_evaluators: Dict[str, Callable] = {}
    
    def register_executor(self, profile: ExecutorProfile):
        """Register an executor with its capabilities"""
        self.executors[profile.name] = profile
    
    def register_context_signal(self, signal_name: str, evaluator: Callable):
        """
        Register a way to evaluate a context signal
        
        Args:
            signal_name: Name of the signal (e.g., "needs_history")
            evaluator: Function(context_dict) -> float between 0.0-1.0
        """
        self.context_evaluators[signal_name] = evaluator
    
    def evaluate_context(self, query: str, context: Dict) -> List[ContextSignal]:
        """
        Extract context signals from the query and conversation context.
        
        This is where contextual malleability lives—evaluating what MATTERS
        for THIS specific query.
        """
        signals = []
        for signal_name, evaluator in self.context_evaluators.items():
            score = evaluator(query, context)
            if score > 0:  # Only include signals that are relevant
                signals.append(ContextSignal(
                    name=signal_name,
                    value=score,
                    weight=score,  # Can be tuned per signal
                    description=f"How important is {signal_name} for this query"
                ))
        return signals
    
    def score_executor(self, executor: ExecutorProfile, signals: List[ContextSignal]) -> float:
        """
        Score an executor for this specific context.
        
        This is the contextual malleability in action:
        Same executor, different contexts = different scores
        """
        score = 0.0
        
        for signal in signals:
            # Check if executor has roles needed for this signal
            if signal.name == "needs_memory":
                if ExecutorRole.MEMORY in executor.roles:
                    score += signal.weight * 0.3  # Memory capability matters
            
            elif signal.name == "needs_speed":
                if ExecutorRole.FAST in executor.roles:
                    score += signal.weight * 0.4  # Speed capability matters
            
            elif signal.name == "needs_reasoning":
                if ExecutorRole.ANALYTICAL in executor.roles:
                    score += signal.weight * 0.35  # Analytical capability matters
            
            elif signal.name == "needs_creativity":
                if ExecutorRole.CREATIVE in executor.roles:
                    score += signal.weight * 0.3  # Creative capability matters
            
            elif signal.name == "needs_current_info":
                if ExecutorRole.CURRENT in executor.roles:
                    score += signal.weight * 0.4  # Fresh knowledge matters
        
        # Apply cost penalty in high-cost contexts
        if any(s.name == "time_sensitive" and s.value > 0.8 for s in signals):
            # If time-sensitive, penalize expensive executors less
            pass  # Could reduce cost_penalty here
        else:
            # Otherwise, cost matters
            cost_factor = 1.0 - min(executor.cost_per_query * 10000, 1.0)  # Normalize cost
            score *= (1.0 + cost_factor)  # Cheaper executors score higher
        
        return score
    
    def route(self, query: str, context: Dict) -> tuple[str, float, List[ContextSignal]]:
        """
        Route based on context.
        
        Returns: (executor_name, confidence, signals_used)
        """
        signals = self.evaluate_context(query, context)
        
        scores = {}
        for executor_name, executor_profile in self.executors.items():
            score = self.score_executor(executor_profile, signals)
            scores[executor_name] = score
        
        if not scores:
            raise ValueError("No executors available")
        
        best_executor = max(scores, key=scores.get)
        confidence = min(scores[best_executor] / (sum(scores.values()) / len(scores)), 1.0)
        
        return best_executor, confidence, signals


def example_setup():
    """Example: Ada + Copilot routing with contextual malleability"""
    
    router = ContextualMalleabilityRouter()
    
    # Register executors
    ada = ExecutorProfile(
        name="ada",
        roles=[ExecutorRole.MEMORY, ExecutorRole.ANALYTICAL, ExecutorRole.SPECIALIZED],
        latency_ms=600,
        cost_per_query=0.0
    )
    
    copilot = ExecutorProfile(
        name="copilot",
        roles=[ExecutorRole.FAST, ExecutorRole.CREATIVE, ExecutorRole.CURRENT],
        latency_ms=50,
        cost_per_query=0.0003
    )
    
    router.register_executor(ada)
    router.register_executor(copilot)
    
    # Register context signal evaluators
    def needs_memory(query: str, context: Dict) -> float:
        """How much does this query need loaded memory/history?"""
        memory_keywords = ["remember", "earlier", "last time", "what did", "you said"]
        if any(kw in query.lower() for kw in memory_keywords):
            return 0.9
        elif len(context.get("history", [])) > 5:  # Rich history available
            return 0.6
        return 0.0
    
    def needs_speed(query: str, context: Dict) -> float:
        """How urgent is this query?"""
        speed_keywords = ["urgent", "asap", "now", "quick", "immediately"]
        if any(kw in query.lower() for kw in speed_keywords):
            return 0.95
        elif len(query) < 20:  # Short queries often need quick answer
            return 0.3
        return 0.0
    
    def needs_reasoning(query: str, context: Dict) -> float:
        """Does this need careful analysis?"""
        reasoning_keywords = ["why", "should", "analyze", "think about", "pros and cons"]
        if any(kw in query.lower() for kw in reasoning_keywords):
            return 0.85
        return 0.0
    
    def needs_current_info(query: str, context: Dict) -> float:
        """Does this need fresh external knowledge?"""
        current_keywords = ["today", "now", "current", "latest", "recent", "tomorrow"]
        if any(kw in query.lower() for kw in current_keywords):
            return 0.8
        return 0.0
    
    router.register_context_signal("needs_memory", needs_memory)
    router.register_context_signal("needs_speed", needs_speed)
    router.register_context_signal("needs_reasoning", needs_reasoning)
    router.register_context_signal("needs_current_info", needs_current_info)
    
    return router


def test_contextual_routing():
    """Demonstrate contextual malleability in routing"""
    
    router = example_setup()
    
    test_cases = [
        ("What did we decide about authentication?", {"history": ["auth discussion"]}),
        ("Fix this typo immediately", {"history": []}),
        ("Should we use async/await here?", {"history": ["performance discussion"]}),
        ("What's the latest on quantum computing?", {"history": []}),
    ]
    
    print("=" * 80)
    print("CONTEXTUAL MALLEABILITY IN ROUTING - DEPLOYMENT DEMO")
    print("=" * 80)
    
    for query, context in test_cases:
        executor, confidence, signals = router.route(query, context)
        
        print(f"\n📨 Query: {query}")
        print(f"  Context: {context}")
        print(f"\n  ✅ Route to: {executor.upper()} (confidence: {confidence:.0%})")
        print(f"\n  Context Signals Evaluated:")
        for signal in signals:
            print(f"    • {signal.explain()}")
    
    print("\n" + "=" * 80)
    print("KEY INSIGHT: CONTEXTUAL MALLEABILITY IN ACTION")
    print("=" * 80)
    print("""
Same executor (Ada), different contexts = different scores

Example:
  Query 1: "What did we decide..."
    → Needs memory? HIGH (0.9)
    → Ada scores HIGH
    
  Query 2: "Fix this typo immediately"
    → Needs speed? HIGH (0.95)
    → Ada scores LOW
    → Copilot wins

SAME EXECUTOR, DIFFERENT DECISION based on CONTEXT.

This is contextual malleability deployed:
  • v2.3.0 research showed context effect size 3.089
  • This router implements that: context drives execution
  • Not "Ada is always better" or "Copilot is always better"
  • Instead: "For THIS context, THIS executor is better"
""")


if __name__ == "__main__":
    test_contextual_routing()
