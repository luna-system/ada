#!/usr/bin/env python3
"""Benchmark suite for ada-translate accuracy.

Tests:
1. Roundtrip fidelity (A → B → A)
2. Semantic preservation (does the code DO the same thing?)
3. Comment handling
4. Cross-language idiom translation

Christmas Eve 2025 - Luna & Ada
"""

import asyncio
import subprocess
import sys
import json
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class TestCase:
    """A single translation test case."""
    name: str
    source_code: str
    source_lang: str
    target_lang: str
    # Optional: expected semantic patterns in output
    expected_patterns: list[str] = field(default_factory=list)
    # Optional: patterns that should NOT appear
    forbidden_patterns: list[str] = field(default_factory=list)
    # Does this test comments?
    tests_comments: bool = False


@dataclass 
class TestResult:
    """Result of a translation test."""
    test_name: str
    success: bool
    source_code: str
    target_code: str
    semantic_core: str
    roundtrip_code: Optional[str] = None
    roundtrip_semantic: Optional[str] = None
    error: Optional[str] = None
    patterns_found: list[str] = field(default_factory=list)
    patterns_missing: list[str] = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST CASES
# ═══════════════════════════════════════════════════════════════════════════════

TEST_CASES = [
    # Basic recursion
    TestCase(
        name="fibonacci_recursion",
        source_code="""def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)""",
        source_lang="python",
        target_lang="rust",
        expected_patterns=["fn fib", "if", "<=", "fib(n"],
    ),
    
    # Higher-order functions
    TestCase(
        name="filter_map_reduce",
        source_code="""const sumActive = items
    .filter(i => i.active)
    .map(i => i.value)
    .reduce((a, b) => a + b, 0);""",
        source_lang="javascript",
        target_lang="python",
        expected_patterns=["filter", "sum", "lambda"],
    ),
    
    # Async/await patterns
    TestCase(
        name="async_fetch",
        source_code="""async def fetch_all(urls):
    import httpx
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        return await asyncio.gather(*tasks)""",
        source_lang="python",
        target_lang="javascript",
        expected_patterns=["async", "await", "Promise", "fetch"],
    ),
    
    # Pattern matching / conditionals
    TestCase(
        name="pattern_matching",
        source_code="""fn describe(n: i32) -> &'static str {
    match n {
        0 => "zero",
        1..=9 => "single digit",
        10..=99 => "double digit", 
        _ => "large"
    }
}""",
        source_lang="rust",
        target_lang="python",
        expected_patterns=["def describe", "if", "elif", "return"],
    ),
    
    # Class/struct with methods
    TestCase(
        name="class_with_methods",
        source_code="""class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def distance(self, other):
        return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5""",
        source_lang="python",
        target_lang="rust",
        expected_patterns=["struct Point", "impl", "fn distance", "f64"],
    ),
    
    # Comments preservation test
    TestCase(
        name="comment_handling",
        source_code="""# Calculate factorial of n
# Uses recursive approach
def factorial(n):
    # Base case
    if n <= 1:
        return 1
    # Recursive case  
    return n * factorial(n - 1)""",
        source_lang="python",
        target_lang="rust",
        expected_patterns=["//", "factorial"],
        tests_comments=True,
    ),
    
    # Error handling patterns
    TestCase(
        name="error_handling",
        source_code="""fn divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        Err("Division by zero".to_string())
    } else {
        Ok(a / b)
    }
}""",
        source_lang="rust", 
        target_lang="python",
        expected_patterns=["def divide", "raise", "return"],
    ),
    
    # List comprehension / functional
    TestCase(
        name="list_comprehension",
        source_code="""squares = [x**2 for x in range(10) if x % 2 == 0]""",
        source_lang="python",
        target_lang="haskell",
        expected_patterns=["[", "|", "^", "mod", "=="],
    ),
]


# ═══════════════════════════════════════════════════════════════════════════════
# TRANSLATION RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

def run_translation(source_code: str, source_lang: str, target_lang: str) -> tuple[str, str]:
    """Run ada-translate and return (target_code, semantic_core)."""
    result = subprocess.run(
        ["uv", "run", "ada-translate", "--from", source_lang, "--to", target_lang, "-s"],
        input=source_code,
        capture_output=True,
        text=True,
        cwd="/home/luna/Code/ada-v1/ada-translate"
    )
    
    output = result.stdout
    
    # Parse output - find semantic core and target code
    semantic_core = ""
    target_code = ""
    
    if "SEMANTIC CORE" in output:
        parts = output.split("═" * 60)
        for i, part in enumerate(parts):
            if "SEMANTIC CORE" in part and i + 1 < len(parts):
                semantic_core = parts[i + 1].strip()
            if "TARGET CODE" in part and i + 1 < len(parts):
                target_code = parts[i + 1].strip()
    
    # Clean up markdown fences
    for fence in ["```semantic", "```python", "```rust", "```javascript", 
                  "```haskell", "```go", "```", "```typescript"]:
        semantic_core = semantic_core.replace(fence, "")
        target_code = target_code.replace(fence, "")
    
    return target_code.strip(), semantic_core.strip()


def run_test(test: TestCase, do_roundtrip: bool = True) -> TestResult:
    """Run a single test case."""
    try:
        # Forward translation
        target_code, semantic_core = run_translation(
            test.source_code, test.source_lang, test.target_lang
        )
        
        # Check expected patterns
        patterns_found = []
        patterns_missing = []
        for pattern in test.expected_patterns:
            if pattern.lower() in target_code.lower():
                patterns_found.append(pattern)
            else:
                patterns_missing.append(pattern)
        
        # Roundtrip if requested
        roundtrip_code = None
        roundtrip_semantic = None
        if do_roundtrip:
            roundtrip_code, roundtrip_semantic = run_translation(
                target_code, test.target_lang, test.source_lang
            )
        
        success = len(patterns_missing) == 0
        
        return TestResult(
            test_name=test.name,
            success=success,
            source_code=test.source_code,
            target_code=target_code,
            semantic_core=semantic_core,
            roundtrip_code=roundtrip_code,
            roundtrip_semantic=roundtrip_semantic,
            patterns_found=patterns_found,
            patterns_missing=patterns_missing,
        )
        
    except Exception as e:
        return TestResult(
            test_name=test.name,
            success=False,
            source_code=test.source_code,
            target_code="",
            semantic_core="",
            error=str(e),
        )


# ═══════════════════════════════════════════════════════════════════════════════
# BENCHMARK RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

def run_benchmark(do_roundtrip: bool = True) -> list[TestResult]:
    """Run all benchmark tests."""
    results = []
    
    print("╔═══════════════════════════════════════════════════════════════════════╗")
    print("║  ADA-TRANSLATE ACCURACY BENCHMARK                                      ║")
    print("╚═══════════════════════════════════════════════════════════════════════╝")
    print()
    
    for i, test in enumerate(TEST_CASES, 1):
        print(f"[{i}/{len(TEST_CASES)}] Testing: {test.name}")
        print(f"    {test.source_lang} → {test.target_lang}", end="")
        if do_roundtrip:
            print(f" → {test.source_lang}", end="")
        print()
        
        result = run_test(test, do_roundtrip)
        results.append(result)
        
        if result.success:
            print(f"    ✅ PASS - patterns found: {result.patterns_found}")
        else:
            print(f"    ❌ FAIL - missing: {result.patterns_missing}")
            if result.error:
                print(f"    Error: {result.error}")
        print()
    
    return results


def analyze_results(results: list[TestResult]) -> dict:
    """Analyze benchmark results."""
    passed = sum(1 for r in results if r.success)
    failed = len(results) - passed
    
    # Analyze semantic preservation
    semantic_patterns = []
    for r in results:
        if r.semantic_core:
            # Count Ada symbols in semantic core
            symbols = "→⟲?∥⏳∧∨¬⟹∃∄∈∅←⊕⊖↻λ∘∀ΣΠℕℤℝ𝕊𝔹"
            count = sum(1 for c in r.semantic_core if c in symbols)
            semantic_patterns.append({
                "test": r.test_name,
                "symbol_count": count,
                "semantic_length": len(r.semantic_core),
                "source_length": len(r.source_code),
                "compression": len(r.source_code) / max(len(r.semantic_core), 1),
            })
    
    # Analyze roundtrip fidelity
    roundtrip_scores = []
    for r in results:
        if r.roundtrip_code:
            # Simple similarity: shared tokens
            source_tokens = set(r.source_code.split())
            roundtrip_tokens = set(r.roundtrip_code.split())
            if source_tokens:
                overlap = len(source_tokens & roundtrip_tokens) / len(source_tokens)
                roundtrip_scores.append(overlap)
    
    return {
        "total_tests": len(results),
        "passed": passed,
        "failed": failed,
        "pass_rate": passed / len(results) * 100,
        "avg_compression": sum(s["compression"] for s in semantic_patterns) / len(semantic_patterns) if semantic_patterns else 0,
        "avg_roundtrip_similarity": sum(roundtrip_scores) / len(roundtrip_scores) * 100 if roundtrip_scores else 0,
        "semantic_patterns": semantic_patterns,
    }


def print_report(results: list[TestResult], analysis: dict):
    """Print detailed benchmark report."""
    print()
    print("═" * 72)
    print("BENCHMARK RESULTS")
    print("═" * 72)
    print()
    print(f"Pass Rate:              {analysis['pass_rate']:.1f}% ({analysis['passed']}/{analysis['total_tests']})")
    print(f"Avg Compression:        {analysis['avg_compression']:.2f}x")
    print(f"Avg Roundtrip Fidelity: {analysis['avg_roundtrip_similarity']:.1f}%")
    print()
    
    print("─" * 72)
    print("SEMANTIC CORE ANALYSIS")
    print("─" * 72)
    for sp in analysis["semantic_patterns"]:
        print(f"  {sp['test']:25} | symbols: {sp['symbol_count']:2} | compression: {sp['compression']:.2f}x")
    print()
    
    print("─" * 72)
    print("DETAILED RESULTS")
    print("─" * 72)
    for r in results:
        status = "✅" if r.success else "❌"
        print(f"\n{status} {r.test_name}")
        print(f"   Semantic Core Preview: {r.semantic_core[:80]}..." if len(r.semantic_core) > 80 else f"   Semantic Core: {r.semantic_core}")
        if r.roundtrip_code:
            print(f"   Roundtrip Preview: {r.roundtrip_code[:60]}..." if len(r.roundtrip_code) > 60 else f"   Roundtrip: {r.roundtrip_code}")


def save_results(results: list[TestResult], analysis: dict, filename: str):
    """Save results to JSON file."""
    data = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "pass_rate": analysis["pass_rate"],
            "avg_compression": analysis["avg_compression"],
            "avg_roundtrip_similarity": analysis["avg_roundtrip_similarity"],
        },
        "results": [
            {
                "name": r.test_name,
                "success": r.success,
                "source": r.source_code,
                "target": r.target_code,
                "semantic": r.semantic_core,
                "roundtrip": r.roundtrip_code,
            }
            for r in results
        ]
    }
    
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nResults saved to: {filename}")


if __name__ == "__main__":
    results = run_benchmark(do_roundtrip=True)
    analysis = analyze_results(results)
    print_report(results, analysis)
    save_results(results, analysis, "benchmark_results.json")
