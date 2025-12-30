#!/usr/bin/env python3
"""
KERNEL 4.0 PHASE 5B: QUICK TEST

Test just the baseline scenario to verify the real API wiring works
before running all 5 scenarios.
"""

import asyncio
import sys
sys.path.insert(0, '/home/luna/Code/ada')

from experiments.phase_5_multi_tool_scenarios import MultiToolTestHarness, MultiToolScenarios


async def main():
    """Quick test of real API execution."""
    harness = MultiToolTestHarness()
    
    print("\n" + "=" * 80)
    print("PHASE 5B QUICK TEST: Baseline Scenario Only")
    print("=" * 80)
    print("\nTesting real Ada API execution with simplest scenario...")
    
    # Test baseline first
    baseline = MultiToolScenarios.quick_fact_check()
    result = await harness.run_scenario(baseline)
    
    print("\n" + "=" * 80)
    print("BASELINE TEST RESULT")
    print("=" * 80)
    print(f"Success: {result.success}")
    print(f"Rounds: {len(result.rounds)}")
    print(f"Tools: {[t.name for t in result.tools_activated]}")
    print(f"Latency: {result.total_latency_ms:.0f}ms")
    print(f"Consciousness: {result.consciousness_rating:.1f}/10")
    
    if result.success:
        print("\n✅ Baseline working! Ready for full Phase 5B execution.")
        return True
    else:
        print("\n❌ Baseline failed. Need to debug before full test.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
