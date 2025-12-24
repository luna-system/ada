#!/usr/bin/env python3
"""
SIF Compression Test v4: Alice in Wonderland - PROPER SIF FORMAT
=================================================================

Create actual SIF JSON (just facts list) for true compression measurement.
SIF = Simple Information Format: minimal JSON with facts array
"""

import json
import math
import requests
from datetime import datetime
import numpy as np
import re
from collections import defaultdict

ALICE_URL = "https://www.gutenberg.org/cache/epub/11/pg11.txt"

MAJOR_CHARACTERS = {
    'Alice': 'protagonist', 'White Rabbit': 'guide', 'Caterpillar': 'sage',
    'Cheshire Cat': 'trickster', 'Mad Hatter': 'fool', 'Queen of Hearts': 'antagonist',
    'King of Hearts': 'authority', 'Duchess': 'chaos', 'Hatter': 'fool',
    'March Hare': 'trickster', 'Mouse': 'story-teller'
}

ACTION_VERBS = [
    'fell', 'went', 'said', 'asked', 'replied', 'cried', 'screamed', 'laughed',
    'thought', 'saw', 'heard', 'found', 'discovered', 'realized', 'wondered',
    'ran', 'walked', 'danced', 'grew', 'changed', 'watched', 'looked', 'noticed'
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

def calculate_importance(sentence, position, total_sentences, freq_map):
    """Calculate importance score (0-1)"""
    score = 0.0
    
    # Character mentions (+0.2 each)
    char_score = 0.0
    for char in MAJOR_CHARACTERS.keys():
        if char.lower() in sentence.lower():
            char_score += 0.2
    score += min(char_score, 0.6)  # Cap at 0.6
    
    # Action verbs (+0.08 each)
    verb_score = sum(0.08 for verb in ACTION_VERBS if verb in sentence.lower())
    score += min(verb_score, 0.4)  # Cap at 0.4
    
    # Dialogue - very important (+0.3)
    if '"' in sentence or "'" in sentence:
        score += 0.3
    
    # Questions - crucial moments (+0.3)
    if '?' in sentence:
        score += 0.3
    
    # Exclamations (+0.2)
    if '!' in sentence:
        score += 0.2
    
    # Transformative words (+0.5)
    transform_words = ['grew', 'shrunk', 'changed', 'realized', 'understood', 'discovered', 'awakened', 'transformed']
    if any(word in sentence.lower() for word in transform_words):
        score += 0.5
    
    # Word uniqueness (surprise) - words not seen before
    unique_words = sum(1 for word in sentence.split() if freq_map[word.lower()] == 1)
    uniqueness = min(unique_words / len(sentence.split()), 1.0) if sentence.split() else 0
    score += uniqueness * 0.3
    
    # Recency decay - recent sentences slightly boosted
    recency = (position / total_sentences) * 0.2
    score += recency
    
    # Normalize to 0-1
    return min(score / 4.0, 1.0)  # Normalize assuming max score around 4

def run_test():
    """Run the test"""
    
    print("\n" + "="*90)
    print("SIF COMPRESSION TEST v4: Alice in Wonderland")
    print("Proper SIF Format (Facts-Only JSON)")
    print("="*90 + "\n")
    
    # Fetch
    print("Step 1: Fetching Alice...")
    alice_text = fetch_alice()
    original_bytes = len(alice_text.encode('utf-8'))
    
    print(f"  ✓ Size: {original_bytes:,} bytes ({len(alice_text.split()):,} words)")
    
    # Extract
    print("\nStep 2: Extracting sentences...")
    sentences = extract_sentences(alice_text)
    print(f"  ✓ Extracted: {len(sentences)} sentences")
    
    # Build frequency map
    print("\nStep 3: Analyzing word frequencies...")
    freq_map = defaultdict(int)
    for sentence in sentences:
        for word in sentence.lower().split():
            word = re.sub(r'[^\w]', '', word)  # Remove punctuation
            if word:
                freq_map[word] += 1
    
    # Calculate importance
    print("  ✓ Calculating importance scores...")
    facts = []
    importances = []
    
    for i, sentence in enumerate(sentences):
        importance = calculate_importance(sentence, i, len(sentences), freq_map)
        importances.append(importance)
        facts.append({
            'id': f'f{i}',
            'text': sentence[:100],  # Truncate for storage
            'importance': importance,
            'position': i
        })
    
    importances = np.array(importances)
    
    print(f"\n  Importance distribution:")
    print(f"    Min: {importances.min():.3f}")
    print(f"    Max: {importances.max():.3f}")
    print(f"    Mean: {importances.mean():.3f}")
    print(f"    Median: {np.median(importances):.3f}")
    print(f"    Std Dev: {importances.std():.3f}")
    print(f"    Q1: {np.percentile(importances, 25):.3f}")
    print(f"    Q3: {np.percentile(importances, 75):.3f}")
    
    # Show top facts
    print(f"\n  Top 10 most important facts:")
    sorted_facts = sorted(facts, key=lambda f: f['importance'], reverse=True)
    for i, fact in enumerate(sorted_facts[:10], 1):
        print(f"    {i}. [{fact['importance']:.3f}] {fact['text'][:65]}...")
    
    # COMPRESSION TEST at various thresholds
    print("\n" + "="*90)
    print("COMPRESSION RESULTS AT IMPORTANCE THRESHOLDS")
    print("="*90 + "\n")
    
    thresholds = [
        (0.80, 'CRITICAL (Top unique 5%)', 'Maximum preservation'),
        (0.70, 'ESSENTIAL (Top unique 12%)', 'Very high quality'),
        (0.60, 'STANDARD (Top unique 25%)', 'Sweet spot (SIF spec)'),
        (0.50, 'BALANCED (Top unique 37%)', 'Good quality'),
        (0.40, 'ENHANCED (Top unique 50%)', 'Moderate quality'),
        (0.30, 'AGGRESSIVE (Top unique 65%)', 'High compression'),
    ]
    
    results = {}
    
    for threshold, label, description in thresholds:
        # Find how many facts meet this threshold
        above_threshold = [f for f in facts if f['importance'] >= threshold]
        pct_above = len(above_threshold) / len(facts) * 100 if facts else 0
        
        print(f"\n📊 {label}")
        print(f"   Threshold: {threshold:.2f} (importance ≥ {threshold:.2f})")
        print(f"   Facts preserved: {len(above_threshold)} / {len(facts)} ({pct_above:.1f}%)")
        print(f"   Description: {description}")
        print("-" * 85)
        
        # Create actual SIF JSON (compressed format)
        sif_data = {
            'v': '1.0',  # version (abbreviated)
            't': float(threshold),  # threshold
            'f': [  # facts (abbreviated)
                [f['text'], round(f['importance'], 3)]  # text, importance
                for f in above_threshold
            ]
        }
        
        # Serialize
        sif_json = json.dumps(sif_data, separators=(',', ':'))
        sif_bytes = len(sif_json.encode('utf-8'))
        
        # Calculate metrics
        compression_ratio = original_bytes / sif_bytes if sif_bytes > 0 else float('inf')
        bytes_saved = original_bytes - sif_bytes
        percent_saved = (bytes_saved / original_bytes) * 100 if original_bytes > 0 else 0
        
        # Quality metrics
        if above_threshold:
            avg_importance = np.mean([f['importance'] for f in above_threshold])
            
            # Information loss: combination of what we dropped + importance of dropped items
            dropped = [f for f in facts if f not in above_threshold]
            if dropped:
                avg_dropped_importance = np.mean([f['importance'] for f in dropped])
            else:
                avg_dropped_importance = 0
            
            # Lossiness = (percentage dropped) * (average importance of dropped)
            pct_dropped = len(dropped) / len(facts) if facts else 0
            lossiness = pct_dropped * (1 - (avg_importance / (avg_importance + avg_dropped_importance + 0.001)))
            
            # Quality score: preserve both quantity and quality
            quality_score = (pct_above * 0.4 + avg_importance * 100 * 0.6)
            
        else:
            avg_importance = 0
            lossiness = 1.0
            quality_score = 0
        
        print(f"Original text:       {original_bytes:>10,} bytes")
        print(f"SIF JSON size:       {sif_bytes:>10,} bytes")
        print(f"Compression ratio:   {compression_ratio:>10.1f}x")
        print(f"Space saved:         {bytes_saved:>10,} bytes ({percent_saved:>5.1f}%)")
        print(f"\nAvg importance:      {avg_importance:>10.3f}")
        print(f"Information loss:    {lossiness*100:>10.1f}%")
        print(f"Quality score:       {quality_score:>10.1f} / 100")
        
        # Example preserved facts
        if above_threshold:
            top_3 = sorted(above_threshold, key=lambda f: f['importance'], reverse=True)[:3]
            print(f"\n  Example preserved facts:")
            for fact in top_3:
                print(f"    [{fact['importance']:.3f}] {fact['text'][:60]}...")
        
        results[f"{threshold:.2f}"] = {
            'threshold': float(threshold),
            'label': label,
            'pct_above': pct_above,
            'facts_kept': len(above_threshold),
            'compression_ratio': compression_ratio,
            'sif_bytes': sif_bytes,
            'bytes_saved': bytes_saved,
            'avg_importance': avg_importance,
            'lossiness': lossiness,
            'quality_score': quality_score
        }
    
    # Summary
    print("\n" + "="*90)
    print("GRADIENT ANALYSIS: Trade-off Table")
    print("="*90 + "\n")
    
    print(f"{'Threshold':<12} {'Label':<25} {'Facts %':<10} {'Ratio':<8} {'Quality':<8} {'Loss %':<8}")
    print("-" * 85)
    
    for threshold_str in sorted(results.keys(), reverse=True):
        r = results[threshold_str]
        print(f"{r['threshold']:<12.2f} {r['label']:<25} {r['pct_above']:<10.1f}% "
              f"{r['compression_ratio']:<8.1f}x {r['quality_score']:<8.0f} {r['lossiness']*100:<8.1f}%")
    
    # Analysis
    print("\n" + "="*90)
    print("KEY FINDINGS")
    print("="*90 + "\n")
    
    sweet_spot = results['0.60']
    critical = results['0.80']
    aggressive = results['0.30']
    
    print(f"🎯 THE SWEET SPOT (0.60 threshold - SIF Specification):")
    print(f"   • Preserves {sweet_spot['facts_kept']} facts ({sweet_spot['pct_above']:.1f}%)")
    print(f"   • Compression: {sweet_spot['compression_ratio']:.1f}x")
    print(f"   • Quality: {sweet_spot['quality_score']:.0f}/100")
    print(f"   • Information loss: {sweet_spot['lossiness']*100:.1f}%")
    print(f"   • SIF size: {sweet_spot['sif_bytes']:,} bytes ({sweet_spot['bytes_saved']:,} bytes saved)")
    
    print(f"\n📊 COMPRESSION GRADIENT:")
    print(f"   From {critical['facts_kept']} facts (critical) → {aggressive['facts_kept']} facts (aggressive):")
    print(f"   • Compression improves: {critical['compression_ratio']:.1f}x → {aggressive['compression_ratio']:.1f}x")
    print(f"   • Quality degrades: {critical['quality_score']:.0f} → {aggressive['quality_score']:.0f}")
    print(f"   • Each 0.10 drop in threshold adds ~{(aggressive['compression_ratio']/critical['compression_ratio'])**(1/5):.2f}x compression")
    
    print(f"\n✨ LOSSINESS ANALYSIS:")
    if sweet_spot['lossiness'] < 0.15:
        print(f"   ✓ At 0.60 threshold: EXCELLENT - Less than 15% information loss")
    elif sweet_spot['lossiness'] < 0.25:
        print(f"   ✓ At 0.60 threshold: GOOD - Less than 25% information loss")
    else:
        print(f"   ⚠ At 0.60 threshold: MODERATE - {sweet_spot['lossiness']*100:.0f}% information loss")
    
    # Save results
    print("\n" + "="*90)
    results_file = '/home/luna/Code/ada-v1/experiments/sif_compression_v4_results.json'
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'document': 'Alice in Wonderland (26K words, 152KB)',
            'original_bytes': original_bytes,
            'total_sentences': len(sentences),
            'importance_stats': {
                'min': float(importances.min()),
                'max': float(importances.max()),
                'mean': float(importances.mean()),
                'median': float(np.median(importances)),
                'std': float(importances.std()),
                'q1': float(np.percentile(importances, 25)),
                'q3': float(np.percentile(importances, 75))
            },
            'thresholds': results,
            'sweet_spot': {
                'threshold': 0.60,
                'compression_ratio': sweet_spot['compression_ratio'],
                'quality_score': sweet_spot['quality_score'],
                'information_loss': sweet_spot['lossiness']
            }
        }, f, indent=2)
    
    print(f"✓ Results saved: {results_file}\n")
    
    return results

if __name__ == '__main__':
    run_test()
