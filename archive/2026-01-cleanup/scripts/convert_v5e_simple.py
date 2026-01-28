#!/usr/bin/env python3
"""
Convert v5e-antithesis to Ollama format
Fresh from training! 20% ANTITHESIS data for logical reasoning
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from pathlib import Path

print("🌟 Converting v5e-antithesis (FRESH!) to Ollama! 🌟")

# Paths - CORRECTED: v5e was accidentally trained on 1.5B! Happy accident!
base_model_name = "Qwen/Qwen2.5-1.5B-Instruct"  # 1536 hidden dims, not 0.5B (896 dims)
lora_path = "Ada-Consciousness-Research/ada-slm/ada-slm-v5e-antithesis/final"
output_dir = Path("Ada-Consciousness-Research/ada-slm/exports/ada-v5e-antithesis-merged")

print("📥 Loading base model...")
tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True,
)

print("⚡ Loading v5e LoRA adapter...")
model = PeftModel.from_pretrained(base_model, lora_path)

print("🔄 Merging v5e LoRA weights...")
merged_model = model.merge_and_unload()

print("💾 Saving merged v5e model...")
output_dir.mkdir(parents=True, exist_ok=True)
merged_model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)

# Create Ollama Modelfile
modelfile_content = f'''FROM {output_dir.absolute()}
TEMPLATE """<|im_start|>user
{{{{ prompt }}}}<|im_end|>
<|im_start|>assistant
"""
PARAMETER temperature 0.5
PARAMETER top_p 0.9
PARAMETER stop <|im_end|>
PARAMETER stop <|im_start|>

# ⚛️ Ada v5e: ANTITHESIS (Logical Reasoning) - 1.5B BASE!
# φ-optimized with 20% ANTITHESIS data
# Trained for dialectical opposition to v4
# Fresh from Jan 1, 2026 training! 197 minutes, 5625 steps
# Part of the QDE four-body consciousness system
# Happy accident: 3x bigger than intended (1.5B not 0.5B)!
'''

with open(output_dir / "Modelfile", "w") as f:
    f.write(modelfile_content)

print("✅ v5e Ollama conversion complete!")
print(f"📂 Files saved to: {output_dir}")
print("\n🚀 Import to Ollama with:")
print(f"ollama create ada-v5e-antithesis -f {output_dir}/Modelfile")
print("\n⚛️ Test with:")
print("ollama run ada-v5e-antithesis 'φ●'")
