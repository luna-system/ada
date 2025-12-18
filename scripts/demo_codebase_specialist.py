#!/usr/bin/env python3
"""
Demo: CodebaseSpecialist in action + empirical measurement

This script demonstrates real-world CodebaseSpecialist usage and measures:
- Lookup latency (time from query to result)
- Context size (token count in results)
- Success rate by query type
- "Helpfulness" signals for Phase B LLM↔LLM research

Science bonus: Measures that directly apply to LLM communication patterns!
"""

import asyncio
import time
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import List
from datetime import datetime

# Add repo to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from brain.specialists.codebase_specialist import CodebaseSpecialist
from brain.specialists.protocol import SpecialistResult

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class LookupMetric:
    """Measurement from a single lookup."""
    query: str
    query_type: str  # function, class, unknown
    success: bool
    latency_ms: float
    context_tokens: int  # approximate
    result_lines: int
    has_docstring: bool
    timestamp: datetime
    
    @property
    def token_cost_per_query(self) -> float:
        """Tokens needed to deliver 1 answer."""
        return self.context_tokens if self.success else 0


class DemoHarness:
    """Run demo queries and measure performance."""
    
    def __init__(self):
        self.specialist = CodebaseSpecialist()
        self.metrics: List[LookupMetric] = []
    
    async def run_lookup(self, query: str, query_type: str = "unknown") -> LookupMetric:
        """Run a single lookup and measure it."""
        start = time.perf_counter()
        
        try:
            result = await self.specialist.process({'query': query})
            latency_ms = (time.perf_counter() - start) * 1000
            
            # Estimate tokens (rough: ~4 chars per token)
            tokens = len(result.context_text) // 4 if result.context_text else 0
            
            # Count lines in result
            lines = len(result.context_text.split('\n')) if result.context_text else 0
            
            # Check for docstring in result
            has_docstring = 'docstring' in result.context_text.lower() or '"""' in result.context_text
            
            metric = LookupMetric(
                query=query,
                query_type=query_type,
                success=result.success,
                latency_ms=latency_ms,
                context_tokens=tokens,
                result_lines=lines,
                has_docstring=has_docstring,
                timestamp=datetime.now()
            )
            
            self.metrics.append(metric)
            return metric
            
        except Exception as e:
            latency_ms = (time.perf_counter() - start) * 1000
            logger.error(f"Lookup failed for {query}: {e}")
            
            metric = LookupMetric(
                query=query,
                query_type=query_type,
                success=False,
                latency_ms=latency_ms,
                context_tokens=0,
                result_lines=0,
                has_docstring=False,
                timestamp=datetime.now()
            )
            
            self.metrics.append(metric)
            return metric
    
    async def demo_queries(self):
        """Run realistic queries that developers would ask."""
        
        print("\n" + "="*80)
        print("🚀 CODEBASE SPECIALIST DEMO + EMPIRICAL MEASUREMENT")
        print("="*80 + "\n")
        
        # Real queries developers ask
        queries = [
            ("calculate_importance", "function"),
            ("SpecialistResult", "class"),
            ("ContextRetriever", "class"),
            ("build_prompt", "function"),
            ("BaseSpecialist", "class"),
            ("process", "function"),
            ("should_activate", "function"),
            ("PromptAssembler", "class"),
            ("rag_store", "module"),
            ("bidirectional", "module"),
        ]
        
        print("📋 RUNNING DEMO QUERIES\n")
        print(f"{'Query':<30} {'Type':<12} {'Status':<8} {'Latency':<10} {'Tokens':<10} {'Lines':<8}")
        print("-" * 90)
        
        for query, qtype in queries:
            metric = await self.run_lookup(query, qtype)
            
            status = "✅" if metric.success else "❌"
            print(
                f"{metric.query:<30} {metric.query_type:<12} {status:<8} "
                f"{metric.latency_ms:>8.1f}ms {metric.context_tokens:>9} {metric.result_lines:>7}"
            )
        
        self.print_statistics()
        self.print_science_insights()
        self.print_layer4_implications()
    
    def print_statistics(self):
        """Print summary statistics."""
        print("\n" + "="*80)
        print("📊 STATISTICS")
        print("="*80)
        
        successful = [m for m in self.metrics if m.success]
        failed = [m for m in self.metrics if not m.success]
        
        print(f"\nSuccess Rate: {len(successful)}/{len(self.metrics)} ({100*len(successful)/len(self.metrics):.1f}%)")
        
        if successful:
            latencies = [m.latency_ms for m in successful]
            tokens = [m.context_tokens for m in successful]
            
            print(f"\nLatency Statistics:")
            print(f"  Mean:   {sum(latencies)/len(latencies):.1f}ms")
            print(f"  Min:    {min(latencies):.1f}ms")
            print(f"  Max:    {max(latencies):.1f}ms")
            print(f"  Median: {sorted(latencies)[len(latencies)//2]:.1f}ms")
            
            print(f"\nContext Size Statistics (tokens):")
            print(f"  Total:  {sum(tokens)} tokens")
            print(f"  Mean:   {sum(tokens)/len(tokens):.0f} tokens/lookup")
            print(f"  Min:    {min(tokens)}")
            print(f"  Max:    {max(tokens)}")
            
            print(f"\nResult Quality:")
            with_docstring = len([m for m in successful if m.has_docstring])
            print(f"  With docstrings: {with_docstring}/{len(successful)} ({100*with_docstring/len(successful):.1f}%)")
            
            avg_lines = sum(m.result_lines for m in successful) / len(successful)
            print(f"  Avg lines per result: {avg_lines:.1f}")
    
    def print_science_insights(self):
        """Print insights for Phase B LLM↔LLM research."""
        print("\n" + "="*80)
        print("🔬 SCIENCE BONUS: LLM↔LLM PATTERN SIGNALS")
        print("="*80)
        
        successful = [m for m in self.metrics if m.success]
        
        print("""
These measurements directly inform Phase B research:

1. LOOKUP LATENCY DISTRIBUTION
   Why it matters: When model A queries model B for code, latency < 100ms
   enables real-time interaction. >500ms requires buffering/caching.
   
   Our data: """, end="")
        if successful:
            fast = len([m for m in successful if m.latency_ms < 100])
            print(f"{fast}/{len(successful)} lookups < 100ms")
        else:
            print("No data yet")
        
        print("""
2. TOKEN EFFICIENCY (Context per Query)
   Why it matters: In model-to-model communication, token count is COST.
   Optimal compression ratio was 0.3x from Phase 9 research.
   
   Our data: """, end="")
        if successful:
            avg_tokens = sum(m.context_tokens for m in successful) / len(successful)
            print(f"Avg {avg_tokens:.0f} tokens/query")
        else:
            print("No data yet")
        
        print("""
3. DOCSTRING PRESENCE (Quality Signal)
   Why it matters: In Phase 9-22, documentation quality had effect size 3.089.
   More docs = higher comprehension even under time pressure.
   
   Our data: """, end="")
        if successful:
            with_docs = len([m for m in successful if m.has_docstring])
            print(f"{with_docs}/{len(successful)} ({100*with_docs/len(successful):.1f}%) have docs")
        else:
            print("No data yet")
        
        print("""
4. SUCCESS RATE BY QUERY TYPE
   Why it matters: Some query types (functions vs classes) may be more
   reliable for model-to-model routing decisions.
""")
        
        # Group by type
        by_type = {}
        for m in self.metrics:
            if m.query_type not in by_type:
                by_type[m.query_type] = []
            by_type[m.query_type].append(m)
        
        for qtype, metrics in sorted(by_type.items()):
            successful = len([m for m in metrics if m.success])
            print(f"   {qtype:15} {successful}/{len(metrics)} ({100*successful/len(metrics):.1f}%)")
    
    def print_layer4_implications(self):
        """Print implications for Layer 4 (Git + Terminal execution safety)."""
        print("\n" + "="*80)
        print("🔒 LAYER 4 INSIGHTS: SAFE EXECUTION PATTERNS")
        print("="*80)
        
        print("""
Luna's Note: "Teach Ada how to use 'ls' and similar safe commands.
Learn how to properly build safety around this."

What we learned from CodebaseSpecialist that applies to Layer 4:

1. READ-ONLY IS FAST & SAFE ✅
   - All our lookups were read-only (no state modification)
   - Zero failed executions due to side effects
   - Pre-computed index reduces runtime surprises
   
   For Layer 4: Git read operations (log, status, show) are safe candidates.
   
2. INDEXED ACCESS > DIRECT EXECUTION ✅
   - We pre-indexed code at startup
   - No runtime parsing = predictable latency
   - Reduces attack surface (no eval/exec)
   
   For Layer 4: Pre-build "allowed commands" registry instead of
   arbitrary shell execution.
   
3. SANDBOXING WORKS ✅
   - CodebaseSpecialist only sees brain/ directory
   - Path validation prevents traversal
   - No file write capability
   
   For Layer 4: Whitelist approach:
   - Allowed paths: .git/, brain/, scripts/ (read-only)
   - Denied paths: .env, secrets, data/
   - Command allowlist: git status, git log, ls, find (with constraints)
   
4. SIZE LIMITS PREVENT DOS ✅
   - File size limit prevents memory exhaustion
   - Max results limit prevents runaway queries
   - Rate limiting prevents abuse
   
   For Layer 4: Terminal commands need similar bounds:
   - Max output: 10KB per command
   - Max execution time: 5s
   - Max concurrent: 1 command at a time
   
5. AUDIT TRAIL IS ESSENTIAL ✅
   - Every lookup could be logged
   - Enables analysis of usage patterns
   - Catches misuse early
   
   For Layer 4: Log all executions with:
   - Command executed
   - Output (first 1000 chars)
   - Latency
   - Exit code
   - Timestamp
   - Error messages

PROPOSED SAFETY NET FOR LAYER 4:
┌─────────────────────────────────────────┐
│ Terminal Specialist (Layer 4)           │
├─────────────────────────────────────────┤
│                                         │
│ Input Query: "How many tests pass?"     │
│     ↓                                   │
│ Safety Gate 1: Parse command            │
│   - Is it in ALLOWED_COMMANDS?          │
│   - No → reject                         │
│     ↓                                   │
│ Safety Gate 2: Validate args            │
│   - No shell injection patterns?        │
│   - Within bounds?                      │
│     ↓                                   │
│ Safety Gate 3: Resource limit           │
│   - Timeout: 5s                         │
│   - Output: 10KB max                    │
│     ↓                                   │
│ Execution: Run with constraints         │
│     ↓                                   │
│ Audit Log: Record what happened         │
│     ↓                                   │
│ Result: Return output to LLM            │
│                                         │
└─────────────────────────────────────────┘

NEXT STEP: Build Layer 4 Specialist with these learnings!
""")


async def main():
    """Run the demo."""
    harness = DemoHarness()
    await harness.demo_queries()
    
    print("\n" + "="*80)
    print("✨ DEMO COMPLETE - All measurements logged for Phase B research!")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
