#!/usr/bin/env python3
"""Benchmark Ada's Dense Notation System.

Christmas Eve 2025 - Let's see what this language can do.

This script tests:
1. Can an LLM produce valid dense notation?
2. What's the actual compression ratio?
3. How does reasoning quality compare?
"""

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Optional

import httpx

from brain.reasoning.dense_thinking import (
    DENSE_SYSTEM_PROMPT,
    HYBRID_SYSTEM_PROMPT,
    DenseThinkingAnalyzer,
    ThinkingMode,
)
from brain.reasoning.ada_symbols import (
    get_all_chars,
    confidence_to_certainty,
    importance_to_attention,
    calculate_compression_ratio,
    ALL_SYMBOLS,
)


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""
    prompt: str
    mode: ThinkingMode
    response: str
    tokens_in: int
    tokens_out: int
    latency_ms: float
    symbols_used: int
    unique_symbols: set
    compression_ratio: float
    has_tool_call: bool
    has_certainty: bool
    has_attention: bool


BENCHMARK_PROMPTS = [
    # Simple factual
    "What is 2+2?",
    
    # Requires reasoning
    "If Alice is taller than Bob, and Bob is taller than Carol, who is shortest?",
    
    # Code-related
    "How would you reverse a string in Python?",
    
    # Multi-step
    "List the steps to make a peanut butter sandwich.",
    
    # Abstract reasoning
    "What's the relationship between compression and intelligence?",
    
    # Tool use scenario (simulated)
    "What files are in the brain/ directory?",
]


async def run_ollama_query(
    prompt: str,
    system_prompt: str,
    model: str = "qwen2.5-coder:7b"
) -> tuple[str, int, int, float]:
    """Run a query against Ollama and return response + metrics."""
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        start = time.perf_counter()
        
        response = await client.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 500,
                }
            }
        )
        
        latency_ms = (time.perf_counter() - start) * 1000
        
        data = response.json()
        return (
            data.get("response", ""),
            data.get("prompt_eval_count", 0),
            data.get("eval_count", 0),
            latency_ms
        )


def analyze_response(response: str, mode: ThinkingMode) -> dict:
    """Analyze a response for dense notation usage."""
    
    symbol_chars = set(get_all_chars())
    
    symbols_found = []
    unique_symbols = set()
    
    for char in response:
        if char in symbol_chars:
            symbols_found.append(char)
            unique_symbols.add(char)
    
    # Check for specific patterns
    has_tool_call = '⚡' in response or 'TOOL_REQUEST' in response
    
    certainty_chars = {'●', '◕', '◑', '◔', '○'}
    has_certainty = bool(unique_symbols & certainty_chars)
    
    attention_chars = {'★', '☆', '◆', '◇'}
    has_attention = bool(unique_symbols & attention_chars)
    
    # Calculate compression
    compression = calculate_compression_ratio(response)
    
    return {
        'symbols_used': len(symbols_found),
        'unique_symbols': unique_symbols,
        'compression_ratio': compression,
        'has_tool_call': has_tool_call,
        'has_certainty': has_certainty,
        'has_attention': has_attention,
    }


async def benchmark_single(
    prompt: str,
    mode: ThinkingMode,
    model: str = "qwen2.5-coder:7b"
) -> BenchmarkResult:
    """Run a single benchmark."""
    
    if mode == ThinkingMode.DENSE:
        system = DENSE_SYSTEM_PROMPT
    elif mode == ThinkingMode.HYBRID:
        system = HYBRID_SYSTEM_PROMPT
    else:
        system = "You are a helpful assistant. Think through problems step by step."
    
    response, tokens_in, tokens_out, latency = await run_ollama_query(
        prompt, system, model
    )
    
    analysis = analyze_response(response, mode)
    
    return BenchmarkResult(
        prompt=prompt,
        mode=mode,
        response=response,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        latency_ms=latency,
        **analysis
    )


async def run_benchmark_suite(model: str = "qwen2.5-coder:7b"):
    """Run the full benchmark suite."""
    
    print("=" * 70)
    print("ADA DENSE NOTATION BENCHMARK")
    print(f"Model: {model}")
    print(f"Symbol vocabulary: {len(ALL_SYMBOLS)} symbols")
    print("=" * 70)
    print()
    
    results = {
        ThinkingMode.DENSE: [],
        ThinkingMode.HYBRID: [],
        ThinkingMode.EXPANDED: [],
    }
    
    for prompt in BENCHMARK_PROMPTS:
        print(f"\n{'─' * 70}")
        print(f"PROMPT: {prompt}")
        print('─' * 70)
        
        for mode in [ThinkingMode.DENSE, ThinkingMode.EXPANDED]:
            try:
                result = await benchmark_single(prompt, mode, model)
                results[mode].append(result)
                
                print(f"\n[{mode.value.upper()}]")
                print(f"  Response ({result.tokens_out} tokens, {result.latency_ms:.0f}ms):")
                
                # Truncate long responses for display
                display_response = result.response[:300]
                if len(result.response) > 300:
                    display_response += "..."
                
                for line in display_response.split('\n')[:8]:
                    print(f"    {line}")
                
                if result.symbols_used > 0:
                    print(f"  Symbols: {result.symbols_used} used, {len(result.unique_symbols)} unique")
                    print(f"  Unique: {result.unique_symbols}")
                    print(f"  Compression: {result.compression_ratio:.2f}x")
                    print(f"  Certainty: {'✓' if result.has_certainty else '✗'}")
                    print(f"  Attention: {'✓' if result.has_attention else '✗'}")
                    
            except Exception as e:
                print(f"  ERROR: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    for mode in [ThinkingMode.DENSE, ThinkingMode.EXPANDED]:
        mode_results = results[mode]
        if not mode_results:
            continue
            
        avg_tokens = sum(r.tokens_out for r in mode_results) / len(mode_results)
        avg_latency = sum(r.latency_ms for r in mode_results) / len(mode_results)
        avg_symbols = sum(r.symbols_used for r in mode_results) / len(mode_results)
        avg_compression = sum(r.compression_ratio for r in mode_results) / len(mode_results)
        
        certainty_rate = sum(1 for r in mode_results if r.has_certainty) / len(mode_results)
        attention_rate = sum(1 for r in mode_results if r.has_attention) / len(mode_results)
        
        print(f"\n{mode.value.upper()}:")
        print(f"  Avg tokens out: {avg_tokens:.1f}")
        print(f"  Avg latency: {avg_latency:.0f}ms")
        print(f"  Avg symbols: {avg_symbols:.1f}")
        print(f"  Avg compression: {avg_compression:.2f}x")
        print(f"  Certainty usage: {certainty_rate*100:.0f}%")
        print(f"  Attention usage: {attention_rate*100:.0f}%")
    
    # Token savings calculation
    if results[ThinkingMode.DENSE] and results[ThinkingMode.EXPANDED]:
        dense_tokens = sum(r.tokens_out for r in results[ThinkingMode.DENSE])
        expanded_tokens = sum(r.tokens_out for r in results[ThinkingMode.EXPANDED])
        
        if expanded_tokens > 0:
            savings = (1 - dense_tokens / expanded_tokens) * 100
            print(f"\nTOKEN SAVINGS: {savings:.1f}% fewer tokens in dense mode")
    
    return results


if __name__ == "__main__":
    print("\n🎄 Christmas Eve 2025 - Testing Ada's Native Language 🎄\n")
    asyncio.run(run_benchmark_suite())
