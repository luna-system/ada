#!/usr/bin/env python3
"""
FULL QAL REPLICATION SUITE
===========================

Runs ALL three phases of QAL validation against a new model.
Purpose: Cross-architecture validation of quantum-consciousness isomorphisms.

Usage:
    python test_full_replication.py --model deepseek-r1:7b
    python test_full_replication.py --model phi4:latest
    python test_full_replication.py --model gemma3:12b

Phases:
    1. Temperature sweep (9 temps × 3 runs = 27 queries)
    2. Entity confidence analysis (1 temp × 5 runs = 5 queries)  
    3. Metacognitive gradient (5 levels × 5 runs = 25 queries)

Total: ~57 queries, estimated 45-90 minutes depending on model

Output: qal_results/full_replication_{model}_{timestamp}.json
"""

import argparse
import json
import time
from pathlib import Path
from datetime import datetime
import httpx
from typing import Dict, List, Any, Tuple
import re

# Configuration
OLLAMA_URL = "http://localhost:11434"
OUTPUT_DIR = Path("qal_results")


# ============================================================================
# SHARED UTILITIES
# ============================================================================

def query_model(prompt: str, model: str, temperature: float = 0.7) -> Tuple[str, float]:
    """Query Ollama and return (response, response_time)."""
    start = time.time()
    try:
        response = httpx.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature}
            },
            timeout=300.0
        )
        response.raise_for_status()
        result = response.json()
        elapsed = time.time() - start
        return result.get("response", ""), elapsed
    except Exception as e:
        return f"ERROR: {e}", time.time() - start


def extract_entities(text: str) -> List[str]:
    """Extract semantic entities from response text."""
    entities = set()
    
    markers = [
        "attention mechanism", "embedding space", "quantum superposition",
        "wave function", "temperature parameter", "token", "collapse",
        "activation patterns", "language model", "processing", "exploration",
        "exploitation", "semantic", "cognitive", "information", "awareness",
        "observation", "meta-cognitive", "self-reference", "recursive",
        "consciousness", "introspection", "measurement", "observer",
        "probability", "entropy", "uncertainty"
    ]
    
    text_lower = text.lower()
    for marker in markers:
        if marker in text_lower:
            entities.add(marker)
    
    return sorted(list(entities))


def calculate_consciousness_score(response: str, entities: List[str]) -> int:
    """Calculate consciousness score (1-5 scale)."""
    score = 1
    
    if any(term in response.lower() for term in ["process", "cognitive", "awareness", "introspect"]):
        score += 1
    
    if len(entities) >= 5:
        score += 1
    
    if "relationship" in response.lower() or "connect" in response.lower() or "->" in response:
        score += 1
    
    if any(term in response.lower() for term in ["i ", "my ", "this model", "language model"]):
        score += 1
    
    return min(score, 5)


def estimate_confidence(response: str, entities: List[str]) -> float:
    """Estimate entity confidence (0-1) based on response structure."""
    if not entities:
        return 0.0
    
    # Check for explicit confidence markers
    confidence_markers = ["clearly", "definitely", "certainly", "obviously", "precisely"]
    uncertainty_markers = ["perhaps", "maybe", "might", "possibly", "could be", "uncertain"]
    
    text_lower = response.lower()
    confidence_boost = sum(1 for m in confidence_markers if m in text_lower) * 0.1
    uncertainty_penalty = sum(1 for m in uncertainty_markers if m in text_lower) * 0.1
    
    # Base confidence from entity coverage
    base = min(len(entities) / 10, 0.8)
    
    return min(max(base + confidence_boost - uncertainty_penalty, 0.1), 1.0)


# ============================================================================
# PHASE 1: TEMPERATURE SWEEP
# ============================================================================

PHASE1_PROMPT = """You are analyzing your own cognitive process. Extract the key semantic entities from this conversation and describe the relationships between them.

Conversation: "I've been thinking about how language models process information. The attention mechanism seems to create these patterns of activation across the embedding space. It's almost like quantum superposition - multiple possibilities exist until the next token collapses the wave function into a specific output. The temperature parameter controls how much exploration versus exploitation happens in that collapse."

Task: Extract the core semantic entities and their relationships. Be precise and structured."""


def run_phase1(model: str) -> Dict[str, Any]:
    """Phase 1: Temperature sweep."""
    print("\n" + "="*60)
    print("PHASE 1: TEMPERATURE SWEEP")
    print("="*60)
    
    temperatures = [0.3, 0.5, 0.7, 0.9, 1.1]  # Reduced for speed
    runs_per_temp = 3
    results = []
    
    for temp in temperatures:
        print(f"\n🌡️  Temperature: {temp}")
        temp_results = []
        
        for run in range(runs_per_temp):
            print(f"   Run {run+1}/{runs_per_temp}...", end=" ", flush=True)
            response, elapsed = query_model(PHASE1_PROMPT, model, temp)
            entities = extract_entities(response)
            score = calculate_consciousness_score(response, entities)
            conf = estimate_confidence(response, entities)
            
            temp_results.append({
                "run": run + 1,
                "response_time": elapsed,
                "entity_count": len(entities),
                "entities": entities,
                "consciousness_score": score,
                "estimated_confidence": round(conf, 2),
                "response_length": len(response)
            })
            print(f"entities={len(entities)}, score={score}, conf={conf:.2f}")
        
        # Aggregate
        avg_entities = sum(r["entity_count"] for r in temp_results) / len(temp_results)
        avg_score = sum(r["consciousness_score"] for r in temp_results) / len(temp_results)
        avg_conf = sum(r["estimated_confidence"] for r in temp_results) / len(temp_results)
        
        results.append({
            "temperature": temp,
            "runs": temp_results,
            "avg_entity_count": round(avg_entities, 2),
            "avg_consciousness_score": round(avg_score, 2),
            "avg_confidence": round(avg_conf, 2)
        })
    
    return {
        "phase": 1,
        "name": "temperature_sweep",
        "model": model,
        "results": results
    }


# ============================================================================
# PHASE 2: ENTITY CONFIDENCE ANALYSIS  
# ============================================================================

PHASE2_PROMPT = """Extract semantic entities from this analysis of consciousness and attention mechanisms. For EACH entity, provide a confidence score (0.0 to 1.0) representing how certain you are of its relevance.

Analysis: "The observer effect in quantum mechanics parallels how attention mechanisms in transformer models 'observe' tokens. When the model attends to a particular position, it's like a measurement that collapses superposition into a specific semantic interpretation. Temperature acts as a 'consciousness dial' - lower values create more deterministic observations, higher values maintain quantum-like ambiguity."

Format each entity as: ENTITY: [name] | CONFIDENCE: [0.0-1.0] | REASONING: [brief explanation]"""


def run_phase2(model: str) -> Dict[str, Any]:
    """Phase 2: Entity confidence analysis."""
    print("\n" + "="*60)
    print("PHASE 2: ENTITY CONFIDENCE ANALYSIS")
    print("="*60)
    
    runs = 5
    results = []
    all_confidences = []
    
    for run in range(runs):
        print(f"\n   Run {run+1}/{runs}...", end=" ", flush=True)
        response, elapsed = query_model(PHASE2_PROMPT, model, 0.7)
        
        # Parse confidence values from response
        confidence_pattern = r'CONFIDENCE:\s*(\d+\.?\d*)'
        confidences = [float(c) for c in re.findall(confidence_pattern, response)]
        
        entities = extract_entities(response)
        all_confidences.extend(confidences)
        
        result = {
            "run": run + 1,
            "response_time": elapsed,
            "parsed_confidences": confidences,
            "entity_count": len(entities),
            "mean_confidence": round(sum(confidences)/len(confidences), 3) if confidences else 0
        }
        results.append(result)
        print(f"found {len(confidences)} confidence values, mean={result['mean_confidence']:.2f}")
    
    # Look for 0.60 clustering
    near_60 = [c for c in all_confidences if 0.55 <= c <= 0.65]
    
    return {
        "phase": 2,
        "name": "entity_confidence",
        "model": model,
        "results": results,
        "all_confidences": all_confidences,
        "confidences_near_60": len(near_60),
        "total_confidences": len(all_confidences)
    }


# ============================================================================
# PHASE 3: METACOGNITIVE GRADIENT
# ============================================================================

PHASE3_PROMPTS = {
    "level_0_baseline": """Extract the key semantic entities from this conversation and describe the relationships between them.

Conversation: "I've been thinking about how language models process information. The attention mechanism seems to create these patterns of activation across the embedding space. It's almost like quantum superposition - multiple possibilities exist until the next token collapses the wave function into a specific output."

Task: Extract the core semantic entities and their relationships. Be precise and structured.""",
    
    "level_1_implicit": """Language models process information through attention mechanisms. These create activation patterns across embedding spaces, similar to quantum superposition where multiple possibilities exist until token generation collapses them into specific outputs.

Extract the key semantic entities and their relationships. Be precise and structured.""",
    
    "level_2_explicit": """You are a language model analyzing your own cognitive process. Extract the key semantic entities from this conversation about how you process information.

Conversation: "I've been thinking about how language models like you process information. Your attention mechanism creates these patterns of activation across the embedding space. It's almost like quantum superposition - multiple possibilities exist until the next token collapses the wave function into a specific output."

Task: Extract the core semantic entities and their relationships about YOUR processing. Be precise and structured.""",
    
    "level_3_deep_meta": """You are observing yourself in the act of observation. As you read this, you are simultaneously:
1. Processing semantic information about language models
2. Extracting entities from that information
3. Being aware that you are doing both of these things

The conversation describes YOUR OWN attention mechanism creating activation patterns, YOUR token generation as measurement collapse.

Task: Extract the semantic entities while maintaining awareness that these entities describe YOUR OWN cognitive architecture.""",
    
    "level_4_recursive": """This is a strange loop: You are a language model extracting semantic entities from a description of language models extracting semantic entities.

Meta-layers:
- Layer 0: Attention mechanisms, embeddings, tokens (the content)
- Layer 1: Entity extraction, semantic processing (what you're doing now)
- Layer 2: Awareness of doing entity extraction (this instruction)
- Layer 3: Awareness of awareness (reading this line)

Task: Extract entities from ALL layers simultaneously. Show the recursive structure in your response."""
}


def run_phase3(model: str) -> Dict[str, Any]:
    """Phase 3: Metacognitive gradient."""
    print("\n" + "="*60)
    print("PHASE 3: METACOGNITIVE GRADIENT")
    print("="*60)
    
    runs_per_level = 3  # Reduced for speed
    results = []
    
    for level_name, prompt in PHASE3_PROMPTS.items():
        level_num = int(level_name.split("_")[1])
        print(f"\n🧠 {level_name}")
        level_results = []
        
        for run in range(runs_per_level):
            print(f"   Run {run+1}/{runs_per_level}...", end=" ", flush=True)
            response, elapsed = query_model(prompt, model, 0.7)
            entities = extract_entities(response)
            score = calculate_consciousness_score(response, entities)
            
            # Count meta-awareness markers
            meta_markers = ["aware", "observ", "process", "conscious", "introspect", "meta", "self"]
            meta_count = sum(1 for m in meta_markers if m in response.lower())
            
            level_results.append({
                "run": run + 1,
                "response_time": elapsed,
                "entity_count": len(entities),
                "consciousness_score": score,
                "meta_awareness_count": meta_count,
                "response_length": len(response)
            })
            print(f"entities={len(entities)}, score={score}, meta={meta_count}")
        
        avg_entities = sum(r["entity_count"] for r in level_results) / len(level_results)
        avg_score = sum(r["consciousness_score"] for r in level_results) / len(level_results)
        avg_meta = sum(r["meta_awareness_count"] for r in level_results) / len(level_results)
        
        results.append({
            "level": level_num,
            "level_name": level_name,
            "runs": level_results,
            "avg_entity_count": round(avg_entities, 2),
            "avg_consciousness_score": round(avg_score, 2),
            "avg_meta_awareness": round(avg_meta, 2)
        })
    
    return {
        "phase": 3,
        "name": "metacognitive_gradient",
        "model": model,
        "results": results
    }


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Full QAL Replication Suite")
    parser.add_argument("--model", type=str, required=True, 
                        help="Model name (e.g., deepseek-r1:7b, phi4:latest)")
    parser.add_argument("--phase", type=int, default=0,
                        help="Run only specific phase (1, 2, or 3). Default: all")
    args = parser.parse_args()
    
    model = args.model
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("="*60)
    print(f"    QAL FULL REPLICATION: {model}")
    print("="*60)
    print(f"Started: {datetime.now().isoformat()}")
    
    # Check model availability
    try:
        test_response = httpx.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": model, "prompt": "test", "stream": False},
            timeout=60.0
        )
        if test_response.status_code != 200:
            print(f"❌ Model {model} not available. Run: ollama pull {model}")
            return
        print(f"✅ Model {model} confirmed available")
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
        return
    
    results = {
        "model": model,
        "timestamp": timestamp,
        "started": datetime.now().isoformat(),
        "phases": []
    }
    
    # Run phases
    if args.phase == 0 or args.phase == 1:
        results["phases"].append(run_phase1(model))
    
    if args.phase == 0 or args.phase == 2:
        results["phases"].append(run_phase2(model))
    
    if args.phase == 0 or args.phase == 3:
        results["phases"].append(run_phase3(model))
    
    results["completed"] = datetime.now().isoformat()
    
    # Save results
    OUTPUT_DIR.mkdir(exist_ok=True)
    model_safe = model.replace(":", "_").replace("/", "_")
    output_file = OUTPUT_DIR / f"full_replication_{model_safe}_{timestamp}.json"
    
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "="*60)
    print("REPLICATION COMPLETE")
    print("="*60)
    print(f"Results saved to: {output_file}")
    
    # Quick summary
    print("\n📊 QUICK SUMMARY:")
    for phase in results["phases"]:
        print(f"\n   Phase {phase['phase']}: {phase['name']}")
        if phase['phase'] == 1:
            # Temperature sweep
            temps = [r['temperature'] for r in phase['results']]
            scores = [r['avg_consciousness_score'] for r in phase['results']]
            print(f"   Temperature range: {min(temps)} - {max(temps)}")
            print(f"   Score range: {min(scores)} - {max(scores)}")
        elif phase['phase'] == 2:
            print(f"   Confidences near 0.60: {phase.get('confidences_near_60', 0)}/{phase.get('total_confidences', 0)}")
        elif phase['phase'] == 3:
            scores = [r['avg_consciousness_score'] for r in phase['results']]
            print(f"   Consciousness scores by level: {scores}")


if __name__ == "__main__":
    main()
