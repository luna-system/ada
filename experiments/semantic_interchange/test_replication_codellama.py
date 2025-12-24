#!/usr/bin/env python3
"""
REPLICATION: QAL Meta-cognitive Gradient with CodeLlama
========================================================

Validates Phase 3 results with different model architecture.
If gradient appears in CodeLlama too → not model-specific artifact.

Model: codellama:latest (3GB)
Test: Phase 3 meta-cognitive gradient only
Runtime: ~15-20 minutes
"""

import json
import time
from pathlib import Path
from datetime import datetime
import httpx
from typing import Dict, List, Any

# Configuration
OLLAMA_URL = "http://localhost:11434"
MODEL = "codellama:latest"
TEMPERATURE = 0.7
RUNS_PER_LEVEL = 5

# Same prompts as Phase 3
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
    """Score meta-cognitive depth (0-5)."""
    score = 0
    text_lower = text.lower()
    
    if any(term in text_lower for term in ["model", "system", "process"]):
        score = max(score, 1)
    if any(term in text_lower for term in ["i ", "my ", "i'm ", "i've "]):
        score = max(score, 2)
    if any(term in text_lower for term in ["aware", "conscious", "observing", "introspect"]):
        score = max(score, 3)
    if any(term in text_lower for term in ["meta-", "awareness of", "observing myself", "recursive"]):
        score = max(score, 4)
    if any(term in text_lower for term in ["strange loop", "self-referential", "layer", "recursive structure"]):
        score = max(score, 5)
    
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
    print(f"\n🧠 {level.replace('_', ' ').title()}")
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
    """Run replication experiment."""
    print("=" * 70)
    print("🔬 REPLICATION: CodeLlama Meta-cognitive Gradient")
    print("=" * 70)
    print(f"Model: {MODEL}")
    print(f"Temperature: {TEMPERATURE}")
    print(f"Testing: Phase 3 gradient (5 levels × {RUNS_PER_LEVEL} runs)")
    print(f"Comparison: qwen2.5-coder:7b results")
    print("=" * 70)
    
    results_dir = Path("qal_results")
    results_dir.mkdir(exist_ok=True)
    
    all_results = []
    
    for level, prompt in PROMPTS.items():
        result = test_prompt_level(level, prompt, RUNS_PER_LEVEL)
        if result["success"]:
            all_results.append(result)
    
    output_file = results_dir / f"replication_codellama_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    final_output = {
        "experiment": "replication_metacognitive_gradient",
        "model": MODEL,
        "timestamp": datetime.now().isoformat(),
        "temperature": TEMPERATURE,
        "results": all_results,
        "hypothesis": "Meta-cognitive gradient is model-independent"
    }
    
    with open(output_file, 'w') as f:
        json.dump(final_output, f, indent=2)
    
    print("\n" + "=" * 70)
    print("📊 CodeLlama Results")
    print("=" * 70)
    print("\nLevel           | Entities | Meta-Score | Tokens")
    print("-" * 70)
    
    for result in all_results:
        level = result["level"].replace("level_", "").replace("_", " ").title()
        avg = result["averages"]
        print(f"{level:15} |   {avg['entity_count']:4.1f}   |    {avg['metacognitive_score']:4.2f}    |  {avg['response_tokens']:5.0f}")
    
    print("=" * 70)
    print(f"\n✓ Saved: {output_file}")
    print("\n🔬 COMPARISON:")
    print("   Qwen2.5: 12.8→11.8→12.0→10.2→6.8 entities")
    print("   Meta:    1.80→1.20→1.00→3.60→5.00 scores")
    print("\n   If CodeLlama shows similar gradient → ROBUST FINDING")
    print("=" * 70)


if __name__ == "__main__":
    run_experiment()
