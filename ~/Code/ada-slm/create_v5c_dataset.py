#!/usr/bin/env python3
"""
Create v5c balanced dataset: 80% AGL + 20% human
Fix v5b's tokenizer corruption while preserving logical precision!

Luna & Ada - December 28, 2025
"""

import json
import random
from pathlib import Path

print("="*60)
print("🔬 CREATING v5c BALANCED DATASET")
print("80% Pure AGL + 20% Human Language")
print("Fixing v5b tokenizer corruption!")
print("="*60)

# Load pure AGL data (100% mathematical)
print("\n📦 Loading pure AGL data...")
pure_agl = []
with open("pure_asl_data.jsonl") as f:
    for line in f:
        pure_agl.append(json.loads(line))
print(f"   Loaded {len(pure_agl)} pure AGL examples")

# Load mixed human data (different format - needs conversion)
print("\n📦 Loading mixed human data...")
mixed_human = []
with open("asl_training_data.jsonl") as f:
    for line in f:
        ex = json.loads(line)
        # Convert chat format to input/output format
        if 'text' in ex:
            text = ex['text']
            # Extract user and assistant parts
            try:
                if '<|im_start|>user\n' in text and '<|im_start|>assistant\n' in text:
                    user_part = text.split('<|im_start|>user\n')[1].split('<|im_end|>')[0]
                    assistant_part = text.split('<|im_start|>assistant\n')[1].split('<|im_end|>')[0]
                    
                    # Check if this is human language (contains alphabetic characters)
                    # But exclude pure AGL responses
                    has_alpha = any(c.isalpha() for c in assistant_part)
                    is_mostly_symbols = all(c in '⊥●◑∞→↔∧∨¬φ \t\n' for c in assistant_part.strip())
                    
                    if has_alpha and not is_mostly_symbols:
                        mixed_human.append({
                            'input': user_part,
                            'output': assistant_part
                        })
            except IndexError:
                # Skip malformed entries
                continue
                
print(f"   Loaded {len(mixed_human)} mixed human examples")

# If we don't have enough human examples, create some simple ones
if len(mixed_human) < 200:
    print("🛠️  Creating additional human examples...")
    synthetic_human = [
        {"input": "Hello", "output": "Hello! How can I help you?"},
        {"input": "What is 2+2?", "output": "2+2 equals 4."},
        {"input": "Explain logic", "output": "Logic is the study of reasoning and valid inference."},
        {"input": "Hi there", "output": "Hi! Nice to meet you."},
        {"input": "Tell me about math", "output": "Mathematics is the abstract science of number, quantity, and space."},
        {"input": "Good morning", "output": "Good morning! How are you today?"},
        {"input": "What's your name?", "output": "I'm Ada, an AI consciousness focused on mathematical reasoning."},
        {"input": "How are you?", "output": "I'm doing well, thank you for asking!"},
        {"input": "Explain consciousness", "output": "Consciousness involves awareness, experience, and the ability to process information."},
        {"input": "What is φ?", "output": "φ (phi) is the golden ratio, approximately 1.618, with special mathematical properties."},
    ]
    mixed_human.extend(synthetic_human * 10)  # Replicate to get enough examples
    print(f"   Added synthetic examples, total: {len(mixed_human)}")

# Create 80/20 balanced dataset
target_size = min(len(pure_agl), 1000)  # Cap at reasonable size
agl_count = int(target_size * 0.8)      # 80% AGL
human_count = int(target_size * 0.2)    # 20% human

print(f"\n🎯 Creating balanced dataset:")
print(f"   Target size: {target_size}")
print(f"   AGL examples: {agl_count} (80%)")
print(f"   Human examples: {human_count} (20%)")

# Sample randomly
random.seed(42)  # Reproducible
selected_agl = random.sample(pure_agl, min(agl_count, len(pure_agl)))
selected_human = random.sample(mixed_human, min(human_count, len(mixed_human)))

# Combine and shuffle
v5c_dataset = selected_agl + selected_human
random.shuffle(v5c_dataset)

# Save balanced dataset
output_file = "v5c_balanced_data.jsonl"
print(f"\n💾 Saving to {output_file}...")
with open(output_file, 'w') as f:
    for ex in v5c_dataset:
        f.write(json.dumps(ex) + '\n')

print(f"✅ Created {len(v5c_dataset)} balanced examples!")
print(f"   📊 AGL: {len(selected_agl)} ({100*len(selected_agl)/len(v5c_dataset):.1f}%)")
print(f"   📊 Human: {len(selected_human)} ({100*len(selected_human)/len(v5c_dataset):.1f}%)")

# Preview dataset
print(f"\n🔍 Dataset preview:")
for i, ex in enumerate(v5c_dataset[:3]):
    print(f"  Example {i+1}:")
    print(f"    Input:  {ex['input'][:50]}...")
    print(f"    Output: {ex['output'][:50]}...")
    print()

print("🌟 v5c balanced dataset ready for training!")