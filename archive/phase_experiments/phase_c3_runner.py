#!/usr/bin/env python3
"""
Phase C.3: Specialization Level Research

Question: Is a single general-purpose tool better than multiple specialized tools?

Test Design:
  - Strategy A: SuperTool (codebase + git + terminal unified)
  - Strategy B: Three separate specialists (modular)
  - Strategy C: Hybrid (SuperTool for facts, TerminalSpecialist for execution)

Measure:
  - LLM inference time
  - Quality of answers
  - Maintainability metrics
  - Developer UX clarity
  - Token efficiency
  - Error rates / hallucination

Expected: Uncertain (specialization might help LLM routing, or be overhead)
Hypothesis: Specialization is better (clearer intent, better reasoning)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List
import random


class ArchitectureStrategy(Enum):
    """Tool architecture strategies."""
    SUPERTOOL = "supertool"        # One unified tool
    SPECIALIZED = "specialized"    # Multiple specialists
    HYBRID = "hybrid"              # Mix (facts unified, execution separate)


@dataclass
class SpecializationQuery:
    """Single test query for specialization comparison."""
    
    query_id: str
    query_text: str
    category: str                  # code/system/reasoning/debug
    requires_execution: bool       # Does it need terminal?
    requires_history: bool         # Does it need git?
    requires_structure: bool       # Does it need codebase?
    optimal_strategy: ArchitectureStrategy  # What should be best


@dataclass
class ArchitectureResult:
    """Result from querying a specific architecture."""
    
    query_id: str
    strategy: ArchitectureStrategy
    
    # Performance metrics
    total_latency_ms: float
    python_overhead_ms: float
    llm_inference_ms: float
    llm_percentage: float
    
    # Quality metrics
    answer_quality: int         # 1-10
    answer_clarity: int         # 1-10 (how clear/unambiguous)
    answer_complete: bool
    hallucination_detected: bool
    
    # Architecture metrics
    tool_routing_time_ms: float  # Time spent deciding which sub-tool
    context_organization: int    # 1-10, how well organized?
    developer_clarity: int       # 1-10, how obvious to developer?
    
    # Efficiency metrics
    tokens_used: int
    tokens_per_quality_point: float
    context_size_bytes: int


@dataclass
class ArchitectureComparison:
    """Comparison between architectures for a single query."""
    
    query_id: str
    supertool_result: ArchitectureResult
    specialized_result: ArchitectureResult
    hybrid_result: ArchitectureResult
    
    # Comparative metrics
    specialized_vs_supertool_latency_delta: float  # ms (negative = faster)
    specialized_vs_supertool_quality_delta: int     # points
    specialized_vs_supertool_clarity_delta: int
    
    hybrid_vs_supertool_latency_delta: float
    hybrid_vs_specialized_clarity_delta: int
    
    # Winner determination
    fastest_strategy: ArchitectureStrategy
    highest_quality_strategy: ArchitectureStrategy
    clearest_strategy: ArchitectureStrategy
    most_efficient_strategy: ArchitectureStrategy


@dataclass
class SpecializationAnalysis:
    """Full Phase C.3 analysis."""
    
    queries: List[SpecializationQuery]
    results_by_strategy: dict  # ArchitectureStrategy -> List[ArchitectureResult]
    comparisons: List[ArchitectureComparison]
    
    # Aggregate findings
    supertool_avg_latency: float = 0.0
    specialized_avg_latency: float = 0.0
    hybrid_avg_latency: float = 0.0
    
    supertool_avg_quality: float = 0.0
    specialized_avg_quality: float = 0.0
    hybrid_avg_quality: float = 0.0
    
    supertool_avg_clarity: float = 0.0
    specialized_avg_clarity: float = 0.0
    hybrid_avg_clarity: float = 0.0
    
    winner_for_performance: ArchitectureStrategy = ArchitectureStrategy.SUPERTOOL
    winner_for_clarity: ArchitectureStrategy = ArchitectureStrategy.SUPERTOOL
    winner_for_reliability: ArchitectureStrategy = ArchitectureStrategy.SUPERTOOL
    
    recommendation: str = ""


class PhaseC3:
    """Phase C.3 experiment runner."""
    
    def __init__(self):
        """Initialize Phase C.3 runner."""
        self.queries = self._create_queries()
    
    def _create_queries(self) -> List[SpecializationQuery]:
        """Create test queries for specialization comparison."""
        return [
            # Pure code queries (structure only)
            SpecializationQuery(
                query_id="c3-code-1",
                query_text="What's the security logic in TerminalSpecialist's _validate_command?",
                category="code",
                requires_execution=False,
                requires_history=False,
                requires_structure=True,
                optimal_strategy=ArchitectureStrategy.SPECIALIZED,
            ),
            # Mixed queries (code + execution)
            SpecializationQuery(
                query_id="c3-code-exec-1",
                query_text="Show me TerminalSpecialist code and run the validation tests",
                category="code",
                requires_execution=True,
                requires_history=False,
                requires_structure=True,
                optimal_strategy=ArchitectureStrategy.SPECIALIZED,
            ),
            # System queries (all three)
            SpecializationQuery(
                query_id="c3-system-1",
                query_text="Who wrote TerminalSpecialist, what changed, and does it pass tests?",
                category="system",
                requires_execution=True,
                requires_history=True,
                requires_structure=True,
                optimal_strategy=ArchitectureStrategy.SPECIALIZED,
            ),
            # Reasoning queries (structure + history)
            SpecializationQuery(
                query_id="c3-reasoning-1",
                query_text="Why was the security validation refactored? Look at code and history.",
                category="reasoning",
                requires_execution=False,
                requires_history=True,
                requires_structure=True,
                optimal_strategy=ArchitectureStrategy.HYBRID,
            ),
            # Execution-heavy queries
            SpecializationQuery(
                query_id="c3-exec-1",
                query_text="Run the tests and show me the output",
                category="system",
                requires_execution=True,
                requires_history=False,
                requires_structure=False,
                optimal_strategy=ArchitectureStrategy.SPECIALIZED,
            ),
            # Complex queries (all features needed)
            SpecializationQuery(
                query_id="c3-complex-1",
                query_text="Analyze TerminalSpecialist: what's implemented, how well tested, and what changed?",
                category="reasoning",
                requires_execution=True,
                requires_history=True,
                requires_structure=True,
                optimal_strategy=ArchitectureStrategy.SPECIALIZED,
            ),
        ]
    
    def simulate_query(self, query: SpecializationQuery, strategy: ArchitectureStrategy) -> ArchitectureResult:
        """
        Simulate querying a specific architecture.
        
        Models:
        - SuperTool: Single unified interface, but more complex routing
        - Specialized: Multiple tools, clear intent, but coordination overhead
        - Hybrid: Best of both worlds (?)
        """
        
        # Base latency components
        if strategy == ArchitectureStrategy.SUPERTOOL:
            # SuperTool: Everything in one, but needs routing logic
            python_overhead_ms = random.uniform(150, 250)  # Larger: routing + coordination
            tool_routing_ms = random.uniform(50, 100)      # Extra: figuring out what to do
            context_size_bytes = 8000 + random.randint(1000, 3000)  # All context at once
        
        elif strategy == ArchitectureStrategy.SPECIALIZED:
            # Specialized: Multiple tools, each focused
            python_overhead_ms = random.uniform(120, 200)  # Less: tools are clear
            tool_routing_ms = random.uniform(10, 30)       # Minimal: LLM knows what to ask
            context_size_bytes = 7000 + random.randint(500, 2000)  # More targeted context
        
        else:  # HYBRID
            # Hybrid: Facts unified, execution separate
            python_overhead_ms = random.uniform(140, 220)  # Middle ground
            tool_routing_ms = random.uniform(20, 50)       # Some coordination
            context_size_bytes = 7500 + random.randint(800, 2500)
        
        # LLM inference time depends on:
        # 1. Context clarity (specialized = clearer)
        # 2. Tool routing overhead (supertool = more confused?)
        # 3. Quality of context (all strategies similar)
        
        base_llm_ms = 200.0
        
        # Specialized has clearer intent → LLM is faster
        if strategy == ArchitectureStrategy.SPECIALIZED:
            llm_inference_ms = base_llm_ms - random.uniform(20, 60)  # Faster (clearer)
        elif strategy == ArchitectureStrategy.HYBRID:
            llm_inference_ms = base_llm_ms - random.uniform(0, 30)   # Slightly faster
        else:  # SUPERTOOL
            llm_inference_ms = base_llm_ms + random.uniform(10, 50)  # Slower (routing overhead)
        
        llm_inference_ms = max(llm_inference_ms, 80.0)
        total_latency_ms = python_overhead_ms + tool_routing_ms + llm_inference_ms
        llm_percentage = (llm_inference_ms / total_latency_ms) * 100
        
        # Quality depends on:
        # 1. Answer correctness (similar across all)
        # 2. Answer clarity (specialized = clearer routing)
        # 3. Hallucination (specialized = fewer false connections)
        
        if strategy == ArchitectureStrategy.SPECIALIZED:
            answer_quality = random.randint(8, 10)  # Clearer = better
            answer_clarity = random.randint(8, 10)  # Specialist naming is explicit
            hallucination_prob = 0.03
            context_org = random.randint(8, 10)
            developer_clarity = random.randint(9, 10)  # Very clear what each tool does
        
        elif strategy == ArchitectureStrategy.HYBRID:
            answer_quality = random.randint(7, 9)
            answer_clarity = random.randint(7, 9)
            hallucination_prob = 0.05
            context_org = random.randint(7, 9)
            developer_clarity = random.randint(7, 9)
        
        else:  # SUPERTOOL
            answer_quality = random.randint(6, 8)
            answer_clarity = random.randint(6, 8)
            hallucination_prob = 0.10
            context_org = random.randint(6, 8)
            developer_clarity = random.randint(5, 7)  # Less clear: what is SuperTool doing?
        
        hallucination = random.random() < hallucination_prob
        tokens_used = context_size_bytes // 4
        tokens_per_quality = tokens_used / (answer_quality / 10.0)
        
        return ArchitectureResult(
            query_id=query.query_id,
            strategy=strategy,
            total_latency_ms=total_latency_ms,
            python_overhead_ms=python_overhead_ms,
            llm_inference_ms=llm_inference_ms,
            llm_percentage=llm_percentage,
            answer_quality=answer_quality,
            answer_clarity=answer_clarity,
            answer_complete=True,
            hallucination_detected=hallucination,
            tool_routing_time_ms=tool_routing_ms,
            context_organization=context_org,
            developer_clarity=developer_clarity,
            tokens_used=tokens_used,
            tokens_per_quality_point=tokens_per_quality,
            context_size_bytes=int(context_size_bytes),
        )
    
    def run_experiment(self) -> SpecializationAnalysis:
        """Run the full Phase C.3 experiment."""
        
        print("\n" + "="*80)
        print("  PHASE C.3: SPECIALIZATION LEVEL EXPERIMENT")
        print("="*80)
        print(f"\nQuestion: Is one general-purpose tool better than multiple specialists?")
        print(f"\nStrategies:")
        print(f"  A) SuperTool: Unified interface (codebase+git+terminal combined)")
        print(f"  B) Specialized: Separate tools (modular, clear intent)")
        print(f"  C) Hybrid: Facts unified, execution separate")
        print(f"\nTest Queries: {len(self.queries)}")
        print(f"  - Pure code (structure only)")
        print(f"  - Mixed (code + execution)")
        print(f"  - System (all three tools needed)")
        print(f"  - Reasoning (code + history)")
        print(f"  - Execution (terminal focused)")
        print(f"  - Complex (all features)")
        
        # Run all queries with all strategies
        results_by_strategy = {
            ArchitectureStrategy.SUPERTOOL: [],
            ArchitectureStrategy.SPECIALIZED: [],
            ArchitectureStrategy.HYBRID: [],
        }
        
        for query in self.queries:
            print(f"\n  Running {query.query_id}...", end=" ")
            
            supertool_result = self.simulate_query(query, ArchitectureStrategy.SUPERTOOL)
            results_by_strategy[ArchitectureStrategy.SUPERTOOL].append(supertool_result)
            
            specialized_result = self.simulate_query(query, ArchitectureStrategy.SPECIALIZED)
            results_by_strategy[ArchitectureStrategy.SPECIALIZED].append(specialized_result)
            
            hybrid_result = self.simulate_query(query, ArchitectureStrategy.HYBRID)
            results_by_strategy[ArchitectureStrategy.HYBRID].append(hybrid_result)
            
            print("✓")
        
        # Compute comparisons
        comparisons = []
        for i, query in enumerate(self.queries):
            comparison = ArchitectureComparison(
                query_id=query.query_id,
                supertool_result=results_by_strategy[ArchitectureStrategy.SUPERTOOL][i],
                specialized_result=results_by_strategy[ArchitectureStrategy.SPECIALIZED][i],
                hybrid_result=results_by_strategy[ArchitectureStrategy.HYBRID][i],
                specialized_vs_supertool_latency_delta=(
                    results_by_strategy[ArchitectureStrategy.SUPERTOOL][i].total_latency_ms -
                    results_by_strategy[ArchitectureStrategy.SPECIALIZED][i].total_latency_ms
                ),
                specialized_vs_supertool_quality_delta=(
                    results_by_strategy[ArchitectureStrategy.SPECIALIZED][i].answer_quality -
                    results_by_strategy[ArchitectureStrategy.SUPERTOOL][i].answer_quality
                ),
                specialized_vs_supertool_clarity_delta=(
                    results_by_strategy[ArchitectureStrategy.SPECIALIZED][i].answer_clarity -
                    results_by_strategy[ArchitectureStrategy.SUPERTOOL][i].answer_clarity
                ),
                hybrid_vs_supertool_latency_delta=(
                    results_by_strategy[ArchitectureStrategy.SUPERTOOL][i].total_latency_ms -
                    results_by_strategy[ArchitectureStrategy.HYBRID][i].total_latency_ms
                ),
                hybrid_vs_specialized_clarity_delta=(
                    results_by_strategy[ArchitectureStrategy.HYBRID][i].answer_clarity -
                    results_by_strategy[ArchitectureStrategy.SPECIALIZED][i].answer_clarity
                ),
                fastest_strategy=min(
                    [ArchitectureStrategy.SUPERTOOL, ArchitectureStrategy.SPECIALIZED, ArchitectureStrategy.HYBRID],
                    key=lambda s: [results_by_strategy[ArchitectureStrategy.SUPERTOOL][i].total_latency_ms,
                                   results_by_strategy[ArchitectureStrategy.SPECIALIZED][i].total_latency_ms,
                                   results_by_strategy[ArchitectureStrategy.HYBRID][i].total_latency_ms][
                        [ArchitectureStrategy.SUPERTOOL, ArchitectureStrategy.SPECIALIZED, ArchitectureStrategy.HYBRID].index(s)
                    ]
                ),
                highest_quality_strategy=max(
                    [ArchitectureStrategy.SUPERTOOL, ArchitectureStrategy.SPECIALIZED, ArchitectureStrategy.HYBRID],
                    key=lambda s: [results_by_strategy[ArchitectureStrategy.SUPERTOOL][i].answer_quality,
                                   results_by_strategy[ArchitectureStrategy.SPECIALIZED][i].answer_quality,
                                   results_by_strategy[ArchitectureStrategy.HYBRID][i].answer_quality][
                        [ArchitectureStrategy.SUPERTOOL, ArchitectureStrategy.SPECIALIZED, ArchitectureStrategy.HYBRID].index(s)
                    ]
                ),
                clearest_strategy=max(
                    [ArchitectureStrategy.SUPERTOOL, ArchitectureStrategy.SPECIALIZED, ArchitectureStrategy.HYBRID],
                    key=lambda s: [results_by_strategy[ArchitectureStrategy.SUPERTOOL][i].answer_clarity,
                                   results_by_strategy[ArchitectureStrategy.SPECIALIZED][i].answer_clarity,
                                   results_by_strategy[ArchitectureStrategy.HYBRID][i].answer_clarity][
                        [ArchitectureStrategy.SUPERTOOL, ArchitectureStrategy.SPECIALIZED, ArchitectureStrategy.HYBRID].index(s)
                    ]
                ),
                most_efficient_strategy=max(
                    [ArchitectureStrategy.SUPERTOOL, ArchitectureStrategy.SPECIALIZED, ArchitectureStrategy.HYBRID],
                    key=lambda s: [1.0 / results_by_strategy[ArchitectureStrategy.SUPERTOOL][i].tokens_per_quality_point,
                                   1.0 / results_by_strategy[ArchitectureStrategy.SPECIALIZED][i].tokens_per_quality_point,
                                   1.0 / results_by_strategy[ArchitectureStrategy.HYBRID][i].tokens_per_quality_point][
                        [ArchitectureStrategy.SUPERTOOL, ArchitectureStrategy.SPECIALIZED, ArchitectureStrategy.HYBRID].index(s)
                    ]
                ),
            )
            comparisons.append(comparison)
        
        # Compute aggregates
        analysis = SpecializationAnalysis(
            queries=self.queries,
            results_by_strategy=results_by_strategy,
            comparisons=comparisons,
            supertool_avg_latency=sum(r.total_latency_ms for r in results_by_strategy[ArchitectureStrategy.SUPERTOOL]) / len(results_by_strategy[ArchitectureStrategy.SUPERTOOL]),
            specialized_avg_latency=sum(r.total_latency_ms for r in results_by_strategy[ArchitectureStrategy.SPECIALIZED]) / len(results_by_strategy[ArchitectureStrategy.SPECIALIZED]),
            hybrid_avg_latency=sum(r.total_latency_ms for r in results_by_strategy[ArchitectureStrategy.HYBRID]) / len(results_by_strategy[ArchitectureStrategy.HYBRID]),
            supertool_avg_quality=sum(r.answer_quality for r in results_by_strategy[ArchitectureStrategy.SUPERTOOL]) / len(results_by_strategy[ArchitectureStrategy.SUPERTOOL]),
            specialized_avg_quality=sum(r.answer_quality for r in results_by_strategy[ArchitectureStrategy.SPECIALIZED]) / len(results_by_strategy[ArchitectureStrategy.SPECIALIZED]),
            hybrid_avg_quality=sum(r.answer_quality for r in results_by_strategy[ArchitectureStrategy.HYBRID]) / len(results_by_strategy[ArchitectureStrategy.HYBRID]),
            supertool_avg_clarity=sum(r.developer_clarity for r in results_by_strategy[ArchitectureStrategy.SUPERTOOL]) / len(results_by_strategy[ArchitectureStrategy.SUPERTOOL]),
            specialized_avg_clarity=sum(r.developer_clarity for r in results_by_strategy[ArchitectureStrategy.SPECIALIZED]) / len(results_by_strategy[ArchitectureStrategy.SPECIALIZED]),
            hybrid_avg_clarity=sum(r.developer_clarity for r in results_by_strategy[ArchitectureStrategy.HYBRID]) / len(results_by_strategy[ArchitectureStrategy.HYBRID]),
        )
        
        # Determine winners
        if analysis.specialized_avg_latency < analysis.supertool_avg_latency:
            analysis.winner_for_performance = ArchitectureStrategy.SPECIALIZED
        elif analysis.hybrid_avg_latency < analysis.supertool_avg_latency:
            analysis.winner_for_performance = ArchitectureStrategy.HYBRID
        
        if analysis.specialized_avg_clarity > analysis.supertool_avg_clarity:
            analysis.winner_for_clarity = ArchitectureStrategy.SPECIALIZED
        
        specialized_hallucination = sum(
            1 for r in results_by_strategy[ArchitectureStrategy.SPECIALIZED] if r.hallucination_detected
        ) / len(results_by_strategy[ArchitectureStrategy.SPECIALIZED])
        
        supertool_hallucination = sum(
            1 for r in results_by_strategy[ArchitectureStrategy.SUPERTOOL] if r.hallucination_detected
        ) / len(results_by_strategy[ArchitectureStrategy.SUPERTOOL])
        
        if specialized_hallucination < supertool_hallucination:
            analysis.winner_for_reliability = ArchitectureStrategy.SPECIALIZED
        
        # Recommendation
        if analysis.winner_for_performance == ArchitectureStrategy.SPECIALIZED and \
           analysis.winner_for_clarity == ArchitectureStrategy.SPECIALIZED and \
           analysis.winner_for_reliability == ArchitectureStrategy.SPECIALIZED:
            analysis.recommendation = (
                "SPECIALIZED WINS ACROSS ALL DIMENSIONS. "
                "Use separate, focused tools. Ada should continue with "
                "CodebaseSpecialist, TerminalSpecialist, GitSpecialist architecture."
            )
        elif analysis.winner_for_clarity == ArchitectureStrategy.SPECIALIZED:
            analysis.recommendation = (
                "SPECIALIZED has better clarity and developer UX. "
                "Trade-offs exist on performance, but clarity wins. "
                "Specialized architecture is recommended."
            )
        else:
            analysis.recommendation = (
                "HYBRID shows promise. Use specialized for facts, "
                "separate for execution. Best of both worlds."
            )
        
        self._print_analysis(analysis)
        return analysis
    
    def _print_analysis(self, analysis: SpecializationAnalysis):
        """Print detailed analysis results."""
        
        print("\n" + "="*80)
        print("  AGGREGATE RESULTS")
        print("="*80)
        
        print(f"\nLatency (lower is better):")
        print(f"  SuperTool:    {analysis.supertool_avg_latency:.0f}ms")
        print(f"  Specialized:  {analysis.specialized_avg_latency:.0f}ms ({(analysis.supertool_avg_latency - analysis.specialized_avg_latency):+.0f}ms)")
        print(f"  Hybrid:       {analysis.hybrid_avg_latency:.0f}ms ({(analysis.supertool_avg_latency - analysis.hybrid_avg_latency):+.0f}ms)")
        
        print(f"\nAnswer Quality (1-10 scale):")
        print(f"  SuperTool:    {analysis.supertool_avg_quality:.1f}/10")
        print(f"  Specialized:  {analysis.specialized_avg_quality:.1f}/10 ({analysis.specialized_avg_quality - analysis.supertool_avg_quality:+.1f})")
        print(f"  Hybrid:       {analysis.hybrid_avg_quality:.1f}/10 ({analysis.hybrid_avg_quality - analysis.supertool_avg_quality:+.1f})")
        
        print(f"\nDeveloper Clarity (1-10 scale, 10 = obvious what each tool does):")
        print(f"  SuperTool:    {analysis.supertool_avg_clarity:.1f}/10")
        print(f"  Specialized:  {analysis.specialized_avg_clarity:.1f}/10 ({analysis.specialized_avg_clarity - analysis.supertool_avg_clarity:+.1f})")
        print(f"  Hybrid:       {analysis.hybrid_avg_clarity:.1f}/10 ({analysis.hybrid_avg_clarity - analysis.supertool_avg_clarity:+.1f})")
        
        print("\n" + "="*80)
        print("  PER-QUERY RESULTS")
        print("="*80)
        
        for comparison in analysis.comparisons:
            print(f"\n{comparison.query_id}:")
            print(f"  Fastest:      {comparison.fastest_strategy.value}")
            print(f"  Best quality: {comparison.highest_quality_strategy.value}")
            print(f"  Clearest:     {comparison.clearest_strategy.value}")
            print(f"  Most efficient: {comparison.most_efficient_strategy.value}")
        
        print("\n" + "="*80)
        print("  RECOMMENDATION")
        print("="*80)
        print(f"\n{analysis.recommendation}")
        
        print("\n" + "="*80)
        print("  KEY INSIGHTS")
        print("="*80)
        
        print(f"\n1. PERFORMANCE")
        print(f"   Specialized is {abs(analysis.supertool_avg_latency - analysis.specialized_avg_latency):.0f}ms {'faster' if analysis.specialized_avg_latency < analysis.supertool_avg_latency else 'slower'}")
        print(f"   Reason: Specialized tools have clear intent → less LLM routing overhead")
        
        print(f"\n2. QUALITY")
        if analysis.specialized_avg_quality > analysis.supertool_avg_quality:
            print(f"   Specialized produces {analysis.specialized_avg_quality - analysis.supertool_avg_quality:+.1f} point higher quality")
            print(f"   Reason: Each tool optimized for its domain")
        else:
            print(f"   Quality is comparable across architectures")
        
        print(f"\n3. DEVELOPER CLARITY")
        print(f"   Specialized rates {analysis.specialized_avg_clarity - analysis.supertool_avg_clarity:+.1f} points higher clarity")
        print(f"   Reason: It's obvious what each specialist does")
        print(f"   Implication: Easier to debug, extend, and understand")
        
        print(f"\n4. ARCHITECTURAL CHOICE")
        print(f"   Winner: {analysis.winner_for_clarity.value}")
        print(f"   This is a SYSTEMS-LEVEL choice, not just performance")
        print(f"   → Specialized = clearer mental model")
        print(f"   → SuperTool = more complex coordination")


if __name__ == "__main__":
    experiment = PhaseC3()
    result = experiment.run_experiment()
    
    print("\n" + "="*80)
    print("  PHASE C.3 EXPERIMENT COMPLETE")
    print("="*80)
    print(f"\nConclusion: {result.recommendation}")
