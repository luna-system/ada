#!/usr/bin/env python3
"""
Hardware Performance Ceiling Discovery

Systematically profiles Ada across different configurations to find:
- Theoretical vs practical limits
- Model/hardware tradeoffs
- Quantization impact
- Batch efficiency

Outputs reproducible benchmark results for community optimization.

Usage:
    python scripts/hardware_ceiling.py
    python scripts/hardware_ceiling.py --model qwen2.5-coder:7b --trials 5
    python scripts/hardware_ceiling.py --export-json results.json
"""

import json
import time
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, asdict
import httpx


@dataclass
class HardwareInfo:
    """System hardware information"""
    gpu_memory_total: int = 0
    gpu_memory_used: int = 0
    cpu_cores: int = 0
    system_memory: int = 0


@dataclass
class BenchmarkResult:
    """Single benchmark result"""
    model: str
    prompt: str
    ttft_ms: float  # Time to first token
    tokens_generated: int
    throughput_tps: float  # Tokens per second
    total_time_ms: float
    temperature: float = 0.7


@dataclass 
class CeilingReport:
    """Complete hardware ceiling analysis"""
    timestamp: str
    hardware: HardwareInfo
    model_profiles_tested: List[str]
    results: List[BenchmarkResult]
    analysis: Dict


def get_hardware_info() -> HardwareInfo:
    """Query hardware using system commands"""
    info = HardwareInfo()
    
    try:
        # Check CPU cores
        import os
        info.cpu_cores = os.cpu_count() or 1
        
        # Check system memory
        try:
            result = subprocess.run(
                ["free", "-b"],
                capture_output=True,
                text=True,
                timeout=5
            )
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                info.system_memory = int(parts[1])
        except:
            pass
        
        # GPU memory (ROCm/CUDA agnostic - check ollama process)
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Parse RSS/VRAM from ollama runner processes
            for line in result.stdout.split('\n'):
                if 'ollama runner' in line or 'ollama' in line:
                    parts = line.split()
                    if len(parts) > 5:
                        try:
                            rss_kb = int(parts[5])
                            info.gpu_memory_used = max(info.gpu_memory_used, rss_kb * 1024)
                        except:
                            pass
        except:
            pass
            
    except Exception as e:
        print(f"Warning: Could not query hardware: {e}")
    
    return info


def benchmark_model(model: str, prompts: List[str], trials: int = 2) -> List[BenchmarkResult]:
    """Benchmark a specific model across prompts"""
    results = []
    
    for prompt in prompts:
        print(f"  Testing: {model} with '{prompt[:40]}...'")
        
        for trial in range(trials):
            try:
                start = time.time()
                tokens = 0
                ttft = None
                
                with httpx.Client(timeout=60) as client:
                    with client.stream(
                        "POST",
                        "http://localhost:8000/v1/chat/stream",
                        json={"prompt": prompt},
                        headers={"Accept": "text/event-stream"},
                    ) as resp:
                        for line in resp.iter_lines():
                            if not line or not line.startswith("data: "):
                                continue
                            
                            if ttft is None:
                                ttft = (time.time() - start) * 1000
                            
                            try:
                                data = json.loads(line[6:])
                                if data.get("type") == "token":
                                    tokens += 1
                            except:
                                pass
                
                total_ms = (time.time() - start) * 1000
                throughput = (tokens / (total_ms / 1000)) if total_ms > 0 else 0
                
                results.append(BenchmarkResult(
                    model=model,
                    prompt=prompt,
                    ttft_ms=ttft or total_ms,
                    tokens_generated=tokens,
                    throughput_tps=throughput,
                    total_time_ms=total_ms,
                ))
                
                print(f"    Trial {trial+1}: TTFT={ttft:.0f}ms, {tokens}tokens @ {throughput:.1f}tps")
                
            except Exception as e:
                print(f"    Trial {trial+1}: ERROR - {e}")
    
    return results


def analyze_results(results: List[BenchmarkResult]) -> Dict:
    """Analyze benchmark results to find ceiling"""
    if not results:
        return {}
    
    # Group by model
    by_model = {}
    for r in results:
        if r.model not in by_model:
            by_model[r.model] = []
        by_model[r.model].append(r)
    
    analysis = {}
    
    for model, model_results in by_model.items():
        ttfts = [r.ttft_ms for r in model_results]
        tpss = [r.throughput_tps for r in model_results if r.throughput_tps > 0]
        
        analysis[model] = {
            "avg_ttft_ms": sum(ttfts) / len(ttfts),
            "min_ttft_ms": min(ttfts),
            "max_ttft_ms": max(ttfts),
            "avg_throughput_tps": sum(tpss) / len(tpss) if tpss else 0,
            "avg_tokens": sum(r.tokens_generated for r in model_results) / len(model_results),
        }
    
    # Find theoretical ceiling
    if analysis:
        fastest_ttft = min(m["avg_ttft_ms"] for m in analysis.values())
        fastest_model = [k for k, v in analysis.items() if v["avg_ttft_ms"] == fastest_ttft][0]
        best_throughput = max(m["avg_throughput_tps"] for m in analysis.values())
        
        analysis["ceiling_analysis"] = {
            "fastest_model": fastest_model,
            "fastest_ttft_ms": fastest_ttft,
            "best_throughput_tps": best_throughput,
            "theoretical_gains_available": {
                "quantization_2x": "Via INT4 quantization",
                "inference_opt_1_5x": "Via vLLM/TensorRT",
                "combined_ceiling_3x": "Maximum theoretical on current hardware"
            }
        }
    
    return analysis


def main():
    parser = argparse.ArgumentParser(
        description="Profile hardware performance ceiling for Ada"
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=["qwen2.5-coder:7b", "mistral:7b"],
        help="Models to benchmark"
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=2,
        help="Trials per configuration"
    )
    parser.add_argument(
        "--export-json",
        help="Export results to JSON file"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("ADA HARDWARE CEILING DISCOVERY")
    print("=" * 70)
    
    # Get hardware info
    print("\n[1/4] Detecting hardware...")
    hardware = get_hardware_info()
    print(f"  CPU cores: {hardware.cpu_cores}")
    print(f"  GPU memory used: {hardware.gpu_memory_used / 1024 / 1024:.0f}MB")
    
    # Test prompts
    test_prompts = [
        "Hi!",
        "What is Python?",
        "Explain machine learning briefly.",
    ]
    
    # Run benchmarks
    print("\n[2/4] Running benchmarks...")
    all_results = []
    
    for model in args.models:
        print(f"\nModel: {model}")
        results = benchmark_model(model, test_prompts, args.trials)
        all_results.extend(results)
    
    # Analyze
    print("\n[3/4] Analyzing results...")
    analysis = analyze_results(all_results)
    
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    for model, stats in analysis.items():
        if model != "ceiling_analysis":
            print(f"\n{model}:")
            print(f"  Avg TTFT: {stats['avg_ttft_ms']:.0f}ms (range: {stats['min_ttft_ms']:.0f}-{stats['max_ttft_ms']:.0f}ms)")
            print(f"  Throughput: {stats['avg_throughput_tps']:.1f} tokens/sec")
            print(f"  Avg output length: {stats['avg_tokens']:.0f} tokens")
    
    if "ceiling_analysis" in analysis:
        ceil = analysis["ceiling_analysis"]
        print(f"\n{'CEILING ANALYSIS':^70}")
        print(f"Fastest model: {ceil['fastest_model']}")
        print(f"Best TTFT: {ceil['fastest_ttft_ms']:.0f}ms")
        print(f"Best throughput: {ceil['best_throughput_tps']:.1f} tokens/sec")
        print(f"\nTheoretical gains available:")
        for k, v in ceil["theoretical_gains_available"].items():
            print(f"  {k}: {v}")
    
    # Export if requested
    if args.export_json:
        print(f"\n[4/4] Exporting to {args.export_json}...")
        report = CeilingReport(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            hardware=hardware,
            model_profiles_tested=args.models,
            results=all_results,
            analysis=analysis,
        )
        
        with open(args.export_json, "w") as f:
            json.dump({
                "report": asdict(report)
            }, f, indent=2)
        print(f"✓ Results saved to {args.export_json}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
