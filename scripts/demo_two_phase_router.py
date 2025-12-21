#!/usr/bin/env python3
"""
Phase 3 Live Demo - Two-Phase Router in Action

Shows how the router classifies different queries and routes them:
1. Tool-only (fast): just call tool, return metadata
2. Tool + Reasoning (thoughtful): call tool, feed to LLM
3. Chat-only (conversational): no tools, just LLM
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "ada-mcp" / "src"))

from ada_mcp.tools.two_phase_router import TwoPhaseRouter

def demo_query(query: str):
    """Show how router handles a query."""
    router = TwoPhaseRouter()
    decision = router.make_decision(query)
    
    print(f"\n{'='*70}")
    print(f"Query: {query!r}")
    print(f"{'='*70}")
    print(f"🎯 Phase:      {decision.phase.upper()}")
    print(f"🔧 Use Tool:   {decision.needs_tool}")
    print(f"🧠 Use LLM:    {decision.needs_llm}")
    if decision.tool_name:
        print(f"📋 Tool:       {decision.tool_name}")
    if decision.reasoning_prompt:
        print(f"💭 Reasoning:  {decision.reasoning_prompt!r}")
    
    # Show execution flow
    print(f"\n📍 Execution Flow:")
    if decision.needs_tool:
        print(f"   1. Execute tool: {decision.tool_name}")
        print(f"   2. Collect metadata (files, actions, timing)")
        if decision.needs_llm:
            print(f"   3. Inject metadata into LLM context")
            print(f"   4. LLM reasons about tool result")
            print(f"   5. Return thoughtful response with transparency")
        else:
            print(f"   3. Return tool result + metadata badges")
    else:
        if decision.needs_llm:
            print(f"   1. Call LLM directly (no tools)")
            print(f"   2. Return conversational response")
        else:
            print(f"   1. Error state (no tool, no LLM)")


# Phase 1: Tool-Only Queries
print("\n" + "🚀 " * 20)
print("PHASE 1: TOOL-ONLY (FAST)")
print("🚀 " * 20)

demo_query("introspect")
demo_query("what files do you read from?")
demo_query("analyze your architecture")

# Phase 2: Tool + Reasoning Queries
print("\n" + "🧠 " * 20)
print("PHASE 2: TOOL + REASONING (THOUGHTFUL)")
print("🧠 " * 20)

demo_query("introspect and suggest the easiest TODO to tackle")
demo_query("read context.md and explain the architecture")
demo_query("analyze the codebase to find bottlenecks")
demo_query("introspect and recommend a refactoring")

# Phase 3: Chat-Only Queries
print("\n" + "💬 " * 20)
print("PHASE 3: CHAT-ONLY (CONVERSATIONAL)")
print("💬 " * 20)

demo_query("tell me a story about programming")
demo_query("hello, how are you?")
demo_query("what do you think about AI?")

# Show the decision tree
print("\n" + "=" * 70)
print("📊 ROUTING DECISION TREE")
print("=" * 70)
print("""
Query comes in
    ↓
Does it mention tools/architecture/files? (TOOL_PATTERNS)
    ├─ NO → Check if it's pure chat (CHAT_PATTERNS)
    │        ├─ YES → CHAT-ONLY (LLM only, no tools)
    │        └─ NO  → ERROR (shouldn't happen)
    │
    └─ YES → Check for reasoning keywords (REASONING_PATTERNS)
             ├─ YES → TOOL+REASONING (tool → metadata → LLM)
             └─ NO  → TOOL-ONLY (tool → metadata → response)

Result:
✅ Tool-only:      Fast, transparent (no LLM latency)
✅ Tool+Reasoning: Thoughtful, informed (LLM reasons about tool data)
✅ Chat-only:      Conversational, no overhead (pure LLM)
""")

# Show how metadata enables phase 2
print("\n" + "=" * 70)
print("📦 HOW METADATA ENABLES PHASE 2 ROUTING")
print("=" * 70)
print("""
Tool execution produces metadata:
{
  "toolName": "introspection",
  "filesAccessed": ["context.md", "codebase-map.json", "TODO.md"],
  "actionsTaken": ["read_file", "parse_json", "analyze"],
  "durationMs": 142
}

This metadata enables Phase 2:
1. Router knows which files were read ✅
2. Router can inject them into LLM context ✅
3. LLM can reason about specific files ✅
4. User sees transparency badges ✅

Example Phase 2 Flow:
User: "introspect and suggest a TODO"
  ↓
Router: "Phase 2 - tool + reasoning"
  ↓
Execute: introspection tool → metadata
  ↓
Inject: metadata into LLM context
  ↓
LLM: "I read your TODO.md (5 items). Here's my suggestion..."
  ↓
Return: Response + transparency (📂 Files: TODO.md, CONVENTIONS.md, ⚡ Time: 142ms)
""")

print("\n✨ Demo complete! Ready to integrate with VS Code UI tomorrow. ✨\n")
