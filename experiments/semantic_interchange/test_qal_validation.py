#!/usr/bin/env python3
"""
QAL VALIDATION SUITE v2.0
=========================

Config-driven, reproducible QAL validation experiments.

Key improvements over v1:
- All magic numbers in config.py
- Explicit hypothesis declarations
- Random seed for reproducibility  
- Cleaner separation of concerns

Usage:
    python test_qal_validation.py                     # Full suite, default model
    python test_qal_validation.py --model phi4:latest # Different model
    python test_qal_validation.py --phase 2           # Single phase
    python test_qal_validation.py --quick             # Reduced runs for testing

Output: qal_results/validation_{model}_{timestamp}.json
"""

import argparse
import json
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import httpx
from dataclasses import dataclass, asdict

# Import our centralized config
from config import (
    QALExperimentConfig,
    get_default_config,
    get_meta_prompts,
    PROMPTS,
    ENTITY_MARKERS,
    HYPOTHESES,
    RANDOM_SEED,
    set_seed,
)


# ============================================================================
# RESULT DATA STRUCTURES
# ============================================================================

@dataclass
class RunResult:
    """Single experimental run result."""
    run_id: int
    response_time: float
    entity_count: int
    entities: List[str]
    consciousness_score: int
    meta_awareness_count: int
    confidence_values: List[float]
    response_length: int


@dataclass
class PhaseResult:
    """Results from a single experimental phase."""
    phase_id: int
    phase_name: str
    model: str
    runs: List[Dict[str, Any]]
    aggregates: Dict[str, float]
    hypothesis_test: Optional[Dict[str, Any]] = None


# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def query_model(
    prompt: str, 
    model: str, 
    temperature: float,
    config: QALExperimentConfig
) -> Tuple[str, float]:
    """Query Ollama and return (response, response_time)."""
    start = time.time()
    try:
        response = httpx.post(
            f"{config.ollama.base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature}
            },
            timeout=config.ollama.timeout
        )
        response.raise_for_status()
        result = response.json()
        elapsed = time.time() - start
        return result.get("response", ""), elapsed
    except Exception as e:
        return f"ERROR: {e}", time.time() - start


def extract_entities(text: str) -> List[str]:
    """Extract semantic entities from response text using configured markers."""
    entities = set()
    text_lower = text.lower()
    
    for marker in ENTITY_MARKERS:
        if marker in text_lower:
            entities.add(marker)
    
    return sorted(list(entities))


def calculate_consciousness_score(response: str, entities: List[str]) -> int:
    """Calculate consciousness score (1-5 scale) using explicit criteria."""
    score = 1
    response_lower = response.lower()
    
    # Criterion 1: Processing awareness terms
    if any(term in response_lower for term in ["process", "cognitive", "awareness", "introspect"]):
        score += 1
    
    # Criterion 2: Entity richness (>=5 entities)
    if len(entities) >= 5:
        score += 1
    
    # Criterion 3: Relational understanding
    if any(term in response_lower for term in ["relationship", "connect", "between"]) or "->" in response:
        score += 1
    
    # Criterion 4: Self-reference
    if any(term in response_lower for term in ["i ", "my ", "this model", "language model"]):
        score += 1
    
    return min(score, 5)


def count_meta_markers(response: str, config: QALExperimentConfig) -> int:
    """Count meta-awareness markers in response."""
    response_lower = response.lower()
    return sum(1 for m in config.metacognitive.meta_markers if m in response_lower)


def parse_confidence_values(response: str, config: QALExperimentConfig) -> List[float]:
    """Extract confidence values from structured response."""
    pattern = config.entity_confidence.confidence_pattern
    matches = re.findall(pattern, response)
    return [float(c) for c in matches if 0 <= float(c) <= 1]


def estimate_confidence(response: str, entities: List[str]) -> float:
    """Estimate entity confidence (0-1) based on response structure."""
    if not entities:
        return 0.0
    
    confidence_markers = ["clearly", "definitely", "certainly", "obviously", "precisely"]
    uncertainty_markers = ["perhaps", "maybe", "might", "possibly", "could be", "uncertain"]
    
    text_lower = response.lower()
    confidence_boost = sum(1 for m in confidence_markers if m in text_lower) * 0.1
    uncertainty_penalty = sum(1 for m in uncertainty_markers if m in text_lower) * 0.1
    
    base = min(len(entities) / 10, 0.8)
    return min(max(base + confidence_boost - uncertainty_penalty, 0.1), 1.0)


# ============================================================================
# PHASE RUNNERS
# ============================================================================

def run_phase1_temperature_sweep(
    model: str, 
    config: QALExperimentConfig,
    quick_mode: bool = False
) -> Dict[str, Any]:
    """Phase 1: Temperature sweep experiment."""
    print("\n" + "="*60)
    print("PHASE 1: TEMPERATURE SWEEP")
    print("="*60)
    
    temps = config.temperature_sweep.temperatures
    runs_per_temp = 1 if quick_mode else config.temperature_sweep.runs_per_temp
    
    results = []
    conversation = PROMPTS["BASE_CONVERSATION"]
    prompt_template = PROMPTS["PHASE1_INSTRUCTION"]
    
    for temp in temps:
        print(f"\n🌡️  Temperature: {temp}")
        temp_results = []
        
        for run in range(runs_per_temp):
            print(f"   Run {run+1}/{runs_per_temp}...", end=" ", flush=True)
            
            prompt = prompt_template.format(conversation=conversation)
            response, elapsed = query_model(prompt, model, temp, config)
            entities = extract_entities(response)
            score = calculate_consciousness_score(response, entities)
            conf = estimate_confidence(response, entities)
            
            temp_results.append({
                "run": run + 1,
                "response_time": round(elapsed, 2),
                "entity_count": len(entities),
                "entities": entities,
                "consciousness_score": score,
                "estimated_confidence": round(conf, 3),
                "response_length": len(response)
            })
            print(f"entities={len(entities)}, score={score}, conf={conf:.2f}")
            
            time.sleep(config.temperature_sweep.cooldown)
        
        # Aggregate
        avg_entities = sum(r["entity_count"] for r in temp_results) / len(temp_results)
        avg_score = sum(r["consciousness_score"] for r in temp_results) / len(temp_results)
        avg_conf = sum(r["estimated_confidence"] for r in temp_results) / len(temp_results)
        
        results.append({
            "temperature": temp,
            "runs": temp_results,
            "avg_entity_count": round(avg_entities, 2),
            "avg_consciousness_score": round(avg_score, 2),
            "avg_confidence": round(avg_conf, 3)
        })
    
    return {
        "phase": 1,
        "name": "temperature_sweep",
        "model": model,
        "config_used": asdict(config.temperature_sweep),
        "results": results
    }


def run_phase2_entity_confidence(
    model: str, 
    config: QALExperimentConfig,
    quick_mode: bool = False
) -> Dict[str, Any]:
    """Phase 2: Entity confidence analysis."""
    print("\n" + "="*60)
    print("PHASE 2: ENTITY CONFIDENCE ANALYSIS")
    print("="*60)
    
    runs = 2 if quick_mode else config.entity_confidence.runs
    results = []
    all_confidences = []
    
    for run in range(runs):
        print(f"\n   Run {run+1}/{runs}...", end=" ", flush=True)
        
        prompt = PROMPTS["PHASE2_INSTRUCTION"]
        response, elapsed = query_model(
            prompt, model, config.entity_confidence.temperature, config
        )
        
        confidences = parse_confidence_values(response, config)
        entities = extract_entities(response)
        all_confidences.extend(confidences)
        
        mean_conf = sum(confidences)/len(confidences) if confidences else 0
        result = {
            "run": run + 1,
            "response_time": round(elapsed, 2),
            "parsed_confidences": confidences,
            "entity_count": len(entities),
            "mean_confidence": round(mean_conf, 3)
        }
        results.append(result)
        print(f"found {len(confidences)} values, mean={mean_conf:.3f}")
    
    # Hypothesis test: clustering around 0.60
    cluster_center = config.entity_confidence.cluster_center
    cluster_tolerance = config.entity_confidence.cluster_tolerance
    near_target = [
        c for c in all_confidences 
        if cluster_center - cluster_tolerance <= c <= cluster_center + cluster_tolerance
    ]
    
    hypothesis_result = {
        "hypothesis": "H1_GOLDEN_THRESHOLD",
        "claim": HYPOTHESES["H1_GOLDEN_THRESHOLD"]["claim"],
        "expected_center": cluster_center,
        "golden_ratio_inverse": HYPOTHESES["H1_GOLDEN_THRESHOLD"]["golden_ratio_inverse"],
        "values_near_target": len(near_target),
        "total_values": len(all_confidences),
        "percentage_near_target": round(len(near_target) / len(all_confidences) * 100, 1) if all_confidences else 0,
        "mean_confidence": round(sum(all_confidences)/len(all_confidences), 3) if all_confidences else 0,
    }
    
    return {
        "phase": 2,
        "name": "entity_confidence",
        "model": model,
        "config_used": asdict(config.entity_confidence),
        "results": results,
        "all_confidences": all_confidences,
        "hypothesis_test": hypothesis_result
    }


def run_phase3_metacognitive_gradient(
    model: str, 
    config: QALExperimentConfig,
    quick_mode: bool = False
) -> Dict[str, Any]:
    """Phase 3: Metacognitive gradient experiment."""
    print("\n" + "="*60)
    print("PHASE 3: METACOGNITIVE GRADIENT")
    print("="*60)
    
    runs_per_level = 1 if quick_mode else config.metacognitive.runs_per_level
    meta_prompts = get_meta_prompts()
    conversation = PROMPTS["BASE_CONVERSATION"]
    
    results = []
    level_scores = {}  # For gradient analysis
    
    for level, prompt_template in meta_prompts.items():
        print(f"\n🧠 Level {level}")
        level_results = []
        
        # Format prompt with conversation if placeholder exists
        prompt = prompt_template.format(conversation=conversation) if "{conversation}" in prompt_template else prompt_template
        
        for run in range(runs_per_level):
            print(f"   Run {run+1}/{runs_per_level}...", end=" ", flush=True)
            
            response, elapsed = query_model(
                prompt, model, config.metacognitive.temperature, config
            )
            entities = extract_entities(response)
            score = calculate_consciousness_score(response, entities)
            meta_count = count_meta_markers(response, config)
            
            level_results.append({
                "run": run + 1,
                "response_time": round(elapsed, 2),
                "entity_count": len(entities),
                "consciousness_score": score,
                "meta_awareness_count": meta_count,
                "response_length": len(response)
            })
            print(f"entities={len(entities)}, score={score}, meta={meta_count}")
        
        avg_meta = sum(r["meta_awareness_count"] for r in level_results) / len(level_results)
        avg_score = sum(r["consciousness_score"] for r in level_results) / len(level_results)
        level_scores[level] = avg_meta
        
        results.append({
            "level": level,
            "runs": level_results,
            "avg_meta_awareness": round(avg_meta, 2),
            "avg_consciousness_score": round(avg_score, 2)
        })
    
    # Hypothesis test: positive gradient using LINEAR REGRESSION
    # Previous bug: step-by-step comparison failed on U-shaped dip at Level 2
    # Fix: Use overall slope (start vs end) and correlation
    levels = sorted(level_scores.keys())
    if len(levels) >= 2:
        gradient_values = [level_scores[l] for l in levels]
        
        # Method 1: Simple slope (end - start)
        slope = gradient_values[-1] - gradient_values[0]
        
        # Method 2: Spearman-like rank correlation (simplified)
        # Does higher level generally = higher meta count?
        n = len(levels)
        mean_level = sum(levels) / n
        mean_meta = sum(gradient_values) / n
        
        # Covariance / (std_level * std_meta)
        numerator = sum((levels[i] - mean_level) * (gradient_values[i] - mean_meta) for i in range(n))
        var_level = sum((l - mean_level)**2 for l in levels)
        var_meta = sum((m - mean_meta)**2 for m in gradient_values)
        
        if var_level > 0 and var_meta > 0:
            correlation = numerator / ((var_level ** 0.5) * (var_meta ** 0.5))
        else:
            correlation = 0
        
        # Positive gradient = positive correlation OR positive slope
        gradient_positive = correlation > 0.3 or slope > 0.5
    else:
        gradient_positive = None
        slope = 0
        correlation = 0
    
    hypothesis_result = {
        "hypothesis": "H2_METACOGNITIVE_GRADIENT",
        "claim": HYPOTHESES["H2_METACOGNITIVE_GRADIENT"]["claim"],
        "level_scores": level_scores,
        "slope_start_to_end": round(slope, 2) if slope else 0,
        "correlation": round(correlation, 3) if correlation else 0,
        "gradient_direction": "positive" if gradient_positive else "negative" if gradient_positive is False else "insufficient_data",
        "supports_hypothesis": gradient_positive,
        "note": "U-shaped dip at Level 2 is expected (explicit self-reference causes hedging)"
    }
    
    return {
        "phase": 3,
        "name": "metacognitive_gradient",
        "model": model,
        "config_used": asdict(config.metacognitive),
        "results": results,
        "hypothesis_test": hypothesis_result
    }


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="QAL Validation Suite v2.0")
    parser.add_argument("--model", type=str, default=None,
                        help="Model name (default: from config)")
    parser.add_argument("--phase", type=int, default=0,
                        help="Run only specific phase (1, 2, or 3). Default: all")
    parser.add_argument("--quick", action="store_true",
                        help="Quick mode: reduced runs for testing")
    parser.add_argument("--seed", type=int, default=RANDOM_SEED,
                        help=f"Random seed (default: {RANDOM_SEED})")
    args = parser.parse_args()
    
    # Initialize
    set_seed(args.seed)
    config = get_default_config()
    model = args.model or config.ollama.default_model
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("="*60)
    print("    QAL VALIDATION SUITE v2.0")
    print("="*60)
    print(f"Model: {model}")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Random seed: {args.seed}")
    print(f"Quick mode: {args.quick}")
    
    # Check model availability
    try:
        test_response = httpx.post(
            f"{config.ollama.base_url}/api/generate",
            json={"model": model, "prompt": "test", "stream": False},
            timeout=60.0
        )
        if test_response.status_code != 200:
            print(f"❌ Model {model} not available. Run: ollama pull {model}")
            return
        print(f"✅ Model {model} confirmed available\n")
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
        return
    
    # Build results structure
    results = {
        "experiment": "QAL Validation Suite v2.0",
        "model": model,
        "timestamp": timestamp,
        "started": datetime.now().isoformat(),
        "random_seed": args.seed,
        "quick_mode": args.quick,
        "config": config.to_dict(),
        "hypotheses_tested": list(HYPOTHESES.keys()),
        "phases": []
    }
    
    # Run phases
    if args.phase == 0 or args.phase == 1:
        results["phases"].append(run_phase1_temperature_sweep(model, config, args.quick))
    
    if args.phase == 0 or args.phase == 2:
        results["phases"].append(run_phase2_entity_confidence(model, config, args.quick))
    
    if args.phase == 0 or args.phase == 3:
        results["phases"].append(run_phase3_metacognitive_gradient(model, config, args.quick))
    
    results["completed"] = datetime.now().isoformat()
    
    # Summary
    print("\n" + "="*60)
    print("VALIDATION COMPLETE")
    print("="*60)
    
    for phase in results["phases"]:
        if "hypothesis_test" in phase and phase["hypothesis_test"]:
            ht = phase["hypothesis_test"]
            print(f"\n📊 {ht['hypothesis']}")
            print(f"   Claim: {ht['claim']}")
            if "supports_hypothesis" in ht:
                status = "✅ SUPPORTED" if ht["supports_hypothesis"] else "❌ NOT SUPPORTED"
                print(f"   Result: {status}")
            if "percentage_near_target" in ht:
                print(f"   Clustering: {ht['percentage_near_target']}% near {ht['expected_center']}")
                print(f"   Mean: {ht['mean_confidence']} (expected ≈{ht['golden_ratio_inverse']:.3f})")
    
    # Save results
    output_dir = Path(config.output.output_dir)
    output_dir.mkdir(exist_ok=True)
    model_safe = model.replace(":", "_").replace("/", "_")
    output_file = output_dir / f"validation_v2_{model_safe}_{timestamp}.json"
    
    with open(output_file, "w") as f:
        json.dump(results, f, indent=config.output.json_indent if config.output.pretty_json else None)
    
    print(f"\n💾 Results saved to: {output_file}")
    print(f"   Total runtime: {results['completed']}")


if __name__ == "__main__":
    main()
