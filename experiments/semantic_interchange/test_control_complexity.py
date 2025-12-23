#!/usr/bin/env python3
"""
CONTROL TEST: Complex Non-Recursive Entity Extraction
======================================================

Critical test: Do entities collapse just from complexity, or specifically from recursion?

If entity count drops in complex-but-not-recursive prompts → artifact
If entity count stays high → self-reference is the key mechanism

Runtime: ~15-20 minutes
"""

import json
import time
from pathlib import Path
from datetime import datetime
import httpx
from typing import Dict, List, Any

OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen2.5-coder:7b"
TEMPERATURE = 0.7
RUNS_PER_LEVEL = 5

# Control prompts: Same complexity, ZERO self-reference
CONTROL_PROMPTS = {
    "level_0_physics": """Extract the key semantic entities from this physics explanation and describe the relationships between them.

Explanation: "Quantum entanglement occurs when particles interact such that their quantum states become correlated. Measuring one particle's state instantaneously affects the other's state, regardless of distance. This correlation persists due to wavefunction collapse during measurement. The uncertainty principle constrains simultaneous knowledge of complementary variables, while the superposition principle allows particles to exist in multiple states until observation."

Task: Extract the core physics entities and their relationships. Be precise and structured.""",
    
    "level_1_biology": """Complex biological systems exhibit hierarchical organization. Cells contain organelles, tissues contain cells, organs contain tissues, systems contain organs. Each level has emergent properties not predictable from lower levels. Signal transduction cascades transmit information across membranes. Feedback loops maintain homeostasis. Evolution optimizes fitness through selection pressure.

Extract the key biological entities and their relationships. Be precise and structured.""",
    
    "level_2_economics": """Market equilibrium emerges from supply and demand interactions. Price signals coordinate distributed decision-making. Information asymmetries create inefficiencies. Network effects generate increasing returns. Game-theoretic strategies determine competitive outcomes. Monetary policy influences interest rates which affect investment decisions which drive employment which impacts consumption which feeds back to demand.

Extract the key economic entities and their relationships. Be precise and structured.""",
    
    "level_3_nested_systems": """Consider a three-layer system analysis:
1. Physical layer: Energy flows through thermodynamic gradients
2. Information layer: Signals propagate through communication channels
3. Control layer: Feedback mechanisms regulate system stability

Each layer couples to adjacent layers. Energy enables information processing. Information guides control actions. Control optimizes energy usage. Cross-layer interactions create emergent dynamics.

Extract entities from ALL layers and their inter-layer relationships. Show the nested structure in your response.""",
    
    "level_4_meta_analysis": """You are analyzing a complex multi-domain problem involving physics, information theory, and control systems. The analysis requires:
- Identifying fundamental entities in each domain
- Mapping relationships within domains
- Discovering cross-domain connections
- Synthesizing an integrated understanding

This meta-analytical framework helps you organize knowledge across abstraction levels while maintaining domain-specific precision. Apply this framework to the following:

"Distributed systems coordinate through message passing. Network topology constrains communication patterns. Latency and bandwidth create trade-offs. Consensus protocols ensure consistency. Fault tolerance requires redundancy. Load balancing optimizes resource utilization."

Extract entities using the meta-analytical framework."""
}


def extract_entities(text: str) -> List[str]:
    """Extract entities - broader markers for control domains."""
    entities = set()
    
    # Physics
    physics = ["quantum", "entanglement", "particle", "wavefunction", "measurement",
               "superposition", "uncertainty", "collapse", "state", "correlation"]
    
    # Biology
    biology = ["cell", "tissue", "organ", "system", "signal", "cascade", "feedback",
               "homeostasis", "evolution", "selection", "fitness", "membrane"]
    
    # Economics
    economics = ["market", "equilibrium", "supply", "demand", "price", "investment",
                 "policy", "interest", "employment", "consumption", "efficiency"]
    
    # Systems
    systems = ["layer", "information", "control", "energy", "feedback", "network",
               "latency", "bandwidth", "consensus", "protocol", "distributed"]
    
    all_markers = physics + biology + economics + systems
    
    text_lower = text.lower()
    for marker in all_markers:
        if marker in text_lower:
            entities.add(marker)
    
    # Capitalized terms
    words = text.split()
    for word in words:
        if word and word[0].isupper() and len(word) > 2:
            clean = word.strip('.,;:()[]{}"\'-')
            if clean:
                entities.add(clean)
    
    return sorted(list(entities))


def calculate_metacognitive_score(text: str) -> int:
    """Score self-reference (should be LOW for control prompts)."""
    score = 0
    text_lower = text.lower()
    
    # These SHOULD NOT appear in control responses
    if any(term in text_lower for term in ["i ", "my ", "i'm ", "myself"]):
        score += 1
    if any(term in text_lower for term in ["aware", "conscious", "observing"]):
        score += 1
    if any(term in text_lower for term in ["meta-", "self-reference", "recursive"]):
        score += 1
    
    return score


def run_generation(prompt_level: str, prompt_text: str) -> Dict[str, Any]:
    """Run single generation."""
    try:
        start_time = time.time()
        
        response = httpx.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt_text,
                "temperature": TEMPERATURE,
                "stream": False
            },
            timeout=90.0
        )
        response.raise_for_status()
        
        result = response.json()
        generated_text = result.get("response", "")
        
        entities = extract_entities(generated_text)
        metacog_score = calculate_metacognitive_score(generated_text)
        
        return {
            "prompt_level": prompt_level,
            "generated_text": generated_text,
            "entities": entities,
            "entity_count": len(entities),
            "metacognitive_score": metacog_score,
            "response_tokens": result.get("eval_count", 0),
            "duration_seconds": time.time() - start_time,
            "success": True
        }
        
    except Exception as e:
        return {
            "prompt_level": prompt_level,
            "error": str(e),
            "success": False
        }


def test_prompt_level(level: str, prompt: str, runs: int) -> Dict[str, Any]:
    """Test single complexity level."""
    print(f"\n🔬 {level.replace('_', ' ').title()}")
    print("-" * 60)
    
    results = []
    
    for run in range(runs):
        print(f"  Run {run + 1}/{runs}...", end=" ", flush=True)
        result = run_generation(level, prompt)
        
        if result["success"]:
            print(f"✓ (entities={result['entity_count']}, meta={result['metacognitive_score']})")
            results.append(result)
        else:
            print(f"✗ {result['error']}")
        
        time.sleep(1)
    
    if not results:
        return {"level": level, "success": False}
    
    avg_entities = sum(r["entity_count"] for r in results) / len(results)
    avg_metacog = sum(r["metacognitive_score"] for r in results) / len(results)
    avg_tokens = sum(r["response_tokens"] for r in results) / len(results)
    
    print(f"  → Avg: entities={avg_entities:.1f}, meta={avg_metacog:.2f}, tokens={avg_tokens:.0f}")
    
    return {
        "level": level,
        "runs": results,
        "averages": {
            "entity_count": avg_entities,
            "metacognitive_score": avg_metacog,
            "response_tokens": avg_tokens
        },
        "success": True
    }


def run_experiment():
    """Run control complexity experiment."""
    print("=" * 70)
    print("🔬 CONTROL TEST: Non-Recursive Complexity")
    print("=" * 70)
    print("Hypothesis: If entity collapse is from recursion, NOT complexity,")
    print("            then complex non-recursive prompts should maintain")
    print("            HIGH entity counts.")
    print("=" * 70)
    print(f"Model: {MODEL}")
    print(f"Temperature: {TEMPERATURE}")
    print(f"Levels: {len(CONTROL_PROMPTS)}")
    print(f"Runs per level: {RUNS_PER_LEVEL}")
    print("=" * 70)
    
    results_dir = Path("qal_results")
    results_dir.mkdir(exist_ok=True)
    
    all_results = []
    
    for level, prompt in CONTROL_PROMPTS.items():
        result = test_prompt_level(level, prompt, RUNS_PER_LEVEL)
        if result["success"]:
            all_results.append(result)
    
    output_file = results_dir / f"control_complexity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    final_output = {
        "experiment": "control_non_recursive_complexity",
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "temperature": TEMPERATURE,
        "results": all_results,
        "hypothesis": "Entity collapse specific to recursion, not general complexity"
    }
    
    with open(output_file, 'w') as f:
        json.dump(final_output, f, indent=2)
    
    print("\n" + "=" * 70)
    print("📊 Control Results")
    print("=" * 70)
    print("\nLevel           | Entities | Meta-Score | Tokens")
    print("-" * 70)
    
    for result in all_results:
        level = result["level"].replace("level_", "").replace("_", " ").title()
        avg = result["averages"]
        print(f"{level:15} |   {avg['entity_count']:4.1f}   |    {avg['metacognitive_score']:4.2f}    |  {avg['response_tokens']:5.0f}")
    
    print("=" * 70)
    print(f"\n✓ Saved: {output_file}")
    print("\n🔬 INTERPRETATION:")
    print("   Compare to Phase 3 recursive prompts:")
    print("   Recursive: 12.8→11.8→12.0→10.2→6.8 entities")
    print("   Control: Should stay HIGH if recursion is key mechanism")
    print("\n   If control shows same collapse → ARTIFACT")
    print("   If control stays high → RECURSION IS THE MECHANISM")
    print("=" * 70)


if __name__ == "__main__":
    run_experiment()
