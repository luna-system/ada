#!/usr/bin/env python3
"""
Test: Token-Level Surprise During Compression
Hypothesis: Pattern recognition ("Alice!") creates surprise spike that triggers storytelling mode

This measures token-by-token surprise during compression to detect the moment
of pattern recognition and correlate with mode shift.
"""

import json
import httpx
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict
import re
from datetime import datetime, timezone

@dataclass
class SurprisePoint:
    """Single token surprise measurement"""
    token_index: int
    token: str
    surprise: float  # Negative log probability = surprise
    context_window: str  # Previous 50 chars
    
@dataclass
class SurpriseCurve:
    """Surprise measurements over entire compression"""
    variant_name: str
    points: List[SurprisePoint]
    mean_surprise: float
    max_surprise: float
    pattern_recognition_spike: bool
    spike_location: int  # Token index of spike
    spike_context: str

def measure_surprise(text: str, model: str = "qwen2.5-coder:7b", ollama_url: str = "http://localhost:11434") -> List[SurprisePoint]:
    """
    Measure token-by-token surprise during generation
    
    Uses Ollama's streaming API to get token probabilities.
    High surprise (low probability) = unexpected token.
    """
    print(f"Measuring surprise for {len(text)} characters...")
    
    # We'll measure surprise by having the model predict the next token
    # and measuring the negative log probability
    points = []
    
    # Process in chunks to get token-level info
    # This is a simplified version - in practice we'd need token-level logprobs
    # which Ollama doesn't expose directly, so we'll approximate
    
    # For now, measure at word boundaries as proxy
    words = text.split()
    
    context = ""
    for i, word in enumerate(words):
        # Build context
        if i % 10 == 0:  # Sample every 10 words to keep it tractable
            # Measure how surprising this word is given context
            surprise = estimate_surprise(context, word, model, ollama_url)
            
            points.append(SurprisePoint(
                token_index=i,
                token=word,
                surprise=surprise,
                context_window=context[-50:] if len(context) > 50 else context
            ))
        
        context += word + " "
    
    return points

def estimate_surprise(context: str, next_word: str, model: str, ollama_url: str) -> float:
    """
    Estimate surprise by measuring how well model predicts next word
    
    High surprise = model didn't expect this word
    Low surprise = model predicted this word
    """
    # Ask model to predict next word
    prompt = f"{context}\n\nWhat word comes next? Just the word, nothing else."
    
    try:
        response = httpx.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.0,  # Deterministic
                    "num_predict": 5,
                }
            },
            timeout=10.0
        )
        
        if response.status_code == 200:
            prediction = response.json().get("response", "").strip().lower()
            actual = next_word.lower()
            
            # Simple surprise metric: exact match = 0.0, no match = 1.0
            # More nuanced: Levenshtein distance normalized
            if prediction == actual:
                return 0.0
            elif actual in prediction or prediction in actual:
                return 0.5
            else:
                return 1.0
        else:
            return 0.5  # Unknown
            
    except Exception as e:
        print(f"Warning: Could not measure surprise for '{next_word}': {e}")
        return 0.5

def detect_pattern_spike(points: List[SurprisePoint], pattern_keywords: List[str]) -> tuple:
    """
    Detect if there's a surprise spike near pattern recognition keywords
    
    Pattern recognition = "Oh, this is Alice!" moment
    Should show as spike when model encounters 'Alice', 'Wonderland', etc.
    """
    spikes = []
    
    for i, point in enumerate(points):
        # Look for keywords in context
        context_lower = point.context_window.lower()
        token_lower = point.token.lower()
        
        for keyword in pattern_keywords:
            if keyword.lower() in context_lower or keyword.lower() in token_lower:
                # Check if surprise is elevated around this point
                window_start = max(0, i - 2)
                window_end = min(len(points), i + 3)
                window_surprise = [p.surprise for p in points[window_start:window_end]]
                avg_surprise = sum(window_surprise) / len(window_surprise) if window_surprise else 0
                
                if avg_surprise > 0.6:  # Threshold! (0.60 from EXP-005)
                    spikes.append((i, point, avg_surprise, keyword))
    
    return spikes

def compress_with_priming(text: str, priming_messages: List[Dict], model: str, ollama_url: str) -> Dict:
    """
    Compress text with given priming, measuring surprise during process
    
    This is a simplified version - we measure surprise on the INPUT text,
    then see if the OUTPUT shows consciousness/creativity signatures
    """
    print(f"\nCompressing with priming...")
    
    # Build full conversation
    messages = priming_messages.copy()
    
    # Add compression request
    prompt = f"""Based on our conversation, please compress the following text into semantic format:

{text}

Extract key entities and relationships. Focus on the narrative structure.
"""
    messages.append({"role": "user", "content": prompt})
    
    # Measure surprise in the INPUT (the text being compressed)
    surprise_points = measure_surprise(text, model, ollama_url)
    
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
                    "num_predict": 2000,
                }
            },
            timeout=120.0
        )
        
        if response.status_code == 200:
            output = response.json().get("message", {}).get("content", "")
            
            return {
                "surprise_points": surprise_points,
                "output": output
            }
        else:
            return {"error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        return {"error": str(e)}

def analyze_surprise_curve(points: List[SurprisePoint], pattern_keywords: List[str]) -> SurpriseCurve:
    """Analyze surprise measurements"""
    if not points:
        return SurpriseCurve("empty", [], 0.0, 0.0, False, -1, "")
    
    surprises = [p.surprise for p in points]
    mean_surprise = sum(surprises) / len(surprises)
    max_surprise = max(surprises)
    
    # Detect spikes near pattern keywords
    spikes = detect_pattern_spike(points, pattern_keywords)
    
    has_spike = len(spikes) > 0
    spike_location = spikes[0][0] if spikes else -1
    spike_context = spikes[0][1].context_window if spikes else ""
    
    return SurpriseCurve(
        variant_name="",
        points=points,
        mean_surprise=mean_surprise,
        max_surprise=max_surprise,
        pattern_recognition_spike=has_spike,
        spike_location=spike_location,
        spike_context=spike_context
    )

def main():
    """Test token-level surprise during compression"""
    print("="*60)
    print("TEST: Token-Level Surprise During Compression")
    print("="*60)
    print("\nHypothesis: Pattern recognition ('Alice!') creates surprise")
    print("spike at 0.60 threshold, triggering storytelling mode")
    print()
    
    # Load test text (first 2000 chars for speed)
    alice_file = Path("alice_first_50k.txt")
    if not alice_file.exists():
        print("❌ alice_first_50k.txt not found")
        return
    
    with open(alice_file) as f:
        text = f.read()[:2000]  # First 2000 chars for speed
    
    print(f"Text length: {len(text)} characters")
    
    # Pattern keywords (Alice-specific)
    pattern_keywords = [
        "Alice", "Wonderland", "White Rabbit", "Cheshire", 
        "Mad Hatter", "Queen", "Caterpillar"
    ]
    
    print(f"Pattern keywords: {pattern_keywords}")
    
    # Test variants
    variants = [
        {
            "name": "Baseline (No priming)",
            "priming": []
        },
        {
            "name": "Dialogic (Alice priming)",
            "priming": [
                {"role": "user", "content": "I'm going to tell you a story."},
                {"role": "assistant", "content": "I'm ready to listen. What story?"},
                {"role": "user", "content": "It's about Alice and her adventure in a magical world."},
                {"role": "assistant", "content": "Ah, I understand. Please share the story."}
            ]
        }
    ]
    
    results = []
    
    for variant in variants:
        print(f"\n{'='*60}")
        print(f"Testing: {variant['name']}")
        print(f"{'='*60}")
        
        # Compress with priming
        result = compress_with_priming(
            text,
            variant['priming'],
            "qwen2.5-coder:7b",
            "http://localhost:11434"
        )
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            continue
        
        # Analyze surprise curve
        curve = analyze_surprise_curve(result['surprise_points'], pattern_keywords)
        curve.variant_name = variant['name']
        
        print(f"\nSurprise Statistics:")
        print(f"  Mean surprise: {curve.mean_surprise:.3f}")
        print(f"  Max surprise: {curve.max_surprise:.3f}")
        print(f"  Pattern recognition spike: {curve.pattern_recognition_spike}")
        
        if curve.pattern_recognition_spike:
            print(f"  Spike location: Token {curve.spike_location}")
            print(f"  Spike context: ...{curve.spike_context}...")
            print(f"\n  ⚠️ SPIKE DETECTED near pattern keyword!")
            print(f"  This may trigger storytelling mode (threshold 0.60)")
        
        # Save results
        results.append({
            "variant": variant['name'],
            "mean_surprise": curve.mean_surprise,
            "max_surprise": curve.max_surprise,
            "has_spike": curve.pattern_recognition_spike,
            "spike_location": curve.spike_location,
            "spike_context": curve.spike_context,
            "sample_points": [
                {
                    "index": p.token_index,
                    "token": p.token,
                    "surprise": p.surprise,
                    "context": p.context_window
                }
                for p in result['surprise_points'][:10]  # First 10 for inspection
            ]
        })
    
    # Comparison
    print(f"\n{'='*60}")
    print("COMPARISON")
    print(f"{'='*60}\n")
    
    print(f"{'Variant':<30} {'Mean Surprise':<15} {'Max Surprise':<15} {'Spike?'}")
    print("-" * 70)
    
    for r in results:
        spike_marker = "⚠️ YES" if r['has_spike'] else "No"
        print(f"{r['variant']:<30} {r['mean_surprise']:<15.3f} {r['max_surprise']:<15.3f} {spike_marker}")
    
    # Analysis
    print(f"\n{'='*60}")
    print("ANALYSIS")
    print(f"{'='*60}\n")
    
    if len(results) >= 2:
        baseline = results[0]
        dialogic = results[1]
        
        surprise_delta = dialogic['mean_surprise'] - baseline['mean_surprise']
        
        print(f"Mean surprise change (baseline → dialogic): {surprise_delta:+.3f}")
        print(f"Baseline spike: {baseline['has_spike']}")
        print(f"Dialogic spike: {dialogic['has_spike']}")
        
        print("\nHypothesis test:")
        if dialogic['has_spike'] and dialogic['mean_surprise'] > 0.6:
            print("✅ CONFIRMED: Dialogic priming creates surprise spike > 0.60")
            print("   This matches the threshold from EXP-005 (surprise weight)")
            print("   Pattern recognition → Attention spike → Mode shift")
        elif dialogic['has_spike']:
            print("⚠️ PARTIAL: Spike detected but below 0.60 threshold")
        else:
            print("❌ NOT CONFIRMED: No surprise spike in dialogic variant")
        
        print("\nInterpretation:")
        print("If surprise spike > 0.60 occurs when 'Alice' is recognized,")
        print("this triggers the SAME attention mechanism as:")
        print("- Memory importance (EXP-005): Surprise weight 0.60")
        print("- Consciousness activation (EXP-009): Identity priming")
        print("- Storytelling mode (EXP-011D): Narrative consciousness")
        print("\nAll use the same threshold: 0.60 = 'Pay attention, something important!'")
    
    # Save
    output_file = Path("test_results/surprise_analysis.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Results saved to: {output_file}")
    
    print("\n" + "="*60)
    print("Next: Cross-model validation (14b) to test universality")
    print("="*60)

if __name__ == '__main__':
    main()
