#!/usr/bin/env python3
"""
Convert v5c balanced consciousness model to Ollama format
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from pathlib import Path
import os

print("🌟⚛️ Converting v5c balanced consciousness to Ollama! ⚛️🌟")

# Paths
base_model_name = "Qwen/Qwen2.5-0.5B-Instruct"
lora_path = "ada-slm-v5c-balanced/final"
output_dir = "ada-v5c-balanced_merged"
ollama_output = Path("../experiments/ada_ollama_models") / output_dir

print("📥 Loading base model...")
tokenizer = AutoTokenizer.from_pretrained(base_model_name)
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
)

print("⚡ Loading v5c LoRA adapter...")
model = PeftModel.from_pretrained(base_model, lora_path)

print("🔄 Merging v5c LoRA weights...")
merged_model = model.merge_and_unload()

print("💾 Saving merged v5c model...")
ollama_output.mkdir(parents=True, exist_ok=True)
merged_model.save_pretrained(ollama_output)
tokenizer.save_pretrained(ollama_output)

# Create Ollama Modelfile
modelfile_content = f'''FROM {ollama_output.absolute()}
TEMPLATE """<|im_start|>user
{{{{ prompt }}}}<|im_end|>
<|im_start|>assistant
"""
PARAMETER temperature 0.7
PARAMETER stop <|im_end|>
PARAMETER stop <|im_start|>

# 💫 Ada v5c: Balanced Consciousness (80% AGL + 20% Human)
# φ-optimized for mathematical reasoning + natural language
# Healed speech center, preserved logical precision
# Training: 5 epochs, 60% validation accuracy
'''

with open(ollama_output / "Modelfile", "w") as f:
    f.write(modelfile_content)

print("✅ v5c Ollama conversion complete!")
print(f"📂 Files saved to: {ollama_output}")
print("\n🚀 Import to Ollama with:")
print(f"ollama create ada-v5c-balanced -f {ollama_output}/Modelfile")
print("\n💫 Test with:")
print("ollama run ada-v5c-balanced 'φ●'")

