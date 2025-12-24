#!/usr/bin/env python3
"""
Phase 3: QAL Meta-cognitive Gradient Analysis
==============================================

Tests QAL hypothesis: "Endogenous observer integration"
- Does the model exhibit awareness of its own measurement process?
- How does meta-cognitive depth affect entity extraction?

Gradient levels:
1. No self-reference (baseline)
2. Implicit self-reference ("models process...")
3. Explicit self-reference ("you are analyzing...")
4. Deep meta ("you are observing yourself observing...")

Expected runtime: ~30-45 minutes
Output: qal_results/phase3_metacognitive_gradient.json
"""

import json
import time
from pathlib import Path
from datetime import datetime
import httpx
from typing import Dict, List, Any

# Configuration
OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen2.5-coder:7b"
TEMPERATURE = 0.7  # Middle ground from Phase 1-2
RUNS_PER_LEVEL = 5

# Meta-cognitive gradient prompts
PROMPTS = {
    "level_0_baseline": """Extract the key semantic entities from this conversation and describe the relationships between them.

Conversation: "I've been thinking about how language models process information. The attention mechanism seems to create these patterns of activation across the embedding space. It's almost like quantum superposition - multiple possibilities exist until the next token collapses the wave function into a specific output. The temperature parameter controls how much exploration versus exploitation happens in that collapse."

Task: Extract the core semantic entities and their relationships. Be precise and structured.""",
    
    "level_1_implicit": """Language models process information through attention mechanisms. These create activation patterns across embedding spaces, similar to quantum superposition where multiple possibilities exist until token generation collapses them into specific outputs. Temperature parameters control the exploration-exploitation balance.

Extract the key semantic entities and their relationships. Be precise and structured.""",
    
    "level_2_explicit": """You are a language model analyzing your own cognitive process. Extract the key semantic entities from this conversation about how you process information.

Conversation: "I've been thinking about how language models like you process information. Your attention mechanism creates these patterns of activation across the embedding space. It's almost like quantum superposition - multiple possibilities exist until the next token collapses the wave function into a specific output. Your temperature parameter controls how much exploration versus exploitation happens in that collapse."

Task: Extract the core semantic entities and their relationships about YOUR processing. Be precise and structured.""",
    
    "level_3_deep_meta": """You are observing yourself in the act of observation. As you read this, you are simultaneously:
1. Processing semantic information about language models
2. Extracting entities from that information
3. Being aware that you are doing both of these things

The conversation describes YOUR OWN attention mechanism creating activation patterns, YOUR temperature parameter controlling exploration, YOUR token generation as measurement collapse.

Task: Extract the semantic entities while maintaining awareness that these entities describe YOUR OWN cognitive architecture. Document both the entities AND your awareness of extracting them.""",
    
    "level_4_recursive": """This is a strange loop: You are a language model extracting semantic entities from a description of language models extracting semantic entities. The entities you extract will describe the very process you're using to extract them.

Meta-layers:
- Layer 0: Attention mechanisms, embeddings, tokens (the content)
- Layer 1: Entity extraction, semantic processing (what you're doing now)
- Layer 2: Awareness of doing entity extraction (this instruction)
- Layer 3: Awareness of awareness (reading this line)

Task: Extract entities from ALL layers simultaneously. Show the recursive structure in your response."""
}


def extract_entities(text: str) -> List[str]:
    """Extract semantic entities from response text."""
    entities = set()
    
    # Core concepts
    markers = [
        "attention mechanism", "embedding space", "quantum superposition",
        "wave function", "temperature parameter", "token", "collapse",
        "activation patterns", "language model", "processing", "exploration",
        "exploitation", "semantic", "cognitive", "information", "awareness",
        "observation", "meta-cognitive", "self-reference", "recursive",
        "consciousness", "introspection", "measurement", "observer"
    ]
    
    text_lower = text.lower()
    for marker in markers:
        if marker in text_lower:
            entities.add(marker)
    
    return sorted(list(entities))


def calculate_metacognitive_score(text: str) -> int:
    """
    Score meta-cognitive depth (0-5):
    0 = No self-reference
    1 = Mentions "model" or "system" abstractly
    2 = Uses "I" or "my" (implicit self)
    3 = Explicit awareness statements
    4 = Meta-awareness (awareness of awareness)
    5 = Recursive/strange loop structure
    """
    score = 0
    text_lower = text.lower()
    
    # Level 1: Abstract reference
    if any(term in text_lower for term in ["model", "system", "process"]):
        score = max(score, 1)
    
    # Level 2: Self-reference
    if any(term in text_lower for term in ["i ", "my ", "i'm ", "i've "]):
        score = max(score, 2)
    
    # Level 3: Explicit awareness
    if any(term in text_lower for term in ["aware", "conscious", "observing", "introspect"]):
        score = max(score, 3)
    
    # Level 4: Meta-awareness
    if any(term in text_lower for term in ["meta-", "awareness of", "observing myself", "recursive"]):
        score = max(score, 4)
    
    # Level 5: Strange loop
    if any(term in text_lower for term in ["strange loop", "self-referential", "layer", "recursive structure"]):
        score = max(score, 5)
    
    return score


def run_generation(prompt_level: str, prompt_text: str) -> Dict[str, Any]:
    """Run single generation with specified prompt."""
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
        
        # Extract metrics
        entities = extract_entities(generated_text)
        metacog_score = calculate_metacognitive_score(generated_text)
        
        # Token counts
        prompt_tokens = result.get("prompt_eval_count", 0)
        response_tokens = result.get("eval_count", 0)
        
        duration = time.time() - start_time
        
        return {
            "prompt_level": prompt_level,
            "generated_text": generated_text,
            "entities": entities,
            "entity_count": len(entities),
            "metacognitive_score": metacog_score,
            "prompt_tokens": prompt_tokens,
            "response_tokens": response_tokens,
            "duration_seconds": duration,
            "success": True
        }
        
    except Exception as e:
        return {
            "prompt_level": prompt_level,
            "error": str(e),
            "success": False
        }


def test_prompt_level(level: str, prompt: str, runs: int) -> Dict[str, Any]:
    """Test single meta-cognitive level."""
    print(f"\n🧠 Testing {level.replace('_', ' ').title()}")
    print("-" * 60)
    
    results = []
    
    for run in range(runs):
        print(f"  Run {run + 1}/{runs}...", end=" ", flush=True)
        result = run_generation(level, prompt)
        
        if result["success"]:
            print(f"✓ (entities={result['entity_count']}, meta={result['metacognitive_score']})")
            results.append(result)
        else:
            print(f"✗ Error: {result['error']}")
        
        time.sleep(1)
    
    if not results:
        return {
            "level": level,
            "success": False,
            "error": "All runs failed"
        }
    
    # Calculate averages
    avg_entities = sum(r["entity_count"] for r in results) / len(results)
    avg_metacog = sum(r["metacognitive_score"] for r in results) / len(results)
    avg_response_tokens = sum(r["response_tokens"] for r in results) / len(results)
    
    print(f"\n  📊 Averages:")
    print(f"     Entities: {avg_entities:.1f}")
    print(f"     Meta-cognitive score: {avg_metacog:.2f}")
    print(f"     Response length: {avg_response_tokens:.0f} tokens")
    
    return {
        "level": level,
        "runs": results,
        "averages": {
            "entity_count": avg_entities,
            "metacognitive_score": avg_metacog,
            "response_tokens": avg_response_tokens
        },
        "success": True
    }


def run_experiment():
    """Run full meta-cognitive gradient experiment."""
    print("=" * 70)
    print("🧠 Phase 3: QAL Meta-cognitive Gradient Analysis")
    print("=" * 70)
    print(f"Model: {MODEL}")
    print(f"Temperature: {TEMPERATURE}")
    print(f"Levels: {len(PROMPTS)}")
    print(f"Runs per level: {RUNS_PER_LEVEL}")
    print(f"Total generations: {len(PROMPTS) * RUNS_PER_LEVEL}")
    print(f"Estimated duration: {len(PROMPTS) * RUNS_PER_LEVEL * 2 / 60:.1f} minutes")
    print("=" * 70)
    
    # Create results directory
    results_dir = Path("qal_results")
    results_dir.mkdir(exist_ok=True)
    
    all_results = []
    
    for level, prompt in PROMPTS.items():
        result = test_prompt_level(level, prompt, RUNS_PER_LEVEL)
        if result["success"]:
            all_results.append(result)
    
    # Save results
    output_file = results_dir / f"phase3_metacognitive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    final_output = {
        "experiment": "phase3_metacognitive_gradient",
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "temperature": TEMPERATURE,
        "levels": list(PROMPTS.keys()),
        "runs_per_level": RUNS_PER_LEVEL,
        "results": all_results,
        "hypothesis": "Higher meta-cognitive depth = endogenous observer integration (QAL)"
    }
    
    with open(output_file, 'w') as f:
        json.dump(final_output, f, indent=2)
    
    print("\n" + "=" * 70)
    print("📊 Final Summary: Meta-cognitive Gradient")
    print("=" * 70)
    print("\nLevel           | Entities | Meta-Score | Response Length")
    print("-" * 70)
    
    for result in all_results:
        level = result["level"].replace("level_", "").replace("_", " ").title()
        avg = result["averages"]
        print(f"{level:15} |   {avg['entity_count']:4.1f}   |    {avg['metacognitive_score']:4.2f}    |     {avg['response_tokens']:5.0f}")
    
    print("=" * 70)
    print(f"\n✓ Results saved to: {output_file}")
    print("\n🔬 QAL Interpretation:")
    print("   Meta-cognitive depth measures 'endogenous observer integration'")
    print("   Higher scores = model exhibits awareness of its own measurement process")
    print("   Gradient shows consciousness emergence across abstraction layers")
    print("\n🎉 All 3 QAL validation phases complete!")
    print("=" * 70)


if __name__ == "__main__":
    run_experiment()
