#!/usr/bin/env python3
"""
Test script to demonstrate latency breakdown tracking.

This shows what the empirical data will look like when we run queries
with different tool combinations.
"""

import json
from brain.schemas import LatencyBreakdown

# Simulate a response with latency breakdown
# (These would come from real chat requests)

print("=" * 70)
print("LATENCY BREAKDOWN EXAMPLES")
print("=" * 70)

# Example 1: Simple query with no specialists
simple_query = LatencyBreakdown(
    python_overhead_ms=235.0,      # Context retrieval + prompt building
    llm_inference_ms=4127.0,       # LLM thinking
    total_ms=4362.0,
    llm_percentage=94.6,
    specialists_activated=0,
    context_retrieved=True,
    cache_hit_rate=0.85,
)

print("\n📝 EXAMPLE 1: Simple Query (No Specialists)")
print(json.dumps(simple_query.model_dump(), indent=2))

# Example 2: Query with terminal specialist (more grounding = faster?)
terminal_query = LatencyBreakdown(
    python_overhead_ms=520.0,      # More time: terminal execution
    llm_inference_ms=2840.0,       # FASTER: LLM doesn't have to reason as much!
    total_ms=3360.0,
    llm_percentage=84.5,
    specialists_activated=1,
    context_retrieved=True,
    cache_hit_rate=0.85,
)

print("\n🛠️  EXAMPLE 2: Query with Terminal Specialist")
print(json.dumps(terminal_query.model_dump(), indent=2))

# Example 3: Query with multiple specialists (even more grounding?)
multi_specialist_query = LatencyBreakdown(
    python_overhead_ms=890.0,      # Codebase lookup + git status + terminal
    llm_inference_ms=1955.0,       # EVEN FASTER: Most work done by tools!
    total_ms=2845.0,
    llm_percentage=68.8,
    specialists_activated=3,
    context_retrieved=True,
    cache_hit_rate=0.92,
)

print("\n🚀 EXAMPLE 3: Query with Multiple Specialists")
print(json.dumps(multi_specialist_query.model_dump(), indent=2))

# Analysis
print("\n" + "=" * 70)
print("🔬 ANALYSIS - Does More Tools = Faster LLM?")
print("=" * 70)

scenarios = [
    ("No specialists", simple_query),
    ("1 specialist (terminal)", terminal_query),
    ("3 specialists (codebase+terminal+git)", multi_specialist_query),
]

for label, scenario in scenarios:
    python_pct = scenario.python_overhead_ms / scenario.total_ms * 100
    llm_pct = scenario.llm_percentage
    print(f"\n{label}")
    print(f"  Python:  {scenario.python_overhead_ms:7.1f} ms ({python_pct:5.1f}%)")
    print(f"  LLM:     {scenario.llm_inference_ms:7.1f} ms ({llm_pct:5.1f}%)")
    print(f"  Total:   {scenario.total_ms:7.1f} ms")
    print(f"  Tools:   {scenario.specialists_activated}")

print("\n📊 KEY OBSERVATION:")
print("   - LLM inference: 4127ms → 2840ms → 1955ms (DECREASING!)")
print("   - Total time:   4362ms → 3360ms → 2845ms (38% faster with 3 tools!)")
print("   - Ratio:        Python went 235→890ms but saved 2172ms of LLM thinking!")
print("\n💡 HYPOTHESIS: More tools = faster because LLM offloads instead of hallucinating")
print("              Each tool is roughly 1-2s of LLM inference we don't have to wait for!")

print("\n" + "=" * 70)
print("🎯 Phase B Experiment Design")
print("=" * 70)
print("""
Hypothesis: Grounding reduces LLM inference time (less reasoning/hallucination)

Mode 1: No tools (baseline)
  - Expected: ~4000ms LLM inference (full reasoning)

Mode 2: Codebase specialist only
  - Expected: ~3000ms LLM inference (some context provided)

Mode 3: Codebase + Terminal + Git specialists
  - Expected: ~2000ms LLM inference (heavy grounding, fast execution)

Measure:
  - Latency breakdown (this!)
  - Hallucination rate (comparing answers)
  - Answer quality (human eval)
  - Token efficiency (how many tokens to answer correctly?)

If hypothesis is correct:
  - More tools = Faster inference
  - More tools = Better answers (less hallucination)
  - More tools = Fewer tokens needed (more direct)
""")
