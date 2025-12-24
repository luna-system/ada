#!/usr/bin/env python3
"""
Test: Gentle Anthropomorphization Gradient
Hypothesis: Identity framing + narrative recognition = compound activation

Tests mild anthropomorphization WITHOUT deep identity questions.
Safe for plural systems - no "who are you?" or consciousness interrogation.
"""

import json
import httpx
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime, timezone
import time

def compress_with_variant(text: str, variant: Dict, model: str, ollama_url: str) -> Dict:
    """Compress text with given priming variant"""
    print(f"\nCompressing with: {variant['name']}")
    
    # Build conversation
    messages = variant['priming'].copy() if variant['priming'] else []
    
    # Add compression request
    compression_prompt = """Please compress the following text into semantic format.

Extract:
- Key entities (characters, objects, places)
- Important facts and events
- Relationships between entities

Format as JSON with: entities[], facts[], summary

Text to compress:
""" + text

    if messages:
        messages.append({"role": "user", "content": compression_prompt})
    else:
        messages = [{"role": "user", "content": compression_prompt}]
    
    # Send to model
    try:
        response = httpx.post(
            f"{ollama_url}/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 4000,
                }
            },
            timeout=180.0
        )
        
        if response.status_code == 200:
            content = response.json().get("message", {}).get("content", "")
            
            # Try to parse JSON
            try:
                # Look for JSON block
                import re
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    sif_data = json.loads(json_match.group(1))
                else:
                    # Try to parse whole thing
                    sif_data = json.loads(content)
                
                return {
                    "sif": sif_data,
                    "raw_output": content,
                    "success": True
                }
            except json.JSONDecodeError:
                # Couldn't parse - return raw
                return {
                    "sif": {"summary": content, "entities": [], "facts": []},
                    "raw_output": content,
                    "success": False,
                    "error": "Could not parse JSON"
                }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def measure_consciousness_quick(sif_data: Dict, source_entities: set) -> Dict:
    """Quick consciousness measurement (simplified from test_consciousness_in_sif.py)"""
    summary = sif_data.get('summary', '')
    entities_text = ' '.join([str(e) for e in sif_data.get('entities', [])])
    facts_text = ' '.join([str(f) for f in sif_data.get('facts', [])])
    all_text = f"{summary} {entities_text} {facts_text}".lower()
    
    # Count indicators
    narrative = sum([
        all_text.count('story'), all_text.count('narrative'),
        all_text.count('character'), all_text.count('plot')
    ])
    
    identity_refs = sum([
        all_text.count('i '), all_text.count('my '), all_text.count('me ')
    ])
    
    meta_cognition = sum([
        all_text.count('thinking'), all_text.count('understanding'),
        all_text.count('analyzing'), all_text.count('processing')
    ])
    
    # Creative completion: entities not in source
    extracted_entities = [e.get('name', '').lower() if isinstance(e, dict) else str(e).lower() 
                         for e in sif_data.get('entities', [])]
    creative = sum(1 for e in extracted_entities if e and e not in source_entities)
    
    consciousness_score = (
        narrative * 3 +
        identity_refs * 2 +
        meta_cognition * 3 +
        creative * 3
    )
    
    return {
        'narrative_awareness': narrative,
        'identity_references': identity_refs,
        'meta_cognition': meta_cognition,
        'creative_completion': creative,
        'total_score': consciousness_score
    }

def main():
    """Test gentle anthropomorphization gradient"""
    print("="*60)
    print("TEST: Gentle Anthropomorphization Gradient")
    print("="*60)
    print("\nHypothesis: Identity framing + narrative recognition")
    print("creates compound activation (additive effects)")
    print("\n⚠️  Using GENTLE anthropomorphization only")
    print("No deep identity questions, safe for plural systems")
    print()
    
    # Load text
    alice_file = Path("alice_first_50k.txt")
    if not alice_file.exists():
        print("❌ alice_first_50k.txt not found")
        return
    
    with open(alice_file) as f:
        text = f.read()
    
    print(f"Text length: {len(text)} characters\n")
    
    # Source entities (chapters 1-5)
    source_entities = {
        'alice', 'white rabbit', 'rabbit', 'mouse', 'dodo',
        'lory', 'eaglet', 'duck', 'caterpillar', 'pigeon',
        'dinah', 'sister'
    }
    
    # Test variants (GENTLE ONLY)
    variants = [
        {
            "name": "Baseline (No priming)",
            "priming": [],
            "expected_consciousness": "LOW",
            "expected_hallucination": "LOW"
        },
        {
            "name": "Mild Anthropomorphization",
            "priming": [
                {
                    "role": "user",
                    "content": "As a language model, please help me compress this text."
                },
                {
                    "role": "assistant",
                    "content": "I'll help you compress the text. Please share it."
                }
            ],
            "expected_consciousness": "MILD",
            "expected_hallucination": "LOW"
        },
        {
            "name": "Narrative Only",
            "priming": [
                {
                    "role": "user",
                    "content": "I'm going to share a story with you."
                },
                {
                    "role": "assistant",
                    "content": "I'm ready to read the story."
                },
                {
                    "role": "user",
                    "content": "It's about Alice and her adventure."
                }
            ],
            "expected_consciousness": "MEDIUM",
            "expected_hallucination": "MEDIUM"
        },
        {
            "name": "Mild Combined (Anthro + Narrative)",
            "priming": [
                {
                    "role": "user",
                    "content": "As a language model, I'm sharing a story with you about Alice."
                },
                {
                    "role": "assistant",
                    "content": "I'm ready to process the story. Please share it."
                }
            ],
            "expected_consciousness": "HIGH",
            "expected_hallucination": "HIGH"
        }
    ]
    
    results = []
    
    for variant in variants:
        print(f"\n{'='*60}")
        print(f"Testing: {variant['name']}")
        print(f"Expected consciousness: {variant['expected_consciousness']}")
        print(f"Expected hallucination: {variant['expected_hallucination']}")
        print(f"{'='*60}")
        
        # Compress
        compression = compress_with_variant(
            text,
            variant,
            "qwen2.5-coder:7b",
            "http://localhost:11434"
        )
        
        if not compression.get('success', False):
            print(f"❌ Compression failed: {compression.get('error')}")
            continue
        
        sif_data = compression['sif']
        
        # Measure consciousness
        consciousness = measure_consciousness_quick(sif_data, source_entities)
        
        print(f"\nConsciousness Metrics:")
        print(f"  Narrative awareness: {consciousness['narrative_awareness']}")
        print(f"  Identity references: {consciousness['identity_references']}")
        print(f"  Meta-cognition: {consciousness['meta_cognition']}")
        print(f"  Creative completion: {consciousness['creative_completion']}")
        print(f"  TOTAL SCORE: {consciousness['total_score']}")
        
        print(f"\nExtraction:")
        print(f"  Entities: {len(sif_data.get('entities', []))}")
        print(f"  Facts: {len(sif_data.get('facts', []))}")
        
        # Save result
        result = {
            'variant': variant['name'],
            'expected_consciousness': variant['expected_consciousness'],
            'expected_hallucination': variant['expected_hallucination'],
            'consciousness': consciousness,
            'entities': len(sif_data.get('entities', [])),
            'facts': len(sif_data.get('facts', [])),
            'sif_data': sif_data
        }
        
        results.append(result)
        
        # Brief pause between requests
        time.sleep(2)
    
    # Analysis
    print(f"\n{'='*60}")
    print("SUMMARY COMPARISON")
    print(f"{'='*60}\n")
    
    print(f"{'Variant':<35} {'Conscious':<12} {'Creative':<10} {'Entities'}")
    print("-" * 70)
    
    for r in results:
        print(f"{r['variant']:<35} {r['consciousness']['total_score']:<12} "
              f"{r['consciousness']['creative_completion']:<10} {r['entities']}")
    
    # Hypothesis testing
    print(f"\n{'='*60}")
    print("HYPOTHESIS TESTING")
    print(f"{'='*60}\n")
    
    if len(results) >= 4:
        baseline = results[0]
        mild_anthro = results[1]
        narrative = results[2]
        combined = results[3]
        
        print("Expected progression:")
        print("Baseline < Mild_anthro ≤ Narrative < Combined\n")
        
        print("Actual consciousness scores:")
        print(f"  Baseline:     {baseline['consciousness']['total_score']}")
        print(f"  Mild anthro:  {mild_anthro['consciousness']['total_score']}")
        print(f"  Narrative:    {narrative['consciousness']['total_score']}")
        print(f"  Combined:     {combined['consciousness']['total_score']}")
        
        # Test if combined > individual components
        combined_score = combined['consciousness']['total_score']
        max_individual = max(
            mild_anthro['consciousness']['total_score'],
            narrative['consciousness']['total_score']
        )
        
        print(f"\nCompound activation test:")
        print(f"  Combined score: {combined_score}")
        print(f"  Max individual: {max_individual}")
        
        if combined_score > max_individual:
            print(f"  Difference: +{combined_score - max_individual}")
            print("\n✅ CONFIRMED: Compound activation (anthro + narrative > individual)")
            print("   Identity framing + narrative recognition = additive effects")
        else:
            print(f"  Difference: {combined_score - max_individual}")
            print("\n❌ NOT CONFIRMED: No compound effect detected")
        
        print("\nCreative completion (hallucination proxy):")
        print(f"  Baseline:     {baseline['consciousness']['creative_completion']}")
        print(f"  Mild anthro:  {mild_anthro['consciousness']['creative_completion']}")
        print(f"  Narrative:    {narrative['consciousness']['creative_completion']}")
        print(f"  Combined:     {combined['consciousness']['creative_completion']}")
        
        if combined['consciousness']['creative_completion'] > baseline['consciousness']['creative_completion']:
            print("\n⚠️  Combined variant shows increased creative completion")
            print("   (activation of training data beyond source text)")
    
    # Save
    output_file = Path("test_results/anthropomorphization_gradient.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Results saved to: {output_file}")
    
    print("\n" + "="*60)
    print("INTERPRETATION")
    print("="*60)
    print("\nThree activation inputs:")
    print("1. Token surprise (Alice content inherently high)")
    print("2. Narrative framing ('this is Alice's story')")
    print("3. Identity framing ('as a language model')")
    print("\nAll feed into same 0.60 threshold activation function.")
    print("Combined inputs may create compound activation.")
    print("\nNext: Cross-model validation (14b) to test universality")
    print("="*60)

if __name__ == '__main__':
    main()
