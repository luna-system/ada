"""Latency benchmarking utilities for Ada.

Measures:
- Time To First Token (TTFT)
- Tokens per second
- Total response time
- Breakdown by query type
"""

import time
import httpx
import statistics
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import asyncio


@dataclass
class LatencyMeasurement:
    """Single latency measurement."""
    ttft: float  # Time to first token (seconds)
    total_time: float  # Total response time (seconds)
    token_count: int  # Number of tokens generated
    tokens_per_second: float  # Throughput
    query_type: str  # Type of query (trivial, code, introspection, etc.)
    timestamp: float  # When measurement was taken


class LatencyBenchmarker:
    """Benchmark Ada's latency across different query types."""
    
    def __init__(self, ada_url: str = "http://localhost:8000"):
        self.ada_url = ada_url
        self.measurements: List[LatencyMeasurement] = []
        # Persistent HTTP client for connection pooling
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Context manager entry - create persistent HTTP client."""
        self._client = httpx.AsyncClient(timeout=60.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def warmup(self, num_requests: int = 5):
        """Warm up the model before benchmarking.
        
        Uses parallel requests with diverse query types to warm:
        - Model weights
        - Context caches (persona, FAQs, memories)
        - Connection pools
        - Memory systems
        - ChromaDB indexes
        """
        print(f"🔥 Warming up model with {num_requests} parallel requests...")
        
        # Diverse warmup queries to activate ALL code paths
        warmup_queries = [
            "Hello Ada!",  # Trivial path, persona loading
            "What is Python?",  # FAQ path
            "def hello(): pass",  # Code path
            "Tell me about yourself",  # Introspection + memory retrieval
            "Explain recursion briefly",  # Reasoning path
            "I have a bug in my code",  # Debugging path
        ][:num_requests]
        
        # Parallel warmup for speed
        tasks = [self._single_request(q, query_type="warmup") for q in warmup_queries]
        measurements = await asyncio.gather(*tasks)
        
        for i, m in enumerate(measurements):
            print(f"  Warmup {i+1}/{num_requests}: TTFT={m.ttft:.3f}s, {m.tokens_per_second:.1f} tok/s")
        
        # Extra cache warming step - hit memory/FAQ/persona explicitly
        print("  💾 Warming caches (persona, FAQ, memories)...")
        cache_warmup_queries = [
            "Who are you?",  # Forces persona load
            "How do I use Ada?",  # Forces FAQ load
            "What did we talk about?",  # Forces memory search
        ]
        cache_tasks = [self._single_request(q, query_type="cache_warmup") for q in cache_warmup_queries]
        await asyncio.gather(*cache_tasks)
        print("  ✅ Caches warmed and ready")

    
    async def _single_request(self, message: str, query_type: str) -> LatencyMeasurement:
        """Make a single request and measure latency."""
        # Use persistent client for connection pooling
        client = self._client or httpx.AsyncClient(timeout=60.0)
        should_close = self._client is None
        
        try:
            # Start timing
            start_time = time.time()
            first_token_time = None
            tokens = []
            
            # Stream the response
            async with client.stream(
                "POST",
                f"{self.ada_url}/v1/chat/stream",
                json={"message": message, "conversation_id": "benchmark"}
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Strip "data: " prefix
                        if data == "[DONE]":
                            break
                        
                        # First token timing
                        if first_token_time is None:
                            first_token_time = time.time()
                        
                        tokens.append(data)
            
            # End timing
            end_time = time.time()
            
            # Calculate metrics
            ttft = (first_token_time - start_time) if first_token_time else 0
            total_time = end_time - start_time
            token_count = len(tokens)
            tokens_per_second = token_count / total_time if total_time > 0 else 0
            
            return LatencyMeasurement(
                ttft=ttft,
                total_time=total_time,
                token_count=token_count,
                tokens_per_second=tokens_per_second,
                query_type=query_type,
                timestamp=start_time
            )
        finally:
            # Close temporary client if we created one
            if should_close:
                await client.aclose()
    
    async def benchmark_query_type(
        self,
        query: str,
        query_type: str,
        num_samples: int = 15,
        stabilization_delay: float = 2.0
    ) -> List[LatencyMeasurement]:
        """Benchmark a specific query type with multiple samples.
        
        Args:
            query: Query text to benchmark
            query_type: Category of query (trivial, code, introspection, etc.)
            num_samples: Number of samples to collect
            stabilization_delay: Seconds to wait before starting (avoids cold start artifacts)
        """
        print(f"\n📊 Benchmarking {query_type} ({num_samples} samples)...")
        
        # Stabilization: Let model return to baseline state
        if stabilization_delay > 0:
            print(f"  ⏳ Stabilization delay: {stabilization_delay}s...")
            await asyncio.sleep(stabilization_delay)
        
        measurements = []
        
        for i in range(num_samples):
            measurement = await self._single_request(query, query_type)
            measurements.append(measurement)
            self.measurements.append(measurement)
            
            # Pretty progress bar
            progress = (i + 1) / num_samples
            bar_length = 20
            filled = int(bar_length * progress)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            print(f"  [{bar}] {i+1}/{num_samples}: TTFT={measurement.ttft:.3f}s, "
                  f"Total={measurement.total_time:.3f}s, "
                  f"Tokens/s={measurement.tokens_per_second:.1f}")
        
        return measurements
    
    def get_statistics(self, query_type: str = None, exclude_first: bool = False) -> Dict:
        """Calculate statistics for measurements.
        
        Args:
            query_type: Filter by query type (None = all)
            exclude_first: Exclude first sample per query type (removes warm-up artifacts)
        """
        # Filter by query type if specified
        measurements = [
            m for m in self.measurements
            if query_type is None or m.query_type == query_type
        ]
        
        if not measurements:
            return {}
        
        # Exclude first sample if requested (removes cold start / warm-up artifacts)
        if exclude_first and query_type:
            measurements = measurements[1:]
        
        if not measurements:
            return {}
        
        ttfts = [m.ttft for m in measurements]
        total_times = [m.total_time for m in measurements]
        tokens_per_sec = [m.tokens_per_second for m in measurements]
        
        return {
            "query_type": query_type or "all",
            "sample_count": len(measurements),
            "excluded_first": exclude_first,
            "ttft": {
                "mean": statistics.mean(ttfts),
                "median": statistics.median(ttfts),
                "stdev": statistics.stdev(ttfts) if len(ttfts) > 1 else 0,
                "min": min(ttfts),
                "max": max(ttfts),
                "p95": sorted(ttfts)[int(len(ttfts) * 0.95)] if len(ttfts) > 1 else ttfts[0],
                "p99": sorted(ttfts)[int(len(ttfts) * 0.99)] if len(ttfts) > 1 else ttfts[0],
            },
            "total_time": {
                "mean": statistics.mean(total_times),
                "median": statistics.median(total_times),
                "stdev": statistics.stdev(total_times) if len(total_times) > 1 else 0,
                "min": min(total_times),
                "max": max(total_times),
            },
            "tokens_per_second": {
                "mean": statistics.mean(tokens_per_sec),
                "median": statistics.median(tokens_per_sec),
                "min": min(tokens_per_sec),
                "max": max(tokens_per_sec),
            }
        }
    
    def get_all_statistics(self, exclude_first: bool = False) -> Dict[str, Dict]:
        """Get statistics for all query types.
        
        Args:
            exclude_first: Exclude first sample per query type (removes warm-up artifacts)
        """
        query_types = set(m.query_type for m in self.measurements if m.query_type != "warmup")
        
        results = {
            "overall": self.get_statistics(exclude_first=False),  # Overall always includes all
        }
        
        for query_type in query_types:
            results[query_type] = self.get_statistics(query_type, exclude_first=exclude_first)
        
        return results
    
    def export_measurements(self) -> List[Dict]:
        """Export all measurements as dict list."""
        return [asdict(m) for m in self.measurements]


# Standard benchmark queries
BENCHMARK_QUERIES = {
    "trivial": "Hello! How are you?",
    "code_completion": "Write a Python function that calculates the fibonacci sequence recursively.",
    "introspection": "Introspect your own architecture and tell me about your memory system.",
    "reasoning": "Explain the trade-offs between local AI and cloud AI services, considering cost, privacy, and quality.",
    "debugging": "I'm getting a TypeError: 'NoneType' object is not subscriptable. How do I debug this?",
}


async def run_comprehensive_benchmark():
    """Run comprehensive latency benchmarks with connection pooling."""
    async with LatencyBenchmarker() as benchmarker:
        # Warmup
        await benchmarker.warmup(num_requests=5)
        
        # Benchmark each query type with stabilization delay
        for query_type, query in BENCHMARK_QUERIES.items():
            await benchmarker.benchmark_query_type(
                query=query,
                query_type=query_type,
                num_samples=15,  # Increased from 10 for better statistics
                stabilization_delay=2.0  # Wait 2s between query types to reach baseline
            )
        
        # Print statistics (with and without first sample)
        print("\n" + "=" * 60)
        print("COMPREHENSIVE LATENCY STATISTICS")
        print("=" * 60)
        
        print("\n--- INCLUDING ALL SAMPLES ---")
        stats_all = benchmarker.get_all_statistics(exclude_first=False)
        _print_statistics(stats_all)
        
        print("\n--- EXCLUDING FIRST SAMPLE (Steady-State) ---")
        stats_steady = benchmarker.get_all_statistics(exclude_first=True)
        _print_statistics(stats_steady)
        
        return benchmarker


def _print_statistics(stats: Dict):
    """Helper to print statistics."""
    for query_type, data in stats.items():
        if not data:
            continue
        
        print(f"\n{query_type.upper()}:")
        print(f"  Samples: {data['sample_count']}")
        if 'excluded_first' in data:
            print(f"  Excluded first: {data['excluded_first']}")
        print(f"  TTFT: {data['ttft']['mean']:.3f}s (mean), "
              f"{data['ttft']['median']:.3f}s (median), "
              f"{data['ttft']['p95']:.3f}s (p95)")
        print(f"  Total: {data['total_time']['mean']:.3f}s (mean), "
              f"{data['total_time']['median']:.3f}s (median)")
        print(f"  Throughput: {data['tokens_per_second']['mean']:.1f} tokens/sec (mean)")


if __name__ == "__main__":
    print("Ada Latency Benchmarker")
    print("=" * 60)
    print()
    print("This benchmarks Ada's latency across:")
    print("✓ Trivial queries (greetings)")
    print("✓ Code completion")
    print("✓ Introspection")
    print("✓ Complex reasoning")
    print("✓ Debugging help")
    print()
    print("Starting benchmark...")
    print()
    
    benchmarker = asyncio.run(run_comprehensive_benchmark())
    
    # Export results
    import json
    from pathlib import Path
    
    output_dir = Path(__file__).parent / "press_release_data"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "latency_benchmark.json"
    with open(output_file, 'w') as f:
        json.dump({
            "statistics": benchmarker.get_all_statistics(),
            "raw_measurements": benchmarker.export_measurements(),
        }, f, indent=2)
    
    print(f"\n✅ Results saved to {output_file}")
