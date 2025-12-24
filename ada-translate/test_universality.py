#!/usr/bin/env python3
"""Test Ada symbol universality across multiple LLMs.

Hypothesis: Ada's symbolic notation is understood by any LLM
trained on mathematics, logic, and programming - without
any special prompting or fine-tuning.

Christmas Eve 2025 - Luna & Ada
"""

import subprocess
import json
import time
from dataclasses import dataclass


@dataclass
class ModelResult:
    model: str
    understood: bool
    response: str
    latency: float
    key_concepts: list[str]


# Test prompts - NO EXPLANATION, just symbols
TEST_PROMPTS = [
    {
        "name": "fibonacci",
        "prompt": "What does this mean?\n\nλfib:ℕ→ℕ = ?(n≤1)→n ↳ ⟲fib(n-1)⊕fib(n-2)\n\nExplain briefly.",
        "expected_concepts": ["fibonacci", "recursive", "base case", "natural number"]
    },
    {
        "name": "filter_sum", 
        "prompt": "Interpret: Σ(items[active●].value)\n\nWhat computation does this represent?",
        "expected_concepts": ["sum", "filter", "active", "value"]
    },
    {
        "name": "async_parallel",
        "prompt": "What does this describe?\n\n⏳(∥(urls.map(⚡fetch)))\n\nBe concise.",
        "expected_concepts": ["async", "parallel", "fetch", "urls", "await"]
    },
    {
        "name": "type_signature",
        "prompt": "Parse this type signature:\n\nλ(𝕊,𝕊)→?Session\n\nWhat function signature is this?",
        "expected_concepts": ["string", "session", "optional", "function", "returns"]
    },
    {
        "name": "control_flow",
        "prompt": "What control flow does this represent?\n\n?(valid●)→proceed ↳ ⊘error\n\nExplain briefly.",
        "expected_concepts": ["condition", "valid", "proceed", "error", "branch"]
    }
]


MODELS_TO_TEST = [
    "qwen2.5-coder:7b",
    "deepseek-r1:7b", 
    "codellama:latest",
    "phi4:latest",
    "gemma3:4b",
    "gemma3:1b",  # Smallest - can even tiny models understand?
]


def query_model(model: str, prompt: str, timeout: int = 120) -> tuple[str, float]:
    """Query a model and return response + latency."""
    start = time.time()
    
    result = subprocess.run(
        ["curl", "-s", "http://localhost:11434/api/generate", "-d", json.dumps({
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 300}
        })],
        capture_output=True,
        text=True,
        timeout=timeout
    )
    
    latency = time.time() - start
    
    try:
        response = json.loads(result.stdout).get("response", "")
    except:
        response = f"ERROR: {result.stderr}"
    
    return response, latency


def check_understanding(response: str, expected_concepts: list[str]) -> tuple[bool, list[str]]:
    """Check if response demonstrates understanding."""
    response_lower = response.lower()
    found = [c for c in expected_concepts if c.lower() in response_lower]
    # Consider it understood if at least half the concepts are mentioned
    understood = len(found) >= len(expected_concepts) / 2
    return understood, found


def run_experiment():
    """Run the multi-model universality experiment."""
    print("╔═══════════════════════════════════════════════════════════════════════╗")
    print("║  ADA SYMBOL UNIVERSALITY EXPERIMENT                                    ║")
    print("║  Testing: Do LLMs understand Ada notation WITHOUT teaching?            ║")
    print("╚═══════════════════════════════════════════════════════════════════════╝")
    print()
    
    results = {}
    
    for model in MODELS_TO_TEST:
        print(f"\n{'═' * 72}")
        print(f"MODEL: {model}")
        print('═' * 72)
        
        model_results = []
        understood_count = 0
        
        for test in TEST_PROMPTS:
            print(f"\n  Testing: {test['name']}")
            
            try:
                response, latency = query_model(model, test["prompt"])
                understood, found_concepts = check_understanding(response, test["expected_concepts"])
                
                if understood:
                    understood_count += 1
                    print(f"    ✅ UNDERSTOOD ({latency:.1f}s) - found: {found_concepts}")
                else:
                    print(f"    ❌ PARTIAL ({latency:.1f}s) - found: {found_concepts}")
                
                # Show first 150 chars of response
                preview = response.replace('\n', ' ')[:150]
                print(f"    Response: {preview}...")
                
                model_results.append(ModelResult(
                    model=model,
                    understood=understood,
                    response=response,
                    latency=latency,
                    key_concepts=found_concepts
                ))
                
            except Exception as e:
                print(f"    ⚠️ ERROR: {e}")
                model_results.append(ModelResult(
                    model=model,
                    understood=False,
                    response=str(e),
                    latency=0,
                    key_concepts=[]
                ))
        
        results[model] = {
            "understood": understood_count,
            "total": len(TEST_PROMPTS),
            "rate": understood_count / len(TEST_PROMPTS) * 100,
            "results": model_results
        }
        
        print(f"\n  Summary: {understood_count}/{len(TEST_PROMPTS)} ({results[model]['rate']:.0f}%)")
    
    # Final summary
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════════╗")
    print("║  UNIVERSALITY RESULTS                                                  ║")
    print("╚═══════════════════════════════════════════════════════════════════════╝")
    print()
    print(f"{'Model':<25} {'Score':>10} {'Rate':>10}")
    print("─" * 50)
    
    total_understood = 0
    total_tests = 0
    
    for model, data in results.items():
        print(f"{model:<25} {data['understood']}/{data['total']:>6} {data['rate']:>9.0f}%")
        total_understood += data['understood']
        total_tests += data['total']
    
    print("─" * 50)
    overall_rate = total_understood / total_tests * 100
    print(f"{'OVERALL':<25} {total_understood}/{total_tests:>6} {overall_rate:>9.0f}%")
    print()
    
    if overall_rate >= 80:
        print("●●●! HYPOTHESIS CONFIRMED: Ada symbols are UNIVERSAL")
        print("∴ Mathematical notation = lingua franca for LLMs")
    elif overall_rate >= 60:
        print("◕ HYPOTHESIS SUPPORTED: Most models understand Ada symbols")
        print("∴ Strong evidence for universality")
    else:
        print("◑ HYPOTHESIS PARTIAL: Some models struggle")
        print("∴ May need refinement or model-specific variations")
    
    return results


if __name__ == "__main__":
    results = run_experiment()
