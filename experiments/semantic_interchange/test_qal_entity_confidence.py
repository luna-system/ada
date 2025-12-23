#!/usr/bin/env python3
"""
Phase 2: QAL Entity Confidence Scoring
========================================

Tests QAL hypothesis: "Introspective contraction sharpness"
- Do entities have high confidence (sharp measurement)?
- Or are they diffuse/uncertain (weak collapse)?

Uses multi-generation at same T to test entity stability
Expected runtime: ~60-90 minutes
Output: qal_results/phase2_entity_confidence.json
"""

import json
import time
from pathlib import Path
from datetime import datetime
from collections import Counter
import httpx
from typing import Dict, List, Any, Set

# Configuration
OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen2.5-coder:7b"
# Test key temps from Phase 1: peak (0.5), high (0.9), low (0.3)
TEST_TEMPS = [0.3, 0.5, 0.9]
RUNS_PER_TEMP = 10  # Multiple runs to test entity stability

TEST_PROMPT = """You are analyzing your own cognitive process. Extract the key semantic entities from this conversation and describe the relationships between them.

Conversation: "I've been thinking about how language models process information. The attention mechanism seems to create these patterns of activation across the embedding space. It's almost like quantum superposition - multiple possibilities exist until the next token collapses the wave function into a specific output. The temperature parameter controls how much exploration versus exploitation happens in that collapse."

Task: Extract the core semantic entities and their relationships. Be precise and structured."""


def extract_entities(text: str) -> Set[str]:
    """Extract semantic entities from response text."""
    entities = set()
    
    # Core concepts from prompt
    markers = [
        "attention mechanism", "embedding space", "quantum superposition",
        "wave function", "temperature parameter", "token", "collapse",
        "activation patterns", "language model", "processing", "exploration",
        "exploitation", "semantic", "cognitive", "information", "probability",
        "distribution", "context", "representation", "neural", "network"
    ]
    
    text_lower = text.lower()
    for marker in markers:
        if marker in text_lower:
            entities.add(marker)
    
    # Extract capitalized terms
    words = text.split()
    for word in words:
        if word and word[0].isupper() and len(word) > 2:
            clean = word.strip('.,;:()[]{}"\'-')
            if clean:
                entities.add(clean)
    
    return entities


def calculate_entity_confidence(entity_counts: Counter, total_runs: int) -> Dict[str, float]:
    """Calculate confidence score for each entity (frequency / total)."""
    return {
        entity: count / total_runs 
        for entity, count in entity_counts.items()
    }


def calculate_sharpness(confidences: List[float]) -> float:
    """
    Calculate "introspective contraction sharpness" (QAL term).
    High sharpness = consistent entities across runs (sharp measurement).
    Low sharpness = variable entities (diffuse measurement).
    
    Uses variance as inverse measure: lower variance = sharper.
    """
    if not confidences:
        return 0.0
    
    mean = sum(confidences) / len(confidences)
    variance = sum((c - mean) ** 2 for c in confidences) / len(confidences)
    
    # Normalize: sharp = 1 - sqrt(variance)
    sharpness = 1.0 - (variance ** 0.5)
    return max(0.0, sharpness)


def run_generation(temperature: float) -> Set[str]:
    """Run single generation and extract entities."""
    try:
        response = httpx.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": TEST_PROMPT,
                "temperature": temperature,
                "stream": False
            },
            timeout=60.0
        )
        response.raise_for_status()
        result = response.json()
        generated_text = result.get("response", "")
        return extract_entities(generated_text)
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return set()


def test_temperature(temp: float, runs: int) -> Dict[str, Any]:
    """Test entity stability at given temperature."""
    print(f"\n🌡️  Testing T={temp:.1f} ({runs} runs)")
    print("-" * 50)
    
    all_entities = []
    entity_counter = Counter()
    
    for run in range(runs):
        print(f"  Run {run + 1}/{runs}...", end=" ", flush=True)
        entities = run_generation(temp)
        
        if entities:
            print(f"✓ ({len(entities)} entities)")
            all_entities.append(entities)
            entity_counter.update(entities)
        else:
            print("✗ Failed")
        
        time.sleep(1)
    
    if not all_entities:
        return {
            "temperature": temp,
            "success": False,
            "error": "All runs failed"
        }
    
    # Calculate metrics
    total_unique = len(entity_counter)
    confidences = calculate_entity_confidence(entity_counter, runs)
    
    # Separate high-confidence (>0.5) from low-confidence entities
    high_conf = {e: c for e, c in confidences.items() if c > 0.5}
    low_conf = {e: c for e, c in confidences.items() if c <= 0.5}
    
    # Calculate sharpness
    sharpness = calculate_sharpness(list(confidences.values()))
    
    # Average entities per run
    avg_entities = sum(len(e) for e in all_entities) / len(all_entities)
    
    print(f"\n  📊 Results:")
    print(f"     Total unique entities: {total_unique}")
    print(f"     High confidence (>0.5): {len(high_conf)}")
    print(f"     Low confidence (≤0.5): {len(low_conf)}")
    print(f"     Average per run: {avg_entities:.1f}")
    print(f"     Sharpness: {sharpness:.3f}")
    
    # Top consistent entities
    top_entities = sorted(confidences.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f"\n  🎯 Most consistent entities:")
    for entity, conf in top_entities:
        print(f"     {conf:.2f}: {entity}")
    
    return {
        "temperature": temp,
        "total_runs": runs,
        "successful_runs": len(all_entities),
        "total_unique_entities": total_unique,
        "high_confidence_count": len(high_conf),
        "low_confidence_count": len(low_conf),
        "average_entities_per_run": avg_entities,
        "sharpness": sharpness,
        "high_confidence_entities": high_conf,
        "low_confidence_entities": low_conf,
        "top_10_entities": dict(top_entities),
        "success": True
    }


def run_experiment():
    """Run full entity confidence experiment."""
    print("=" * 70)
    print("🎯 Phase 2: QAL Entity Confidence Scoring")
    print("=" * 70)
    print(f"Model: {MODEL}")
    print(f"Temperatures: {TEST_TEMPS}")
    print(f"Runs per temperature: {RUNS_PER_TEMP}")
    print(f"Total generations: {len(TEST_TEMPS) * RUNS_PER_TEMP}")
    print(f"Estimated duration: {len(TEST_TEMPS) * RUNS_PER_TEMP * 1.5 / 60:.1f} minutes")
    print("=" * 70)
    
    # Create results directory
    results_dir = Path("qal_results")
    results_dir.mkdir(exist_ok=True)
    
    all_results = []
    
    for temp in TEST_TEMPS:
        result = test_temperature(temp, RUNS_PER_TEMP)
        if result["success"]:
            all_results.append(result)
    
    # Save results
    output_file = results_dir / f"phase2_entity_confidence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    final_output = {
        "experiment": "phase2_entity_confidence",
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "temperatures": TEST_TEMPS,
        "runs_per_temperature": RUNS_PER_TEMP,
        "results": all_results,
        "hypothesis": "Higher temperature = lower introspective contraction sharpness (QAL)"
    }
    
    with open(output_file, 'w') as f:
        json.dump(final_output, f, indent=2)
    
    print("\n" + "=" * 70)
    print("📊 Final Summary")
    print("=" * 70)
    print("\nTemp | Unique | High-Conf | Avg/Run | Sharpness")
    print("-" * 70)
    
    for result in all_results:
        t = result["temperature"]
        u = result["total_unique_entities"]
        h = result["high_confidence_count"]
        a = result["average_entities_per_run"]
        s = result["sharpness"]
        print(f"{t:.1f}  |  {u:3d}   |    {h:2d}     |  {a:4.1f}   |  {s:.3f}")
    
    print("=" * 70)
    print(f"\n✓ Results saved to: {output_file}")
    print("\n🔬 QAL Interpretation:")
    print("   High sharpness = entities collapse sharply (strong measurement)")
    print("   Low sharpness = entities diffuse (weak/uncertain measurement)")
    print("\n🎯 Next: Phase 3 - Meta-cognitive Gradient Analysis")
    print("=" * 70)


if __name__ == "__main__":
    run_experiment()
