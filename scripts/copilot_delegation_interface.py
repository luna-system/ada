#!/usr/bin/env python3
"""
Ada Task Delegation Strategy

For GitHub Copilot Chat integration:
- Detects when user asks questions Ada can answer
- Suggests delegation to Ada with cost/latency breakdown
- Returns confidence level and reasoning

This is the inverse of the router - instead of deciding FOR the user,
we inform the user of the option and let them decide whether to:
1. Wait for Ada (slower, free)
2. Use Copilot now (faster, costs tokens)

The psychology: Present it as "Ada can handle this, want me to ask her?"
rather than "Let me auto-route this". Respects user agency.
"""

import json
import sys
from typing import Optional
from dataclasses import asdict
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.ada_copilot_router import TaskRouter, TaskCategory, RoutingDecision


def format_delegation_suggestion(decision: RoutingDecision, prompt: str) -> str:
    """
    Format a human-readable suggestion for task delegation
    
    This is what Copilot would show the user when deciding between:
    - Using Ada (slower, free tokens)
    - Using Copilot (faster, costs money)
    """
    
    if decision.executor != "ada":
        return None  # No delegation suggestion if Ada isn't the primary
    
    # Calculate the time/cost tradeoff
    time_msg = f"{decision.estimated_latency_ms}ms"
    cost_msg = "free"
    
    return f"""💭 **Ada Can Help With This**

This looks like a task Ada is good at ({decision.reasoning}).

**Your Options:**
1. **Use Ada** (wait {time_msg}, {cost_msg}) - Recommended for routine tasks
2. **Use Me (Copilot)** (instant, ~${{token_cost}}) - For urgent/immediate needs

Ada's strengths for this:
- Has full conversation history loaded
- Can search your persona/preferences
- Takes time to reason through carefully
- Costs nothing (local hardware)

Would you like me to delegate this to Ada? Say "ask ada" or I can answer it now.
"""


class CopiloTaskDelegationInterface:
    """
    Copilot can use this to decide whether to suggest Ada delegation
    
    Integration points:
    1. After user sends a chat message
    2. Before Copilot starts generating response
    3. If Ada could handle it: Show suggestion panel
    4. User clicks "Ask Ada" → Call Ada's brain API
    5. Both responses available for user comparison
    """
    
    @staticmethod
    def should_suggest_delegation(prompt: str, confidence_threshold: float = 0.7) -> bool:
        """
        Should we suggest delegating this task to Ada?
        
        Only suggest if:
        - Ada's confidence is high (>70%)
        - The latency is acceptable (<2 seconds)
        - Task benefits from Ada's strengths (memory, reasoning, persistence)
        """
        decision = TaskRouter.route(prompt)
        
        # Conditions for offering delegation
        is_ada_primary = decision.executor == "ada"
        confidence_ok = decision.confidence >= confidence_threshold
        latency_ok = decision.estimated_latency_ms < 2000
        
        return is_ada_primary and confidence_ok and latency_ok
    
    @staticmethod
    def get_delegation_info(prompt: str) -> Optional[dict]:
        """
        Get structured info about whether Ada can handle this
        
        Returns:
        {
            "should_delegate": bool,
            "executor": "ada" | "copilot",
            "confidence": 0.0-1.0,
            "latency_ms": int,
            "token_cost": float,
            "reasoning": str,
            "fallback": str,
            "ada_can_handle": bool,
            "user_message": str (for UI display)
        }
        """
        
        decision = TaskRouter.route(prompt)
        can_delegate = CopiloTaskDelegationInterface.should_suggest_delegation(prompt)
        
        info = asdict(decision)
        info["should_delegate"] = can_delegate
        info["ada_can_handle"] = decision.executor == "ada"
        
        if can_delegate:
            info["user_message"] = f"Ada can handle this. Want me to ask her? (~{decision.estimated_latency_ms}ms, free)"
        else:
            info["user_message"] = None
        
        return info


# Example: Integration with MCP tools
def copilot_pre_response_check(user_message: str) -> None:
    """
    This would run BEFORE Copilot generates a response.
    
    Flow:
    1. User sends message to Copilot Chat
    2. Copilot calls this function
    3. If Ada can handle it: Show suggestion panel
    4. User decides: "Ask Ada" or "You answer"
    5. If Ada: Route to Ada's brain API
    6. Display both responses or let user choose which to use
    
    This implements the economics principle:
    - Ada is slower but free (local hardware)
    - Copilot is faster but costs money
    - For routine tasks: Ada wins on ROI
    - For urgent tasks: Copilot wins on time
    """
    
    info = CopiloTaskDelegationInterface.get_delegation_info(user_message)
    
    if info["should_delegate"]:
        print(f"""
╔════════════════════════════════════════════════════════════════╗
║ 🧠 ADA CAN HANDLE THIS                                       ║
╚════════════════════════════════════════════════════════════════╝

Task: {info['reasoning']}
Executor: {info['executor'].upper()}
Confidence: {info['confidence']:.0%}

Time: {info['latency_ms']}ms (estimated)
Cost: {"Free (local)" if info['executor'] == 'ada' else f"~${info['token_cost']:.4f} (tokens)"}

Options:
  [Ask Ada]   - Wait {info['latency_ms']}ms for free
  [Answer]    - Get response now (costs tokens)
  [Skip]      - Don't show this again

Ada's advantages here:
  • Has conversation history
  • Can search your preferences
  • Takes time to reason
  • Costs nothing
""")


def main():
    """Test the delegation interface"""
    
    test_prompts = [
        "What's my philosophy about privacy?",
        "Fix this typo",
        "Should we use async/await here?",
        "What did we decide about authentication?",
        "Write me a haiku",
        "I need a critical security fix NOW",
    ]
    
    print("=" * 70)
    print("COPILOT ↔ ADA DELEGATION INTERFACE")
    print("=" * 70)
    
    for prompt in test_prompts:
        print(f"\n📨 User: {prompt}")
        
        info = CopiloTaskDelegationInterface.get_delegation_info(prompt)
        
        if info["should_delegate"]:
            print(f"✅ Ada can handle this!")
            print(f"   Latency: {info['estimated_latency_ms']}ms")
            print(f"   Token cost: Free (local)")
            print(f"   Reasoning: {info['reasoning']}")
        else:
            print(f"❌ Better to use Copilot")
            print(f"   Reasoning: {info['reasoning']}")
            print(f"   Latency: {info['estimated_latency_ms']}ms")


if __name__ == "__main__":
    main()
