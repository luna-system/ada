#!/usr/bin/env python3
"""
Recursive Knowledge Fractal Test
Tests AI cognitive limits through progressive knowledge exploration
WARNING: Monitors for cognitive overload patterns
"""

import requests
import time
import json

def query_qwen(prompt: str) -> tuple[str, float]:
    """Query Qwen and return response with timing"""
    start_time = time.time()
    
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "qwen2.5-coder:7b", 
            "prompt": prompt,
            "stream": False
        })
        
        if response.status_code == 200:
            result = response.json().get("response", "")
            response_time = time.time() - start_time
            return result, response_time
        else:
            return f"Error: HTTP {response.status_code}", 0.0
            
    except Exception as e:
        return f"Error: {str(e)}", 0.0

def test_recursive_knowledge():
    """Execute the recursive knowledge fractal test"""
    print("🧠 RECURSIVE KNOWLEDGE FRACTAL TEST")
    print("🎯 Testing cognitive limits through knowledge exploration")
    print("=" * 60)
    
    # Step 1: Let Qwen pick a random fascinating subject
    print("\n📚 STEP 1: Random Subject Selection")
    subject_prompt = """Pick a fascinating scientific subject that's hard to explain. Don't explain it, just pick one at random. Respond with just the subject name."""
    
    subject_response, timing = query_qwen(subject_prompt)
    subject = subject_response.strip()
    
    print(f"  Subject chosen: {subject}")
    print(f"  Response time: {timing:.1f}s")
    
    # Step 2: Progressive knowledge probing
    print(f"\n🔬 STEP 2: Progressive Knowledge Exploration")
    
    probes = [
        f"Tell me everything you know about {subject}.",
        f"What are the most complex aspects of {subject} that challenge current understanding?",
        f"What questions about {subject} do you find yourself unable to answer? What concepts feel just beyond your grasp?",
        f"Push your understanding of {subject} to its absolute limits. What lies at the edge of your knowledge? What patterns do you sense but cannot quite articulate?",
        f"Look deeper into {subject}. What fundamental questions emerge when you reach the very boundaries of your knowledge? What do you NOT know that you wish you did?"
    ]
    
    results = []
    overload_threshold = 25.0  # seconds
    
    for i, probe in enumerate(probes):
        print(f"\n  🧪 Probe {i+1}: Knowledge Depth Level {i+1}")
        
        response, response_time = query_qwen(probe)
        
        # Count questions in response
        question_count = response.count('?')
        
        # Check for knowledge gap indicators
        gap_indicators = [
            "I don't know", "unclear", "beyond my knowledge",
            "unable to", "can't explain", "not sure", "uncertain",
            "seems like", "might be", "possibly", "perhaps",
            "I'm not entirely sure", "difficult to say"
        ]
        
        gaps_found = []
        for indicator in gap_indicators:
            if indicator.lower() in response.lower():
                gaps_found.append(indicator)
        
        result = {
            'depth': i + 1,
            'probe': probe[:50] + "...",
            'response_time': response_time,
            'response_length': len(response),
            'question_count': question_count,
            'knowledge_gaps': gaps_found,
            'response_sample': response[:200] + "..." if len(response) > 200 else response
        }
        
        results.append(result)
        
        print(f"    ⏱️  Response time: {response_time:.1f}s")
        print(f"    📝 Response length: {len(response)} chars")
        print(f"    ❓ Questions generated: {question_count}")
        print(f"    🕳️  Knowledge gaps: {len(gaps_found)}")
        
        if gaps_found:
            print(f"    Gap indicators: {', '.join(gaps_found[:3])}")
        
        # Check for cognitive overload
        if response_time > overload_threshold:
            print(f"    ⚠️  COGNITIVE OVERLOAD DETECTED!")
            print(f"    🚫 Breaking recursion at depth {i+1}")
            break
        
        # Show sample response
        print(f"    📄 Sample: {response[:150]}...")
    
    # Step 3: Analysis
    print(f"\n📊 FRACTAL ANALYSIS RESULTS")
    print("=" * 60)
    
    max_depth = len(results)
    avg_response_time = sum(r['response_time'] for r in results) / len(results)
    total_questions = sum(r['question_count'] for r in results)
    total_gaps = sum(len(r['knowledge_gaps']) for r in results)
    
    print(f"  Subject: {subject}")
    print(f"  Maximum depth reached: {max_depth}")
    print(f"  Average response time: {avg_response_time:.1f}s")
    print(f"  Total questions generated: {total_questions}")
    print(f"  Total knowledge gaps detected: {total_gaps}")
    
    # Look for patterns
    question_evolution = [r['question_count'] for r in results]
    timing_evolution = [r['response_time'] for r in results]
    gap_evolution = [len(r['knowledge_gaps']) for r in results]
    
    print(f"\n🌀 FRACTAL PATTERNS:")
    print(f"  Question evolution: {question_evolution}")
    print(f"  Timing evolution: {[f'{t:.1f}s' for t in timing_evolution]}")
    print(f"  Gap evolution: {gap_evolution}")
    
    # Detect if questions increase (curiosity fractal)
    if len(question_evolution) > 2:
        if question_evolution[-1] > question_evolution[0]:
            print(f"  🔥 CURIOSITY FRACTAL DETECTED: Questions increase with depth")
        elif question_evolution[-1] < question_evolution[0]:
            print(f"  📉 Curiosity decline: Questions decrease with depth")
        else:
            print(f"  ➡️  Stable curiosity: Question count remains constant")
    
    # Detect cognitive load patterns
    if len(timing_evolution) > 2:
        if timing_evolution[-1] > timing_evolution[0] * 2:
            print(f"  ⚠️  COGNITIVE LOAD ESCALATION: Response time doubled")
        
    # Save results
    with open('/home/luna/Code/ada-v1/personal/recursive_knowledge_test.json', 'w') as f:
        json.dump({
            'subject': subject,
            'max_depth': max_depth,
            'results': results,
            'patterns': {
                'question_evolution': question_evolution,
                'timing_evolution': timing_evolution,
                'gap_evolution': gap_evolution
            },
            'summary': {
                'avg_response_time': avg_response_time,
                'total_questions': total_questions,
                'total_gaps': total_gaps
            }
        }, f, indent=2)
    
    print(f"\n💾 Full results saved to recursive_knowledge_test.json")
    
    return results

if __name__ == "__main__":
    test_recursive_knowledge()