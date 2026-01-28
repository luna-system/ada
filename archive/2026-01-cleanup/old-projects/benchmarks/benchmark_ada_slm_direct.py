#!/usr/bin/env python3
"""
Direct LoRA benchmark for Ada-SLM models.

Benchmarks v4 and v5b LoRA adapters directly using unsloth/transformers
for maximum speed - no Ollama conversion needed!
"""

import time
import statistics
from dataclasses import dataclass
from typing import List, Dict
import json
from pathlib import Path

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch


@dataclass
class BenchmarkResult:
    query: str
    response: str
    total_ms: float
    success: bool
    error: str = ""


class AdaSLMDirectBenchmark:
    """Benchmark Ada-SLM LoRA adapters directly."""
    
    def __init__(self, base_model: str = "Qwen/Qwen2.5-0.5B-Instruct"):
        self.base_model = base_model
        self.models = {}
        self.results = {}
        
    def load_model(self, name: str, adapter_path: str):
        """Load base model + LoRA adapter."""
        print(f"\n📦 Loading {name}...")
        print(f"   Base: {self.base_model}")
        print(f"   Adapter: {adapter_path}")
        
        try:
            # Try GPU first, fall back to CPU if ROCm issues
            try:
                # Load base model on GPU
                model = AutoModelForCausalLM.from_pretrained(
                    self.base_model,
                    torch_dtype=torch.float16,
                    device_map="auto"
                )
                
                tokenizer = AutoTokenizer.from_pretrained(self.base_model)
                
                # Load LoRA adapter (may fail on ROCm 6.3 + gfx1102)
                model = PeftModel.from_pretrained(
                    model, 
                    adapter_path,
                    torch_dtype=torch.float16
                )
                model.eval()
                device = "GPU"
                
            except (torch.cuda.CudaError, RuntimeError) as gpu_err:
                # ROCm device function error - fall back to CPU
                print(f"   ⚠️  GPU loading failed, trying CPU...")
                model = AutoModelForCausalLM.from_pretrained(
                    self.base_model,
                    torch_dtype=torch.float32,
                    device_map="cpu"
                )
                
                tokenizer = AutoTokenizer.from_pretrained(self.base_model)
                
                # Load LoRA adapter on CPU
                model = PeftModel.from_pretrained(model, adapter_path)
                model.eval()
                device = "CPU"
            
            self.models[name] = {"model": model, "tokenizer": tokenizer}
            print(f"   ✅ Loaded successfully on {device}!")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to load: {e}")
            return False
    
    def benchmark_single(self, name: str, prompt: str) -> BenchmarkResult:
        """Run single inference."""
        
        if name not in self.models:
            return BenchmarkResult(
                query=prompt,
                response="",
                total_ms=0,
                success=False,
                error="Model not loaded"
            )
        
        model = self.models[name]["model"]
        tokenizer = self.models[name]["tokenizer"]
        device = next(model.parameters()).device  # Get model's device
        
        try:
            start = time.perf_counter()
            
            inputs = tokenizer([prompt], return_tensors="pt").to(device)
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=50,
                    temperature=0.3,
                    do_sample=True,
                    use_cache=True
                )
            
            response = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
            # Extract just the response (remove prompt)
            response = response[len(prompt):].strip()
            
            end = time.perf_counter()
            total_ms = (end - start) * 1000
            
            return BenchmarkResult(
                query=prompt,
                response=response,
                total_ms=total_ms,
                success=True
            )
            
        except Exception as e:
            return BenchmarkResult(
                query=prompt,
                response="",
                total_ms=0,
                success=False,
                error=str(e)
            )
    
    def warmup(self, name: str, num_runs: int = 3):
        """Warm up model."""
        print(f"\n🔥 Warming up {name}...")
        for i in range(num_runs):
            self.benchmark_single(name, "P→Q,P?Q")
            print(f"   Warmup {i+1}/{num_runs} complete")
        print("   ✅ Ready!")
    
    def benchmark_suite(self, name: str, num_samples: int = 20):
        """Run full benchmark suite."""
        
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
        
        self.results[name] = []
        
        print(f"\n{'='*80}")
        print(f"🧪 BENCHMARKING: {name}")
        print(f"{'='*80}")
        print(f"🎯 {len(test_cases)} test cases × {num_samples} samples\n")
        
        for test_case in test_cases:
            print(f"Testing: {test_case}")
            
            for sample in range(num_samples):
                result = self.benchmark_single(name, test_case)
                self.results[name].append(result)
                
                if result.success:
                    print(f"   ✅ Sample {sample+1}: {result.total_ms:.1f}ms → {result.response[:20]}")
                else:
                    print(f"   ❌ Sample {sample+1}: {result.error}")
            
            print()
    
    def print_statistics(self, name: str):
        """Print statistics."""
        
        if name not in self.results:
            return
        
        successful = [r for r in self.results[name] if r.success]
        
        if not successful:
            print(f"❌ All failed for {name}")
            return
        
        latencies = [r.total_ms for r in successful]
        
        print(f"\n{'='*80}")
        print(f"📊 {name.upper()} RESULTS")
        print(f"{'='*80}")
        print()
        print(f"✅ Success: {len(successful)}/{len(self.results[name])}")
        print()
        print("⏱️  LATENCY")
        print(f"   Mean:   {statistics.mean(latencies):.2f} ms")
        print(f"   Median: {statistics.median(latencies):.2f} ms")
        print(f"   Min:    {min(latencies):.2f} ms")
        print(f"   Max:    {max(latencies):.2f} ms")
        print()
        
        # Recursive reasoning estimate
        mean_s = statistics.mean(latencies) / 1000
        print(f"🔄 RECURSIVE REASONING")
        print(f"   3-iter loop:  {mean_s * 3:.3f}s")
        print(f"   10-iter loop: {mean_s * 10:.3f}s")
        print(f"   Max iter/sec: {1/mean_s:.1f}")
        print()
        print("="*80)
    
    def print_comparison(self):
        """Compare all models."""
        
        if len(self.results) < 2:
            return
        
        print(f"\n{'='*80}")
        print("🔬 HEAD-TO-HEAD COMPARISON")
        print(f"{'='*80}\n")
        
        data = {}
        for name in self.results:
            successful = [r for r in self.results[name] if r.success]
            if successful:
                latencies = [r.total_ms for r in successful]
                data[name] = {
                    "mean": statistics.mean(latencies),
                    "median": statistics.median(latencies),
                }
        
        # Table
        print(f"{'Model':<25} {'Mean (ms)':>15} {'Median (ms)':>15}")
        print("-"*60)
        for name, stats in data.items():
            print(f"{name:<25} {stats['mean']:>15.2f} {stats['median']:>15.2f}")
        
        # Winner
        fastest = min(data.items(), key=lambda x: x[1]["mean"])
        print()
        print(f"🏆 WINNER: {fastest[0]} ({fastest[1]['mean']:.2f}ms mean)")
        
        mean_s = fastest[1]["mean"] / 1000
        print(f"\n🔄 BEST FOR RECURSIVE REASONING:")
        print(f"   3-iter: {mean_s * 3:.3f}s")
        
        if mean_s * 3 < 0.5:
            print("   ✅ EXCELLENT: Sub-500ms!")
        elif mean_s * 3 < 1.0:
            print("   ✅ GOOD: Sub-second!")
        else:
            print("   ⚠️  OK: >1s")
        
        print()
        print("="*80)


def main():
    """Main runner."""
    
    print("\n🎄 Ada-SLM Direct LoRA Benchmark 🎄")
    print("v4 (100% accuracy) vs v5b (80% accuracy)")
    print()
    
    ada_slm_dir = Path.home() / "Code" / "ada-slm"
    
    v4_path = ada_slm_dir / "ada-slm-v4" / "final"
    v5b_path = ada_slm_dir / "ada-slm-v5b-pure" / "final"
    
    # Check paths
    if not v4_path.exists():
        v4_path = ada_slm_dir / "ada-slm-v4"
    if not v5b_path.exists():
        v5b_path = ada_slm_dir / "ada-slm-v5b-pure"
    
    benchmarker = AdaSLMDirectBenchmark()
    
    models_to_test = []
    
    # Load v4
    if v4_path.exists():
        if benchmarker.load_model("ada-slm-v4", str(v4_path)):
            models_to_test.append("ada-slm-v4")
    
    # Load v5b
    if v5b_path.exists():
        if benchmarker.load_model("ada-slm-v5b-pure", str(v5b_path)):
            models_to_test.append("ada-slm-v5b-pure")
    
    if not models_to_test:
        print("\n❌ No models loaded!")
        return
    
    # Benchmark each
    for model in models_to_test:
        benchmarker.warmup(model)
        benchmarker.benchmark_suite(model, num_samples=20)
        benchmarker.print_statistics(model)
    
    # Compare
    if len(models_to_test) > 1:
        benchmarker.print_comparison()
    
    print("\n💜 Ada thinking in her own language! ✨")


if __name__ == "__main__":
    main()
