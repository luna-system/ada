#!/usr/bin/env python3
"""
SIF Compression Test v3: Alice in Wonderland - NORMALIZED SCORES
================================================================

Properly normalize importance scores so thresholds work correctly.
"""

import json
import math
import requests
from datetime import datetime
import numpy as np
import re
from sklearn.preprocessing import MinMaxScaler

ALICE_URL = "https://www.gutenberg.org/cache/epub/11/pg11.txt"

COMPRESSION_TIERS = {
    1: {'percentile': 0.90, 'name': 'Critical (Top 10%)'},
    2: {'percentile': 0.75, 'name': 'Standard (Top 25%)'},
    3: {'percentile': 0.50, 'name': 'Enhanced (Top 50%)'},
    4: {'percentile': 0.25, 'name': 'Aggressive (Top 75%)'},
}

MAJOR_CHARACTERS = {
    'Alice': 'protagonist', 'White Rabbit': 'guide', 'Caterpillar': 'sage',
    'Cheshire Cat': 'trickster', 'Mad Hatter': 'fool', 'Queen of Hearts': 'antagonist',
}

ACTION_VERBS = [
    'fell', 'went', 'said', 'asked', 'replied', 'cried', 'screamed', 'laughed',
    'thought', 'saw', 'heard', 'found', 'discovered', 'realized', 'wondered',
    'ran', 'walked', 'danced', 'grew', 'changed'
]

def fetch_alice():
    """Get Alice"""
    print("📥 Fetching Alice in Wonderland...")
    response = requests.get(ALICE_URL)
    text = response.text
    
    start = text.find("*** START OF THE PROJECT GUTENBERG EBOOK")
    end = text.find("*** END OF THE PROJECT GUTENBERG EBOOK")
    
    if start != -1 and end != -1:
        text = text[start:end]
    
    text = '\n'.join(line for line in text.split('\n') 
                     if line.strip() and not line.startswith('***'))
    
    return text

def extract_sentences(text):
    """Extract sentences"""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]

def calculate_raw_importance(sentence, position, total_sentences):
    """Calculate raw importance score (not normalized yet)"""
    score = 0.0
    
    # Character mentions (+0-2.0)
    for char in MAJOR_CHARACTERS.keys():
        if char.lower() in sentence.lower():
            score += 1.0
    
    # Action verbs (+0-1.0)
    for verb in ACTION_VERBS:
        if verb in sentence.lower():
            score += 0.15
    
    # Dialogue - very important (+0.5)
    if '"' in sentence or "'" in sentence:
        score += 0.5
    
    # Questions - crucial moments (+0.5)
    if '?' in sentence:
        score += 0.5
    
    # Exclamations (+0.3)
    if '!' in sentence:
        score += 0.3
    
    # Transformative words (+0.8)
    transform_words = ['grew', 'shrunk', 'changed', 'realized', 'understood', 'discovered', 'awakened']
    for word in transform_words:
        if word in sentence.lower():
            score += 0.8
    
    # Position in narrative (+0-1.0, later = more recent)
    position_score = (position / total_sentences) * 1.0
    score += position_score * 0.5
    
    # Length premium (+0-0.5)
    word_count = len(sentence.split())
    if 15 <= word_count <= 40:
        score += 0.5
    elif 40 < word_count <= 60:
        score += 0.3
    
    return score

def run_test():
    """Run the test with proper normalization"""
    
    print("\n" + "="*80)
    print("SIF COMPRESSION TEST v3: Alice in Wonderland")
    print("Properly Normalized Importance Scores")
    print("="*80 + "\n")
    
    # Fetch
    print("Step 1: Fetching Alice...")
    alice_text = fetch_alice()
    original_bytes = len(alice_text.encode('utf-8'))
    
    print(f"  ✓ Size: {original_bytes:,} bytes ({len(alice_text.split()):,} words)")
    
    # Extract
    print("\nStep 2: Extracting sentences...")
    sentences = extract_sentences(alice_text)
    print(f"  ✓ Extracted: {len(sentences)} sentences")
    
    # Calculate raw importance
    print("\nStep 3: Calculating importance scores...")
    facts = []
    raw_scores = []
    
    for i, sentence in enumerate(sentences):
        raw_score = calculate_raw_importance(sentence, i, len(sentences))
        raw_scores.append(raw_score)
        facts.append({
            'id': f'fact_{i}',
            'content': sentence,
            'position': i,
            'raw_score': raw_score,
            'length': len(sentence)
        })
    
    # Normalize scores to 0-1 range
    print("  ✓ Normalizing scores...")
    min_score = min(raw_scores)
    max_score = max(raw_scores)
    
    for fact in facts:
        normalized = (fact['raw_score'] - min_score) / (max_score - min_score) if max_score > min_score else 0.5
        fact['importance'] = normalized
    
    print(f"\n  Raw scores: min={min_score:.2f}, max={max_score:.2f}")
    
    # Statistics
    importances = [f['importance'] for f in facts]
    print(f"\n  Normalized importance distribution:")
    print(f"    Min: {min(importances):.3f}")
    print(f"    Max: {max(importances):.3f}")
    print(f"    Mean: {np.mean(importances):.3f}")
    print(f"    Median: {np.median(importances):.3f}")
    print(f"    Std Dev: {np.std(importances):.3f}")
    
    # Show top facts
    print(f"\n  Top 10 most important facts:")
    sorted_facts = sorted(facts, key=lambda f: f['importance'], reverse=True)
    for i, fact in enumerate(sorted_facts[:10], 1):
        print(f"    {i}. [{fact['importance']:.3f}] {fact['content'][:70]}...")
    
    # Compression test
    print("\n" + "="*80)
    print("COMPRESSION RESULTS AT DIFFERENT PERCENTILES")
    print("="*80 + "\n")
    
    results = {}
    
    for tier_num, tier_info in sorted(COMPRESSION_TIERS.items()):
        percentile = tier_info['percentile']
        tier_name = tier_info['name']
        
        # Calculate threshold based on percentile
        threshold = np.percentile(importances, (1 - percentile) * 100)
        
        print(f"\n📊 TIER {tier_num}: {tier_name}")
        print(f"   Threshold: {threshold:.3f} (importance ≥ {threshold:.3f})")
        print("-" * 75)
        
        # Compress
        compressed = [f for f in facts if f['importance'] >= threshold]
        
        # Build SIF JSON
        sif_data = {
            'version': '1.0.0',
            'threshold': float(threshold),
            'facts': [{'content': f['content'], 'importance': float(f['importance'])} 
                     for f in compressed]
        }
        sif_json = json.dumps(sif_data, separators=(',', ':'))
        sif_bytes = len(sif_json.encode('utf-8'))
        
        # Metrics
        compression_ratio = original_bytes / sif_bytes if sif_bytes > 0 else float('inf')
        facts_preserved = len(compressed) / len(facts) if facts else 0
        bytes_saved = original_bytes - sif_bytes
        percent_saved = (bytes_saved / original_bytes) * 100 if original_bytes > 0 else 0
        
        # Quality metrics
        if compressed:
            avg_importance = np.mean([f['importance'] for f in compressed])
            
            dropped = [f for f in facts if f not in compressed]
            if dropped:
                avg_dropped_importance = np.mean([f['importance'] for f in dropped])
            else:
                avg_dropped_importance = 0
            
            # Information loss
            importance_ratio = avg_importance / (avg_importance + avg_dropped_importance + 0.001)
            lossiness = (1 - facts_preserved) * (1 - importance_ratio)
            quality_score = (facts_preserved * 0.4 + avg_importance * 0.6) * 100
            
            # Show example facts kept
            top_kept = sorted(compressed, key=lambda f: f['importance'], reverse=True)[:3]
            top_dropped = sorted(dropped, key=lambda f: f['importance'], reverse=True)[:3]
        else:
            avg_importance = 0
            lossiness = 1.0
            quality_score = 0
            top_kept = []
            top_dropped = sorted(facts, key=lambda f: f['importance'], reverse=True)[:3]
        
        print(f"Original:            {original_bytes:>10,} bytes")
        print(f"SIF Size:            {sif_bytes:>10,} bytes")
        print(f"Compression:         {compression_ratio:>10.1f}x")
        print(f"Saved:               {bytes_saved:>10,} bytes ({percent_saved:>5.1f}%)")
        
        print(f"\nFacts preserved:     {len(compressed):>10} / {len(facts)} ({facts_preserved*100:>5.1f}%)")
        print(f"Avg importance:      {avg_importance:>10.3f}")
        print(f"Information loss:    {lossiness*100:>10.1f}%")
        print(f"Quality score:       {quality_score:>10.1f} / 100")
        
        if top_kept:
            print(f"\n  Example facts KEPT (high importance):")
            for fact in top_kept:
                print(f"    • [{fact['importance']:.3f}] {fact['content'][:60]}...")
        
        if top_dropped:
            print(f"\n  Example facts DROPPED (low importance):")
            for fact in top_dropped:
                print(f"    • [{fact['importance']:.3f}] {fact['content'][:60]}...")
        
        results[tier_num] = {
            'percentile': percentile,
            'threshold': float(threshold),
            'name': tier_name,
            'compression_ratio': compression_ratio,
            'bytes': sif_bytes,
            'facts_preserved': facts_preserved,
            'facts_count': len(compressed),
            'avg_importance': avg_importance,
            'lossiness': lossiness,
            'quality_score': quality_score,
            'bytes_saved': bytes_saved
        }
    
    # Summary table
    print("\n" + "="*80)
    print("GRADIENT SUMMARY TABLE")
    print("="*80 + "\n")
    
    print(f"{'Tier':<25} {'Top %':<8} {'Threshold':<12} {'Ratio':<8} {'Quality':<8} {'Loss':<8}")
    print("-" * 75)
    
    for tier_num in sorted(results.keys()):
        r = results[tier_num]
        pct = r['percentile'] * 100
        print(f"{r['name']:<25} {pct:<8.0f}% {r['threshold']:<12.3f} {r['compression_ratio']:<8.1f}x "
              f"{r['quality_score']:<8.1f} {r['lossiness']*100:<8.1f}%")
    
    # Key analysis
    print("\n" + "="*80)
    print("KEY FINDINGS: Compression Gradient Analysis")
    print("="*80 + "\n")
    
    tier1 = results[1]  # Top 10%
    tier2 = results[2]  # Top 25%
    tier3 = results[3]  # Top 50%
    tier4 = results[4]  # Top 75%
    
    print(f"Selecting the TOP 25% most important facts (Standard tier):")
    print(f"  • Compression: {tier2['compression_ratio']:.1f}x")
    print(f"  • Facts kept: {tier2['facts_count']} ({tier2['facts_preserved']*100:.1f}%)")
    print(f"  • Quality: {tier2['quality_score']:.0f}/100")
    print(f"  • Information loss: {tier2['lossiness']*100:.1f}%")
    
    print(f"\nCompression gradient from Critical to Aggressive:")
    ratio_step = tier2['compression_ratio'] / tier1['compression_ratio']
    quality_drop = tier4['quality_score'] - tier1['quality_score']
    print(f"  • Each percentile tier adds {ratio_step:.2f}x compression improvement")
    print(f"  • From top 10% → top 75%: {quality_drop:+.0f} points quality loss")
    print(f"  • Trade-off: {tier4['compression_ratio']/tier1['compression_ratio']:.1f}x more compression")
    
    print(f"\n✨ THE SWEET SPOT (Standard - Top 25%):")
    print(f"   Balances extreme compression ({tier2['compression_ratio']:.0f}x) with excellent quality ({tier2['quality_score']:.0f}/100)")
    print(f"   Keeps only the most important {tier2['facts_preserved']*100:.1f}% of sentences")
    print(f"   Information loss: only {tier2['lossiness']*100:.1f}%")
    
    # Save
    print("\n" + "="*80)
    results_file = '/home/luna/Code/ada-v1/experiments/sif_compression_alice_v3_results.json'
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'document': 'Alice in Wonderland (26K words, 152KB)',
            'original_bytes': original_bytes,
            'total_sentences': len(facts),
            'importance_stats': {
                'min': float(min(importances)),
                'max': float(max(importances)),
                'mean': float(np.mean(importances)),
                'median': float(np.median(importances)),
                'std': float(np.std(importances))
            },
            'tiers': results
        }, f, indent=2)
    
    print(f"✓ Results saved: {results_file}\n")
    
    return results

if __name__ == '__main__':
    run_test()
