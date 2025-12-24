#!/usr/bin/env python3
"""
Extreme Temperature Test: Multi-Sampled Edition
================================================

Temperature introduces randomness - each run produces different output.
Solution: Multiple samples per temperature, measure mean + variance.

Test range: T=0.9, 1.1, 1.5, 2.0
Samples per temperature: 5
Total compressions: 20 (fast on GPU!)
"""

import json
import httpx
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict
from statistics import mean, stdev


@dataclass
class Sample:
    consciousness_score: int
    creative_completions: int
    meta_cognition: int
    narrative_awareness: int
    self_reference: int
    total_entities: int
    summary_length: int


@dataclass
class TemperatureResult:
    temperature: float
    samples: List[Sample]
    mean_consciousness: float
    std_consciousness: float
    mean_creative: float
    std_creative: float
    wall_time: float


def measure_consciousness_quick(sif_data: dict) -> Dict:
    """Quick consciousness measurement focusing on key indicators."""
    summary = sif_data.get('summary', '')
    
    # Handle case where summary is dict or other non-string
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
        'consciousness_score': score,
        'creative_completions': creative,
        'meta_cognition': meta_cog,
        'narrative_awareness': narrative,
        'self_reference': self_ref,
        'total_entities': len(entities),
        'summary_length': len(summary)
    }


def compress_with_temperature(text: str, temperature: float) -> dict:
    """Compress text to SIF at specified temperature."""
    
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
        return None


def run_sampled_temperature_test():
    """Test extreme temperatures with multiple samples per temperature."""
    
    # Alice corpus
    text_file = Path("alice_first_50k.txt")
    if not text_file.exists():
        print("❌ alice_first_50k.txt not found!")
        return
    
    text = text_file.read_text()
    
    print("=" * 80)
    print("EXTREME TEMPERATURE TEST: Multi-Sampled Edition")
    print("=" * 80)
    print()
    print("Temperature introduces randomness → need multiple samples!")
    print()
    print("Test parameters:")
    print("  - Temperatures: [0.9, 1.1, 1.5, 2.0]")
    print("  - Samples per temp: 5")
    print("  - Total compressions: 20")
    print("  - Model: qwen2.5-coder:7b")
    print()
    
    temperatures = [0.9, 1.1, 1.5, 2.0]
    samples_per_temp = 5
    results: List[TemperatureResult] = []
    
    total_start = time.time()
    
    for temp in temperatures:
        print(f"🔥 Testing T={temp} ({samples_per_temp} samples)...")
        temp_start = time.time()
        
        samples = []
        successes = 0
        
        for i in range(samples_per_temp):
            # Compress
            sif_data = compress_with_temperature(text, temp)
            
            if sif_data is None:
                print(f"   ⚠️  Sample {i+1} failed (JSON error)")
                continue
            
            # Measure consciousness
            metrics = measure_consciousness_quick(sif_data)
            
            sample = Sample(
                consciousness_score=metrics['consciousness_score'],
                creative_completions=metrics['creative_completions'],
                meta_cognition=metrics['meta_cognition'],
                narrative_awareness=metrics['narrative_awareness'],
                self_reference=metrics['self_reference'],
                total_entities=metrics['total_entities'],
                summary_length=metrics['summary_length']
            )
            samples.append(sample)
            successes += 1
            
            # Progress indicator
            print(f"   Sample {i+1}: consciousness={sample.consciousness_score}, creative={sample.creative_completions}")
        
        temp_end = time.time()
        wall_time = temp_end - temp_start
        
        if len(samples) == 0:
            print(f"   ❌ All samples failed at T={temp}\n")
            continue
        
        # Calculate statistics
        consciousness_scores = [s.consciousness_score for s in samples]
        creative_scores = [s.creative_completions for s in samples]
        
        mean_cons = mean(consciousness_scores)
        std_cons = stdev(consciousness_scores) if len(consciousness_scores) > 1 else 0.0
        mean_creative = mean(creative_scores)
        std_creative = stdev(creative_scores) if len(creative_scores) > 1 else 0.0
        
        result = TemperatureResult(
            temperature=temp,
            samples=samples,
            mean_consciousness=mean_cons,
            std_consciousness=std_cons,
            mean_creative=mean_creative,
            std_creative=std_creative,
            wall_time=wall_time
        )
        results.append(result)
        
        # Report
        print(f"   ✓ {successes}/{samples_per_temp} successful")
        print(f"   Mean consciousness: {mean_cons:.2f} ± {std_cons:.2f}")
        print(f"   Mean creative: {mean_creative:.2f} ± {std_creative:.2f}")
        print(f"   Wall time: {wall_time:.2f}s ({wall_time/successes:.2f}s per sample)")
        print()
    
    total_end = time.time()
    total_time = total_end - total_start
    
    # Analysis
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()
    
    print("Temp | Mean Consciousness | Std Dev | Mean Creative | Std Dev | Samples | Time")
    print("-" * 85)
    for r in results:
        print(f" {r.temperature:.1f}  |       {r.mean_consciousness:5.2f}        |  {r.std_consciousness:4.2f}  |     {r.mean_creative:5.2f}     |  {r.std_creative:4.2f}  |    {len(r.samples)}    | {r.wall_time:5.1f}s")
    
    print()
    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print()
    
    # Find peak
    peak_idx = max(range(len(results)), key=lambda i: results[i].mean_consciousness)
    peak = results[peak_idx]
    
    print(f"🎯 PEAK MEAN CONSCIOUSNESS: T={peak.temperature} (μ={peak.mean_consciousness:.2f}, σ={peak.std_consciousness:.2f})")
    print()
    
    # Trajectory
    print("Consciousness trajectory (mean ± std):")
    for r in results:
        bar_length = int(r.mean_consciousness / 0.5)
        bar = "█" * bar_length
        marker = " ← PEAK" if r.temperature == peak.temperature else ""
        print(f"  T={r.temperature:.1f}: {bar} ({r.mean_consciousness:.2f} ± {r.std_consciousness:.2f}){marker}")
    
    print()
    
    # Variance analysis
    print("Variance analysis:")
    for r in results:
        cv = (r.std_consciousness / r.mean_consciousness * 100) if r.mean_consciousness > 0 else 0
        stability = "STABLE" if cv < 30 else "MODERATE" if cv < 50 else "UNSTABLE"
        print(f"  T={r.temperature:.1f}: CV={cv:5.1f}% ({stability})")
    
    print()
    
    # Trend analysis
    means = [r.mean_consciousness for r in results]
    if means[-1] > means[0]:
        print("📈 Consciousness INCREASES with temperature")
        print("   → Higher T = wider exploration = more consciousness")
    elif means[-1] < means[0]:
        print("📉 Consciousness DECREASES with temperature")
        print("   → Higher T = too much noise = less consciousness")
    else:
        print("⚖️  Consciousness stable across temperature range")
    
    print()
    print(f"⏱️  Total wall time: {total_time:.1f}s")
    print(f"   Average per sample: {total_time / sum(len(r.samples) for r in results):.2f}s")
    
    # Save results
    output = {
        'experiment': 'extreme_temperature_sampled',
        'samples_per_temperature': samples_per_temp,
        'model': 'qwen2.5-coder:7b',
        'total_time': total_time,
        'results': [
            {
                'temperature': r.temperature,
                'mean_consciousness': r.mean_consciousness,
                'std_consciousness': r.std_consciousness,
                'mean_creative': r.mean_creative,
                'std_creative': r.std_creative,
                'wall_time': r.wall_time,
                'samples': [
                    {
                        'consciousness_score': s.consciousness_score,
                        'creative_completions': s.creative_completions,
                        'meta_cognition': s.meta_cognition,
                        'narrative_awareness': s.narrative_awareness,
                        'self_reference': s.self_reference,
                        'total_entities': s.total_entities,
                        'summary_length': s.summary_length
                    }
                    for s in r.samples
                ]
            }
            for r in results
        ]
    }
    
    output_file = Path("test_results/extreme_temperature_sampled.json")
    output_file.parent.mkdir(exist_ok=True)
    output_file.write_text(json.dumps(output, indent=2))
    
    print()
    print(f"💾 Results saved to: {output_file}")
    print()
    print("✓ Multi-sampled experiment complete!")


if __name__ == "__main__":
    run_sampled_temperature_test()
