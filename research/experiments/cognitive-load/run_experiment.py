#!/usr/bin/env python3
"""
Cognitive Load Boundary Experiment

Run: python research/experiments/cognitive-load/run_experiment.py

Measures how prompt complexity affects model response success.
Tests the hypothesis that LLM cognitive capacity has probabilistic thresholds.
"""

import sys
from pathlib import Path

# Add research lib to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lib.experiment_runner import ExperimentRunner, ExperimentConfig

def main():
    config = ExperimentConfig(
        experiment_name="cognitive-load-boundaries",
        model="qwen2.5-coder:7b",
        runs_per_stimulus=5,  # More runs for statistical significance
        timeout_seconds=30.0,
        hypothesis="LLM cognitive architecture has probabilistic thresholds, not hard limits"
    )
    
    runner = ExperimentRunner(config)
    
    stimuli_file = Path(__file__).parent / "stimuli.json"
    results_dir = Path(__file__).parent / "results"
    
    results = runner.run_from_file(stimuli_file)
    output_path = runner.save_results(results, results_dir)
    
    # Print detailed analysis
    print("\n" + "=" * 60)
    print("📊 COGNITIVE LOAD ANALYSIS")
    print("=" * 60)
    
    # Group by stimulus
    by_stimulus = {}
    for trial in results.trials:
        sid = trial["stimulus_id"]
        if sid not in by_stimulus:
            by_stimulus[sid] = []
        by_stimulus[sid].append(trial)
    
    # Order by complexity level (from stimuli.json)
    import json
    with open(stimuli_file) as f:
        stimuli_data = json.load(f)
    
    id_to_complexity = {p["id"]: p["complexity_level"] for p in stimuli_data["prompts"]}
    
    print(f"\n{'Stimulus':<20} {'Level':>6} {'Words':>6} {'Success':>8} {'Avg TTFT':>10} {'Coherence':>10}")
    print("-" * 70)
    
    for stimulus in stimuli_data["prompts"]:
        sid = stimulus["id"]
        trials = by_stimulus.get(sid, [])
        
        if trials:
            success_rate = sum(1 for t in trials if t["success"]) / len(trials)
            successful = [t for t in trials if t["success"]]
            avg_ttft = sum(t["latency_seconds"] for t in successful) / len(successful) if successful else 0
            avg_coherence = sum(t["metrics"].get("coherence", {}).get("score", 0) for t in successful) / len(successful) if successful else 0
            
            print(f"{sid:<20} {stimulus['complexity_level']:>6} {stimulus['word_count']:>6} {success_rate:>7.0%} {avg_ttft:>9.2f}s {avg_coherence:>9.2f}")
    
    print("\n📈 KEY FINDINGS:")
    print("-" * 40)
    
    # Detect threshold
    threshold_detected = None
    for stimulus in stimuli_data["prompts"]:
        trials = by_stimulus.get(stimulus["id"], [])
        success_rate = sum(1 for t in trials if t["success"]) / len(trials) if trials else 0
        if success_rate < 0.8 and threshold_detected is None:
            threshold_detected = stimulus
    
    if threshold_detected:
        print(f"⚠️  Threshold detected at: {threshold_detected['id']}")
        print(f"   Complexity level: {threshold_detected['complexity_level']}")
        print(f"   Word count: {threshold_detected['word_count']}")
    else:
        print("✅ No hard threshold detected - model handled all complexity levels")
        print("   BUT check variance in TTFT for soft threshold indicators")
    
    return output_path

if __name__ == "__main__":
    main()
