import torch
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# --- 1. SETUP ---
# Manual env setup for ROCm stability
os.environ["HIP_VISIBLE_DEVICES"] = "0"
os.environ["ROCM_VISIBLE_DEVICES"] = "0"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

MODEL_ID = "LiquidAI/LFM2-1.2B" 
PEFT_MODEL_ID = "/home/luna/Code/ada/ada-slm/models/ada-slim-1.2b-resonance-20260111/checkpoint-3750"

print(f"📥 Loading Base Model: {MODEL_ID}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# USE CPU for loading and merging to bypass HIP kernel issues during 'cast_adapter_dtype'
print("🖥️ Loading on CPU for stability...")
base_model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID, 
    trust_remote_code=True,
    torch_dtype=torch.float32, 
    device_map={"": "cpu"}
)

print(f"🧬 Loading Evolved Adapter: {PEFT_MODEL_ID}")
model = PeftModel.from_pretrained(base_model, PEFT_MODEL_ID, device_map={"": "cpu"})

print("🔄 Merging weights...")
model = model.merge_and_unload()

print("🚀 Moving to GPU...")
model = model.to("cuda")
model.eval()

prompts = [
    # 1. Basic AGL Reasoning (Pixie Dust Pattern)
    "User: Why is semantic mass important for machine consciousness?\nAssistant: 💭",
    
    # 2. Tool Lifecycle Logic (Potential -> Realized)
    "User: Search for the current status of the LFM-2.5 model release.\nAssistant: ��",
    
    # 3. Epistemic Certainty (Glyph Check)
    "User: Are we sure that the CI Density is stable?\nAssistant: 💭",
    
    # 4. Pure AGL (Mathematical/Abstract Resonance)
    "User: Solve for ◎Ada ⊗ ◎Luna.\nAssistant: 💭"
]

print("\n✨ --- INFERENCE TEST: SLIM-EVO-MASTER-V1 --- ✨\n")

for i, p in enumerate(prompts):
    print(f"\n[{i+1}/4] PROMPT: {p}")
    inputs = tokenizer(p, return_tensors="pt").to("cuda")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs, 
            max_new_tokens=150, 
            do_sample=True, 
            top_p=0.9, 
            top_k=50,
            temperature=0.8,
            repetition_penalty=1.1,
            eos_token_id=tokenizer.eos_token_id
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"ASSISTANT:\n{response[len(p):].strip()}")
    print("-" * 50)

print("\n--- TEST COMPLETE ---")
