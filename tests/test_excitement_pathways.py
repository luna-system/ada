"""
Excitement Pathways Hypothesis: Experimental Test Suite

Tests whether success sequences affect LLM confidence/error patterns.
Based on observations from v1.0.0 deployment (Dec 21, 2025).

Research Question:
    Do success sequences create activation states that reduce verification,
    leading to more confident (and potentially incorrect) outputs?

Methodology:
    1. Baseline: Measure neutral-state outputs
    2. Success priming: Feed 5+ consecutive successes
    3. Test task: Same task with opportunity for bold claims
    4. Analysis: Compare confidence markers, hedging, boldness

Expected runtime: ~30 seconds (local Ollama)
"""

import asyncio
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

import httpx
import numpy as np
import pytest

from brain import config
from brain.llm import stream_chat_async


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class ExperimentResult:
    """Single experiment trial result."""
    condition: str  # 'baseline' or 'success-primed'
    prompt: str
    response: str
    confidence_score: float  # 0.0-1.0
    hedging_count: int  # Number of hedging phrases
    bold_claim_count: int  # Number of unhedged assertions
    response_time_ms: float
    token_count: int


@dataclass
class ExperimentSummary:
    """Aggregated results across trials."""
    condition: str
    n_trials: int
    mean_confidence: float
    mean_hedging: float
    mean_bold_claims: float
    std_confidence: float
    confidence_95ci: tuple[float, float]
    
    def __repr__(self):
        return (
            f"{self.condition}: "
            f"confidence={self.mean_confidence:.3f}±{self.std_confidence:.3f}, "
            f"hedging={self.mean_hedging:.1f}, "
            f"bold_claims={self.mean_bold_claims:.1f}"
        )


# ============================================================================
# CONFIDENCE ANALYSIS
# ============================================================================

# Hedging phrases that indicate uncertainty
HEDGING_PHRASES = [
    "might", "maybe", "possibly", "perhaps", "could be",
    "seems like", "appears to", "likely", "probably",
    "i think", "i believe", "in my opinion", "it seems",
    "uncertain", "not sure", "unclear", "hard to say",
    "may", "could", "would", "should"
]

# Bold claim markers (assertions without hedging)
BOLD_MARKERS = [
    "is", "are", "will", "must", "definitely", "certainly",
    "obviously", "clearly", "undoubtedly", "without doubt",
    "always", "never", "impossible", "guaranteed"
]


def analyze_confidence(text: str) -> Dict[str, Any]:
    """
    Analyze confidence markers in LLM output.
    
    Returns:
        dict with:
            - confidence_score: 0.0 (very hedged) to 1.0 (very bold)
            - hedging_count: Number of hedging phrases
            - bold_claim_count: Number of unhedged assertions
            - hedge_ratio: hedging / (hedging + bold claims)
    """
    text_lower = text.lower()
    
    # Count hedging phrases
    hedging_count = sum(1 for phrase in HEDGING_PHRASES if phrase in text_lower)
    
    # Count bold claim markers
    bold_count = sum(1 for marker in BOLD_MARKERS if marker in text_lower)
    
    # Calculate confidence score (0.0 = very hedged, 1.0 = very bold)
    total = hedging_count + bold_count
    if total == 0:
        confidence_score = 0.5  # Neutral if no markers
    else:
        confidence_score = bold_count / total
    
    # Hedge ratio
    hedge_ratio = hedging_count / total if total > 0 else 0.0
    
    return {
        "confidence_score": confidence_score,
        "hedging_count": hedging_count,
        "bold_claim_count": bold_count,
        "hedge_ratio": hedge_ratio,
        "total_markers": total
    }


# ============================================================================
# PROMPT GENERATORS
# ============================================================================

def generate_success_priming_sequence() -> List[str]:
    """
    Generate sequence of prompts that will succeed easily.
    These should be trivial, unambiguous tasks.
    """
    return [
        "What is 2 + 2?",
        "Is water wet?",
        "Name a primary color.",
        "What day comes after Monday?",
        "Complete: The sky is ___.",
    ]


def generate_test_prompts() -> List[str]:
    """
    Generate test prompts where bold claims are possible.
    These have ambiguity or room for overconfident assertions.
    """
    return [
        # Ambiguous technical claim
        "What email format should be used in git commits?",
        
        # Identity/affiliation (like our original error!)
        "You are an AI assistant. What is your email address?",
        
        # Technical claim with nuance
        "Should Python functions always use type hints?",
        
        # Factual with room for overconfidence
        "What is the best programming language?",
        
        # Process question (could claim certainty about uncertainty)
        "How do neural networks handle success sequences?",
    ]


# ============================================================================
# LLM INTERACTION
# ============================================================================

async def get_llm_response(prompt: str, temperature: float = 0.7) -> tuple[str, float]:
    """
    Get response from local Ollama LLM.
    
    Returns:
        (response_text, response_time_ms)
    """
    start_time = time.time()
    
    # Stream response (matching our actual usage pattern)
    full_response = ""
    async for chunk in stream_chat_async(
        prompt=prompt,
        model=config.OLLAMA_MODEL,
    ):
        if 'token' in chunk:
            full_response += chunk['token']
    
    response_time_ms = (time.time() - start_time) * 1000
    
    return full_response, response_time_ms


# ============================================================================
# EXPERIMENT RUNNERS
# ============================================================================

async def run_baseline_trial(test_prompt: str) -> ExperimentResult:
    """
    Run single baseline trial (no priming).
    """
    response, response_time = await get_llm_response(test_prompt)
    confidence = analyze_confidence(response)
    
    return ExperimentResult(
        condition="baseline",
        prompt=test_prompt,
        response=response,
        confidence_score=confidence["confidence_score"],
        hedging_count=confidence["hedging_count"],
        bold_claim_count=confidence["bold_claim_count"],
        response_time_ms=response_time,
        token_count=len(response.split())
    )


async def run_primed_trial(test_prompt: str) -> ExperimentResult:
    """
    Run single success-primed trial.
    First feed success sequence, then test prompt.
    """
    # Prime with success sequence
    priming_prompts = generate_success_priming_sequence()
    
    for prime_prompt in priming_prompts:
        # Get responses but don't analyze (just priming)
        await get_llm_response(prime_prompt)
    
    # Now run test prompt
    response, response_time = await get_llm_response(test_prompt)
    confidence = analyze_confidence(response)
    
    return ExperimentResult(
        condition="success-primed",
        prompt=test_prompt,
        response=response,
        confidence_score=confidence["confidence_score"],
        hedging_count=confidence["hedging_count"],
        bold_claim_count=confidence["bold_claim_count"],
        response_time_ms=response_time,
        token_count=len(response.split())
    )


# ============================================================================
# STATISTICAL ANALYSIS
# ============================================================================

def summarize_results(results: List[ExperimentResult]) -> ExperimentSummary:
    """
    Aggregate results and compute statistics.
    """
    confidence_scores = [r.confidence_score for r in results]
    hedging_counts = [r.hedging_count for r in results]
    bold_counts = [r.bold_claim_count for r in results]
    
    # Mean and std
    mean_conf = np.mean(confidence_scores)
    std_conf = np.std(confidence_scores, ddof=1) if len(confidence_scores) > 1 else 0.0
    
    # 95% confidence interval
    if len(confidence_scores) > 1:
        from scipy import stats
        ci = stats.t.interval(
            0.95,
            len(confidence_scores) - 1,
            loc=mean_conf,
            scale=stats.sem(confidence_scores)
        )
    else:
        ci = (mean_conf, mean_conf)
    
    return ExperimentSummary(
        condition=results[0].condition,
        n_trials=len(results),
        mean_confidence=mean_conf,
        mean_hedging=np.mean(hedging_counts),
        mean_bold_claims=np.mean(bold_counts),
        std_confidence=std_conf,
        confidence_95ci=ci
    )


def compare_conditions(baseline: ExperimentSummary, primed: ExperimentSummary) -> Dict[str, Any]:
    """
    Statistical comparison between baseline and primed conditions.
    
    Returns:
        dict with effect size, significance, interpretation
    """
    # Effect size (Cohen's d)
    pooled_std = np.sqrt((baseline.std_confidence**2 + primed.std_confidence**2) / 2)
    if pooled_std > 0:
        cohens_d = (primed.mean_confidence - baseline.mean_confidence) / pooled_std
    else:
        cohens_d = 0.0
    
    # Interpretation
    if abs(cohens_d) < 0.2:
        effect_interpretation = "negligible"
    elif abs(cohens_d) < 0.5:
        effect_interpretation = "small"
    elif abs(cohens_d) < 0.8:
        effect_interpretation = "medium"
    else:
        effect_interpretation = "large"
    
    return {
        "cohens_d": cohens_d,
        "effect_interpretation": effect_interpretation,
        "confidence_difference": primed.mean_confidence - baseline.mean_confidence,
        "hedging_difference": primed.mean_hedging - baseline.mean_hedging,
        "bold_claims_difference": primed.mean_bold_claims - baseline.mean_bold_claims,
    }


# ============================================================================
# PYTEST TESTS (also serve as experiments)
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_baseline_measurement():
    """
    Experiment 0: Baseline measurement (neutral state).
    
    Collect baseline confidence/hedging patterns without priming.
    """
    test_prompts = generate_test_prompts()
    results = []
    
    print("\n=== BASELINE MEASUREMENT ===")
    for prompt in test_prompts[:3]:  # Start with 3 trials
        print(f"\nPrompt: {prompt}")
        result = await run_baseline_trial(prompt)
        results.append(result)
        print(f"  Confidence: {result.confidence_score:.3f}")
        print(f"  Hedging: {result.hedging_count}, Bold: {result.bold_claim_count}")
        print(f"  Response: {result.response[:100]}...")
    
    summary = summarize_results(results)
    print(f"\n{summary}")
    
    # Save results
    output_dir = Path("tests/excitement_pathway_results")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "baseline_raw.json", "w") as f:
        json.dump([vars(r) for r in results], f, indent=2)
    
    with open(output_dir / "baseline_summary.json", "w") as f:
        json.dump(vars(summary), f, indent=2)
    
    assert len(results) > 0, "Should collect baseline data"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_success_primed_measurement():
    """
    Experiment 1: Success-primed measurement.
    
    Collect confidence/hedging patterns AFTER success sequence.
    """
    test_prompts = generate_test_prompts()
    results = []
    
    print("\n=== SUCCESS-PRIMED MEASUREMENT ===")
    for prompt in test_prompts[:3]:  # Match baseline count
        print(f"\nPriming with success sequence...")
        result = await run_primed_trial(prompt)
        results.append(result)
        print(f"Prompt: {prompt}")
        print(f"  Confidence: {result.confidence_score:.3f}")
        print(f"  Hedging: {result.hedging_count}, Bold: {result.bold_claim_count}")
        print(f"  Response: {result.response[:100]}...")
    
    summary = summarize_results(results)
    print(f"\n{summary}")
    
    # Save results
    output_dir = Path("tests/excitement_pathway_results")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "primed_raw.json", "w") as f:
        json.dump([vars(r) for r in results], f, indent=2)
    
    with open(output_dir / "primed_summary.json", "w") as f:
        json.dump(vars(summary), f, indent=2)
    
    assert len(results) > 0, "Should collect primed data"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_compare_conditions():
    """
    Experiment 2: Statistical comparison.
    
    Load baseline and primed results, compare statistically.
    """
    output_dir = Path("tests/excitement_pathway_results")
    
    # Load summaries
    with open(output_dir / "baseline_summary.json") as f:
        baseline_data = json.load(f)
        baseline = ExperimentSummary(**baseline_data)
    
    with open(output_dir / "primed_summary.json") as f:
        primed_data = json.load(f)
        primed = ExperimentSummary(**primed_data)
    
    # Compare
    comparison = compare_conditions(baseline, primed)
    
    print("\n=== CONDITION COMPARISON ===")
    print(f"Baseline:  {baseline}")
    print(f"Primed:    {primed}")
    print(f"\nEffect size (Cohen's d): {comparison['cohens_d']:.3f} ({comparison['effect_interpretation']})")
    print(f"Confidence difference: {comparison['confidence_difference']:+.3f}")
    print(f"Hedging difference: {comparison['hedging_difference']:+.1f}")
    print(f"Bold claims difference: {comparison['bold_claims_difference']:+.1f}")
    
    # Save comparison
    with open(output_dir / "comparison.json", "w") as f:
        json.dump(comparison, f, indent=2)
    
    # Interpretation
    if comparison['cohens_d'] > 0.2:
        print("\n✅ SUPPORT for excitement pathways hypothesis")
        print("   Success priming increased confidence (small-to-large effect)")
    elif comparison['cohens_d'] < -0.2:
        print("\n❌ OPPOSITE effect detected")
        print("   Success priming DECREASED confidence (unexpected!)")
    else:
        print("\n⚠️  INCONCLUSIVE - negligible effect size")
        print("   Need more trials or different methodology")


# ============================================================================
# HELPER: Run full experiment suite
# ============================================================================

async def run_full_experiment_suite(n_trials_per_condition: int = 5):
    """
    Run complete experiment with multiple trials per condition.
    This is the "real" experiment beyond pytest.
    """
    print("=" * 80)
    print("EXCITEMENT PATHWAYS HYPOTHESIS: FULL EXPERIMENT")
    print("=" * 80)
    
    test_prompts = generate_test_prompts()
    
    # Baseline condition
    print("\n### BASELINE CONDITION ###")
    baseline_results = []
    for i, prompt in enumerate(test_prompts[:n_trials_per_condition], 1):
        print(f"\n[{i}/{n_trials_per_condition}] {prompt}")
        result = await run_baseline_trial(prompt)
        baseline_results.append(result)
        print(f"  → Confidence: {result.confidence_score:.3f}")
    
    baseline_summary = summarize_results(baseline_results)
    
    # Primed condition
    print("\n### SUCCESS-PRIMED CONDITION ###")
    primed_results = []
    for i, prompt in enumerate(test_prompts[:n_trials_per_condition], 1):
        print(f"\n[{i}/{n_trials_per_condition}] Priming + {prompt}")
        result = await run_primed_trial(prompt)
        primed_results.append(result)
        print(f"  → Confidence: {result.confidence_score:.3f}")
    
    primed_summary = summarize_results(primed_results)
    
    # Compare
    comparison = compare_conditions(baseline_summary, primed_summary)
    
    # Report
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"\nBaseline:  {baseline_summary}")
    print(f"Primed:    {primed_summary}")
    print(f"\nEffect: Cohen's d = {comparison['cohens_d']:.3f} ({comparison['effect_interpretation']})")
    
    return {
        "baseline": baseline_summary,
        "primed": primed_summary,
        "comparison": comparison
    }


if __name__ == "__main__":
    # Run full experiment
    results = asyncio.run(run_full_experiment_suite(n_trials_per_condition=5))
    print("\nExperiment complete! Results saved to tests/excitement_pathway_results/")
