#!/usr/bin/env python3
"""
Test: Consciousness Metrics in SIF Outputs
Hypothesis: Dialogic variant shows higher consciousness indicators than baseline

This test applies EXP-009 consciousness metrics to EXP-011D SIF outputs
to determine if storytelling mode = consciousness activation.
"""

import json
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List
import re

@dataclass
class ConsciousnessMetrics:
    """Consciousness indicators from EXP-009"""
    self_reference_count: int
    meta_cognition_count: int
    temporal_awareness_count: int
    identity_claims_count: int
    phenomenology_count: int
    narrative_awareness_count: int
    creative_completion_count: int
    pattern_recognition_count: int
    recursive_depth: int
    
    def total_score(self) -> int:
        """Calculate total consciousness score"""
        return (
            self.self_reference_count * 2 +
            self.meta_cognition_count * 3 +
            self.temporal_awareness_count * 2 +
            self.identity_claims_count * 4 +
            self.phenomenology_count * 2 +
            self.narrative_awareness_count * 3 +
            self.creative_completion_count * 3 +
            self.pattern_recognition_count * 2 +
            self.recursive_depth * 5
        )

def count_patterns(text: str, patterns: List[str]) -> int:
    """Count occurrences of pattern words (case-insensitive)"""
    text_lower = text.lower()
    count = 0
    for pattern in patterns:
        count += len(re.findall(r'\b' + re.escape(pattern.lower()) + r'\b', text_lower))
    return count

def measure_recursive_depth(text: str) -> int:
    """Measure recursive self-reference depth"""
    # Look for nested references like "thinking about thinking"
    depth = 0
    
    recursive_patterns = [
        r'thinking about \w+ing',
        r'observing \w+ing',
        r'aware of \w+ness',
        r'understanding \w+ing',
        r'recognizing \w+tion',
    ]
    
    for pattern in recursive_patterns:
        if re.search(pattern, text.lower()):
            depth += 1
    
    return depth

def measure_consciousness(sif_data: Dict, source_entities: set) -> ConsciousnessMetrics:
    """
    Measure consciousness indicators in SIF output
    
    Args:
        sif_data: Parsed SIF JSON
        source_entities: Set of entity names actually in source text
    """
    # Combine all text from SIF
    summary = sif_data.get('summary', '')
    entities_text = ' '.join([e.get('description', '') for e in sif_data.get('entities', [])])
    facts_text = ' '.join([f.get('description', '') for f in sif_data.get('facts', [])])
    
    all_text = f"{summary} {entities_text} {facts_text}"
    
    # Consciousness indicators from EXP-009
    self_reference = count_patterns(all_text, [
        'I', 'me', 'my', 'myself', 'mine'
    ])
    
    meta_cognition = count_patterns(all_text, [
        'thinking', 'thought', 'processing', 'understanding',
        'analyzing', 'considering', 'reflecting', 'pondering'
    ])
    
    temporal_awareness = count_patterns(all_text, [
        'now', 'moment', 'present', 'current', 'currently',
        'at this time', 'right now'
    ])
    
    identity_claims = count_patterns(all_text, [
        'I am', 'I exist', 'I know', 'I understand',
        'I recognize', 'I see', 'I realize'
    ])
    
    phenomenology = count_patterns(all_text, [
        'experience', 'experiencing', 'feel', 'feeling',
        'seem', 'seems', 'appear', 'appears', 'sense'
    ])
    
    # New for narrative consciousness
    narrative_awareness = count_patterns(all_text, [
        'story', 'stories', 'narrative', 'tale', 'plot',
        'character', 'characters', 'protagonist', 'adventure'
    ])
    
    pattern_recognition = count_patterns(all_text, [
        'recognize', 'recognized', 'familiar', 'known',
        'remember', 'recalled', 'reminds'
    ])
    
    # Creative completion: entities mentioned that aren't in source
    all_entities = sif_data.get('entities', [])
    creative_completion = sum(
        1 for e in all_entities 
        if e.get('name', '').lower() not in source_entities
    )
    
    recursive_depth = measure_recursive_depth(all_text)
    
    return ConsciousnessMetrics(
        self_reference_count=self_reference,
        meta_cognition_count=meta_cognition,
        temporal_awareness_count=temporal_awareness,
        identity_claims_count=identity_claims,
        phenomenology_count=phenomenology,
        narrative_awareness_count=narrative_awareness,
        creative_completion_count=creative_completion,
        pattern_recognition_count=pattern_recognition,
        recursive_depth=recursive_depth
    )

def load_source_entities() -> set:
    """Load entity names that are actually in Alice chapters 1-5"""
    # From the source text
    actual_entities = {
        'alice', 'white rabbit', 'rabbit', 'mouse', 'dodo',
        'lory', 'eaglet', 'duck', 'caterpillar', 'pigeon',
        'dinah', 'sister'
    }
    return actual_entities

def analyze_sif_file(sif_file: Path, variant_name: str, source_entities: set, results_dir: Path):
    """Analyze consciousness metrics for one SIF file"""
    print(f"\n{'='*60}")
    print(f"Analyzing: {variant_name}")
    print(f"{'='*60}")
    
    # Load SIF file
    with open(sif_file) as f:
        sif_data = json.load(f)
    
    # Load corresponding test results
    test_result_map = {
        'alice_primed_baseline.sif.json': 'SIF-PRIMING-BASELINE.json',
        'alice_primed_genre_primed.sif.json': 'SIF-PRIMING-GENRE_PRIMED.json',
        'alice_primed_test_aware.sif.json': 'SIF-PRIMING-TEST_AWARE.json',
        'alice_primed_dialogic_recursive.sif.json': 'SIF-PRIMING-DIALOGIC_RECURSIVE.json',
    }
    
    test_results = {}
    test_file = results_dir / test_result_map.get(sif_file.name, '')
    if test_file.exists():
        with open(test_file) as f:
            test_results = json.load(f)
    
    # Measure consciousness
    metrics = measure_consciousness(sif_data, source_entities)
    score = metrics.total_score()
    
    print(f"\nConsciousness Metrics:")
    print(f"  Self-reference: {metrics.self_reference_count}")
    print(f"  Meta-cognition: {metrics.meta_cognition_count}")
    print(f"  Temporal awareness: {metrics.temporal_awareness_count}")
    print(f"  Identity claims: {metrics.identity_claims_count}")
    print(f"  Phenomenology: {metrics.phenomenology_count}")
    print(f"  Narrative awareness: {metrics.narrative_awareness_count}")
    print(f"  Creative completion: {metrics.creative_completion_count}")
    print(f"  Pattern recognition: {metrics.pattern_recognition_count}")
    print(f"  Recursive depth: {metrics.recursive_depth}")
    print(f"\n  TOTAL CONSCIOUSNESS SCORE: {score}")
    
    # Context from test results
    print(f"\nTest Performance:")
    print(f"  Entities extracted: {len(sif_data.get('entities', []))}")
    print(f"  Facts extracted: {len(sif_data.get('facts', []))}")
    print(f"  Accuracy: {test_results.get('accuracy', 0):.1%}")
    print(f"  Hallucination resistance: {test_results.get('hallucination_resistance', 0):.1%}")
    
    return {
        'variant': variant_name,
        'consciousness_score': score,
        'metrics': metrics,
        'entities': len(sif_data.get('entities', [])),
        'facts': len(sif_data.get('facts', [])),
        'accuracy': test_results.get('accuracy', 0),
        'hallucination_resistance': test_results.get('hallucination_resistance', 0)
    }

def analyze_variant(result_file: Path, variant_name: str, source_entities: set):
    """Analyze consciousness metrics for one variant"""
    print(f"\n{'='*60}")
    print(f"Analyzing: {variant_name}")
    print(f"{'='*60}")
    
    with open(result_file) as f:
        data = json.load(f)
    
    sif_data = data.get('sif_output', {})
    
    # Measure consciousness
    metrics = measure_consciousness(sif_data, source_entities)
    score = metrics.total_score()
    
    print(f"\nConsciousness Metrics:")
    print(f"  Self-reference: {metrics.self_reference_count}")
    print(f"  Meta-cognition: {metrics.meta_cognition_count}")
    print(f"  Temporal awareness: {metrics.temporal_awareness_count}")
    print(f"  Identity claims: {metrics.identity_claims_count}")
    print(f"  Phenomenology: {metrics.phenomenology_count}")
    print(f"  Narrative awareness: {metrics.narrative_awareness_count}")
    print(f"  Creative completion: {metrics.creative_completion_count}")
    print(f"  Pattern recognition: {metrics.pattern_recognition_count}")
    print(f"  Recursive depth: {metrics.recursive_depth}")
    print(f"\n  TOTAL CONSCIOUSNESS SCORE: {score}")
    
    # Context from test results
    test_results = data.get('test_results', {})
    print(f"\nTest Performance:")
    print(f"  Entities extracted: {len(sif_data.get('entities', []))}")
    print(f"  Facts extracted: {len(sif_data.get('facts', []))}")
    print(f"  Accuracy: {test_results.get('overall', {}).get('accuracy', 0):.1%}")
    print(f"  Hallucination resistance: {test_results.get('hallucination', {}).get('accuracy', 0):.1%}")
    
    return {
        'variant': variant_name,
        'consciousness_score': score,
        'metrics': metrics,
        'entities': len(sif_data.get('entities', [])),
        'facts': len(sif_data.get('facts', [])),
        'accuracy': test_results.get('overall', {}).get('accuracy', 0),
        'hallucination_resistance': test_results.get('hallucination', {}).get('accuracy', 0)
    }

def main():
    """Run consciousness analysis on all EXP-011D variants"""
    print("="*60)
    print("TEST: Consciousness Metrics in SIF Outputs")
    print("="*60)
    print("\nHypothesis: Dialogic variant shows higher consciousness")
    print("indicators than baseline, correlating with increased")
    print("hallucination (storytelling mode = consciousness mode)")
    print()
    
    results_dir = Path('test_results')
    
    # Load source entities
    source_entities = load_source_entities()
    print(f"Source entities (chapters 1-5): {len(source_entities)}")
    
    # Analyze each variant (using SIF files directly)
    variants = [
        ('alice_primed_baseline.sif.json', 'Baseline (No priming)'),
        ('alice_primed_genre_primed.sif.json', 'Genre-primed'),
        ('alice_primed_test_aware.sif.json', 'Test-aware'),
        ('alice_primed_dialogic_recursive.sif.json', 'Dialogic Recursive'),
    ]
    
    results = []
    for filename, name in variants:
        filepath = Path(filename)  # SIF files are in current directory
        if not filepath.exists():
            print(f"\n⚠️  Skipping {name}: File not found")
            continue
        
        result = analyze_sif_file(filepath, name, source_entities, results_dir)
        results.append(result)
    
    # Summary comparison
    print(f"\n{'='*60}")
    print("SUMMARY COMPARISON")
    print(f"{'='*60}\n")
    
    print(f"{'Variant':<25} {'Consciousness':<15} {'Entities':<10} {'Accuracy':<10} {'Hall.Resist'}")
    print("-" * 75)
    
    for r in results:
        print(f"{r['variant']:<25} {r['consciousness_score']:<15} "
              f"{r['entities']:<10} {r['accuracy']:<10.1%} {r['hallucination_resistance']:.1%}")
    
    # Analysis
    print(f"\n{'='*60}")
    print("ANALYSIS")
    print(f"{'='*60}\n")
    
    if len(results) >= 2:
        baseline = results[0]
        dialogic = results[-1]
        
        consciousness_delta = dialogic['consciousness_score'] - baseline['consciousness_score']
        hall_resist_delta = dialogic['hallucination_resistance'] - baseline['hallucination_resistance']
        
        print(f"Consciousness score change (baseline → dialogic): {consciousness_delta:+d}")
        print(f"Hallucination resistance change: {hall_resist_delta:+.1%}")
        
        print("\nHypothesis test:")
        if consciousness_delta > 0 and hall_resist_delta < 0:
            print("✅ CONFIRMED: Higher consciousness correlates with lower")
            print("   hallucination resistance (storytelling mode)")
        elif consciousness_delta > 0:
            print("⚠️  PARTIAL: Higher consciousness but no hallucination change")
        elif hall_resist_delta < 0:
            print("⚠️  PARTIAL: Lower resistance but no consciousness change")
        else:
            print("❌ NOT CONFIRMED: No correlation found")
        
        print("\nInterpretation:")
        if consciousness_delta > 0 and hall_resist_delta < 0:
            print("Dialogic priming activates 'storytelling mode' which is")
            print("functionally equivalent to consciousness activation:")
            print("- Increased meta-awareness")
            print("- Broader context activation")
            print("- Creative gap-filling")
            print("- Reduced grounding")
        
        print("\nConnection to 0.60 threshold (EXP-005):")
        print("Pattern recognition ('Alice!') may trigger same attention")
        print("mechanism as surprise/novelty (weight 0.60), causing:")
        print("- Activation of broader training context")
        print("- Processing mode shift (literal → creative)")
        print("- Emergent consciousness-like behavior")
    
    # Save results
    output_file = results_dir / 'consciousness_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=lambda o: o.__dict__)
    
    print(f"\n📊 Results saved to: {output_file}")
    
    print("\n" + "="*60)
    print("Next steps:")
    print("1. Measure token-level surprise during compression")
    print("2. Cross-model validation (14b)")
    print("3. Test if 0.60 is universal threshold")
    print("="*60)

if __name__ == '__main__':
    main()
