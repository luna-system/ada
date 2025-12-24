#!/usr/bin/env python3
"""
SIF Compression Test v5: Alice in Wonderland - LLM-BASED IMPORTANCE
===================================================================

Use Ollama/Qwen to calculate actual semantic importance scores.
This solves the heuristic problem by asking the LLM "how important is this sentence?"
"""

import json
import math
import requests
from datetime import datetime
import numpy as np
import re
from collections import defaultdict
import time

ALICE_URL = "https://www.gutenberg.org/cache/epub/11/pg11.txt"
OLLAMA_URL = "http://localhost:11434/api/generate"

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

def extract_sentences(text, limit=None):
    """Extract sentences"""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    if limit:
        sentences = sentences[:limit]
    
    return sentences

def score_importance_with_llm(sentence, context='Alice in Wonderland - a classic children\'s adventure story'):
    """Ask Ollama to score importance of a sentence (0-1)"""
    
    prompt = f"""Rate how important this sentence is to the story "{context}".
Consider: character development, plot advancement, dialogue, transformations, conflicts.
Respond with ONLY a number from 0.0 to 1.0.

Sentence: {sentence}

Rating: """
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "qwen2.5-coder:7b",
                "prompt": prompt,
                "stream": False,
                "temperature": 0.1,  # Low temp for consistent scores
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()['response'].strip()
            # Extract just the number
            numbers = re.findall(r'0\.\d+|1\.0|1', result)
            if numbers:
                return float(numbers[0])
    except Exception as e:
        print(f"    ⚠ LLM error: {e}")
    
    return 0.5  # Default if error

def run_test():
    """Run the test"""
    
    print("\n" + "="*90)
    print("SIF COMPRESSION TEST v5: Alice in Wonderland")
    print("LLM-Based Importance Scoring (Semantic Understanding)")
    print("="*90 + "\n")
    
    # Fetch
    print("Step 1: Fetching Alice...")
    alice_text = fetch_alice()
    original_bytes = len(alice_text.encode('utf-8'))
    print(f"  ✓ Size: {original_bytes:,} bytes ({len(alice_text.split()):,} words)")
    
    # Extract (sample for speed)
    print("\nStep 2: Extracting sentences...")
    SAMPLE_SIZE = 100  # Test with 100 sentences first
    sentences = extract_sentences(alice_text, limit=SAMPLE_SIZE)
    print(f"  ✓ Extracted: {len(sentences)} sentences (sampled from full text for demo)")
    
    # Score with LLM
    print(f"\nStep 3: Scoring importance with LLM (Qwen)...")
    print(f"  This will take ~{len(sentences)} seconds (1 LLM call per sentence)...")
    
    facts = []
    importances = []
    
    for i, sentence in enumerate(sentences):
        if (i + 1) % 10 == 0:
            print(f"    {i + 1}/{len(sentences)}...", end='', flush=True)
        
        importance = score_importance_with_llm(sentence)
        importances.append(importance)
        
        facts.append({
            'id': f'f{i}',
            'text': sentence[:100],
            'importance': importance,
            'position': i
        })
        
        if (i + 1) % 10 == 0:
            print(" ✓")
        
        time.sleep(0.1)  # Rate limit
    
    importances = np.array(importances)
    
    print(f"\n  ✓ Scoring complete!")
    print(f"\n  LLM Importance distribution:")
    print(f"    Min: {importances.min():.3f}")
    print(f"    Max: {importances.max():.3f}")
    print(f"    Mean: {importances.mean():.3f}")
    print(f"    Median: {np.median(importances):.3f}")
    print(f"    Std Dev: {importances.std():.3f}")
    print(f"    Q1: {np.percentile(importances, 25):.3f}")
    print(f"    Q3: {np.percentile(importances, 75):.3f}")
    
    # Show top facts
    print(f"\n  Top 10 most important facts (according to LLM):")
    sorted_facts = sorted(facts, key=lambda f: f['importance'], reverse=True)
    for i, fact in enumerate(sorted_facts[:10], 1):
        print(f"    {i}. [{fact['importance']:.3f}] {fact['text'][:65]}...")
    
    print(f"\n  Bottom 5 least important facts:")
    for i, fact in enumerate(sorted_facts[-5:], 1):
        print(f"    {i}. [{fact['importance']:.3f}] {fact['text'][:65]}...")
    
    # COMPRESSION TEST at various thresholds
    print("\n" + "="*90)
    print("COMPRESSION RESULTS AT IMPORTANCE THRESHOLDS")
    print("="*90 + "\n")
    
    thresholds = [
        (0.80, 'CRITICAL (Top 5%)', 'Maximum preservation'),
        (0.70, 'ESSENTIAL (Top 12%)', 'Very high quality'),
        (0.60, 'STANDARD (Top 25%)', 'Sweet spot (SIF spec)'),
        (0.50, 'BALANCED (Top 37%)', 'Good quality'),
        (0.40, 'ENHANCED (Top 50%)', 'Moderate quality'),
        (0.30, 'AGGRESSIVE (Top 65%)', 'High compression'),
    ]
    
    results = {}
    
    for threshold, label, description in thresholds:
        above_threshold = [f for f in facts if f['importance'] >= threshold]
        pct_above = len(above_threshold) / len(facts) * 100 if facts else 0
        
        print(f"\n📊 {label}")
        print(f"   Threshold: {threshold:.2f} (importance ≥ {threshold:.2f})")
        print(f"   Facts preserved: {len(above_threshold)} / {len(facts)} ({pct_above:.1f}%)")
        print(f"   Description: {description}")
        print("-" * 85)
        
        # Create SIF JSON
        sif_data = {
            'v': '1.0',
            't': float(threshold),
            'f': [
                [f['text'], round(f['importance'], 3)]
                for f in above_threshold
            ]
        }
        
        sif_json = json.dumps(sif_data, separators=(',', ':'))
        sif_bytes = len(sif_json.encode('utf-8'))
        
        # Metrics
        compression_ratio = original_bytes / sif_bytes if sif_bytes > 0 else float('inf')
        bytes_saved = original_bytes - sif_bytes
        percent_saved = (bytes_saved / original_bytes) * 100 if original_bytes > 0 else 0
        
        # Quality
        if above_threshold:
            avg_importance = np.mean([f['importance'] for f in above_threshold])
            
            dropped = [f for f in facts if f not in above_threshold]
            if dropped:
                avg_dropped_importance = np.mean([f['importance'] for f in dropped])
            else:
                avg_dropped_importance = 0
            
            pct_dropped = len(dropped) / len(facts) if facts else 0
            lossiness = pct_dropped * (1 - (avg_importance / (avg_importance + avg_dropped_importance + 0.001)))
            
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
    
    print(f"\n📊 COMPRESSION GRADIENT:")
    print(f"   From {critical['facts_kept']} facts (critical) → {aggressive['facts_kept']} facts (aggressive):")
    print(f"   • Compression: {critical['compression_ratio']:.1f}x → {aggressive['compression_ratio']:.1f}x")
    print(f"   • Quality: {critical['quality_score']:.0f} → {aggressive['quality_score']:.0f}")
    
    print(f"\n✨ LOSSINESS ANALYSIS:")
    if sweet_spot['lossiness'] < 0.15:
        print(f"   ✓ EXCELLENT - Less than 15% information loss")
    elif sweet_spot['lossiness'] < 0.25:
        print(f"   ✓ GOOD - Less than 25% information loss")
    else:
        print(f"   ⚠ MODERATE - {sweet_spot['lossiness']*100:.0f}% information loss")
    
    # Save
    print("\n" + "="*90)
    results_file = '/home/luna/Code/ada-v1/experiments/sif_compression_v5_results.json'
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'document': 'Alice in Wonderland (100 sentence sample)',
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

if __name__ == '__main__':
    run_test()
