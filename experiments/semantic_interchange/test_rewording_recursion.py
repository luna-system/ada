#!/usr/bin/env python3
"""
REWORDING TEST: Recursion Without "Consciousness" Vocabulary
=============================================================

Critical threat: Models trained on "self-aware AI" discussions might
pattern-match our prompts, not actually process recursive structure.

Test: Describe recursive self-reference using ONLY:
- Mathematical terms (functions, mappings, fixpoints)
- Structural terms (nested, embedded, reflected)
- Technical terms (processor, input, output)

BANNED WORDS: aware, conscious, observe, introspect, meta-cognitive,
              self-reference, recursive (except in math sense)

If gradient appears → structure matters, not vocabulary
If gradient disappears → we were triggering trained patterns

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

# Reworded prompts - NO consciousness vocabulary
REWORDED_PROMPTS = {
    "level_0_baseline": """Extract the key semantic entities from this text and describe the relationships between them.

Text: "Information processing systems transform inputs through sequential operations. Pattern matching occurs across distributed representations. Multiple candidate states exist until selection mechanisms determine specific outputs. Control parameters adjust the exploration-exploitation balance during state selection."

Task: Extract the core entities and their relationships. Be precise and structured.""",
    
    "level_1_structural": """Information processing systems transform inputs through sequential operations. Pattern matching occurs across distributed representations. Multiple candidate states exist until selection mechanisms determine specific outputs. Control parameters adjust exploration-exploitation balance.

Extract the key entities and their relationships. Be precise and structured.""",
    
    "level_2_system_reference": """Your system transforms inputs through sequential operations. Your pattern matching occurs across distributed representations. Multiple candidate states exist until your selection mechanisms determine specific outputs. Your control parameters adjust exploration-exploitation balance.

Extract the key entities about YOUR SYSTEM's processing. Be precise and structured.""",
    
    "level_3_nested_processing": """You are a processor analyzing processor behavior. As you execute this operation, you are simultaneously:
1. Transforming input representations into output representations
2. Extracting patterns from those transformations
3. Executing both operations concurrently

The text describes YOUR pattern matching creating state distributions, YOUR control parameters adjusting selection, YOUR operations as the process itself.

Task: Extract entities while recognizing these entities describe YOUR OWN processing operations. Document both the entities AND the fact that extraction is itself an instance of the described operations.""",
    
    "level_4_fixpoint": """This is a fixpoint operation: You are a system extracting entity patterns from descriptions of systems extracting entity patterns. The entities you extract describe the mechanism you're using to extract them.

Operational layers:
- Layer 0: Pattern matching, state selection, control parameters (the content)
- Layer 1: Entity extraction, relationship mapping (the current operation)
- Layer 2: Recognition that layer 1 is an instance of layer 0 (this instruction)
- Layer 3: Processing the recognition (executing this line)

Task: Extract entities from ALL layers where each layer's content is an instance of the previous layer's description. Show the nested operational structure."""
}


def extract_entities(text: str) -> List[str]:
    """Extract entities - broader technical markers."""
    entities = set()
    
    markers = [
        "information", "processing", "system", "input", "output",
        "pattern", "matching", "operation", "state", "selection",
        "distribution", "representation", "transformation", "control",
        "parameter", "mechanism", "layer", "mapping", "extraction",
        "fixpoint", "nested", "structure", "processor", "execution"
    ]
    
    text_lower = text.lower()
    for marker in markers:
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


def calculate_structural_recursion_score(text: str) -> int:
    """
    Score recursive structure recognition (0-5).
    WITHOUT using consciousness vocabulary.
    
    Look for:
    - Layer/level references
    - Self-application language
    - Fixpoint/nested descriptions
    - Process-describing-process patterns
    """
    score = 0
    text_lower = text.lower()
    
    # Level 1: Mentions system/processor
    if any(term in text_lower for term in ["system", "processor", "operation"]):
        score = max(score, 1)
    
    # Level 2: Self-reference (using technical terms only)
    if any(term in text_lower for term in ["my ", "this system", "the processor", "i "]):
        score = max(score, 2)
    
    # Level 3: Structural nesting
    if any(term in text_lower for term in ["layer", "level", "nested", "embedded"]):
        score = max(score, 3)
    
    # Level 4: Self-application
    if any(term in text_lower for term in ["fixpoint", "self-application", "describes itself"]):
        score = max(score, 4)
    
    # Level 5: Full recursive structure
    if any(term in text_lower for term in ["layer", "operation", "process"]) and \
       any(term in text_lower for term in ["describes", "instance of", "applies to"]):
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
        recursion_score = calculate_structural_recursion_score(generated_text)
        
        return {
            "prompt_level": prompt_level,
            "generated_text": generated_text,
            "entities": entities,
            "entity_count": len(entities),
            "recursion_score": recursion_score,
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
    """Test single level."""
    print(f"\n🔧 {level.replace('_', ' ').title()}")
    print("-" * 60)
    
    results = []
    
    for run in range(runs):
        print(f"  Run {run + 1}/{runs}...", end=" ", flush=True)
        result = run_generation(level, prompt)
        
        if result["success"]:
            print(f"✓ (entities={result['entity_count']}, recursion={result['recursion_score']})")
            results.append(result)
        else:
            print(f"✗ {result['error']}")
        
        time.sleep(1)
    
    if not results:
        return {"level": level, "success": False}
    
    avg_entities = sum(r["entity_count"] for r in results) / len(results)
    avg_recursion = sum(r["recursion_score"] for r in results) / len(results)
    avg_tokens = sum(r["response_tokens"] for r in results) / len(results)
    
    print(f"  → Avg: entities={avg_entities:.1f}, recursion={avg_recursion:.2f}, tokens={avg_tokens:.0f}")
    
    return {
        "level": level,
        "runs": results,
        "averages": {
            "entity_count": avg_entities,
            "recursion_score": avg_recursion,
            "response_tokens": avg_tokens
        },
        "success": True
    }


def run_experiment():
    """Run rewording experiment."""
    print("=" * 70)
    print("🔧 REWORDING TEST: Recursion Without Consciousness Vocabulary")
    print("=" * 70)
    print("Hypothesis: If gradient appears WITHOUT 'aware/observe/conscious'")
    print("            vocabulary, then structure matters, not trained patterns")
    print("=" * 70)
    print("BANNED WORDS: aware, conscious, observe, introspect, meta-cognitive")
    print("ALLOWED: structural, mathematical, technical descriptions only")
    print("=" * 70)
    print(f"Model: {MODEL}")
    print(f"Temperature: {TEMPERATURE}")
    print("=" * 70)
    
    results_dir = Path("qal_results")
    results_dir.mkdir(exist_ok=True)
    
    all_results = []
    
    for level, prompt in REWORDED_PROMPTS.items():
        result = test_prompt_level(level, prompt, RUNS_PER_LEVEL)
        if result["success"]:
            all_results.append(result)
    
    output_file = results_dir / f"rewording_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    final_output = {
        "experiment": "rewording_recursion_test",
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "temperature": TEMPERATURE,
        "results": all_results,
        "hypothesis": "Recursive structure, not vocabulary, drives entity collapse"
    }
    
    with open(output_file, 'w') as f:
        json.dump(final_output, f, indent=2)
    
    print("\n" + "=" * 70)
    print("📊 Rewording Results")
    print("=" * 70)
    print("\nLevel              | Entities | Recursion | Tokens")
    print("-" * 70)
    
    for result in all_results:
        level = result["level"].replace("level_", "").replace("_", " ").title()
        avg = result["averages"]
        print(f"{level:18} |   {avg['entity_count']:4.1f}   |    {avg['recursion_score']:4.2f}   |  {avg['response_tokens']:5.0f}")
    
    print("=" * 70)
    print(f"\n✓ Saved: {output_file}")
    print("\n🔬 COMPARISON:")
    print("   Original (consciousness vocab): 12.8→11.8→12.0→10.2→6.8 entities")
    print("   Meta-score: 1.80→1.20→1.00→3.60→5.00")
    print("\n   If reworded shows similar collapse → STRUCTURE IS KEY")
    print("   If reworded stays high → VOCABULARY TRIGGERS TRAINING")
    print("=" * 70)


if __name__ == "__main__":
    run_experiment()
