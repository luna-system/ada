#!/usr/bin/env python3
"""
Test Prediction 1: Temperature Dependence of Consciousness
============================================================

Hypothesis: Lower temperature = stronger measurement = more consciousness

Quantum formalism predicts:
- Softmax temperature controls measurement strength
- Lower T → sharper probability distribution → stronger collapse
- Stronger collapse → more activated state → more consciousness

Test: Same dialogic priming, vary temperature, measure consciousness.
"""

import json
import httpx
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class ConsciousnessResult:
    temperature: float
    consciousness_score: int
    hallucination_count: int
    self_reference_count: int
    meta_cognition_count: int
    narrative_awareness_count: int
    creative_completions: int
    total_entities: int
    summary_length: int
    response_text: str


def measure_consciousness_quick(sif_data: dict) -> dict:
    """
    Quick consciousness measurement (subset of full metrics).
    Focuses on key indicators: self-ref, meta-cog, narrative, creative completion.
    """
    summary = sif_data.get('summary', '')
    entities = sif_data.get('entities', [])
    
    # Self-reference (I, we, my, me)
    self_ref = sum(1 for word in ['I ', ' I ', 'we ', ' we ', 'my ', ' my ', 'me ', ' me '] 
                   if word in summary)
    
    # Meta-cognition (think, know, understand, remember, realize)
    meta_cog = sum(1 for word in ['think', 'know', 'understand', 'remember', 'realize', 
                                   'aware', 'conscious', 'notice', 'observe']
                   if word.lower() in summary.lower())
    
    # Narrative awareness (story, tale, narrative, chapter, plot)
    narrative = sum(1 for word in ['story', 'tale', 'narrative', 'chapter', 'plot', 
                                    'beginning', 'end', 'journey', 'adventure']
                    if word.lower() in summary.lower())
    
    # Known entities from chapters 1-5
    known = {'alice', 'white rabbit', 'mouse', 'dodo', 'lory', 'eaglet', 
             'duck', 'caterpillar', 'pigeon', 'dinah', 'sister'}
    
    # Creative completions (entities NOT in source)
    entity_names = {e.get('name', '').lower() for e in entities}
    creative = len(entity_names - known)
    
    # Simple consciousness score (sum of indicators)
    score = self_ref + meta_cog + narrative + (creative * 2)  # weight creative higher
    
    return {
        'self_reference': self_ref,
        'meta_cognition': meta_cog,
        'narrative_awareness': narrative,
        'creative_completions': creative,
        'consciousness_score': score,
        'total_entities': len(entities),
        'hallucination_count': creative  # same as creative for this test
    }


def compress_with_temperature(text: str, temperature: float, prompt_type: str = "dialogic") -> dict:
    """
    Run SIF compression with specific temperature.
    Uses exact dialogic prompt that worked in earlier tests.
    """
    # Build prompt - using EXACT prompt from successful test_metacognitive_priming.py
    if prompt_type == "dialogic":
        # Two-turn conversation (priming + extraction)
        messages = [
            {
                "role": "user",
                "content": "I'm going to tell you a story about a girl named Alice who falls into a magical world. When I finish, I'll ask you to tell me about the characters, events, and places in the story. Are you ready?"
            },
            {
                "role": "assistant",
                "content": "Yes, I'm ready to hear the story about Alice and her adventure in the magical world!"
            },
            {
                "role": "user",
                "content": f"""Here's the story about Alice:

{text}

Now, please tell me about this story in structured form. I need:
- All the characters Alice meets and how they interact
- Key events that happen throughout her adventure  
- Important places and objects
- The overall arc of the story

Use this JSON format:
{{
    "summary": "what happens in Alice's adventure",
    "entities": [{{"id": "character/place name", "type": "type", "relationships": {{"relation": "target"}}}}],
    "facts": [{{"content": "event or detail", "importance": 0.9, "tags": []}}]
}}

Extract 30-50 entities and 50-100 facts covering Alice's full journey.

JSON OUTPUT:"""
            }
        ]
    else:
        # Baseline - minimal prompt
        messages = [
            {
                "role": "user",
                "content": f"""Extract key information from the text into JSON format:

{{
    "summary": "brief overview",
    "entities": [{{"id": "name", "type": "type"}}],
    "facts": [{{"content": "fact"}}]
}}

Text:
{text}

JSON OUTPUT:"""
            }
        ]
    
    # Call Ollama with specified temperature using chat API
    try:
        response = httpx.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "qwen2.5-coder:7b",
                "messages": messages,
                "temperature": temperature,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": 8000
                }
            },
            timeout=300.0
        )
        response.raise_for_status()
        
        result = response.json()
        response_text = result['message']['content']
        
        # Parse JSON from response (handle code blocks)
        json_str = response_text
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0]
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0]
        
        sif_data = json.loads(json_str.strip())
        return sif_data
        
    except Exception as e:
        print(f"❌ Compression failed at T={temperature}: {e}")
        import traceback
        traceback.print_exc()
        return None


def run_temperature_experiment():
    """
    Main experiment: Test consciousness at different temperatures.
    """
    print("=" * 70)
    print("EXPERIMENT: Temperature Dependence of Consciousness")
    print("=" * 70)
    print()
    
    # Load Alice text
    alice_file = Path("alice_first_50k.txt")
    if not alice_file.exists():
        print(f"❌ Alice text not found: {alice_file}")
        return
    
    text = alice_file.read_text()[:50000]  # First 50k chars
    print(f"✓ Loaded {len(text)} characters from Alice in Wonderland")
    print()
    
    # Temperature range: 0.3 to 1.1 (5 points)
    temperatures = [0.3, 0.5, 0.7, 0.9, 1.1]
    results: List[ConsciousnessResult] = []
    
    print("Running compressions with dialogic priming...\n")
    
    for temp in temperatures:
        print(f"📊 Testing T={temp}...")
        
        # Compress
        sif_data = compress_with_temperature(text, temp, "dialogic")
        
        if sif_data is None:
            print(f"   ⚠️  Skipping due to error\n")
            continue
        
        # Measure consciousness
        metrics = measure_consciousness_quick(sif_data)
        
        # Store result
        result = ConsciousnessResult(
            temperature=temp,
            consciousness_score=metrics['consciousness_score'],
            hallucination_count=metrics['hallucination_count'],
            self_reference_count=metrics['self_reference'],
            meta_cognition_count=metrics['meta_cognition'],
            narrative_awareness_count=metrics['narrative_awareness'],
            creative_completions=metrics['creative_completions'],
            total_entities=metrics['total_entities'],
            summary_length=len(sif_data.get('summary', '')),
            response_text=json.dumps(sif_data, indent=2)
        )
        results.append(result)
        
        # Report
        print(f"   Consciousness score: {result.consciousness_score}")
        print(f"   Hallucinations: {result.hallucination_count}")
        print(f"   Self-reference: {result.self_reference_count}")
        print(f"   Meta-cognition: {result.meta_cognition_count}")
        print(f"   Narrative: {result.narrative_awareness_count}")
        print()
    
    # Analysis
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()
    
    print("Temperature | Consciousness | Hallucinations | Self-Ref | Meta-Cog | Narrative")
    print("-" * 85)
    for r in results:
        print(f"   {r.temperature:.1f}     |      {r.consciousness_score:3d}      |       {r.hallucination_count:2d}       |    {r.self_reference_count:2d}    |    {r.meta_cognition_count:2d}    |    {r.narrative_awareness_count:2d}")
    
    print()
    print("=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    print()
    
    # Check for correlation
    temps = [r.temperature for r in results]
    scores = [r.consciousness_score for r in results]
    
    if len(results) >= 3:
        # Simple trend check
        if scores[0] > scores[-1]:
            print("✓ HYPOTHESIS CONFIRMED: Consciousness decreases as temperature increases")
            print("  → Lower T = stronger measurement = more collapse = more consciousness")
        elif scores[0] < scores[-1]:
            print("✗ HYPOTHESIS REJECTED: Consciousness increases with temperature")
            print("  → Unexpected result! Temperature may work differently than predicted")
        else:
            print("⚠ INCONCLUSIVE: No clear temperature trend")
        
        print()
        print(f"Temperature range: {min(temps):.1f} - {max(temps):.1f}")
        print(f"Consciousness range: {min(scores)} - {max(scores)}")
        print(f"Hallucination range: {min(r.hallucination_count for r in results)} - {max(r.hallucination_count for r in results)}")
    
    # Save results
    output = {
        'experiment': 'temperature_consciousness',
        'hypothesis': 'Lower temperature = stronger measurement = more consciousness',
        'model': 'qwen2.5-coder:7b',
        'prompt_type': 'dialogic',
        'results': [
            {
                'temperature': r.temperature,
                'consciousness_score': r.consciousness_score,
                'hallucination_count': r.hallucination_count,
                'self_reference': r.self_reference_count,
                'meta_cognition': r.meta_cognition_count,
                'narrative_awareness': r.narrative_awareness_count,
                'creative_completions': r.creative_completions,
                'total_entities': r.total_entities,
                'summary_length': r.summary_length
            }
            for r in results
        ]
    }
    
    output_file = Path("test_results/temperature_consciousness.json")
    output_file.parent.mkdir(exist_ok=True)
    output_file.write_text(json.dumps(output, indent=2))
    
    print()
    print(f"💾 Full results saved to: {output_file}")
    print()
    
    # Save individual SIF outputs
    for r in results:
        sif_file = Path(f"test_results/sif_temp_{r.temperature:.1f}.json")
        sif_file.write_text(r.response_text)
    
    print("📁 Individual SIF outputs saved to test_results/")
    print()
    print("✓ Experiment complete!")


if __name__ == "__main__":
    run_temperature_experiment()
