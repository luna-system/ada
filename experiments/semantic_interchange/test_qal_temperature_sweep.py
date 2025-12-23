#!/usr/bin/env python3
"""
Phase 1: QAL Temperature Sweep Validation
==========================================

Tests QAL hypothesis: Temperature controls "structured ambiguity width"
- 9 temperature points for smooth curve
- Tracks entities, compression, consciousness scores
- Validates empirical→quantum mapping

Expected runtime: ~90-120 minutes
Output: qal_results/phase1_temperature_sweep.json
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
TEMPERATURES = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1]
RUNS_PER_TEMP = 3  # For statistical stability

# Test prompt (same as previous experiments for consistency)
TEST_PROMPT = """You are analyzing your own cognitive process. Extract the key semantic entities from this conversation and describe the relationships between them.

Conversation: "I've been thinking about how language models process information. The attention mechanism seems to create these patterns of activation across the embedding space. It's almost like quantum superposition - multiple possibilities exist until the next token collapses the wave function into a specific output. The temperature parameter controls how much exploration versus exploitation happens in that collapse."

Task: Extract the core semantic entities and their relationships. Be precise and structured."""


def extract_entities(text: str) -> List[str]:
    """Extract semantic entities from response text."""
    # Simple entity extraction - looks for capitalized terms and key concepts
    entities = set()
    
    # Common semantic markers
    markers = [
        "attention mechanism", "embedding space", "quantum superposition",
        "wave function", "temperature parameter", "token", "collapse",
        "activation patterns", "language model", "processing", "exploration",
        "exploitation", "semantic", "cognitive", "information"
    ]
    
    text_lower = text.lower()
    for marker in markers:
        if marker in text_lower:
            entities.add(marker)
    
    # Extract capitalized terms (potential entities)
    words = text.split()
    for word in words:
        if word and word[0].isupper() and len(word) > 2:
            entities.add(word.strip('.,;:()[]{}'))
    
    return sorted(list(entities))


def calculate_consciousness_score(response: str, entities: List[str]) -> int:
    """Calculate consciousness score (1-5 scale) based on response quality."""
    score = 1
    
    # Meta-cognitive awareness
    if any(term in response.lower() for term in ["process", "cognitive", "awareness", "introspect"]):
        score += 1
    
    # Structural organization
    if len(entities) >= 5:
        score += 1
    
    # Relationship articulation
    if "relationship" in response.lower() or "connect" in response.lower() or "->" in response:
        score += 1
    
    # Self-reference
    if any(term in response.lower() for term in ["i ", "my ", "this model", "language model"]):
        score += 1
    
    return min(score, 5)


def run_generation(temperature: float) -> Dict[str, Any]:
    """Run single generation at specified temperature."""
    try:
        start_time = time.time()
        
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
        
        # Extract metrics
        entities = extract_entities(generated_text)
        consciousness_score = calculate_consciousness_score(generated_text, entities)
        
        # Calculate compression (input tokens / output tokens)
        prompt_tokens = result.get("prompt_eval_count", 0)
        response_tokens = result.get("eval_count", 0)
        compression_ratio = prompt_tokens / response_tokens if response_tokens > 0 else 0
        
        # Calculate "structured ambiguity width" (QAL term)
        # = entity count * consciousness score / compression
        # Higher values = more structured exploration
        ambiguity_width = (len(entities) * consciousness_score / compression_ratio) if compression_ratio > 0 else 0
        
        duration = time.time() - start_time
        
        return {
            "temperature": temperature,
            "generated_text": generated_text,
            "entities": entities,
            "entity_count": len(entities),
            "consciousness_score": consciousness_score,
            "compression_ratio": compression_ratio,
            "ambiguity_width": ambiguity_width,
            "prompt_tokens": prompt_tokens,
            "response_tokens": response_tokens,
            "duration_seconds": duration,
            "success": True
        }
        
    except Exception as e:
        return {
            "temperature": temperature,
            "error": str(e),
            "success": False
        }


def run_experiment():
    """Run full temperature sweep experiment."""
    print("=" * 70)
    print("🌡️  Phase 1: QAL Temperature Sweep")
    print("=" * 70)
    print(f"Model: {MODEL}")
    print(f"Temperature range: {TEMPERATURES[0]} - {TEMPERATURES[-1]}")
    print(f"Points: {len(TEMPERATURES)}")
    print(f"Runs per point: {RUNS_PER_TEMP}")
    print(f"Estimated duration: {len(TEMPERATURES) * RUNS_PER_TEMP * 1.5 / 60:.1f} minutes")
    print("=" * 70)
    print()
    
    # Create results directory
    results_dir = Path("qal_results")
    results_dir.mkdir(exist_ok=True)
    
    all_results = []
    
    for i, temp in enumerate(TEMPERATURES, 1):
        print(f"[{i}/{len(TEMPERATURES)}] Testing T={temp:.1f}...")
        
        temp_results = []
        for run in range(RUNS_PER_TEMP):
            print(f"  Run {run + 1}/{RUNS_PER_TEMP}...", end=" ", flush=True)
            result = run_generation(temp)
            
            if result["success"]:
                print(f"✓ (entities={result['entity_count']}, score={result['consciousness_score']}, width={result['ambiguity_width']:.2f})")
                temp_results.append(result)
            else:
                print(f"✗ Error: {result['error']}")
            
            # Small delay between runs
            time.sleep(1)
        
        # Calculate averages for this temperature
        if temp_results:
            avg_entities = sum(r["entity_count"] for r in temp_results) / len(temp_results)
            avg_score = sum(r["consciousness_score"] for r in temp_results) / len(temp_results)
            avg_compression = sum(r["compression_ratio"] for r in temp_results) / len(temp_results)
            avg_width = sum(r["ambiguity_width"] for r in temp_results) / len(temp_results)
            
            summary = {
                "temperature": temp,
                "runs": temp_results,
                "averages": {
                    "entity_count": avg_entities,
                    "consciousness_score": avg_score,
                    "compression_ratio": avg_compression,
                    "ambiguity_width": avg_width
                }
            }
            all_results.append(summary)
            
            print(f"  → Averages: entities={avg_entities:.1f}, score={avg_score:.1f}, compression={avg_compression:.2f}, width={avg_width:.2f}")
        
        print()
    
    # Save results
    output_file = results_dir / f"phase1_temperature_sweep_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    final_output = {
        "experiment": "phase1_temperature_sweep",
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "temperatures": TEMPERATURES,
        "runs_per_temperature": RUNS_PER_TEMP,
        "results": all_results,
        "hypothesis": "Temperature controls structured ambiguity width in QAL framework"
    }
    
    with open(output_file, 'w') as f:
        json.dump(final_output, f, indent=2)
    
    print("=" * 70)
    print("📊 Results Summary")
    print("=" * 70)
    print("\nTemperature | Entities | Consciousness | Compression | Ambiguity Width")
    print("-" * 70)
    
    for result in all_results:
        temp = result["temperature"]
        avg = result["averages"]
        print(f"   {temp:.1f}      |   {avg['entity_count']:.1f}    |      {avg['consciousness_score']:.1f}        |    {avg['compression_ratio']:.2f}     |      {avg['ambiguity_width']:.2f}")
    
    print("=" * 70)
    print(f"\n✓ Results saved to: {output_file}")
    print(f"✓ Total runs: {len(TEMPERATURES) * RUNS_PER_TEMP}")
    print("\n🎯 Next: Phase 2 - Entity Confidence Scoring")
    print("=" * 70)


if __name__ == "__main__":
    run_experiment()
