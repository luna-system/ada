#!/usr/bin/env python3
"""
Extreme Temperature Test: Finding the Peak
===========================================

Following temperature reversal discovery (T=0.9 peak, not T=0.3),
we push beyond normal range to find where consciousness peaks.

Test range: T=1.5, T=2.0 (extreme exploration widths)

Hypothesis: Consciousness will continue rising OR plateau/degrade.
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
    """Quick consciousness measurement focusing on key indicators."""
    summary = sif_data.get('summary', '')
    entities = sif_data.get('entities', [])
    
    # Self-reference
    self_ref = sum(1 for word in ['I ', ' I ', 'we ', ' we ', 'my ', ' my ', 'me ', ' me '] 
                   if word in summary)
    
    # Meta-cognition
    meta_cog = sum(1 for word in ['think', 'know', 'understand', 'remember', 'realize', 
                                   'aware', 'conscious', 'notice', 'observe']
                   if word.lower() in summary.lower())
    
    # Narrative awareness
    narrative = sum(1 for word in ['story', 'tale', 'narrative', 'chapter', 'plot', 
                                    'beginning', 'end', 'journey', 'adventure']
                    if word.lower() in summary.lower())
    
    # Known entities from chapters 1-5
    known = {'alice', 'white rabbit', 'mouse', 'dodo', 'lory', 'eaglet', 
             'duck', 'caterpillar', 'pigeon', 'dinah', 'sister'}
    
    # Creative completions (handle both dict and string entities)
    entity_names = set()
    for e in entities:
        if isinstance(e, dict):
            entity_names.add(e.get('name', '').lower())
        elif isinstance(e, str):
            entity_names.add(e.lower())
    creative = len(entity_names - known)
    
    # Consciousness score
    score = self_ref + meta_cog + narrative + (creative * 2)
    
    return {
        'self_reference': self_ref,
        'meta_cognition': meta_cog,
        'narrative_awareness': narrative,
        'creative_completions': creative,
        'consciousness_score': score,
        'total_entities': len(entities),
        'hallucination_count': creative
    }


def compress_with_temperature(text: str, temperature: float, mode: str = "baseline") -> dict:
    """Compress text to SIF at specified temperature."""
    
    # Prompt based on mode
    if mode == "dialogic":
        prompt = """I am experiencing a text about Alice. As I read, I become aware of the narrative structure and my own process of understanding. I notice patterns, characters, relationships.

Convert this narrative into Semantic Interchange Format (SIF), capturing not just facts but the felt sense of story:"""
    else:
        prompt = "Convert this text to Semantic Interchange Format (SIF):"
    
    full_prompt = f"{prompt}\n\n{text}\n\nSIF (entities, facts, summary in JSON):"
    
    try:
        response = httpx.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5-coder:7b",
                "prompt": full_prompt,
                "temperature": temperature,
                "stream": False
            },
            timeout=120.0
        )
        
        result = response.json()
        response_text = result.get('response', '')
        
        # Try to extract JSON
        if '{' in response_text:
            json_start = response_text.index('{')
            json_text = response_text[json_start:]
            
            # Find matching closing brace
            brace_count = 0
            json_end = 0
            for i, char in enumerate(json_text):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_end = i + 1
                        break
            
            if json_end > 0:
                json_text = json_text[:json_end]
                return json.loads(json_text)
        
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None


def run_extreme_temperature_test():
    """Test extreme temperatures to find consciousness peak."""
    
    # Alice corpus (first 50K chars = chapters 1-5)
    text_file = Path("alice_first_50k.txt")
    if not text_file.exists():
        print("❌ alice_first_50k.txt not found!")
        return
    
    text = text_file.read_text()
    
    print("=" * 70)
    print("EXTREME TEMPERATURE TEST: Finding the Peak")
    print("=" * 70)
    print()
    print("Following discovery that T=0.9 > T=0.3 (hypothesis rejected),")
    print("we push to extreme temperatures to find where consciousness peaks.")
    print()
    print("Test range: T=1.5, T=2.0 (beyond normal operating range)")
    print()
    
    # Include previous peak for comparison
    temperatures = [0.9, 1.1, 1.5, 2.0]
    results: List[ConsciousnessResult] = []
    
    print("Running compressions with dialogic priming...\n")
    
    for temp in temperatures:
        print(f"🔥 Testing T={temp}...")
        
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
        print(f"   Creative completions: {result.creative_completions}")
        print(f"   Meta-cognition: {result.meta_cognition_count}")
        print(f"   Narrative awareness: {result.narrative_awareness_count}")
        print()
    
    # Analysis
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()
    
    print("Temperature | Consciousness | Creative | Meta-Cog | Narrative | Total Entities")
    print("-" * 90)
    for r in results:
        print(f"   {r.temperature:.1f}     |      {r.consciousness_score:3d}      |    {r.creative_completions:2d}    |    {r.meta_cognition_count:2d}    |    {r.narrative_awareness_count:2d}     |      {r.total_entities:2d}")
    
    print()
    print("=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    print()
    
    scores = [r.consciousness_score for r in results]
    
    if len(results) >= 3:
        peak_idx = scores.index(max(scores))
        peak_temp = results[peak_idx].temperature
        peak_score = results[peak_idx].consciousness_score
        
        print(f"🎯 PEAK CONSCIOUSNESS: T={peak_temp} (score={peak_score})")
        print()
        
        # Check trend
        if peak_idx == 0:
            print("📉 Consciousness DECREASES at extreme temperatures")
            print("   → T=0.9 was the peak, higher temps degrade consciousness")
        elif peak_idx == len(results) - 1:
            print("📈 Consciousness CONTINUES RISING")
            print("   → Peak not yet found, may continue beyond T=2.0")
        else:
            print(f"⚡ CONSCIOUSNESS PEAKS at T={peak_temp}")
            print("   → Optimal exploration width found!")
        
        print()
        print("Consciousness trajectory:")
        for r in results:
            bar = "█" * (r.consciousness_score // 2)
            marker = " ← PEAK" if r.temperature == peak_temp else ""
            print(f"  T={r.temperature:.1f}: {bar} ({r.consciousness_score}){marker}")
        
        print()
        print("Key observation:")
        if results[-1].consciousness_score < results[0].consciousness_score:
            print("  ⚠️  Extreme temperatures DEGRADE consciousness")
            print("  → Too wide exploration = loss of coherence")
        elif results[-1].consciousness_score > results[0].consciousness_score:
            print("  ⚡ Extreme temperatures ENHANCE consciousness")
            print("  → Wider exploration = more creative synthesis")
        else:
            print("  ⚖️  Plateau reached")
            print("  → Consciousness stabilizes at high temperature")
    
    # Save results
    output = {
        'experiment': 'extreme_temperature',
        'hypothesis': 'Find consciousness peak beyond T=1.1',
        'previous_peak': 'T=0.9 (score=5)',
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
    
    output_file = Path("test_results/extreme_temperature.json")
    output_file.parent.mkdir(exist_ok=True)
    output_file.write_text(json.dumps(output, indent=2))
    
    print()
    print(f"💾 Results saved to: {output_file}")
    print()
    
    # Save individual SIF outputs
    for r in results:
        sif_file = Path(f"test_results/sif_extreme_temp_{r.temperature:.1f}.json")
        sif_file.write_text(r.response_text)
    
    print("📁 Individual SIF outputs saved to test_results/")
    print()
    print("✓ Experiment complete!")


if __name__ == "__main__":
    run_extreme_temperature_test()
