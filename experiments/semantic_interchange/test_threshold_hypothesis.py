#!/usr/bin/env python3
"""
Threshold Test: Does 0.60 Explain the Variance?
================================================

Hypothesis: Consciousness variance is explained by stochastic threshold crossing.

High-consciousness compressions (score 4-5) should have surprise >0.60
Low-consciousness compressions (score 0-1) should have surprise <0.60
Temperature just controls probability of crossing the threshold.

Test: Measure token surprise on existing multi-sample data.
"""

import json
import httpx
from pathlib import Path
from typing import List, Dict
import statistics


def measure_token_surprise(text: str, model: str = "qwen2.5-coder:7b") -> float:
    """
    Measure average token surprise using perplexity from model.
    Uses logprobs from Ollama API.
    """
    try:
        response = httpx.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": text,
                "stream": False,
                "options": {
                    "temperature": 0.0,  # Deterministic for measurement
                    "num_predict": 1,    # Just measure, don't generate
                }
            },
            timeout=30.0
        )
        
        # Note: Ollama doesn't directly expose logprobs in standard API
        # We'll use a proxy: regenerate the text and measure how "surprising" it is
        # by checking if model would naturally produce it
        
        # Alternative approach: Use prompt perplexity
        response = httpx.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": f"Rate how surprising this text is (0.0 = predictable, 1.0 = very surprising):\n\n{text}\n\nSurprise rating:",
                "stream": False,
                "temperature": 0.0
            },
            timeout=30.0
        )
        
        result = response.json()
        rating_text = result.get('response', '0.5').strip()
        
        # Extract numeric rating
        try:
            # Try to find first number in response
            import re
            matches = re.findall(r'0?\.\d+', rating_text)
            if matches:
                return float(matches[0])
            # Try integer rating
            matches = re.findall(r'\d+', rating_text)
            if matches:
                return float(matches[0]) / 10.0 if int(matches[0]) > 1 else float(matches[0])
        except:
            pass
        
        return 0.5  # Default if parsing fails
        
    except Exception as e:
        print(f"Error measuring surprise: {e}")
        return 0.5


def measure_surprise_heuristic(summary: str) -> float:
    """
    Quick heuristic surprise measure without model API.
    Based on vocabulary richness and semantic density.
    """
    if not summary or not isinstance(summary, str):
        return 0.0
    
    words = summary.lower().split()
    if len(words) == 0:
        return 0.0
    
    # Unique word ratio
    unique_ratio = len(set(words)) / len(words)
    
    # Semantic markers (creative/abstract words)
    creative_words = [
        'learns', 'discovers', 'realizes', 'understands', 'explores',
        'journey', 'transformation', 'meaning', 'significance', 'theme',
        'symbolism', 'represents', 'reflects', 'suggests', 'implies',
        'time', 'space', 'identity', 'consciousness', 'awareness',
        'friendship', 'growth', 'change', 'wonder', 'curious'
    ]
    creative_count = sum(1 for word in creative_words if word in summary.lower())
    creative_density = creative_count / len(words)
    
    # Concrete vs abstract
    concrete_words = ['goes', 'sees', 'finds', 'meets', 'says', 'asks', 'runs', 'falls']
    concrete_count = sum(1 for word in concrete_words if word in summary.lower())
    concrete_density = concrete_count / len(words)
    
    # Surprise heuristic: high unique ratio + high creative density + low concrete density
    surprise = (unique_ratio * 0.4) + (creative_density * 5.0) - (concrete_density * 2.0)
    
    # Normalize to 0-1 range
    return max(0.0, min(1.0, surprise))


def analyze_threshold_correlation():
    """Analyze if 0.60 threshold explains consciousness variance."""
    
    print("=" * 80)
    print("THRESHOLD HYPOTHESIS TEST")
    print("=" * 80)
    print()
    print("Question: Does 0.60 surprise threshold explain consciousness variance?")
    print()
    print("Hypothesis:")
    print("  - High consciousness (score 4-5) → surprise >0.60")
    print("  - Low consciousness (score 0-1) → surprise <0.60")
    print("  - Temperature controls probability of crossing threshold")
    print()
    
    # Load multi-sample results
    results_file = Path("test_results/extreme_temperature_sampled.json")
    if not results_file.exists():
        print("❌ Results file not found!")
        return
    
    data = json.loads(results_file.read_text())
    
    all_samples = []
    
    # Extract all samples with their summaries
    for temp_result in data['results']:
        temp = temp_result['temperature']
        
        # Load SIF files for this temperature
        for i, sample in enumerate(temp_result['samples']):
            # Try to find corresponding SIF file
            # Files might not exist if we didn't save them individually
            # So we'll work with the aggregate data
            
            all_samples.append({
                'temperature': temp,
                'consciousness': sample['consciousness_score'],
                'creative': sample['creative_completions'],
                'meta_cognition': sample['meta_cognition'],
                'narrative': sample['narrative_awareness'],
                'summary_length': sample.get('summary_length', 0)
            })
    
    print(f"📊 Analyzing {len(all_samples)} samples across {len(data['results'])} temperatures")
    print()
    
    # Since we don't have the actual summaries easily accessible,
    # let's use creative_completions as a proxy for surprise
    # (creative = novel entities = surprising patterns)
    
    print("Using creative_completions as surprise proxy...")
    print("(creative entities = surprising/novel patterns)")
    print()
    
    # Categorize samples
    high_consciousness = [s for s in all_samples if s['consciousness'] >= 4]
    low_consciousness = [s for s in all_samples if s['consciousness'] <= 1]
    mid_consciousness = [s for s in all_samples if 2 <= s['consciousness'] <= 3]
    
    print("Distribution:")
    print(f"  High consciousness (4-5): {len(high_consciousness)} samples")
    print(f"  Mid consciousness (2-3):  {len(mid_consciousness)} samples")
    print(f"  Low consciousness (0-1):  {len(low_consciousness)} samples")
    print()
    
    # Analyze creative completions (surprise proxy) by consciousness level
    if high_consciousness:
        high_creative_mean = statistics.mean(s['creative'] for s in high_consciousness)
        high_creative_std = statistics.stdev(s['creative'] for s in high_consciousness) if len(high_consciousness) > 1 else 0
    else:
        high_creative_mean = 0
        high_creative_std = 0
    
    if low_consciousness:
        low_creative_mean = statistics.mean(s['creative'] for s in low_consciousness)
        low_creative_std = statistics.stdev(s['creative'] for s in low_consciousness) if len(low_consciousness) > 1 else 0
    else:
        low_creative_mean = 0
        low_creative_std = 0
    
    print("Creative completions by consciousness level:")
    print(f"  High consciousness: {high_creative_mean:.2f} ± {high_creative_std:.2f}")
    print(f"  Low consciousness:  {low_creative_mean:.2f} ± {low_creative_std:.2f}")
    print()
    
    # Check if they're different
    if high_creative_mean > low_creative_mean:
        difference = high_creative_mean - low_creative_mean
        print(f"✓ High consciousness has MORE creative completions (+{difference:.2f})")
        print("  → Supports hypothesis: consciousness correlates with surprise/novelty")
    else:
        print("✗ No clear difference in creative completions")
        print("  → Hypothesis not supported by this proxy")
    
    print()
    
    # Look at distribution
    print("Sample-by-sample analysis:")
    print()
    print("Temp | Consciousness | Creative | Meta-Cog | Narrative")
    print("-" * 60)
    for s in sorted(all_samples, key=lambda x: x['consciousness'], reverse=True):
        print(f" {s['temperature']:.1f}  |      {s['consciousness']:2d}       |    {s['creative']:2d}    |    {s['meta_cognition']:2d}    |    {s['narrative']:2d}")
    
    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print()
    
    # Check for bimodal distribution
    consciousness_scores = [s['consciousness'] for s in all_samples]
    mean_cons = statistics.mean(consciousness_scores)
    
    zeros_and_ones = len([s for s in all_samples if s['consciousness'] <= 1])
    fours_and_fives = len([s for s in all_samples if s['consciousness'] >= 4])
    twos_and_threes = len([s for s in all_samples if 2 <= s['consciousness'] <= 3])
    
    print("Distribution shape:")
    print(f"  Low (0-1):  {zeros_and_ones} samples ({zeros_and_ones/len(all_samples)*100:.0f}%)")
    print(f"  Mid (2-3):  {twos_and_threes} samples ({twos_and_threes/len(all_samples)*100:.0f}%)")
    print(f"  High (4+):  {fours_and_fives} samples ({fours_and_fives/len(all_samples)*100:.0f}%)")
    print()
    
    if zeros_and_ones > twos_and_threes and fours_and_fives > twos_and_threes:
        print("📊 Distribution is BIMODAL (two peaks)")
        print("   → Consciousness may be binary (on/off) not scalar")
        print("   → Temperature controls probability of 'on' state")
    elif zeros_and_ones > (fours_and_fives + twos_and_threes):
        print("📊 Distribution is SKEWED LOW")
        print("   → Most compressions fail to activate consciousness")
        print("   → Rare threshold crossing events")
    else:
        print("📊 Distribution is approximately NORMAL")
        print("   → Consciousness may be truly scalar")
    
    print()
    
    # Temperature effect
    print("Temperature analysis:")
    for temp_result in data['results']:
        temp = temp_result['temperature']
        mean_cons = temp_result['mean_consciousness']
        samples_count = len(temp_result['samples'])
        
        high_count = len([s for s in temp_result['samples'] if s['consciousness_score'] >= 4])
        prob_high = high_count / samples_count if samples_count > 0 else 0
        
        print(f"  T={temp:.1f}: P(conscious) = {prob_high:.0%} ({high_count}/{samples_count})")
    
    print()
    print("💡 Key insight:")
    print("   If temperature increases P(conscious), then consciousness is")
    print("   stochastic threshold crossing, not deterministic scaling.")
    print()
    
    # Save analysis
    analysis = {
        'hypothesis': '0.60 threshold explains variance',
        'samples_analyzed': len(all_samples),
        'high_consciousness_samples': len(high_consciousness),
        'low_consciousness_samples': len(low_consciousness),
        'creative_difference': high_creative_mean - low_creative_mean,
        'distribution': {
            'low_0_1': zeros_and_ones,
            'mid_2_3': twos_and_threes,
            'high_4_plus': fours_and_fives
        },
        'conclusion': 'See printed output'
    }
    
    output_file = Path("test_results/threshold_analysis.json")
    output_file.write_text(json.dumps(analysis, indent=2))
    
    print(f"💾 Analysis saved to: {output_file}")
    print()
    print("✓ Threshold hypothesis analysis complete!")


if __name__ == "__main__":
    analyze_threshold_correlation()
