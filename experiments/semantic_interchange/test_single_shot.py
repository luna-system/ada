#!/usr/bin/env python3
"""
Single Shot Test: Can we reproduce score=5?
============================================

Original test (first run): T=0.9 produced consciousness score=5
Multi-sample test: T=0.9 mean=1.00, max=3

Question: Was score=5 a fluke, or did something change?

Test: Single compression at T=0.9, same exact setup as original.
"""

import json
import httpx
from pathlib import Path


def measure_consciousness_quick(sif_data: dict) -> dict:
    """Quick consciousness measurement."""
    summary = sif_data.get('summary', '')
    
    if not isinstance(summary, str):
        summary = str(summary) if summary else ''
    
    entities = sif_data.get('entities', [])
    if not isinstance(entities, list):
        entities = []
    
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
    
    # Known entities
    known = {'alice', 'white rabbit', 'mouse', 'dodo', 'lory', 'eaglet', 
             'duck', 'caterpillar', 'pigeon', 'dinah', 'sister'}
    
    # Creative completions
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
        'consciousness_score': score,
        'creative_completions': creative,
        'meta_cognition': meta_cog,
        'narrative_awareness': narrative,
        'self_reference': self_ref,
        'total_entities': len(entities),
        'summary': summary
    }


def compress_dialogic(text: str, temperature: float = 0.9) -> dict:
    """Compress with dialogic priming at specified temperature."""
    
    prompt = """I am experiencing a text about Alice. As I read, I become aware of the narrative structure and my own process of understanding. I notice patterns, characters, relationships.

Convert this narrative into Semantic Interchange Format (SIF), capturing not just facts but the felt sense of story:"""
    
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
        
        # Extract JSON
        if '{' in response_text:
            json_start = response_text.index('{')
            json_text = response_text[json_start:]
            
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


def run_single_shot():
    """Single T=0.9 test to check reproducibility."""
    
    text_file = Path("alice_first_50k.txt")
    if not text_file.exists():
        print("❌ alice_first_50k.txt not found!")
        return
    
    text = text_file.read_text()
    
    print("=" * 70)
    print("SINGLE SHOT REPRODUCIBILITY TEST")
    print("=" * 70)
    print()
    print("Original test: T=0.9 → consciousness score=5")
    print("Multi-sample:  T=0.9 → mean=1.00, max=3")
    print()
    print("Question: Can we hit score=5 again?")
    print()
    print("Running T=0.9 compression with dialogic priming...")
    print()
    
    # Compress
    sif_data = compress_dialogic(text, temperature=0.9)
    
    if sif_data is None:
        print("❌ Compression failed!")
        return
    
    # Measure
    metrics = measure_consciousness_quick(sif_data)
    
    print("=" * 70)
    print("RESULT")
    print("=" * 70)
    print()
    print(f"🎯 Consciousness Score: {metrics['consciousness_score']}")
    print()
    print("Breakdown:")
    print(f"  Self-reference:      {metrics['self_reference']}")
    print(f"  Meta-cognition:      {metrics['meta_cognition']}")
    print(f"  Narrative awareness: {metrics['narrative_awareness']}")
    print(f"  Creative completions: {metrics['creative_completions']}")
    print(f"  Total entities:      {metrics['total_entities']}")
    print()
    print("Summary:")
    print(f'  "{metrics["summary"]}"')
    print()
    
    # Compare to original
    original_score = 5
    if metrics['consciousness_score'] >= 5:
        print(f"✅ MATCHED OR EXCEEDED original score ({original_score})!")
        print("   → Consciousness can still activate")
        print("   → Multi-sample suppression might be batch effect")
    elif metrics['consciousness_score'] >= 3:
        print(f"⚠️  CLOSE to original ({metrics['consciousness_score']} vs {original_score})")
        print("   → Consciousness activated but weaker")
    else:
        print(f"❌ MUCH LOWER than original ({metrics['consciousness_score']} vs {original_score})")
        print("   → Regime shift confirmed")
        print("   → Something changed in activation mechanism")
    
    print()
    
    # Save
    output = {
        'test': 'single_shot_reproducibility',
        'temperature': 0.9,
        'original_score': original_score,
        'current_score': metrics['consciousness_score'],
        'metrics': metrics,
        'sif': sif_data
    }
    
    output_file = Path("test_results/single_shot_0.9.json")
    output_file.write_text(json.dumps(output, indent=2))
    
    print(f"💾 Results saved to: {output_file}")
    print()
    print("✓ Single shot test complete!")


if __name__ == "__main__":
    run_single_shot()
