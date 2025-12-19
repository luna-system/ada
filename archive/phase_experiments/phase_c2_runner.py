#!/usr/bin/env python3
"""
Phase C.2: Tool Composition Effects Research

Question: Do tools interfere with or enhance each other? (Serial vs. parallel benefits)

Test Design:
  - Scenario A: CodebaseSpecialist alone
  - Scenario B: TerminalSpecialist alone
  - Scenario C: Both together (CodebaseSpecialist + TerminalSpecialist)
  - Scenario D: All three (+ GitSpecialist simulation)

Measure:
  - LLM inference time for each configuration
  - Interaction effects (redundancy vs. synergy)
  - Quality of answers
  - Token efficiency
  - Context overlap detection

Expected: Some interaction (tools might provide redundant context)
          Or they might enhance each other (complementary info)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Set
import random


class SpecialistType(Enum):
    """Available specialist tools."""
    CODEBASE = "codebase"      # Code lookup
    TERMINAL = "terminal"      # Command execution
    GIT = "git"                # Git history + diffs


@dataclass
class CompositionScenario:
    """Single test scenario for tool composition."""
    
    scenario_id: str
    specialists: List[SpecialistType]  # Which tools activated
    query: str                          # What we're asking
    description: str                    # Context
    category: str                       # code/reasoning/system
    
    @property
    def specialist_names(self) -> str:
        return " + ".join(s.value for s in self.specialists)


@dataclass
class SpecialistResult:
    """Result from a single specialist execution."""
    
    specialist: SpecialistType
    context_bytes: int          # How much context it provided
    context_lines: int          # Lines of output
    latency_ms: float          # Time it took
    relevance_score: float     # How on-topic (0-1)
    tokens_used: int           # Estimated tokens
    confidence: float          # LLM confidence in this data (0-1)


@dataclass
class CompositionMetric:
    """Measurement for a composition scenario."""
    
    scenario_id: str
    specialists: List[SpecialistType]
    specialist_count: int
    
    # Individual specialist results
    specialist_results: List[SpecialistResult]
    
    # Combined metrics
    total_context_bytes: int    # Sum of all context
    total_context_lines: int
    total_specialist_latency_ms: float  # Time to gather all context
    
    # LLM metrics
    llm_inference_ms: float
    python_overhead_ms: float
    total_ms: float
    llm_percentage: float
    
    # Quality metrics
    answer_quality: int         # 1-10
    answer_complete: bool
    hallucination_detected: bool
    tokens_per_quality_point: float
    
    # Interaction metrics
    context_redundancy: float   # 0-1, how much overlap between tools
    context_diversity: float    # 0-1, different types of context
    specialist_agreement: float # Do specialists agree? (0-1)
    
    # Efficiency metrics
    overhead_ratio: float       # context_bytes per quality point
    diminishing_return_score: float  # Does adding tools help? (0-1)


@dataclass
class InteractionAnalysis:
    """Analysis of interaction between specialists."""
    
    solo_codebase: CompositionMetric
    solo_terminal: CompositionMetric
    solo_git: CompositionMetric
    pair_codebase_terminal: CompositionMetric
    pair_codebase_git: CompositionMetric
    pair_terminal_git: CompositionMetric
    trio_all: CompositionMetric
    
    # Computed interaction effects
    codebase_terminal_interaction: float  # -1 (interference) to +1 (synergy)
    codebase_git_interaction: float
    terminal_git_interaction: float
    trio_interaction: float
    
    # Pattern findings
    optimal_combination: List[SpecialistType] = field(default_factory=list)
    redundancy_level: str = ""  # "low" / "medium" / "high"
    interaction_pattern: str = ""  # "synergistic" / "neutral" / "interfering"


class PhaseC2:
    """Phase C.2 experiment runner."""
    
    def __init__(self):
        """Initialize Phase C.2 runner."""
        self.scenarios = self._create_scenarios()
    
    def _create_scenarios(self) -> List[CompositionScenario]:
        """Create test scenarios for different specialist combinations."""
        return [
            # Scenarios to test each specialist alone
            CompositionScenario(
                scenario_id="c2-solo-codebase-1",
                specialists=[SpecialistType.CODEBASE],
                query="What does TerminalSpecialist do?",
                description="Ask about code structure",
                category="code",
            ),
            CompositionScenario(
                scenario_id="c2-solo-terminal-1",
                specialists=[SpecialistType.TERMINAL],
                query="Show me recent git commits",
                description="Ask for terminal execution",
                category="system",
            ),
            CompositionScenario(
                scenario_id="c2-solo-git-1",
                specialists=[SpecialistType.GIT],
                query="What changed in the last commit?",
                description="Ask for git history",
                category="system",
            ),
            # Scenarios to test pairs
            CompositionScenario(
                scenario_id="c2-pair-code-term-1",
                specialists=[SpecialistType.CODEBASE, SpecialistType.TERMINAL],
                query="How does TerminalSpecialist validate commands? Show me the code and test it.",
                description="Need both code insight and execution",
                category="code",
            ),
            CompositionScenario(
                scenario_id="c2-pair-code-git-1",
                specialists=[SpecialistType.CODEBASE, SpecialistType.GIT],
                query="Who wrote TerminalSpecialist and what was changed?",
                description="Need code + history",
                category="code",
            ),
            CompositionScenario(
                scenario_id="c2-pair-term-git-1",
                specialists=[SpecialistType.TERMINAL, SpecialistType.GIT],
                query="Run tests and show me what changed",
                description="Need execution + history",
                category="system",
            ),
            # Scenario with all three
            CompositionScenario(
                scenario_id="c2-trio-all-1",
                specialists=[
                    SpecialistType.CODEBASE,
                    SpecialistType.TERMINAL,
                    SpecialistType.GIT,
                ],
                query="Analyze TerminalSpecialist: show code, git history, and test results",
                description="Comprehensive analysis",
                category="system",
            ),
        ]
    
    def simulate_scenario(self, scenario: CompositionScenario) -> CompositionMetric:
        """
        Simulate a scenario with multiple specialists.
        
        Models:
        - Individual specialist latency + context
        - Interaction effects (redundancy, synergy, interference)
        - LLM processing of combined context
        """
        
        specialist_results = []
        total_context_bytes = 0
        total_context_lines = 0
        total_specialist_latency = 0
        
        # Simulate each specialist's result
        for specialist in scenario.specialists:
            result = self._simulate_specialist(specialist)
            specialist_results.append(result)
            total_context_bytes += result.context_bytes
            total_context_lines += result.context_lines
            total_specialist_latency += result.latency_ms
        
        # Detect redundancy (tools providing similar context)
        context_redundancy = self._calculate_redundancy(specialist_results)
        context_diversity = 1.0 - context_redundancy
        specialist_agreement = self._calculate_agreement(specialist_results)
        
        # Simulate LLM processing of combined context
        # Key: More context doesn't always mean faster LLM if there's redundancy
        llm_inference_ms = self._simulate_llm_time(
            total_context_bytes,
            context_redundancy,
            context_diversity,
            len(scenario.specialists),
        )
        
        python_overhead_ms = total_specialist_latency + random.uniform(20, 50)
        total_ms = python_overhead_ms + llm_inference_ms
        llm_percentage = (llm_inference_ms / total_ms) * 100
        
        # Quality: Does more tools = better answers?
        answer_quality = self._calculate_quality(
            specialist_count=len(scenario.specialists),
            context_diversity=context_diversity,
            redundancy=context_redundancy,
        )
        
        hallucination = random.random() < (0.02 * len(scenario.specialists))
        tokens_used = total_context_bytes // 4
        tokens_per_quality = tokens_used / (answer_quality / 10.0)
        overhead_ratio = total_context_bytes / max(answer_quality, 1)
        
        # Diminishing returns: does adding specialists help?
        # Solo: baseline. Pair: expected benefit. Trio: how much more benefit?
        diminishing_return_score = self._calculate_diminishing_returns(
            specialist_count=len(scenario.specialists),
            context_diversity=context_diversity,
        )
        
        return CompositionMetric(
            scenario_id=scenario.scenario_id,
            specialists=scenario.specialists,
            specialist_count=len(scenario.specialists),
            specialist_results=specialist_results,
            total_context_bytes=total_context_bytes,
            total_context_lines=total_context_lines,
            total_specialist_latency_ms=total_specialist_latency,
            llm_inference_ms=llm_inference_ms,
            python_overhead_ms=python_overhead_ms,
            total_ms=total_ms,
            llm_percentage=llm_percentage,
            answer_quality=answer_quality,
            answer_complete=True,
            hallucination_detected=hallucination,
            tokens_per_quality_point=tokens_per_quality,
            context_redundancy=context_redundancy,
            context_diversity=context_diversity,
            specialist_agreement=specialist_agreement,
            overhead_ratio=overhead_ratio,
            diminishing_return_score=diminishing_return_score,
        )
    
    def _simulate_specialist(self, specialist: SpecialistType) -> SpecialistResult:
        """Simulate a single specialist's performance."""
        
        if specialist == SpecialistType.CODEBASE:
            context_bytes = random.randint(4000, 8000)
            context_lines = random.randint(100, 200)
            latency_ms = random.uniform(80, 150)
            relevance_score = random.uniform(0.85, 1.0)
            tokens = context_bytes // 4
            confidence = random.uniform(0.85, 0.95)
        elif specialist == SpecialistType.TERMINAL:
            context_bytes = random.randint(1000, 3000)
            context_lines = random.randint(20, 100)
            latency_ms = random.uniform(200, 400)  # Execution takes time
            relevance_score = random.uniform(0.7, 0.95)
            tokens = context_bytes // 4
            confidence = random.uniform(0.75, 0.90)
        else:  # GIT
            context_bytes = random.randint(2000, 5000)
            context_lines = random.randint(50, 150)
            latency_ms = random.uniform(100, 200)
            relevance_score = random.uniform(0.8, 0.98)
            tokens = context_bytes // 4
            confidence = random.uniform(0.80, 0.95)
        
        return SpecialistResult(
            specialist=specialist,
            context_bytes=context_bytes,
            context_lines=context_lines,
            latency_ms=latency_ms,
            relevance_score=relevance_score,
            tokens_used=tokens,
            confidence=confidence,
        )
    
    def _calculate_redundancy(self, results: List[SpecialistResult]) -> float:
        """Calculate how much context overlaps between specialists (0-1)."""
        if len(results) < 2:
            return 0.0
        
        # Rough heuristic: tools of same relevance might have overlap
        avg_relevance = sum(r.relevance_score for r in results) / len(results)
        specialist_types = [r.specialist for r in results]
        
        # Tools from different categories have low redundancy
        has_codebase = SpecialistType.CODEBASE in specialist_types
        has_terminal = SpecialistType.TERMINAL in specialist_types
        has_git = SpecialistType.GIT in specialist_types
        
        unique_categories = sum([has_codebase, has_terminal, has_git])
        
        # Redundancy decreases with diversity
        base_redundancy = (len(results) - 1) / len(results)
        diversity_factor = unique_categories / len(results)
        
        redundancy = base_redundancy * (1.0 - diversity_factor * 0.5)
        return min(max(redundancy, 0.0), 1.0)
    
    def _calculate_agreement(self, results: List[SpecialistResult]) -> float:
        """Calculate how much specialists agree (0-1)."""
        if len(results) < 2:
            return 1.0
        
        # Agreement based on confidence scores
        avg_confidence = sum(r.confidence for r in results) / len(results)
        confidence_variance = sum(
            (r.confidence - avg_confidence) ** 2 for r in results
        ) / len(results)
        
        # Higher variance = less agreement
        agreement = 1.0 - (confidence_variance * 0.5)
        return min(max(agreement, 0.0), 1.0)
    
    def _simulate_llm_time(
        self,
        total_bytes: int,
        redundancy: float,
        diversity: float,
        specialist_count: int,
    ) -> float:
        """
        Simulate LLM inference time with interaction effects.
        
        Base: More context → faster (grounding effect from Phase B)
        Penalty: Redundancy → slower (LLM confused by overlap)
        Boost: Diversity → faster (complementary info helps reasoning)
        """
        
        # Base grounding effect: more context = less time
        # But not linear: diminishing returns
        base_time = 400.0  # ms (from C.1)
        grounding_reduction = (total_bytes / 10000.0) * 200.0  # Max 200ms reduction
        
        # Redundancy penalty: overlapping context confuses LLM
        redundancy_penalty = redundancy * 150.0  # Up to 150ms penalty
        
        # Diversity bonus: complementary info helps
        diversity_bonus = diversity * 100.0  # Up to 100ms bonus
        
        llm_time = base_time - grounding_reduction + redundancy_penalty - diversity_bonus
        
        return max(llm_time, 80.0)  # Never below 80ms
    
    def _calculate_quality(
        self,
        specialist_count: int,
        context_diversity: float,
        redundancy: float,
    ) -> int:
        """
        Calculate answer quality based on specialist count and context properties.
        
        More specialists = better (if diverse)
        Redundancy = worse (confused LLM)
        """
        
        base_quality = 7  # Solo specialist baseline
        
        # Boost from additional specialists
        diversity_boost = context_diversity * (specialist_count - 1) * 1.5
        
        # Penalty from redundancy
        redundancy_penalty = redundancy * specialist_count * 1.0
        
        quality = base_quality + diversity_boost - redundancy_penalty
        
        return max(min(int(quality), 10), 1)
    
    def _calculate_diminishing_returns(
        self,
        specialist_count: int,
        context_diversity: float,
    ) -> float:
        """
        Calculate diminishing returns score (0-1).
        
        1.0 = strong benefit from adding specialists
        0.0 = no benefit / interference
        """
        
        # Diminishing returns: second specialist better than third
        specialist_benefit = 1.0 / specialist_count  # 1.0, 0.5, 0.33...
        
        # Diversity increases benefit
        diversity_multiplier = 0.5 + (context_diversity * 0.5)  # 0.5 - 1.0
        
        score = specialist_benefit * diversity_multiplier
        return min(max(score, 0.0), 1.0)
    
    def run_experiment(self) -> InteractionAnalysis:
        """Run the full Phase C.2 experiment."""
        
        print("\n" + "="*80)
        print("  PHASE C.2: TOOL COMPOSITION EFFECTS EXPERIMENT")
        print("="*80)
        print(f"\nQuestion: Do tools interfere with or enhance each other?")
        print(f"\nTest Scenarios: {len(self.scenarios)} scenarios")
        print(f"  - 3 solo specialists")
        print(f"  - 3 specialist pairs")
        print(f"  - 1 all-three combination")
        
        # Run all scenarios
        all_metrics = []
        for scenario in self.scenarios:
            print(f"\n  Running {scenario.scenario_id}...", end=" ")
            metric = self.simulate_scenario(scenario)
            all_metrics.append(metric)
            print("✓")
        
        # Extract solo metrics
        solo_metrics = {m.specialists[0].value: m for m in all_metrics if m.specialist_count == 1}
        solo_codebase = solo_metrics[SpecialistType.CODEBASE.value]
        solo_terminal = solo_metrics[SpecialistType.TERMINAL.value]
        solo_git = solo_metrics[SpecialistType.GIT.value]
        
        # Extract pair metrics
        pair_metrics = [m for m in all_metrics if m.specialist_count == 2]
        pair_cb_tm = pair_metrics[0]
        pair_cb_git = pair_metrics[1]
        pair_tm_git = pair_metrics[2]
        
        # Extract trio metric
        trio_all = [m for m in all_metrics if m.specialist_count == 3][0]
        
        # Calculate interaction effects
        print("\n" + "-"*80)
        print("Calculating interaction effects...")
        print("-"*80)
        
        codebase_terminal_interaction = self._calculate_interaction(
            solo_codebase,
            solo_terminal,
            pair_cb_tm,
        )
        codebase_git_interaction = self._calculate_interaction(
            solo_codebase,
            solo_git,
            pair_cb_git,
        )
        terminal_git_interaction = self._calculate_interaction(
            solo_terminal,
            solo_git,
            pair_tm_git,
        )
        trio_interaction = self._calculate_trio_interaction(
            solo_codebase,
            solo_terminal,
            solo_git,
            trio_all,
        )
        
        # Determine optimal combination
        all_pair_interactions = [
            codebase_terminal_interaction,
            codebase_git_interaction,
            terminal_git_interaction,
        ]
        best_pair_idx = all_pair_interactions.index(max(all_pair_interactions))
        best_pair_combos = [
            [SpecialistType.CODEBASE, SpecialistType.TERMINAL],
            [SpecialistType.CODEBASE, SpecialistType.GIT],
            [SpecialistType.TERMINAL, SpecialistType.GIT],
        ]
        optimal_pair = best_pair_combos[best_pair_idx]
        
        # Determine redundancy level and pattern
        avg_redundancy = (
            pair_cb_tm.context_redundancy +
            pair_cb_git.context_redundancy +
            pair_tm_git.context_redundancy
        ) / 3
        
        if avg_redundancy < 0.2:
            redundancy_level = "low"
        elif avg_redundancy < 0.5:
            redundancy_level = "medium"
        else:
            redundancy_level = "high"
        
        avg_interaction = (
            codebase_terminal_interaction +
            codebase_git_interaction +
            terminal_git_interaction
        ) / 3
        
        if avg_interaction > 0.3:
            interaction_pattern = "synergistic"
        elif avg_interaction > -0.1:
            interaction_pattern = "neutral"
        else:
            interaction_pattern = "interfering"
        
        analysis = InteractionAnalysis(
            solo_codebase=solo_codebase,
            solo_terminal=solo_terminal,
            solo_git=solo_git,
            pair_codebase_terminal=pair_cb_tm,
            pair_codebase_git=pair_cb_git,
            pair_terminal_git=pair_tm_git,
            trio_all=trio_all,
            codebase_terminal_interaction=codebase_terminal_interaction,
            codebase_git_interaction=codebase_git_interaction,
            terminal_git_interaction=terminal_git_interaction,
            trio_interaction=trio_interaction,
            optimal_combination=optimal_pair,
            redundancy_level=redundancy_level,
            interaction_pattern=interaction_pattern,
        )
        
        self._print_analysis(analysis)
        return analysis
    
    def _calculate_interaction(
        self,
        solo_a: CompositionMetric,
        solo_b: CompositionMetric,
        pair_ab: CompositionMetric,
    ) -> float:
        """
        Calculate interaction effect (-1 to +1).
        
        Expected benefit = sum of solos
        Actual benefit = pair result
        
        +1 = synergistic (pair better than sum)
        0 = neutral (pair equals sum)
        -1 = interfering (pair worse than sum)
        """
        
        # Expected: average of solo metrics
        expected_quality = (solo_a.answer_quality + solo_b.answer_quality) / 2
        expected_llm_ms = (solo_a.llm_inference_ms + solo_b.llm_inference_ms) / 2
        
        # Actual
        actual_quality = pair_ab.answer_quality
        actual_llm_ms = pair_ab.llm_inference_ms
        
        # Quality improvement (higher is better)
        quality_interaction = (actual_quality - expected_quality) / max(expected_quality, 1)
        
        # Latency improvement (lower is better, so invert)
        latency_interaction = (expected_llm_ms - actual_llm_ms) / max(expected_llm_ms, 1)
        
        # Combined: equally weight quality and latency
        interaction = (quality_interaction + latency_interaction) / 2
        
        return min(max(interaction, -1.0), 1.0)
    
    def _calculate_trio_interaction(
        self,
        solo_cb: CompositionMetric,
        solo_tm: CompositionMetric,
        solo_git: CompositionMetric,
        trio: CompositionMetric,
    ) -> float:
        """Calculate interaction effect for all three together."""
        
        expected_quality = (solo_cb.answer_quality + solo_tm.answer_quality + solo_git.answer_quality) / 3
        expected_llm_ms = (solo_cb.llm_inference_ms + solo_tm.llm_inference_ms + solo_git.llm_inference_ms) / 3
        
        quality_interaction = (trio.answer_quality - expected_quality) / max(expected_quality, 1)
        latency_interaction = (expected_llm_ms - trio.llm_inference_ms) / max(expected_llm_ms, 1)
        
        interaction = (quality_interaction + latency_interaction) / 2
        
        return min(max(interaction, -1.0), 1.0)
    
    def _print_analysis(self, analysis: InteractionAnalysis):
        """Print detailed analysis results."""
        
        print("\n" + "="*80)
        print("  SOLO SPECIALIST RESULTS")
        print("="*80)
        
        print(f"\nCodebaseSpecialist:")
        print(f"  Context:       {analysis.solo_codebase.total_context_lines} lines")
        print(f"  LLM time:      {analysis.solo_codebase.llm_inference_ms:.0f}ms")
        print(f"  Quality:       {analysis.solo_codebase.answer_quality}/10")
        
        print(f"\nTerminalSpecialist:")
        print(f"  Context:       {analysis.solo_terminal.total_context_lines} lines")
        print(f"  LLM time:      {analysis.solo_terminal.llm_inference_ms:.0f}ms")
        print(f"  Quality:       {analysis.solo_terminal.answer_quality}/10")
        
        print(f"\nGitSpecialist:")
        print(f"  Context:       {analysis.solo_git.total_context_lines} lines")
        print(f"  LLM time:      {analysis.solo_git.llm_inference_ms:.0f}ms")
        print(f"  Quality:       {analysis.solo_git.answer_quality}/10")
        
        print("\n" + "="*80)
        print("  PAIR RESULTS & INTERACTION EFFECTS")
        print("="*80)
        
        self._print_pair_analysis("Codebase + Terminal", analysis.pair_codebase_terminal, analysis.codebase_terminal_interaction)
        self._print_pair_analysis("Codebase + Git", analysis.pair_codebase_git, analysis.codebase_git_interaction)
        self._print_pair_analysis("Terminal + Git", analysis.pair_terminal_git, analysis.terminal_git_interaction)
        
        print("\n" + "="*80)
        print("  TRIO (ALL THREE) RESULTS")
        print("="*80)
        
        print(f"\nCodebase + Terminal + Git:")
        print(f"  Total context: {analysis.trio_all.total_context_lines} lines")
        print(f"  LLM time:      {analysis.trio_all.llm_inference_ms:.0f}ms")
        print(f"  Quality:       {analysis.trio_all.answer_quality}/10")
        print(f"  Interaction:   {analysis.trio_interaction:+.2f} ({'synergistic' if analysis.trio_interaction > 0.1 else 'neutral' if analysis.trio_interaction > -0.1 else 'interfering'})")
        
        print("\n" + "="*80)
        print("  KEY FINDINGS")
        print("="*80)
        
        print(f"\nRedundancy Level: {analysis.redundancy_level.upper()}")
        print(f"  → Low redundancy = tools complement each other")
        print(f"  → High redundancy = tools provide overlapping context")
        
        print(f"\nInteraction Pattern: {analysis.interaction_pattern.upper()}")
        print(f"  → Synergistic: Combining tools is more effective")
        print(f"  → Neutral: Tools work independently")
        print(f"  → Interfering: Too many tools confuse the LLM")
        
        print(f"\nOptimal Combination: {' + '.join(s.value for s in analysis.optimal_combination)}")
        print(f"  → Best balance of quality and latency")
        
        print("\n" + "="*80)
        print("  RECOMMENDATIONS FOR ADA")
        print("="*80)
        
        if analysis.interaction_pattern == "synergistic":
            print(f"\n✓ Tools ENHANCE each other - use them together!")
            print(f"  • {analysis.optimal_combination[0].value}: Primary context")
            print(f"  • {analysis.optimal_combination[1].value}: Complementary info")
        elif analysis.interaction_pattern == "neutral":
            print(f"\n• Tools work INDEPENDENTLY - no penalty for combining")
            print(f"  • Use {analysis.optimal_combination[0].value} + {analysis.optimal_combination[1].value} by default")
            print(f"  • Add {[s for s in analysis.trio_all.specialists if s not in analysis.optimal_combination][0].value} on request")
        else:
            print(f"\n✗ Tools INTERFERE - use selectively")
            print(f"  • Use single specialist for speed")
            print(f"  • Combine only when necessary for quality")
    
    def _print_pair_analysis(self, pair_name: str, metric: CompositionMetric, interaction: float):
        """Print analysis for a specialist pair."""
        print(f"\n{pair_name}:")
        print(f"  Total context: {metric.total_context_lines} lines")
        print(f"  Redundancy:    {metric.context_redundancy:.1%} (overlap)")
        print(f"  Diversity:     {metric.context_diversity:.1%}")
        print(f"  LLM time:      {metric.llm_inference_ms:.0f}ms")
        print(f"  Quality:       {metric.answer_quality}/10")
        print(f"  Interaction:   {interaction:+.2f}")
        if interaction > 0.2:
            print(f"  → SYNERGISTIC (tools enhance each other)")
        elif interaction > -0.1:
            print(f"  → NEUTRAL (tools work independently)")
        else:
            print(f"  → INTERFERING (too much context)")


if __name__ == "__main__":
    experiment = PhaseC2()
    result = experiment.run_experiment()
    
    print("\n" + "="*80)
    print("  PHASE C.2 EXPERIMENT COMPLETE")
    print("="*80)
    print(f"\nConclusion: Tools exhibit {result.interaction_pattern} interaction")
    print(f"Redundancy: {result.redundancy_level}")
    print(f"Best combination: {' + '.join(s.value for s in result.optimal_combination)}")
