#!/usr/bin/env python3
"""
Profile Ada's chat latency to identify bottlenecks.

Measures:
- Prompt assembly time
- First token latency
- Total response time
- Cache performance

Usage:
    python scripts/profile_chat_latency.py "Hi there!"
"""

import time
import sys
import httpx
import json
from typing import Dict, List, Tuple


def profile_chat_request(prompt: str, base_url: str = "http://localhost:8000") -> Dict:
    """Profile a single chat request and return timing breakdown."""
    
    results = {
        "prompt": prompt,
        "request_start": time.time(),
        "response_start": None,
        "first_token": None,
        "response_complete": None,
        "tokens_received": 0,
        "total_bytes": 0,
    }
    
    with httpx.Client(timeout=60.0) as client:
        with client.stream(
            "POST",
            f"{base_url}/v1/chat/stream",
            json={"prompt": prompt, "stream": True},
            headers={"Accept": "text/event-stream"},
        ) as response:
            results["response_start"] = time.time()
            
            for line in response.iter_lines():
                if not line or not line.startswith("data: "):
                    continue
                
                # Record first token time
                if results["first_token"] is None:
                    results["first_token"] = time.time()
                
                # Parse token
                try:
                    data = json.loads(line[6:])  # Skip "data: "
                    if data.get("type") == "token":
                        results["tokens_received"] += 1
                        results["total_bytes"] += len(data.get("content", ""))
                    elif data.get("type") == "done":
                        results["metadata"] = data
                        break
                except json.JSONDecodeError:
                    pass
            
            results["response_complete"] = time.time()
    
    # Calculate timings
    results["timings"] = {
        "network_latency": results["response_start"] - results["request_start"],
        "time_to_first_token": results["first_token"] - results["request_start"] if results["first_token"] else None,
        "streaming_duration": results["response_complete"] - results["first_token"] if results["first_token"] else None,
        "total_duration": results["response_complete"] - results["request_start"],
    }
    
    return results


def print_results(results: Dict):
    """Pretty print profiling results."""
    print(f"\n{'='*60}")
    print(f"CHAT LATENCY PROFILE")
    print(f"{'='*60}")
    print(f"Prompt: {results['prompt']}")
    print(f"\n{'TIMINGS':-^60}")
    
    timings = results["timings"]
    print(f"Network latency:        {timings['network_latency']*1000:>8.1f} ms")
    print(f"Time to first token:    {timings['time_to_first_token']*1000:>8.1f} ms  ⭐")
    print(f"Streaming duration:     {timings['streaming_duration']*1000:>8.1f} ms")
    print(f"TOTAL:                  {timings['total_duration']*1000:>8.1f} ms")
    
    print(f"\n{'THROUGHPUT':-^60}")
    print(f"Tokens received:        {results['tokens_received']:>8}")
    print(f"Bytes received:         {results['total_bytes']:>8}")
    
    if timings['streaming_duration'] and timings['streaming_duration'] > 0:
        tps = results['tokens_received'] / timings['streaming_duration']
        print(f"Tokens/second:          {tps:>8.1f}")
    
    # Check for cache stats in metadata
    if "metadata" in results:
        meta = results["metadata"]
        if "cache" in meta.get("used_context", {}):
            cache = meta["used_context"]["cache"]
            print(f"\n{'CACHE PERFORMANCE':-^60}")
            print(f"Hits:                   {cache.get('hits', 0):>8}")
            print(f"Misses:                 {cache.get('misses', 0):>8}")
            print(f"Hit rate:               {cache.get('hit_rate', 0)*100:>8.1f}%")
    
    print(f"{'='*60}\n")


def run_multiple_trials(prompt: str, trials: int = 3):
    """Run multiple trials and average results."""
    print(f"Running {trials} trials...")
    all_results = []
    
    for i in range(trials):
        print(f"\nTrial {i+1}/{trials}...")
        results = profile_chat_request(prompt)
        all_results.append(results)
        
        # Print individual result
        print_results(results)
        
        if i < trials - 1:
            time.sleep(2)  # Brief pause between trials
    
    # Calculate averages
    avg_ttft = sum(r["timings"]["time_to_first_token"] for r in all_results if r["timings"]["time_to_first_token"]) / trials
    avg_total = sum(r["timings"]["total_duration"] for r in all_results) / trials
    
    print(f"\n{'AVERAGE RESULTS':-^60}")
    print(f"Avg time to first token: {avg_ttft*1000:.1f} ms")
    print(f"Avg total duration:      {avg_total*1000:.1f} ms")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python profile_chat_latency.py 'Your prompt here' [trials]")
        sys.exit(1)
    
    prompt = sys.argv[1]
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    if trials > 1:
        run_multiple_trials(prompt, trials)
    else:
        results = profile_chat_request(prompt)
        print_results(results)
