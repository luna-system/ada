#!/usr/bin/env python3
"""
SIF Compression Test v2: Alice in Wonderland - IMPROVED IMPORTANCE CALCULATION
===============================================================================

Using smarter heuristics for importance that capture semantic richness.
"""

import json
import math
import requests
from datetime import datetime
import numpy as np
import re

# === FETCH DATA ===
ALICE_URL = "https://www.gutenberg.org/cache/epub/11/pg11.txt"

COMPRESSION_TIERS = {
    1: {'threshold': 0.75, 'name': 'Critical (Absolute Core)'},
    2: {'threshold': 0.60, 'name': 'Standard (Golden Ratio)'},
    3: {'threshold': 0.50, 'name': 'Enhanced'},
    4: {'threshold': 0.30, 'name': 'Aggressive (Everything)'},
}

WEIGHTS = {
    'surprise': 0.60,
    'relevance': 0.20,
    'decay': 0.10,
    'habituation': 0.10
}

# === CHARACTERS & THEMES ===
MAJOR_CHARACTERS = {
    'Alice': 'protagonist', 'White Rabbit': 'guide', 'Caterpillar': 'sage',
    'Cheshire Cat': 'trickster', 'Mad Hatter': 'fool', 'Queen of Hearts': 'antagonist',
    'King of Hearts': 'authority', 'Duchess': 'chaos', 'Mock Turtle': 'victim',
    'Gryphon': 'companion', 'March Hare': 'madness', 'Dormouse': 'sleep'
}

KEY_CONCEPTS = [
    'fall', 'grow', 'shrink', 'grow', 'dream', 'reality', 'logic', 'madness',
    'time', 'tea', 'trial', 'execution', 'curiosity', 'change', 'identity'
]

ACTION_VERBS = [
    'fell', 'fell', 'came', 'went', 'said', 'asked', 'replied', 'cried', 'screamed',
    'laughed', 'thought', 'saw', 'heard', 'found', 'discovered', 'realized',
    'understood', 'noticed', 'wondered', 'decided', 'ran', 'walked', 'danced'
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

def score_character_mention(sentence):
    """Score: -1 to 1 based on character mentions"""
    score = 0
    for char, role in MAJOR_CHARACTERS.items():
        if char.lower() in sentence.lower():
            # Protagonist mentions are most important
            if role == 'protagonist':
                score += 0.3
            elif role in ['antagonist', 'guide']:
                score += 0.2
            else:
                score += 0.1
    
    return min(score, 1.0)

def score_action_content(sentence):
    """Score: 0-1 based on action/narrative content"""
    score = 0
    
    # Action verbs
    for verb in ACTION_VERBS:
        if verb in sentence.lower():
            score += 0.15
    
    # Narrative markers
    narrative_markers = ['suddenly', 'then', 'soon', 'meanwhile', 'however', 'next']
    for marker in narrative_markers:
        if marker in sentence.lower():
            score += 0.1
    
    # Dialogue (often important)
    if '"' in sentence or "'" in sentence:
        score += 0.2
    
    # Questions (often crucial moments)
    if '?' in sentence:
        score += 0.15
    
    # Exclamations (emotional peaks)
    if '!' in sentence:
        score += 0.1
    
    return min(score, 1.0)

def score_concept_content(sentence):
    """Score: 0-1 based on key concept mentions"""
    score = 0
    
    for concept in KEY_CONCEPTS:
        if concept in sentence.lower():
            score += 0.08
    
    return min(score, 1.0)

def score_transformation(sentence):
    """Score: 0-1 for growth/change/transformation"""
    transform_words = [
        'grew', 'shrunk', 'changed', 'became', 'transform', 'changed',
        'realized', 'understood', 'learned', 'discovered', 'awakened'
    ]
    
    score = 0
    for word in transform_words:
        if word in sentence.lower():
            score += 0.2
    
    return min(score, 1.0)

def score_length_and_substance(sentence):
    """Score: longer, more complex sentences tend to be more important"""
    word_count = len(sentence.split())
    
    # Optimal range: 15-40 words
    if 15 <= word_count <= 40:
        return 0.3
    elif 40 < word_count <= 60:
        return 0.25
    elif word_count > 60:
        return 0.2
    else:
        return 0.1

def calculate_surprise_v2(sentence, full_text):
    """Better surprise: how unique are the word patterns?"""
    words = set(sentence.lower().split())
    full_words = set(full_text.lower().split())
    
    unique_ratio = len(words - full_words) / (len(words) + 0.1)
    
    # Inverse: more unique = higher surprise
    return min(unique_ratio * 2, 1.0)

def calculate_importance_v2(sentence, full_text, all_sentences, position):
    """Improved importance calculation"""
    
    # Component scores (all 0-1)
    character_score = score_character_mention(sentence)
    action_score = score_action_content(sentence)
    concept_score = score_concept_content(sentence)
    transform_score = score_transformation(sentence)
    length_score = score_length_and_substance(sentence)
    surprise_score = calculate_surprise_v2(sentence, full_text)
    
    # Surprise dominates (0.60)
    s = surprise_score
    
    # Relevance = combination of action, character, concept, transformation
    r = (action_score + character_score + concept_score + transform_score) / 4.0
    
    # Decay = position in narrative (later = more recent understanding)
    d = 0.3 + (position / len(all_sentences)) * 0.7
    
    # Habituation = inverse of length score (common patterns less important)
    h = 1.0 - (length_score * 0.3)
    
    # Apply weights
    importance = (
        WEIGHTS['surprise'] * s +
        WEIGHTS['relevance'] * r +
        WEIGHTS['decay'] * d +
        WEIGHTS['habituation'] * h
    )
    
    return max(0.0, min(1.0, importance))

def compress_at_threshold(facts, threshold):
    """Keep facts above threshold"""
    return [f for f in facts if f.get('importance', 0) >= threshold]

def reconstruct_narrative(facts, max_length=500):
    """Reconstruct narrative from compressed facts"""
    # Sort by position in original text
    sorted_facts = sorted(facts, key=lambda f: f.get('position', 0))
    
    narrative = ""
    for fact in sorted_facts[:30]:  # Show top 30
        narrative += fact['content'] + " "
        if len(narrative) > max_length:
            break
    
    return narrative.strip()

def calculate_semantic_similarity(original_text, reconstructed_text):
    """Simple similarity: word overlap"""
    orig_words = set(original_text.lower().split())
    recon_words = set(reconstructed_text.lower().split())
    
    if not orig_words:
        return 0.0
    
    overlap = len(orig_words & recon_words)
    return overlap / len(orig_words)

# === MAIN TEST ===

def run_test():
    """Run the improved test"""
    
    print("\n" + "="*80)
    print("SIF COMPRESSION TEST v2: Alice in Wonderland")
    print("Improved Importance Calculation")
    print("="*80 + "\n")
    
    # Fetch
    print("Step 1: Fetching Alice...")
    alice_text = fetch_alice()
    original_bytes = len(alice_text.encode('utf-8'))
    
    print(f"  ✓ Loaded: {len(alice_text):,} characters")
    print(f"  ✓ Size: {original_bytes:,} bytes")
    print(f"  ✓ Words: {len(alice_text.split()):,}")
    
    # Extract
    print("\nStep 2: Extracting sentences...")
    sentences = extract_sentences(alice_text)
    print(f"  ✓ Extracted: {len(sentences)} sentences")
    
    # Calculate importance
    print("\nStep 3: Calculating importance (improved)...")
    facts = []
    
    for i, sentence in enumerate(sentences):
        importance = calculate_importance_v2(sentence, alice_text, sentences, i)
        facts.append({
            'id': f'fact_{i}',
            'content': sentence,
            'position': i,
            'importance': importance,
            'length': len(sentence)
        })
    
    print(f"  ✓ Calculated importance for {len(facts)} facts")
    
    # Statistics
    importances = [f['importance'] for f in facts]
    print(f"\nImportance distribution:")
    print(f"  Min: {min(importances):.3f}")
    print(f"  Max: {max(importances):.3f}")
    print(f"  Mean: {np.mean(importances):.3f}")
    print(f"  Median: {np.median(importances):.3f}")
    print(f"  Std Dev: {np.std(importances):.3f}")
    
    # Show top facts
    print(f"\nTop 10 most important facts:")
    sorted_facts = sorted(facts, key=lambda f: f['importance'], reverse=True)
    for i, fact in enumerate(sorted_facts[:10], 1):
        print(f"  {i}. [{fact['importance']:.3f}] {fact['content'][:70]}...")
    
    # Compression test
    print("\n" + "="*80)
    print("COMPRESSION RESULTS AT DIFFERENT THRESHOLDS")
    print("="*80 + "\n")
    
    results = {}
    
    for tier_num, tier_info in sorted(COMPRESSION_TIERS.items()):
        threshold = tier_info['threshold']
        tier_name = tier_info['name']
        
        print(f"\n📊 TIER {tier_num}: {tier_name} (≥ {threshold:.2f})")
        print("-" * 75)
        
        # Compress
        compressed = compress_at_threshold(facts, threshold)
        
        # Build SIF JSON
        sif_data = {
            'version': '1.0.0',
            'threshold': threshold,
            'facts': [{'content': f['content'], 'importance': f['importance']} 
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
            avg_length_preserved = np.mean([f['length'] for f in compressed])
            
            # Lossiness: (1 - facts_preserved) weighted by importance
            dropped = [f for f in facts if f not in compressed]
            avg_dropped_importance = np.mean([f['importance'] for f in dropped]) if dropped else 0
            
            lossiness = (1 - facts_preserved) * (1 - avg_importance / (avg_importance + avg_dropped_importance + 0.01))
            quality_score = (facts_preserved * 0.4 + avg_importance * 0.6) * 100
        else:
            avg_importance = 0
            lossiness = 1.0
            quality_score = 0
        
        # Reconstruct and measure similarity
        narrative = reconstruct_narrative(compressed)
        semantic_sim = calculate_semantic_similarity(alice_text, narrative) if narrative else 0
        
        print(f"Original:            {original_bytes:>10,} bytes")
        print(f"SIF Size:            {sif_bytes:>10,} bytes")
        print(f"Compression:         {compression_ratio:>10.1f}x")
        print(f"Saved:               {bytes_saved:>10,} bytes ({percent_saved:>5.1f}%)")
        
        print(f"\nFacts preserved:     {len(compressed):>10} / {len(facts)} ({facts_preserved*100:>5.1f}%)")
        print(f"Avg importance:      {avg_importance:>10.3f}")
        print(f"Information loss:    {lossiness*100:>10.1f}%")
        print(f"Quality score:       {quality_score:>10.1f} / 100")
        print(f"Semantic sim:        {semantic_sim*100:>10.1f}%")
        
        results[tier_num] = {
            'threshold': threshold,
            'name': tier_name,
            'compression_ratio': compression_ratio,
            'bytes': sif_bytes,
            'facts_preserved': facts_preserved,
            'facts_count': len(compressed),
            'avg_importance': avg_importance,
            'lossiness': lossiness,
            'quality_score': quality_score,
            'semantic_similarity': semantic_sim,
            'bytes_saved': bytes_saved
        }
    
    # Summary table
    print("\n" + "="*80)
    print("GRADIENT SUMMARY TABLE")
    print("="*80 + "\n")
    
    print(f"{'Tier':<20} {'Threshold':<12} {'Ratio':<8} {'Facts':<8} {'Loss':<8} {'Quality':<10}")
    print("-" * 75)
    
    for tier_num in sorted(results.keys()):
        r = results[tier_num]
        print(f"{r['name']:<20} {r['threshold']:<12.2f} {r['compression_ratio']:<8.1f}x "
              f"{r['facts_count']:<8} {r['lossiness']*100:<8.1f}% {r['quality_score']:<10.1f}")
    
    # Analysis
    print("\n" + "="*80)
    print("ANALYSIS: The 0.60 Threshold")
    print("="*80 + "\n")
    
    tier2 = results[2]  # Standard (0.60)
    tier1 = results[1]  # Critical (0.75)
    tier3 = results[3]  # Enhanced (0.50)
    tier4 = results[4]  # Aggressive (0.30)
    
    print(f"At the GOLDEN RATIO (0.60):")
    print(f"  • Compression: {tier2['compression_ratio']:.1f}x")
    print(f"  • Facts kept: {tier2['facts_count']} ({tier2['facts_preserved']*100:.1f}%)")
    print(f"  • Quality: {tier2['quality_score']:.0f}/100")
    print(f"  • Information loss: {tier2['lossiness']*100:.1f}%")
    print(f"  • Semantic similarity: {tier2['semantic_similarity']*100:.1f}%")
    
    print(f"\n Compared to Critical (0.75):")
    ratio_improvement = tier2['compression_ratio'] / tier1['compression_ratio']
    quality_diff = tier2['quality_score'] - tier1['quality_score']
    print(f"  • {ratio_improvement:.2f}x better compression")
    print(f"  • Quality difference: {quality_diff:+.1f} points")
    
    print(f"\nCompared to Enhanced (0.50):")
    ratio_diff = tier3['compression_ratio'] / tier2['compression_ratio']
    quality_gain = tier3['quality_score'] - tier2['quality_score']
    print(f"  • Trade off: {ratio_diff:.2f}x more compression for {quality_gain:+.1f} quality points")
    
    print(f"\nCompared to Aggressive (0.30):")
    ratio_gain = tier4['compression_ratio'] / tier2['compression_ratio']
    quality_loss = tier4['quality_score'] - tier2['quality_score']
    print(f"  • {ratio_gain:.2f}x more compression, but {quality_loss:+.1f} quality points")
    
    # Save
    print("\n" + "="*80)
    results_file = '/home/luna/Code/ada-v1/experiments/sif_compression_alice_v2_results.json'
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'document': 'Alice in Wonderland (26K words)',
            'original_bytes': original_bytes,
            'total_facts': len(facts),
            'importance_stats': {
                'min': float(min(importances)),
                'max': float(max(importances)),
                'mean': float(np.mean(importances)),
                'median': float(np.median(importances)),
                'std': float(np.std(importances))
            },
            'tiers': results
        }, f, indent=2)
    
    print(f"✓ Results saved: {results_file}")
    
    return results

if __name__ == '__main__':
    run_test()
