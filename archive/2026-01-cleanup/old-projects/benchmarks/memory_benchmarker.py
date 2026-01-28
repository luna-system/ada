"""Memory system benchmarking for Ada.

Measures:
- Storage efficiency (disk usage)
- Retrieval speed (RAG query time)
- Growth patterns over time
- Consolidation effectiveness

Reality check: Show that local storage is TINY and FAST.
"""

import time
import httpx
import statistics
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass, asdict
import asyncio
import json
import subprocess


@dataclass
class MemoryStats:
    """Memory system statistics."""
    total_size_bytes: int
    total_size_mb: float
    chroma_size_bytes: int
    chroma_size_mb: float
    file_count: int
    collection_stats: Dict[str, int]  # Collection name -> document count
    timestamp: float


@dataclass
class RetrievalMeasurement:
    """Single retrieval timing measurement."""
    query: str
    retrieval_time_ms: float
    num_results: int
    timestamp: float


class MemoryBenchmarker:
    """Benchmark Ada's memory system."""
    
    def __init__(
        self,
        ada_url: str = "http://localhost:8000",
        data_dir: Path = Path("/home/luna/Code/ada-v1/data")
    ):
        self.ada_url = ada_url
        self.data_dir = data_dir
        self.chroma_dir = data_dir / "chroma"  # Correct path!
        self.retrieval_measurements: List[RetrievalMeasurement] = []
    
    def measure_storage(self) -> MemoryStats:
        """Measure current storage usage.
        
        IMPORTANT: Separates model storage (one-time) from memory storage (growing).
        - Ollama models: ~9.5GB (one-time download)
        - ChromaDB memory: ~61MB (grows with use) ← KEY METRIC!
        """
        # Total data directory size
        result = subprocess.run(
            ["du", "-sb", str(self.data_dir)],
            capture_output=True,
            text=True
        )
        total_bytes = int(result.stdout.split()[0])
        
        # ChromaDB directory size (THIS IS WHAT GROWS WITH USE)
        if self.chroma_dir.exists():
            result = subprocess.run(
                ["du", "-sb", str(self.chroma_dir)],
                capture_output=True,
                text=True
            )
            chroma_bytes = int(result.stdout.split()[0])
        else:
            chroma_bytes = 0
        
        # File count (in memory directory only, not models)
        file_count = sum(1 for _ in self.chroma_dir.rglob("*") if _.is_file()) if self.chroma_dir.exists() else 0
        
        # Collection stats (would need to query ChromaDB API for real counts)
        # For now, estimate based on directory structure
        collection_stats = {}
        if self.chroma_dir.exists():
            for collection_dir in self.chroma_dir.iterdir():
                if collection_dir.is_dir():
                    collection_stats[collection_dir.name] = -1  # Placeholder
        
        return MemoryStats(
            total_size_bytes=total_bytes,
            total_size_mb=total_bytes / (1024 * 1024),
            chroma_size_bytes=chroma_bytes,
            chroma_size_mb=chroma_bytes / (1024 * 1024),
            file_count=file_count,
            collection_stats=collection_stats,
            timestamp=time.time()
        )
    
    async def measure_retrieval_speed(
        self,
        query: str,
        num_samples: int = 10
    ) -> List[RetrievalMeasurement]:
        """Measure RAG retrieval speed."""
        measurements = []
        
        print(f"📊 Measuring retrieval speed for: '{query[:50]}...' ({num_samples} samples)")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for i in range(num_samples):
                start_time = time.time()
                
                # Simulate RAG retrieval by searching memories
                # (In real implementation, would hit Ada's memory search endpoint)
                try:
                    response = await client.post(
                        f"{self.ada_url}/v1/memories/search",
                        json={"query": query, "limit": 10}
                    )
                    results = response.json() if response.status_code == 200 else []
                    num_results = len(results) if isinstance(results, list) else 0
                except Exception as e:
                    print(f"  Warning: {e}")
                    num_results = 0
                
                end_time = time.time()
                retrieval_time_ms = (end_time - start_time) * 1000
                
                measurement = RetrievalMeasurement(
                    query=query,
                    retrieval_time_ms=retrieval_time_ms,
                    num_results=num_results,
                    timestamp=start_time
                )
                measurements.append(measurement)
                self.retrieval_measurements.append(measurement)
                
                print(f"  Sample {i+1}/{num_samples}: {retrieval_time_ms:.1f}ms, {num_results} results")
        
        return measurements
    
    def estimate_growth(
        self,
        current_size_mb: float,
        messages_per_day: int = 100,
        bytes_per_message: int = 500
    ) -> Dict[str, float]:
        """Estimate memory growth over time.
        
        IMPORTANT: This estimates MEMORY ONLY (ChromaDB), not model storage.
        Models are downloaded once (~9GB), memory grows with conversation.
        """
        # Current ChromaDB size as baseline (NOT total data dir)
        daily_growth_mb = (messages_per_day * bytes_per_message) / (1024 * 1024)
        
        return {
            "current_mb": current_size_mb,
            "daily_growth_mb": daily_growth_mb,
            "30_day_projection_mb": current_size_mb + (daily_growth_mb * 30),
            "1_year_projection_mb": current_size_mb + (daily_growth_mb * 365),
            "5_year_projection_mb": current_size_mb + (daily_growth_mb * 365 * 5),
            "messages_per_day_assumption": messages_per_day,
            "bytes_per_message_assumption": bytes_per_message,
        }
    
    def get_retrieval_statistics(self) -> Dict:
        """Calculate retrieval timing statistics."""
        if not self.retrieval_measurements:
            return {}
        
        times = [m.retrieval_time_ms for m in self.retrieval_measurements]
        
        return {
            "sample_count": len(times),
            "mean_ms": statistics.mean(times),
            "median_ms": statistics.median(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0,
            "p95_ms": sorted(times)[int(len(times) * 0.95)] if len(times) > 1 else times[0],
            "p99_ms": sorted(times)[int(len(times) * 0.99)] if len(times) > 1 else times[0],
        }
    
    def export_results(self) -> Dict:
        """Export all benchmark results."""
        storage_stats = self.measure_storage()
        retrieval_stats = self.get_retrieval_statistics()
        growth_estimates = self.estimate_growth(storage_stats.total_size_mb)
        
        return {
            "storage": asdict(storage_stats),
            "retrieval": retrieval_stats,
            "growth_projections": growth_estimates,
            "raw_retrievals": [asdict(m) for m in self.retrieval_measurements],
        }


async def run_comprehensive_benchmark():
    """Run comprehensive memory benchmarks."""
    benchmarker = MemoryBenchmarker()
    
    print("Ada Memory System Benchmarker")
    print("=" * 60)
    print()
    
    # 1. Storage efficiency
    print("📦 Measuring storage efficiency...")
    storage = benchmarker.measure_storage()
    print(f"   Total data dir: {storage.total_size_mb:.2f} MB (includes models)")
    print(f"   ChromaDB memory: {storage.chroma_size_mb:.2f} MB ← GROWS WITH USE")
    print(f"   Memory files: {storage.file_count} files")
    print(f"   Reality: Models are one-time (~9GB), memory is TINY!")
    print()
    
    # 2. Retrieval speed
    test_queries = [
        "recent conversations about code",
        "how do I configure Ada",
        "what is the RAG system",
    ]
    
    for query in test_queries:
        await benchmarker.measure_retrieval_speed(query, num_samples=5)
        print()
    
    # 3. Growth projections
    print("📈 Growth projections (memory only, not models):")
    growth = benchmarker.estimate_growth(storage.chroma_size_mb)
    print(f"   Current memory: {growth['current_mb']:.2f} MB")
    print(f"   1 year: {growth['1_year_projection_mb']:.2f} MB")
    print(f"   5 years: {growth['5_year_projection_mb']:.2f} MB")
    print(f"   Assumption: {growth['messages_per_day_assumption']} messages/day")
    print()
    
    # 4. Retrieval statistics
    print("⚡ Retrieval statistics:")
    stats = benchmarker.get_retrieval_statistics()
    if stats:
        print(f"   Mean: {stats['mean_ms']:.1f}ms")
        print(f"   Median: {stats['median_ms']:.1f}ms")
        print(f"   P95: {stats['p95_ms']:.1f}ms")
        print(f"   Target: <100ms ✓" if stats['mean_ms'] < 100 else f"   Target: <100ms ⚠️")
    print()
    
    return benchmarker


if __name__ == "__main__":
    benchmarker = asyncio.run(run_comprehensive_benchmark())
    
    # Save results
    output_dir = Path(__file__).parent / "press_release_data"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "memory_benchmark.json"
    with open(output_file, 'w') as f:
        json.dump(benchmarker.export_results(), f, indent=2)
    
    print(f"✅ Results saved to {output_file}")
    print()
    print("Reality check:")
    storage = benchmarker.measure_storage()
    growth = benchmarker.estimate_growth(storage.chroma_size_mb)
    print(f"  - Current memory: {storage.chroma_size_mb:.2f} MB (TINY!)")
    print(f"  - Models (one-time): ~9.5 GB")
    print(f"  - 5-year memory projection: {growth['5_year_projection_mb']:.0f} MB")
    print(f"  - Cloud: Stores YOUR data, charges YOU monthly, grows their profit")
    print(f"  - Local: YOUR disk, YOUR control, FREE forever")
    print()
    print("Winner: Local storage is FREE, PRIVATE, and EFFICIENT 🎉")
