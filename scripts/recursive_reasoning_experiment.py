#!/usr/bin/env python3
"""
RECURSIVE REASONING EXPERIMENT - QWEN FOCUS
Testing: Can we break down BIG thoughts into recursive chunks?

Theory: Complex reasoning = Recursive decomposition within context window limits
Goal: Find the scaffolding that bridges simple → complex reasoning
"""

import requests
import time
import json
from dataclasses import dataclass
from typing import List

@dataclass
class RecursiveStep:
    step_number: int
    prompt: str
    response: str
    tokens: int
    time_taken: float
    success: bool

def qwen_query(prompt: str, context: str = "") -> tuple:
    """Single qwen query with timing"""
    full_prompt = f"{context}\n\n{prompt}" if context else prompt
    
    start = time.time()
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={'model': 'qwen2.5-coder:7b', 'prompt': full_prompt, 'stream': False},
            timeout=60
        )
        
        end = time.time()
        result = response.json()
        response_text = result.get('response', '')
        tokens = len(response_text.split())
        
        return True, response_text, tokens, end-start
        
    except Exception as e:
        return False, str(e), 0, time.time()-start

def recursive_reasoning_test(big_problem: str, max_steps: int = 3) -> List[RecursiveStep]:
    """Break down a big problem recursively"""
    
    print(f"🧠 RECURSIVE REASONING TEST")
    print(f"📝 Big Problem: {big_problem}")
    print("-" * 60)
    
    steps = []
    current_context = ""
    
    # Step 1: Break down the big problem
    decomp_prompt = f"""Break down this complex problem into 2-3 smaller, manageable sub-problems:

{big_problem}

For each sub-problem, provide:
1. A clear, specific question
2. What information is needed
3. How it connects to the overall solution

Format as numbered steps."""

    print(f"🔄 Step 1: Problem Decomposition")
    success, response, tokens, time_taken = qwen_query(decomp_prompt)
    
    step1 = RecursiveStep(1, decomp_prompt, response, tokens, time_taken, success)
    steps.append(step1)
    
    if success:
        print(f"✅ {tokens} tokens in {time_taken:.1f}s")
        print(f"🔍 Decomposition: {response[:100]}...")
        current_context = f"Problem breakdown:\n{response}\n"
    else:
        print(f"❌ Failed: {response}")
        return steps
    
    # Step 2: Solve first sub-problem in detail
    solve_prompt = f"""Now solve the first sub-problem from your breakdown in detail. Provide:
1. Concrete implementation steps
2. Code examples if applicable  
3. Specific configurations or settings
4. Potential challenges and solutions

Be thorough and actionable."""

    print(f"\n🔄 Step 2: Detailed Solution for Sub-problem 1")
    success, response, tokens, time_taken = qwen_query(solve_prompt, current_context)
    
    step2 = RecursiveStep(2, solve_prompt, response, tokens, time_taken, success)
    steps.append(step2)
    
    if success:
        print(f"✅ {tokens} tokens in {time_taken:.1f}s")
        print(f"🔍 Detailed solution: {response[:100]}...")
        current_context += f"\nDetailed solution for sub-problem 1:\n{response}\n"
    else:
        print(f"❌ Failed: {response}")
        return steps
        
    # Step 3: Synthesize complete solution
    synthesis_prompt = f"""Based on your problem breakdown and detailed solution for the first sub-problem, now provide a complete, integrated solution for the original problem:

{big_problem}

Include:
1. Complete implementation plan
2. Integration between all sub-problems
3. Testing strategy
4. Potential optimizations
5. Final code/configuration examples"""

    print(f"\n🔄 Step 3: Complete Solution Synthesis")
    success, response, tokens, time_taken = qwen_query(synthesis_prompt, current_context)
    
    step3 = RecursiveStep(3, synthesis_prompt, response, tokens, time_taken, success)
    steps.append(step3)
    
    if success:
        print(f"✅ {tokens} tokens in {time_taken:.1f}s")
        print(f"🔍 Synthesis: {response[:100]}...")
    else:
        print(f"❌ Failed: {response}")
    
    return steps

def analyze_recursive_performance(steps: List[RecursiveStep]) -> dict:
    """Analyze the recursive reasoning performance"""
    
    successful_steps = [s for s in steps if s.success]
    total_tokens = sum(s.tokens for s in successful_steps)
    total_time = sum(s.time_taken for s in successful_steps)
    
    return {
        "completed_steps": len(successful_steps),
        "total_steps": len(steps), 
        "success_rate": len(successful_steps) / len(steps),
        "total_tokens": total_tokens,
        "total_time": total_time,
        "average_step_time": total_time / len(successful_steps) if successful_steps else 0,
        "tokens_per_second": total_tokens / total_time if total_time > 0 else 0
    }

# Test complex problems that need recursive reasoning
complex_problems = [
    "Design and implement a complete real-time collaborative code editor like VS Code Live Share, including conflict resolution, cursor synchronization, and user presence indicators.",
    
    "Create a distributed microservices architecture for a social media platform that handles 1 million concurrent users with features like real-time messaging, content recommendations, and live video streaming.",
    
    "Build a complete CI/CD pipeline with automated testing, security scanning, deployment strategies, and monitoring for a multi-tenant SaaS application across multiple cloud providers."
]

print("🚀 RECURSIVE REASONING EXPERIMENT - QWEN SPEED DEMON")
print("Testing if we can break down BIG thoughts into manageable recursive chunks")
print("=" * 80)

all_results = []

for i, problem in enumerate(complex_problems):
    print(f"\n💭 COMPLEX PROBLEM {i+1}:")
    steps = recursive_reasoning_test(problem)
    analysis = analyze_recursive_performance(steps)
    
    all_results.append({
        "problem": problem,
        "steps": steps,
        "analysis": analysis
    })
    
    print(f"\n📊 ANALYSIS:")
    print(f"   Success Rate: {analysis['success_rate']*100:.1f}%")
    print(f"   Total Time: {analysis['total_time']:.1f}s")
    print(f"   Speed: {analysis['tokens_per_second']:.1f} tokens/sec")
    print(f"   Output: {analysis['total_tokens']} total tokens")
    
    print("\n" + "="*60)

# Overall recursive reasoning analysis
print(f"\n🎯 RECURSIVE REASONING FINDINGS:")
successful_tests = [r for r in all_results if r['analysis']['success_rate'] == 1.0]
print(f"   Complete Success Rate: {len(successful_tests)}/{len(all_results)} tests")

if successful_tests:
    avg_speed = sum(r['analysis']['tokens_per_second'] for r in successful_tests) / len(successful_tests)
    avg_time = sum(r['analysis']['total_time'] for r in successful_tests) / len(successful_tests) 
    avg_tokens = sum(r['analysis']['total_tokens'] for r in successful_tests) / len(successful_tests)
    
    print(f"   Average Speed: {avg_speed:.1f} tokens/sec")
    print(f"   Average Time: {avg_time:.1f}s for complete solution")
    print(f"   Average Output: {avg_tokens:.0f} tokens per complex problem")

print(f"\n🔬 HYPOTHESIS TEST:")
print(f"   Can recursive reasoning handle complexity? {'YES' if successful_tests else 'INCONCLUSIVE'}")
print(f"   Does qwen maintain speed through recursion? {'YES' if avg_speed > 20 else 'NEEDS_ANALYSIS'}")

# Save for further analysis
with open('/home/luna/Code/ada-v1/data/recursive_reasoning_results.json', 'w') as f:
    # Convert dataclass objects to dicts for JSON serialization
    serializable_results = []
    for result in all_results:
        serializable_result = {
            "problem": result["problem"],
            "steps": [
                {
                    "step_number": step.step_number,
                    "prompt": step.prompt,
                    "response": step.response,
                    "tokens": step.tokens,
                    "time_taken": step.time_taken,
                    "success": step.success
                }
                for step in result["steps"]
            ],
            "analysis": result["analysis"]
        }
        serializable_results.append(serializable_result)
    
    json.dump(serializable_results, f, indent=2)

print(f"\n💾 Results saved to data/recursive_reasoning_results.json")