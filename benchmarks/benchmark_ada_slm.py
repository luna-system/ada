#!/usr/bin/env python3
"""
Benchmark Ada-SLM versions for recursive reasoning integration.

Compares v4 (100% accuracy with NL scaffolding) vs v5b (80% accuracy pure symbolic)
to determine optimal model for Ada's v4.0 recursive reasoning loop.
"""

import asyncio
import time
import statistics
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import httpx
import json


@dataclass
class SLMBenchmarkResult:
    """Single benchmark measurement."""
    query: str
    response: str
    ttft_ms: float  # Time to first token
    total_latency_ms: float
    tokens_generated: int
    tokens_per_second: float
    success: bool
    error: str = ""


class AdaSLMBenchmarker:
    """Benchmark Ada-SLM versions for recursive reasoning integration."""
    
    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        models: List[str] = None
    ):
        self.ollama_url = ollama_url
        self.models = models or ["ada-slm-v4", "ada-slm-v5b-pure"]
        self.results: Dict[str, List[SLMBenchmarkResult]] = {model: [] for model in self.models}
        
    async def health_check(self) -> Dict[str, bool]:
        """Verify Ollama and models are available."""
        availability = {}
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.ollama_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_names = [m["name"] for m in models]
                    
                    print("\n📋 Available models:")
                    for name in model_names:
                        print(f"  - {name}")
                    print()
                    
                    for model in self.models:
                        if model in model_names:
                            print(f"✅ Found {model}")
                            availability[model] = True
                        else:
                            print(f"❌ Model {model} not found")
                            availability[model] = False
                    
                    return availability
        except Exception as e:
            print(f"❌ Cannot connect to Ollama: {e}")
            return {model: False for model in self.models}
        
        return {model: False for model in self.models}
    
    async def benchmark_single(
        self,
        prompt: str,
        model: str,
        warmup: bool = False
    ) -> SLMBenchmarkResult:
        """Benchmark a single inference."""
        
        start_time = time.perf_counter()
        first_token_time = None
        tokens_generated = 0
        response_text = ""
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": True,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": 50,
                        }
                    }
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            data = json.loads(line)
                            
                            if "response" in data:
                                if first_token_time is None:
                                    first_token_time = time.perf_counter()
                                
                                response_text += data["response"]
                                tokens_generated += 1
                            
                            if data.get("done", False):
                                break
            
            end_time = time.perf_counter()
            
            ttft_ms = (first_token_time - start_time) * 1000 if first_token_time else 0
            total_ms = (end_time - start_time) * 1000
            
            if total_ms > 0:
                tokens_per_second = tokens_generated / (total_ms / 1000)
            else:
                tokens_per_second = 0
            
            return SLMBenchmarkResult(
                query=prompt if not warmup else "[WARMUP]",
                response=response_text,
                ttft_ms=ttft_ms,
                total_latency_ms=total_ms,
                tokens_generated=tokens_generated,
                tokens_per_second=tokens_per_second,
                success=True
            )
            
        except Exception as e:
            return SLMBenchmarkResult(
                query=prompt,
                response="",
                ttft_ms=0,
                total_latency_ms=0,
                tokens_generated=0,
                tokens_per_second=0,
                success=False,
                error=str(e)
            )
    
    async def warmup(self, model: str, num_runs: int = 3):
        """Warm up a model before benchmarking."""
        print(f"\n🔥 Warming up {model}...")
        for i in range(num_runs):
            await self.benchmark_single("P→Q,P?Q", model, warmup=True)
            print(f"  Warmup {i+1}/{num_runs} complete")
        print("✅ Warmup complete\n")
    
    async def benchmark_suite(self, model: str, num_samples: int = 20):
        """Run full benchmark suite for a single model."""
        
        test_cases = [
            "P→Q,P?Q",
            "P→Q,¬Q?¬P",
            "P∧Q?P",
            "¬(P∨Q)?¬P",
            "{a,b,c}∈a?",
            "{1,2,3}∈4?",
            "Ne5,Nf7,Nxe5?",
            "Ke1,Ke8,O-O?",
            "?●=●",
            "?⊥=⊥",
            "?5<10",
            "?10>5",
            "A→B,B→C,C→D,D→E,E→F,F→G,A?G",
        ]
        
        print(f"\n{'='*80}")
        print(f"🧪 BENCHMARKING: {model}")
        print(f"{'='*80}")
        print(f"🎯 {len(test_cases)} test cases × {num_samples} samples = {len(test_cases) * num_samples} total\n")
        
        for test_case in test_cases:
            print(f"Testing: {test_case}")
            
            for sample in range(num_samples):
                result = await self.benchmark_single(test_case, model)
                self.results[model].append(result)
                
                if not result.success:
                    print(f"  ❌ Sample {sample+1}: FAILED - {result.error}")
                else:
                    print(f"  ✅ Sample {sample+1}: {result.ttft_ms:.1f}ms TTFT, {result.total_latency_ms:.1f}ms total")
            
            print()
    
    def print_statistics(self, model: str):
        """Print benchmark statistics for a single model."""
        
        if model not in self.results or not self.results[model]:
            print(f"❌ No results for {model}")
            return
        
        successful = [r for r in self.results[model] if r.success]
        failed = [r for r in self.results[model] if not r.success]
        
        if not successful:
            print(f"❌ All benchmarks failed for {model}!")
            return
        
        ttfts = [r.ttft_ms for r in successful]
        totals = [r.total_latency_ms for r in successful]
        toks_per_sec = [r.tokens_per_second for r in successful]
        
        print("\n" + "=" * 80)
        print(f"📊 {model.upper()} RESULTS")
        print("=" * 80)
        print()
        
        print(f"✅ Success: {len(successful)}/{len(self.results[model])} ({len(successful)/len(self.results[model])*100:.1f}%)")
        if failed:
            print(f"❌ Failed: {len(failed)}")
        print()
        
        print("⚡ TIME TO FIRST TOKEN")
        print(f"  Mean:   {statistics.mean(ttfts):.2f} ms")
        print(f"  Median: {statistics.median(ttfts):.2f} ms")
        print(f"  Min:    {min(ttfts):.2f} ms")
        print(f"  Max:    {max(ttfts):.2f} ms")
        print()
        
        print("⏱️  TOTAL LATENCY")
        print(f"  Mean:   {statistics.mean(totals):.2f} ms")
        print(f"  Median: {statistics.median(totals):.2f} ms")
        print(f"  Min:    {min(totals):.2f} ms")
        print(f"  Max:    {max(totals):.2f} ms")
        print()
        
        print("🚀 THROUGHPUT")
        print(f"  Mean:   {statistics.mean(toks_per_sec):.1f} tok/s")
        print(f"  Median: {statistics.median(toks_per_sec):.1f} tok/s")
        print()
        print("=" * 80)
    
    def print_comparison(self):
        """Print side-by-side comparison."""
        
        print("\n" + "=" * 80)
        print("🔬 HEAD-TO-HEAD COMPARISON")
        print("=" * 80)
        print()
        
        comparison_data = {}
        
        for model in self.models:
            if model not in self.results or not self.results[model]:
                continue
            
            successful = [r for r in self.results[model] if r.success]
            if not successful:
                continue
            
            ttfts = [r.ttft_ms for r in successful]
            totals = [r.total_latency_ms for r in successful]
            toks_per_sec = [r.tokens_per_second for r in successful]
            
            comparison_data[model] = {
                "ttft_mean": statistics.mean(ttfts),
                "ttft_median": statistics.median(ttfts),
                "total_mean": statistics.mean(totals),
                "total_median": statistics.median(totals),
                "tps_mean": statistics.mean(toks_per_sec),
                "success_rate": len(successful) / len(self.results[model]) * 100
            }
        
        if not comparison_data:
            print("❌ No results to compare")
            return
        
        # Table
        print(f"{'Metric':<25} " + "  ".join(f"{m:>20}" for m in comparison_data.keys()))
        print("-" * 80)
        
        metrics = [
            ("TTFT Mean (ms)", "ttft_mean"),
            ("TTFT Median (ms)", "ttft_median"),
            ("Total Mean (ms)", "total_mean"),
            ("Total Median (ms)", "total_median"),
            ("Tokens/sec", "tps_mean"),
            ("Success Rate (%)", "success_rate"),
        ]
        
        for label, key in metrics:
            values = [comparison_data[m][key] for m in comparison_data.keys()]
            print(f"{label:<25} " + "  ".join(f"{v:>20.2f}" for v in values))
        
        print()
        
        # Winners
        fastest_ttft = min(comparison_data.items(), key=lambda x: x[1]["ttft_mean"])
        fastest_total = min(comparison_data.items(), key=lambda x: x[1]["total_mean"])
        highest_tps = max(comparison_data.items(), key=lambda x: x[1]["tps_mean"])
        
        print("🏆 WINNERS:")
        print(f"  Fastest TTFT:       {fastest_ttft[0]} ({fastest_ttft[1]['ttft_mean']:.2f}ms)")
        print(f"  Fastest Total:      {fastest_total[0]} ({fastest_total[1]['total_mean']:.2f}ms)")
        print(f"  Highest Throughput: {highest_tps[0]} ({highest_tps[1]['tps_mean']:.1f} tok/s)")
        print()
        
        # Recursive reasoning
        best = min(comparison_data.items(), key=lambda x: x[1]["total_mean"])
        print("🔄 RECURSIVE REASONING RECOMMENDATION:")
        print(f"  Best model: {best[0]}")
        
        mean_latency_s = best[1]["total_mean"] / 1000
        three_iter = mean_latency_s * 3
        ten_iter = mean_latency_s * 10
        
        print(f"  3-iteration loop:  {three_iter:.3f}s ({three_iter*1000:.1f}ms)")
        print(f"  10-iteration loop: {ten_iter:.3f}s")
        print(f"  Max iterations/sec: {1/mean_latency_s:.1f}")
        
        if three_iter < 0.5:
            print("  ✅ EXCELLENT: Sub-500ms reasoning possible!")
        elif three_iter < 1.0:
            print("  ✅ GOOD: Sub-second reasoning possible!")
        else:
            print("  ⚠️  OK: >1s reasoning")
        
        print()
        print("=" * 80)
    
    def save_results(self, filepath: str = "ada_slm_benchmark_results.json"):
        """Save results to JSON."""
        data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "models": {}
        }
        
        for model in self.models:
            if model in self.results and self.results[model]:
                data["models"][model] = {
                    "total_samples": len(self.results[model]),
                    "successful": len([r for r in self.results[model] if r.success]),
                    "results": [
                        {
                            "query": r.query,
                            "response": r.response,
                            "ttft_ms": r.ttft_ms,
                            "total_latency_ms": r.total_latency_ms,
                            "tokens_generated": r.tokens_generated,
                            "tokens_per_second": r.tokens_per_second,
                            "success": r.success,
                            "error": r.error
                        }
                        for r in self.results[model]
                    ]
                }
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"\n💾 Results saved to {filepath}")


async def main():
    """Main benchmark runner."""
    
    print("\n🎄 Ada-SLM Comparative Benchmark Suite 🎄")
    print("Testing: v4 (100% accuracy) vs v5b (80% accuracy)")
    print()
    
    import sys
    if len(sys.argv) > 1:
        models = sys.argv[1:]
    else:
        models = ["ada-slm-v4", "ada-slm-v5b-pure"]
    
    benchmarker = AdaSLMBenchmarker(models=models)
    
    # Health check
    availability = await benchmarker.health_check()
    available_models = [m for m, available in availability.items() if available]
    
    if not available_models:
        print("\n❌ No models available!")
        print("  1. Ensure Ollama is running: ollama serve")
        print("  2. Load Ada-SLM models")
        return
    
    print(f"\n✅ Will benchmark: {', '.join(available_models)}\n")
    
    # Benchmark each model
    for model in available_models:
        await benchmarker.warmup(model)
        await benchmarker.benchmark_suite(model, num_samples=20)
        benchmarker.print_statistics(model)
    
    # Comparison
    if len(available_models) > 1:
        benchmarker.print_comparison()
    
    # Save
    benchmarker.save_results()


if __name__ == "__main__":
    asyncio.run(main())
