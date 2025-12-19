#!/usr/bin/env python3
"""Benchmark suite for Ada code completion.

Measures:
- Latency (cold start, warm runs)
- Token efficiency (prompt size vs quality)
- Completion quality (subjective scoring)
- Different code patterns (function, class, import, loop, etc.)

Run with Ada brain active: docker compose up -d brain chroma ollama
"""

import asyncio
import sys
import time
from pathlib import Path
from statistics import mean, median, stdev
from typing import List, Dict, Any

# Add ada-mcp to path
sys.path.insert(0, str(Path(__file__).parent / "ada-mcp" / "src"))

from ada_mcp.tools.complete_code import complete_code


# Test scenarios with expected patterns
SCENARIOS = [
    {
        "name": "Simple Function",
        "code_before": 'def greet(name):\n    message = ',
        "code_after": '\n    return message',
        "language": "python",
        "expected_keywords": ["hello", "name", "f-string", "{"],
        "complexity": "simple",
    },
    {
        "name": "Class Method",
        "code_before": 'class Calculator:\n    def multiply(self, a, b):\n        ',
        "code_after": '',
        "language": "python",
        "expected_keywords": ["return", "a", "*", "b"],
        "complexity": "simple",
    },
    {
        "name": "Loop Logic",
        "code_before": 'numbers = [1, 2, 3, 4, 5]\ntotal = 0\nfor num in numbers:\n    ',
        "code_after": '\nprint(total)',
        "language": "python",
        "expected_keywords": ["total", "+=", "num"],
        "complexity": "medium",
    },
    {
        "name": "Error Handling",
        "code_before": 'def safe_divide(a, b):\n    try:\n        ',
        "code_after": '\n    except ZeroDivisionError:\n        return 0',
        "language": "python",
        "expected_keywords": ["return", "a", "/", "b"],
        "complexity": "medium",
    },
    {
        "name": "List Comprehension",
        "code_before": '# Get squares of even numbers\nnumbers = [1, 2, 3, 4, 5]\nsquares = ',
        "code_after": '\nprint(squares)',
        "language": "python",
        "expected_keywords": ["[", "for", "if", "**", "%"],
        "complexity": "complex",
    },
    {
        "name": "Dictionary Creation",
        "code_before": 'names = ["alice", "bob", "charlie"]\nname_lengths = ',
        "code_after": '\nprint(name_lengths)',
        "language": "python",
        "expected_keywords": ["{", ":", "len", "for"],
        "complexity": "complex",
    },
    {
        "name": "Recursive Function",
        "code_before": '# Calculate factorial recursively\ndef factorial(n):\n    ',
        "code_after": '',
        "language": "python",
        "expected_keywords": ["if", "return", "factorial", "*"],
        "complexity": "complex",
    },
    {
        "name": "Import Statement",
        "code_before": 'from pathlib import ',
        "code_after": '\n\nclass FileHandler:',
        "language": "python",
        "expected_keywords": ["Path"],
        "complexity": "simple",
    },
]


class BenchmarkResult:
    """Result from a single benchmark run."""
    
    def __init__(self, scenario: Dict[str, Any], completion: str, latency: float, success: bool, error: str = None):
        self.scenario = scenario
        self.completion = completion
        self.latency = latency
        self.success = success
        self.error = error
        self.prompt_tokens = len(scenario["code_before"].split()) + len(scenario["code_after"].split())
        self.completion_tokens = len(completion.split()) if completion else 0
        
    def quality_score(self) -> float:
        """Subjective quality score based on expected keywords (0.0-1.0)."""
        if not self.success or not self.completion:
            return 0.0
        
        completion_lower = self.completion.lower()
        expected = self.scenario["expected_keywords"]
        matches = sum(1 for keyword in expected if keyword in completion_lower)
        
        return matches / len(expected) if expected else 0.5


async def run_benchmark(scenario: Dict[str, Any], warmup: bool = False) -> BenchmarkResult:
    """Run a single benchmark scenario."""
    start = time.perf_counter()
    
    try:
        result = await complete_code(
            code_before=scenario["code_before"],
            code_after=scenario["code_after"],
            language=scenario["language"],
        )
        
        latency = time.perf_counter() - start
        
        return BenchmarkResult(
            scenario=scenario,
            completion=result.content if result.success else "",
            latency=latency,
            success=result.success,
            error=result.error if not result.success else None,
        )
        
    except Exception as e:
        latency = time.perf_counter() - start
        return BenchmarkResult(
            scenario=scenario,
            completion="",
            latency=latency,
            success=False,
            error=str(e),
        )


async def run_benchmarks(scenarios: List[Dict[str, Any]], warmup_runs: int = 1, test_runs: int = 3):
    """Run full benchmark suite."""
    print("🔥 Ada Code Completion Benchmark Suite")
    print("=" * 70)
    print(f"Scenarios: {len(scenarios)}")
    print(f"Warmup runs: {warmup_runs}")
    print(f"Test runs per scenario: {test_runs}")
    print()
    
    # Warmup
    print("🔥 Warming up (loading model, caching)...")
    for i in range(warmup_runs):
        scenario = scenarios[0]  # Use first scenario for warmup
        result = await run_benchmark(scenario, warmup=True)
        print(f"   Warmup {i+1}/{warmup_runs}: {result.latency:.2f}s")
    print()
    
    # Run benchmarks
    all_results = []
    
    for scenario in scenarios:
        print(f"📊 Testing: {scenario['name']} ({scenario['complexity']})")
        
        runs = []
        for run in range(test_runs):
            result = await run_benchmark(scenario)
            runs.append(result)
            
            status = "✅" if result.success else "❌"
            quality = result.quality_score()
            print(f"   Run {run+1}: {status} {result.latency*1000:.0f}ms | Quality: {quality:.1%} | Tokens: {result.completion_tokens}")
        
        all_results.extend(runs)
        
        # Per-scenario summary
        latencies = [r.latency for r in runs if r.success]
        qualities = [r.quality_score() for r in runs if r.success]
        
        if latencies:
            print(f"   ⚡ Avg: {mean(latencies)*1000:.0f}ms | Quality: {mean(qualities):.1%}")
        print()
    
    # Overall statistics
    print("=" * 70)
    print("📈 OVERALL RESULTS")
    print("=" * 70)
    
    successful = [r for r in all_results if r.success]
    failed = [r for r in all_results if not r.success]
    
    print(f"Success Rate: {len(successful)}/{len(all_results)} ({len(successful)/len(all_results):.1%})")
    print()
    
    if successful:
        latencies = [r.latency * 1000 for r in successful]  # Convert to ms
        qualities = [r.quality_score() for r in successful]
        prompt_tokens = [r.prompt_tokens for r in successful]
        completion_tokens = [r.completion_tokens for r in successful]
        
        print("⚡ LATENCY (ms):")
        print(f"   Min:     {min(latencies):.0f}ms")
        print(f"   Max:     {max(latencies):.0f}ms")
        print(f"   Mean:    {mean(latencies):.0f}ms")
        print(f"   Median:  {median(latencies):.0f}ms")
        if len(latencies) > 1:
            print(f"   Stdev:   {stdev(latencies):.0f}ms")
        print(f"   Target:  <500ms {'✅ MET' if mean(latencies) < 500 else '❌ MISSED'}")
        print()
        
        print("🎯 QUALITY:")
        print(f"   Mean:    {mean(qualities):.1%}")
        print(f"   Median:  {median(qualities):.1%}")
        print(f"   Target:  >70% {'✅ MET' if mean(qualities) > 0.7 else '⚠️ CLOSE' if mean(qualities) > 0.5 else '❌ MISSED'}")
        print()
        
        print("📊 TOKEN EFFICIENCY:")
        print(f"   Avg Prompt:     {mean(prompt_tokens):.0f} tokens")
        print(f"   Avg Completion: {mean(completion_tokens):.0f} tokens")
        print(f"   Total Avg:      {mean(prompt_tokens) + mean(completion_tokens):.0f} tokens")
        print()
        
        # Performance by complexity
        by_complexity = {}
        for result in successful:
            complexity = result.scenario["complexity"]
            if complexity not in by_complexity:
                by_complexity[complexity] = []
            by_complexity[complexity].append(result)
        
        print("📈 BY COMPLEXITY:")
        for complexity in ["simple", "medium", "complex"]:
            if complexity in by_complexity:
                results = by_complexity[complexity]
                avg_latency = mean(r.latency * 1000 for r in results)
                avg_quality = mean(r.quality_score() for r in results)
                print(f"   {complexity.capitalize():8} - {avg_latency:.0f}ms | Quality: {avg_quality:.1%}")
        print()
    
    if failed:
        print("❌ FAILURES:")
        for result in failed:
            print(f"   {result.scenario['name']}: {result.error}")
        print()
    
    print("=" * 70)
    print("🎉 Benchmark complete!")
    
    # Save detailed results
    return all_results


async def main():
    """Run the benchmark suite."""
    print()
    
    try:
        results = await run_benchmarks(
            scenarios=SCENARIOS,
            warmup_runs=2,
            test_runs=3,
        )
        
        # Exit code based on performance
        successful = [r for r in results if r.success]
        if successful:
            avg_latency = mean(r.latency * 1000 for r in successful)
            avg_quality = mean(r.quality_score() for r in successful)
            
            if avg_latency < 500 and avg_quality > 0.7:
                print("✅ All performance targets met!")
                return 0
            elif avg_latency < 1000 and avg_quality > 0.5:
                print("⚠️ Performance acceptable but not optimal")
                return 0
            else:
                print("❌ Performance below targets")
                return 1
        else:
            print("❌ All tests failed")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Benchmark interrupted")
        return 130
    except Exception as e:
        print(f"\n\n❌ Benchmark error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
