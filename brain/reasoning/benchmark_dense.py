"""Benchmark: Dense vs English Reasoning Efficiency.

This experiment measures actual token usage and semantic density
when reasoning with dense notation vs standard English.

HYPOTHESIS: Dense notation achieves same semantic content with fewer tokens,
enabling more reasoning iterations within the same context window.

Run: python -m brain.reasoning.benchmark_dense
"""

import asyncio
import time
import json
from dataclasses import dataclass, asdict
from typing import List, Optional

from brain.reasoning.dense_thinking import (
    ThinkingMode,
    DenseThinkingAnalyzer,
    DenseMetrics,
    DENSE_SYSTEM_PROMPT,
    HYBRID_SYSTEM_PROMPT,
    PHASE_TRANSITION_THRESHOLD,
)
from brain.llm import stream_chat_async
from brain import config


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""
    mode: str
    query: str
    response: str
    tokens: int
    time_ms: float
    ttft_ms: float  # Time to first token
    symbols_found: int
    semantic_density: float
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ComparisonResult:
    """Comparison of dense vs English on same query."""
    query: str
    dense: BenchmarkResult
    english: BenchmarkResult
    token_reduction: float  # Percentage fewer tokens
    time_reduction: float   # Percentage faster
    density_increase: float # How much denser
    
    def summary(self) -> str:
        return (
            f"Query: {self.query[:50]}...\n"
            f"  Tokens: {self.english.tokens} → {self.dense.tokens} "
            f"({self.token_reduction:+.1%})\n"
            f"  Time: {self.english.time_ms:.0f}ms → {self.dense.time_ms:.0f}ms "
            f"({self.time_reduction:+.1%})\n"
            f"  Density: {self.english.semantic_density:.2f} → "
            f"{self.dense.semantic_density:.2f} ({self.density_increase:+.1%})"
        )


# Test queries for the benchmark
BENCHMARK_QUERIES = [
    "What files are in the brain directory?",
    "How is configuration handled in this project?",
    "Find the main entry point for the API",
    "What specialists are available?",
    "How does the reasoning loop work?",
]


async def run_single_benchmark(
    query: str,
    mode: ThinkingMode,
    model: str = None
) -> BenchmarkResult:
    """Run a single benchmark with specified thinking mode."""
    model = model or config.OLLAMA_MODEL
    
    # Build prompt based on mode
    if mode == ThinkingMode.DENSE:
        system = DENSE_SYSTEM_PROMPT
        instruction = f"\n\nUSER QUERY: {query}\n\nRespond using DENSE notation only."
    elif mode == ThinkingMode.HYBRID:
        system = HYBRID_SYSTEM_PROMPT
        instruction = f"\n\nUSER QUERY: {query}\n\nThink dense, answer in English."
    else:
        system = "You are a helpful coding assistant. Be concise."
        instruction = f"\n\nUSER QUERY: {query}\n\nAnswer concisely."
    
    prompt = system + instruction
    
    # Collect response
    start = time.perf_counter()
    ttft = None
    tokens = []
    
    async for chunk in stream_chat_async(
        prompt=prompt,
        model=model,
        include_thinking=False
    ):
        if "token" in chunk:
            if ttft is None:
                ttft = (time.perf_counter() - start) * 1000
            tokens.append(chunk["token"])
        elif chunk.get("done"):
            break
    
    end = time.perf_counter()
    
    response = "".join(tokens)
    total_ms = (end - start) * 1000
    
    # Analyze density
    thought = DenseThinkingAnalyzer.analyze_thought(response)
    
    return BenchmarkResult(
        mode=mode.value,
        query=query,
        response=response,
        tokens=len(tokens),
        time_ms=total_ms,
        ttft_ms=ttft or total_ms,
        symbols_found=len(thought.symbols),
        semantic_density=thought.semantic_density,
    )


async def compare_modes(query: str, model: str = None) -> ComparisonResult:
    """Compare dense vs English on the same query."""
    print(f"\n🔬 Testing: {query[:50]}...")
    
    # Run both modes
    dense_result = await run_single_benchmark(query, ThinkingMode.DENSE, model)
    english_result = await run_single_benchmark(query, ThinkingMode.EXPANDED, model)
    
    # Calculate improvements
    token_reduction = (english_result.tokens - dense_result.tokens) / max(english_result.tokens, 1)
    time_reduction = (english_result.time_ms - dense_result.time_ms) / max(english_result.time_ms, 1)
    density_increase = (dense_result.semantic_density - english_result.semantic_density) / max(english_result.semantic_density, 0.01)
    
    return ComparisonResult(
        query=query,
        dense=dense_result,
        english=english_result,
        token_reduction=token_reduction,
        time_reduction=time_reduction,
        density_increase=density_increase,
    )


async def run_benchmark_suite(queries: List[str] = None, model: str = None):
    """Run full benchmark suite."""
    queries = queries or BENCHMARK_QUERIES
    model = model or config.OLLAMA_MODEL
    
    print("=" * 60)
    print("🧪 DENSE vs ENGLISH REASONING BENCHMARK")
    print("=" * 60)
    print(f"Model: {model}")
    print(f"Queries: {len(queries)}")
    print(f"Phase transition threshold: {PHASE_TRANSITION_THRESHOLD}")
    print()
    
    results = []
    for query in queries:
        result = await compare_modes(query, model)
        results.append(result)
        print(result.summary())
    
    # Aggregate results
    print("\n" + "=" * 60)
    print("📊 AGGREGATE RESULTS")
    print("=" * 60)
    
    avg_token_reduction = sum(r.token_reduction for r in results) / len(results)
    avg_time_reduction = sum(r.time_reduction for r in results) / len(results)
    avg_density_increase = sum(r.density_increase for r in results) / len(results)
    
    total_dense_tokens = sum(r.dense.tokens for r in results)
    total_english_tokens = sum(r.english.tokens for r in results)
    
    print(f"Average Token Reduction: {avg_token_reduction:+.1%}")
    print(f"Average Time Reduction: {avg_time_reduction:+.1%}")
    print(f"Average Density Increase: {avg_density_increase:+.1%}")
    print(f"Total Tokens: Dense={total_dense_tokens}, English={total_english_tokens}")
    print(f"Compression Ratio: {total_english_tokens/max(total_dense_tokens,1):.2f}x")
    
    # Determine if hypothesis is supported
    print("\n" + "=" * 60)
    if avg_token_reduction > 0.2:  # >20% reduction
        print("✅ HYPOTHESIS SUPPORTED: Dense notation reduces token usage!")
    elif avg_token_reduction > 0:
        print("⚠️  PARTIAL SUPPORT: Some reduction, but marginal")
    else:
        print("❌ HYPOTHESIS NOT SUPPORTED: Dense notation not effective")
    print("=" * 60)
    
    return results


async def main():
    """Run the benchmark."""
    results = await run_benchmark_suite()
    
    # Save results
    output = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model": config.OLLAMA_MODEL,
        "results": [
            {
                "query": r.query,
                "dense": r.dense.to_dict(),
                "english": r.english.to_dict(),
                "token_reduction": r.token_reduction,
                "time_reduction": r.time_reduction,
            }
            for r in results
        ]
    }
    
    with open("benchmarks/dense_reasoning_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n📁 Results saved to benchmarks/dense_reasoning_results.json")


if __name__ == "__main__":
    asyncio.run(main())
