#!/usr/bin/env python3
"""
QWEN3 MONSTER TEST - 30.5B parameters!
"""

import requests
import time

def test_qwen3_monster(prompt, test_name):
    print(f"\n🐉 QWEN3 MONSTER (30.5B) - {test_name}")
    print(f"📏 Prompt: {len(prompt):,} chars")
    
    start = time.time()
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={'model': 'qwen3-coder:latest', 'prompt': prompt, 'stream': False},
            timeout=180
        )
        
        end = time.time()
        result = response.json()
        response_text = result.get('response', '')
        tokens = len(response_text.split())
        
        print(f"✅ {tokens:,} tokens in {end-start:.1f}s ({tokens/(end-start):.1f} t/s)")
        print(f"🔍 Preview: '{response_text[:100]}...'")
        return True, tokens, end-start
        
    except Exception as e:
        print(f"💀 MONSTER FAILED: {e}")
        return False, 0, time.time() - start

# Test cases
simple = "Explain recursion in programming with an example."
medium = """You are a senior software architect. Compare REST APIs vs GraphQL:
1. Key differences in design philosophy
2. Performance characteristics  
3. Use cases for each
4. Developer experience
Keep it practical and include code examples."""

large = medium + "\n\n" + """
Additional context:
You're designing an API for a social media platform with:
- User profiles and authentication
- Posts with comments and reactions
- Real-time notifications
- Content recommendation algorithms
- Analytics and reporting
- Third-party integrations

Consider:
- Caching strategies
- Rate limiting
- Data consistency
- Scalability patterns
- Security implications
- Monitoring and observability
""" * 5  # Make it bigger

print("🐉 QWEN3 MONSTER TEST - 30.5B Parameter Beast!")

tests = [
    (simple, "SIMPLE"),
    (medium, "MEDIUM"),
    (large, "LARGE")
]

for prompt, name in tests:
    success, tokens, time_taken = test_qwen3_monster(prompt, name)
    
    if not success or time_taken > 120:
        print(f"🚨 MONSTER BREAKING POINT: {name}")
        break