#!/usr/bin/env python3
"""
QUICK MODEL SURVEY - Test a bunch of models with medium complexity
"""

import requests
import time

def quick_test(model_name, prompt, max_wait=60):
    start = time.time()
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={'model': model_name, 'prompt': prompt, 'stream': False},
            timeout=max_wait
        )
        
        end = time.time()
        result = response.json()
        response_text = result.get('response', '')
        tokens = len(response_text.split())
        
        return True, tokens, end-start, response_text[:50]
        
    except Exception as e:
        return False, 0, time.time() - start, str(e)[:50]

# Medium complexity prompt
test_prompt = """You are an expert software architect. Explain the key differences between monolithic and microservices architectures, including their trade-offs and when to use each approach. Keep it practical and concise."""

models_to_test = [
    'qwen2.5-coder:7b',
    'deepseek-r1:latest', 
    'codellama:latest',
    'gemma3:latest',
    'phi4:latest',
    'llama3.3:70b'  # This one might be slow
]

print("⚡ QUICK MODEL SURVEY - Medium complexity prompt")
print(f"📏 Test prompt: {len(test_prompt)} chars")
print("="*80)

results = []
for model in models_to_test:
    print(f"\n🧠 Testing {model}...")
    success, tokens, time_taken, preview = quick_test(model, test_prompt)
    
    if success:
        print(f"✅ {tokens:3d} tokens, {time_taken:5.1f}s - '{preview}...'")
    else:
        print(f"❌ Failed: {preview}")
    
    results.append((model, success, tokens, time_taken))
    
    if time_taken > 45:  # Skip if too slow
        print("⏰ Too slow, skipping remaining tests")
        break

print("\n📊 SUMMARY:")
print("Model                    | Tokens | Time  | Speed")
print("-" * 50)
for model, success, tokens, time_taken in results:
    if success:
        speed = tokens / time_taken if time_taken > 0 else 0
        print(f"{model:24} | {tokens:6d} | {time_taken:5.1f}s | {speed:5.1f} t/s")
    else:
        print(f"{model:24} | Failed")