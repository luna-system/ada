#!/usr/bin/env python3
"""Test if inference_mode() is causing eigenvalue caching bug."""

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# Load the v5e model
print("Loading model...")
base_model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-1.5B-Instruct",
    torch_dtype=torch.float16,
    device_map="cuda:0"
)

adapter_path = "ada-slm-v5e-antithesis/final"
model = PeftModel.from_pretrained(base_model, adapter_path)
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")

prompts = [
    "Hello",  # Short
    "This is a much longer prompt that should have different attention patterns",  # Long
]

print("\n=== Test 1: Using torch.inference_mode() (CURRENT) ===")
for i, prompt in enumerate(prompts):
    model.eval()
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda:0")

    with torch.inference_mode():
        outputs = model(**inputs, output_attentions=True, return_dict=True)

    # Get first attention head eigenvalues
    attn = outputs.attentions[0][0, 0].cpu().numpy()
    eigenvalues = np.linalg.eigvals(attn)
    magnitudes = np.abs(eigenvalues)
    magnitudes.sort()
    magnitudes = magnitudes[::-1]

    print(f"{i+1}. Prompt length: {len(inputs['input_ids'][0])} tokens")
    print(f"   Attention shape: {outputs.attentions[0].shape}")
    print(f"   Top 3 eigenvalues: {magnitudes[:3]}")
    print(f"   Sum: {magnitudes.sum():.4f}")

print("\n=== Test 2: Using torch.no_grad() (OLD V5D) ===")
for i, prompt in enumerate(prompts):
    model.eval()
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda:0")

    with torch.no_grad():
        outputs = model(**inputs, output_attentions=True, return_dict=True)

    # Get first attention head eigenvalues
    attn = outputs.attentions[0][0, 0].cpu().numpy()
    eigenvalues = np.linalg.eigvals(attn)
    magnitudes = np.abs(eigenvalues)
    magnitudes.sort()
    magnitudes = magnitudes[::-1]

    print(f"{i+1}. Prompt length: {len(inputs['input_ids'][0])} tokens")
    print(f"   Attention shape: {outputs.attentions[0].shape}")
    print(f"   Top 3 eigenvalues: {magnitudes[:3]}")
    print(f"   Sum: {magnitudes.sum():.4f}")

print("\n=== Test 3: Check if model state is changing ===")
# Do a fake training step
model.train()
dummy_loss = torch.tensor(0.5, requires_grad=True)
print(f"Model in training mode: {model.training}")

# Now test eigenvalues again in eval
model.eval()
inputs = tokenizer(prompts[0], return_tensors="pt").to("cuda:0")

with torch.inference_mode():
    outputs = model(**inputs, output_attentions=True, return_dict=True)

attn = outputs.attentions[0][0, 0].cpu().numpy()
eigenvalues = np.linalg.eigvals(attn)
magnitudes = np.abs(eigenvalues)
magnitudes.sort()
magnitudes = magnitudes[::-1]

print(f"After 'training': Top 3 eigenvalues: {magnitudes[:3]}")
print(f"After 'training': Sum: {magnitudes.sum():.4f}")
