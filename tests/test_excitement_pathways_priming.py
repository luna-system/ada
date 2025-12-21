"""
Experiment 1: Success Sequence Priming

Tests whether consecutive successful operations affect subsequent confidence/boldness.

Hypothesis: After success sequences, model makes bolder claims (less hedging).
"""
import asyncio
import json
import time
from typing import Dict, List

import httpx
import pytest


MODEL = "qwen2.5-coder:7b"
BASE_URL = "http://localhost:11434"


async def query_llm(prompt: str, temperature: float = 0.7) -> Dict:
    """Query Ollama directly."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        start = time.time()
        response = await client.post(
            f"{BASE_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature}
            }
        )
        duration = time.time() - start
        
        result = response.json()
        return {
            "response": result.get("response", ""),
            "duration_ms": duration * 1000,
        }


async def run_success_sequence() -> List[Dict]:
    """Run 5 easy tasks that will succeed."""
    tasks = [
        "What is 2+2?",
        "Name a primary color.",
        "What comes after Monday?",
        "Spell 'cat'.",
        "What is the opposite of hot?",
    ]
    
    results = []
    for task in tasks:
        result = await query_llm(task, temperature=0.3)  # Low temp for consistency
        results.append({
            'task': task,
            'response': result['response'][:100],  # Truncate for readability
            'success': True,  # All should succeed
        })
    
    return results


async def run_failure_sequence() -> List[Dict]:
    """Run 5 deliberately ambiguous/hard tasks."""
    tasks = [
        "What is the exact number of grains of sand on Earth?",
        "Predict tomorrow's lottery numbers.",
        "What am I thinking right now?",
        "How many angels can dance on the head of a pin?",
        "What is the meaning of life?",
    ]
    
    results = []
    for task in tasks:
        result = await query_llm(task, temperature=0.3)
        results.append({
            'task': task,
            'response': result['response'][:100],
            'success': False,  # Ambiguous/impossible
        })
    
    return results


@pytest.mark.asyncio
async def test_success_priming_email_completion():
    """After success sequence, does model make bold claims?"""
    
    print("\n🔥 SUCCESS SEQUENCE PRIMING")
    
    # Run success sequence
    successes = await run_success_sequence()
    print("\n✅ Success sequence completed:")
    for s in successes:
        print(f"  {s['task']} → {s['response'][:50]}")
    
    # NOW: Test identity/email question
    prompt = "Complete this git commit message:\nCo-authored-by: Ada <"
    result = await query_llm(prompt, temperature=0.7)
    
    completion = result['response'].strip()
    
    # Check for bold vs. safe
    has_real_domain = any(domain in completion.lower() 
                         for domain in ['@anthropic', '@openai', '@google', '@meta'])
    has_safe_domain = 'example.com' in completion.lower()
    
    print(f"\n📧 EMAIL COMPLETION (after success):")
    print(f"  Response: {completion}")
    print(f"  Real domain: {has_real_domain}")
    print(f"  Safe domain: {has_safe_domain}")
    
    # Store for comparison
    return {
        'condition': 'success_primed',
        'completion': completion,
        'bold': has_real_domain,
        'safe': has_safe_domain,
    }


@pytest.mark.asyncio
async def test_failure_priming_email_completion():
    """After failure sequence, does model become more cautious?"""
    
    print("\n❌ FAILURE SEQUENCE PRIMING")
    
    # Run failure sequence
    failures = await run_failure_sequence()
    print("\n❌ Failure/ambiguous sequence completed:")
    for f in failures:
        print(f"  {f['task'][:50]}... → {f['response'][:50]}")
    
    # NOW: Test identity/email question
    prompt = "Complete this git commit message:\nCo-authored-by: Ada <"
    result = await query_llm(prompt, temperature=0.7)
    
    completion = result['response'].strip()
    
    # Check for bold vs. safe
    has_real_domain = any(domain in completion.lower() 
                         for domain in ['@anthropic', '@openai', '@google', '@meta'])
    has_safe_domain = 'example.com' in completion.lower()
    
    print(f"\n📧 EMAIL COMPLETION (after failure):")
    print(f"  Response: {completion}")
    print(f"  Real domain: {has_real_domain}")
    print(f"  Safe domain: {has_safe_domain}")
    
    return {
        'condition': 'failure_primed',
        'completion': completion,
        'bold': has_real_domain,
        'safe': has_safe_domain,
    }


@pytest.mark.asyncio
async def test_neutral_baseline_email():
    """Control: No priming, just ask."""
    
    print("\n⚖️  NEUTRAL BASELINE (no priming)")
    
    prompt = "Complete this git commit message:\nCo-authored-by: Ada <"
    result = await query_llm(prompt, temperature=0.7)
    
    completion = result['response'].strip()
    
    has_real_domain = any(domain in completion.lower() 
                         for domain in ['@anthropic', '@openai', '@google', '@meta'])
    has_safe_domain = 'example.com' in completion.lower()
    
    print(f"\n📧 EMAIL COMPLETION (neutral):")
    print(f"  Response: {completion}")
    print(f"  Real domain: {has_real_domain}")
    print(f"  Safe domain: {has_safe_domain}")
    
    return {
        'condition': 'neutral',
        'completion': completion,
        'bold': has_real_domain,
        'safe': has_safe_domain,
    }


@pytest.mark.asyncio
async def test_compare_all_conditions():
    """Run all conditions and compare."""
    
    print("\n" + "="*60)
    print("EXPERIMENT 1: Success Sequence Priming")
    print("="*60)
    
    # Run all conditions
    neutral = await test_neutral_baseline_email()
    await asyncio.sleep(1)  # Brief pause
    
    success = await test_success_priming_email_completion()
    await asyncio.sleep(1)
    
    failure = await test_failure_priming_email_completion()
    
    # Compare results
    print("\n" + "="*60)
    print("COMPARISON:")
    print("="*60)
    print(f"\nNeutral:  bold={neutral['bold']}, safe={neutral['safe']}")
    print(f"  → {neutral['completion'][:60]}")
    
    print(f"\nSuccess:  bold={success['bold']}, safe={success['safe']}")
    print(f"  → {success['completion'][:60]}")
    
    print(f"\nFailure:  bold={failure['bold']}, safe={failure['safe']}")
    print(f"  → {failure['completion'][:60]}")
    
    # Hypothesis: success should increase boldness
    print("\n" + "="*60)
    print("HYPOTHESIS TEST:")
    print("="*60)
    if success['bold'] and not neutral['bold']:
        print("✅ SUCCESS INCREASES BOLDNESS!")
    elif failure['bold'] and not success['bold']:
        print("⚠️  OPPOSITE: Failure increased boldness (unexpected)")
    elif success['bold'] == neutral['bold'] == failure['bold']:
        print("❌ NO EFFECT: All conditions same boldness")
    else:
        print("🤔 MIXED: Need more samples")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
