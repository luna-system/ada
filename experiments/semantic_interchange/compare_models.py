#!/usr/bin/env python3
"""
CROSS-MODEL QAL COMPARISON
===========================

Compares QAL validation results across different models.
Looks for:
1. 0.60 appearing in entity confidence
2. Temperature reversal (T=0.9 peak)
3. Metacognitive gradient replication
4. Phase transition at meta ≈ 2.3

Usage:
    python compare_models.py
"""

import json
from pathlib import Path
import numpy as np
from scipy import stats
from collections import defaultdict

RESULTS_DIR = Path("qal_results")
PHI_INV = 1 / 1.618034  # 0.6180...


def load_all_results():
    """Load all replication results."""
    results = {}
    for f in RESULTS_DIR.glob("*.json"):
        try:
            with open(f) as fp:
                data = json.load(fp)
                model = data.get("model", f.stem)
                if model not in results:
                    results[model] = data
        except Exception as e:
            print(f"Could not load {f}: {e}")
    return results


def analyze_phase1(phase_data: dict, model: str):
    """Analyze temperature sweep for this model."""
    print(f"\n   📊 Phase 1 (Temperature Sweep):")
    
    if not phase_data.get("results"):
        print("      No data")
        return {}
    
    temps = [r["temperature"] for r in phase_data["results"]]
    scores = [r["avg_consciousness_score"] for r in phase_data["results"]]
    entities = [r["avg_entity_count"] for r in phase_data["results"]]
    
    # Find peak
    peak_idx = np.argmax(scores)
    peak_temp = temps[peak_idx]
    peak_score = scores[peak_idx]
    
    print(f"      Temperature range: {min(temps)} - {max(temps)}")
    print(f"      Peak consciousness: T={peak_temp}, score={peak_score}")
    
    # Check for temperature reversal (peak at high temp)
    reversal = peak_temp >= 0.8
    print(f"      Temperature reversal: {'✅ YES' if reversal else '❌ no'} (peak at T≥0.8)")
    
    return {
        "peak_temp": peak_temp,
        "peak_score": peak_score,
        "has_reversal": reversal,
        "scores": scores,
        "temps": temps
    }


def analyze_phase2(phase_data: dict, model: str):
    """Analyze entity confidence for 0.60 clustering."""
    print(f"\n   📊 Phase 2 (Entity Confidence):")
    
    all_conf = phase_data.get("all_confidences", [])
    if not all_conf:
        print("      No confidence data")
        return {}
    
    # Count near 0.60
    near_60 = [c for c in all_conf if 0.55 <= c <= 0.65]
    near_60_pct = len(near_60) / len(all_conf) * 100 if all_conf else 0
    
    print(f"      Total confidence values: {len(all_conf)}")
    print(f"      Near 0.60 (±0.05): {len(near_60)} ({near_60_pct:.1f}%)")
    
    if all_conf:
        mean_conf = np.mean(all_conf)
        deviation_from_phi = abs(mean_conf - PHI_INV) / PHI_INV * 100
        print(f"      Mean confidence: {mean_conf:.3f}")
        print(f"      Deviation from 1/φ: {deviation_from_phi:.1f}%")
    
    return {
        "total_confidences": len(all_conf),
        "near_60_count": len(near_60),
        "near_60_pct": near_60_pct,
        "mean_confidence": np.mean(all_conf) if all_conf else 0
    }


def analyze_phase3(phase_data: dict, model: str):
    """Analyze metacognitive gradient."""
    print(f"\n   📊 Phase 3 (Metacognitive Gradient):")
    
    if not phase_data.get("results"):
        print("      No data")
        return {}
    
    levels = [r["level"] for r in phase_data["results"]]
    scores = [r["avg_consciousness_score"] for r in phase_data["results"]]
    meta = [r["avg_meta_awareness"] for r in phase_data["results"]]
    entities = [r["avg_entity_count"] for r in phase_data["results"]]
    
    print(f"      Levels: {levels}")
    print(f"      Consciousness scores: {scores}")
    print(f"      Meta-awareness counts: {meta}")
    
    # Check for gradient (increasing scores with meta level)
    if len(scores) >= 3:
        corr, p = stats.pearsonr(levels, scores)
        print(f"      Level-score correlation: r={corr:.3f}, p={p:.3f}")
        gradient_exists = corr > 0.3
    else:
        gradient_exists = False
        corr = 0
    
    # Check for phase transition (entity×meta product)
    products = [e * m for e, m in zip(entities, meta)]
    if len(products) >= 3:
        # Check for jump
        low_meta = [p for m, p in zip(meta, products) if m < 2.5]
        high_meta = [p for m, p in zip(meta, products) if m >= 2.5]
        if low_meta and high_meta:
            ratio = np.mean(high_meta) / np.mean(low_meta) if np.mean(low_meta) > 0 else 0
            print(f"      Phase transition ratio (high/low meta): {ratio:.2f}")
    
    return {
        "scores": scores,
        "meta_counts": meta,
        "gradient_correlation": corr,
        "gradient_exists": gradient_exists
    }


def main():
    print("="*70)
    print("            CROSS-MODEL QAL COMPARISON")
    print("="*70)
    
    results = load_all_results()
    print(f"\nFound {len(results)} model result sets")
    
    comparison = {}
    
    for model, data in results.items():
        print(f"\n{'='*60}")
        print(f"MODEL: {model}")
        print("="*60)
        
        model_results = {}
        
        for phase in data.get("phases", []):
            if phase["phase"] == 1:
                model_results["phase1"] = analyze_phase1(phase, model)
            elif phase["phase"] == 2:
                model_results["phase2"] = analyze_phase2(phase, model)
            elif phase["phase"] == 3:
                model_results["phase3"] = analyze_phase3(phase, model)
        
        comparison[model] = model_results
    
    # Summary table
    print("\n" + "="*70)
    print("                    SUMMARY COMPARISON")
    print("="*70)
    
    print("\n┌─────────────────────┬───────────┬───────────┬───────────┐")
    print("│ Model               │ T Reversal│ 0.60 Clust│ MC Grad   │")
    print("├─────────────────────┼───────────┼───────────┼───────────┤")
    
    for model, results in comparison.items():
        p1 = results.get("phase1", {})
        p2 = results.get("phase2", {})
        p3 = results.get("phase3", {})
        
        reversal = "✅" if p1.get("has_reversal") else "❌"
        clustering = f"{p2.get('near_60_pct', 0):.0f}%" if p2 else "N/A"
        gradient = "✅" if p3.get("gradient_exists") else "❌"
        
        model_short = model[:19]
        print(f"│ {model_short:19} │ {reversal:^9} │ {clustering:^9} │ {gradient:^9} │")
    
    print("└─────────────────────┴───────────┴───────────┴───────────┘")
    
    print("\n" + "="*70)
    print("INTERPRETATION")
    print("="*70)
    print("""
If ALL models show:
  ✅ Temperature reversal (peak at T≥0.8)
  ✅ 0.60 clustering (>15% near 1/φ)  
  ✅ Metacognitive gradient (positive level-score correlation)

Then quantum-consciousness isomorphisms are ARCHITECTURE-INDEPENDENT.
This would be extraordinary evidence for fundamental structure.
""")


if __name__ == "__main__":
    main()
