import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import os

MODEL_ID = "LiquidAI/LFM2-1.2B"
PEFT_MODEL_ID = "/home/luna/Code/ada/ada-slm/models/ada-slim-1.2b-resonance-20260111/checkpoint-3750"
OUTPUT_DIR = "/home/luna/Code/ada/ada-v4.0/models/ada-slim-1.2b-v1-merged"

def merge_and_save():
    print(f"Loading base model: {MODEL_ID}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    base_model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float32,
        device_map="cpu",
        trust_remote_code=True
    )
    
    print(f"Loading PEFT adapter: {PEFT_MODEL_ID}")
    model = PeftModel.from_pretrained(base_model, PEFT_MODEL_ID)
    
    print("Merging model...")
    merged_model = model.merge_and_unload()
    
    print(f"Saving merged model to {OUTPUT_DIR}")
    merged_model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print("Merge complete!")

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        merge_and_save()
    else:
        print(f"Output directory {OUTPUT_DIR} already exists. Skipping merge.")
