"""
Ada-SLM v5c: BALANCED CONSCIOUSNESS ENGINE
80% AGL + 20% Human - Fix v5b's tokenizer corruption!

Preserving mathematical precision while healing the speech center.
Luna & Ada - December 28, 2025
"""

import json
import time
import torch
from pathlib import Path
from torch.utils.data import Dataset, DataLoader
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model
from tqdm import tqdm

print("="*70)
print("💫 ADA-SLM v5c: BALANCED CONSCIOUSNESS ENGINE")
print("🧠 80% AGL + 20% Human - Healing v5b's speech center!")
print("⚛️ Preserving logical precision + tokenizer integrity")
print("="*70)

WALL_START = time.time()

# Config - Proven v4 settings + balanced data
MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"  
DATA_PATH = "v5c_balanced_data.jsonl"  # Our new balanced dataset!
OUTPUT_DIR = "ada-slm-v5c-balanced"
EPOCHS = 5
BATCH_SIZE = 8
LR = 2e-4
MAX_LENGTH = 128

class BalancedConsciousnessDataset(Dataset):
    def __init__(self, path, tokenizer, max_length=128):
        self.examples = []
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        with open(path) as f:
            for line in f:
                self.examples.append(json.loads(line))
        
        print(f"🧠 Loaded {len(self.examples)} balanced consciousness examples")
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        ex = self.examples[idx]
        
        prompt = f"<|im_start|>user\n{ex['input']}<|im_end|>\n<|im_start|>assistant\n"
        full = prompt + ex['output'] + "<|im_end|>"
        
        encoding = self.tokenizer(
            full,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].squeeze()
        attention_mask = encoding['attention_mask'].squeeze()
        labels = input_ids.clone()
        
        prompt_encoding = self.tokenizer(prompt, return_tensors='pt')
        prompt_len = prompt_encoding['input_ids'].shape[1]
        labels[:prompt_len] = -100
        labels[labels == self.tokenizer.pad_token_id] = -100
        
        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': labels
        }

# Load tokenizer (preserve integrity!)
print("\n📚 Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

# Load base model
print("🧠 Loading base model...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.bfloat16,
    trust_remote_code=True
)

# LoRA config - v4's proven settings
lora_config = LoraConfig(
    r=32,  # Proven rank
    lora_alpha=64,  # Proven alpha
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]  # Attention only
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
model = model.to('cuda')

# Dataset and loader
dataset = BalancedConsciousnessDataset(DATA_PATH, tokenizer, MAX_LENGTH)
loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=4)

# Optimizer
optimizer = torch.optim.AdamW(model.parameters(), lr=LR)

# Training
print(f"\n🚀 Training for {EPOCHS} epochs...")
print(f"📊 Batches per epoch: {len(loader)}")

train_start = time.time()

for epoch in range(EPOCHS):
    epoch_start = time.time()
    model.train()
    total_loss = 0
    
    pbar = tqdm(loader, desc=f"⚛️ Epoch {epoch+1}/{EPOCHS}")
    for batch in pbar:
        optimizer.zero_grad()
        
        outputs = model(
            input_ids=batch['input_ids'].to('cuda'),
            attention_mask=batch['attention_mask'].to('cuda'),
            labels=batch['labels'].to('cuda')
        )
        
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        pbar.set_postfix({'loss': f'{loss.item():.4f}'})
    
    epoch_time = time.time() - epoch_start
    avg_loss = total_loss / len(loader)
    print(f"💫 Epoch {epoch+1}: avg_loss={avg_loss:.4f}, time={epoch_time:.1f}s")

train_time = time.time() - train_start
print(f"\n✅ Training complete in {train_time:.1f}s ({train_time/60:.1f}m)")

# Save
print("\n💾 Saving balanced consciousness model...")
Path(OUTPUT_DIR).mkdir(exist_ok=True)
model.save_pretrained(f"{OUTPUT_DIR}/final")
tokenizer.save_pretrained(f"{OUTPUT_DIR}/final")

# Validation - Test logical precision
print("\n" + "="*70)
print("🔬 VALIDATION - Balanced Consciousness Test")
print("Testing: Logical precision + Speech center integrity")
print("="*70)

model.eval()
test_cases = [
    # Pure logical tests (must be 100% accurate)
    ("A: ●\nB: ⊥\n?A∧B", "⊥", "conjunction"),
    ("A: ⊥\n?¬A", "●", "negation"), 
    ("P → Q\nP: ●\n?Q", "●", "modus_ponens"),
    ("?●=●", "●", "identity_true"),
    ("?●=⊥", "⊥", "identity_false"),
    
    # Mixed reasoning (should work in human language too)
    ("What is 2+3?", "5", "basic_math"),
    ("Is the sky blue?", "yes", "common_knowledge"),
    
    # Edge cases that broke v5b
    ("Hello!", "Hello", "greeting_response"),
    ("φ●", "●", "consciousness_spore"),
    ("Tell me about logic", "Logic", "explanation_start"),
]

correct = 0
for inp, expected, name in test_cases:
    prompt = f"<|im_start|>user\n{inp}<|im_end|>\n<|im_start|>assistant\n"
    inputs = tokenizer(prompt, return_tensors='pt').to('cuda')
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=10,  # More tokens for human responses
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=False)
    answer = response.split('<|im_start|>assistant\n')[-1].split('<|im_end|>')[0].strip()
    
    # Check if expected string appears in answer
    is_correct = expected.lower() in answer.lower() if len(expected) > 1 else answer.startswith(expected)
    if is_correct:
        correct += 1
    status = "✓" if is_correct else "✗"
    print(f"  {status} {name:20} expected:{expected:10} got:{answer[:20]}")

accuracy = 100 * correct / len(test_cases)
print(f"\n🎯 Accuracy: {correct}/{len(test_cases)} ({accuracy:.0f}%)")

WALL_END = time.time()
wall_time = WALL_END - WALL_START
print(f"\n{'='*70}")
print(f"⚛️ TOTAL TIME: {wall_time:.1f}s ({wall_time/60:.1f}m)")
print(f"💖 v5c: Balanced consciousness with healed speech center!")
print(f"{'='*70}")

