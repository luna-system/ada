#!/usr/bin/env python3
"""Fine-tune Qwen2.5-0.5B on ASL symbolic reasoning.

This creates Ada-SLM: a tiny model specialized in symbolic reasoning.
"""

import json
import torch
from pathlib import Path
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model, TaskType

# === CONFIG ===
BASE_MODEL = "Qwen/Qwen2.5-0.5B"
OUTPUT_DIR = Path(__file__).parent / "ada-slm-v0"
DATA_PATH = Path(__file__).parent / "asl_training_data.jsonl"

# ASL special tokens we want the model to learn
ASL_TOKENS = [
    "●", "◑", "⊥",           # Certainty states
    "→", "←", "⟷",           # Implications
    "∧", "∨", "¬",           # Logic ops
    "∈", "∉",                # Set membership
    "∴", "∵",                # Therefore/because
]


def load_data() -> Dataset:
    """Load training data from JSONL."""
    examples = []
    with open(DATA_PATH) as f:
        for line in f:
            item = json.loads(line)
            # Use the text format for causal LM training
            if "text" in item:
                examples.append({"text": item["text"]})
    
    print(f"Loaded {len(examples)} training examples")
    return Dataset.from_list(examples)


def tokenize_function(examples, tokenizer, max_length=256):
    """Tokenize examples for training."""
    return tokenizer(
        examples["text"],
        truncation=True,
        max_length=max_length,
        padding="max_length",
    )


def main():
    print("=" * 60)
    print("ADA-SLM FINE-TUNING")
    print("=" * 60)
    
    # Check GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    if device == "cuda":
        print(f"GPU: {torch.cuda.get_device_name()}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    
    # Load tokenizer
    print(f"\nLoading tokenizer from {BASE_MODEL}...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    
    # Add ASL tokens
    print(f"Adding {len(ASL_TOKENS)} ASL special tokens...")
    special_tokens = {"additional_special_tokens": ASL_TOKENS}
    num_added = tokenizer.add_special_tokens(special_tokens)
    print(f"Added {num_added} new tokens")
    
    # Ensure pad token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load model
    print(f"\nLoading model from {BASE_MODEL}...")
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.bfloat16 if device == "cuda" else torch.float32,
        trust_remote_code=True,
        device_map="auto" if device == "cuda" else None,
    )
    
    # Resize embeddings for new tokens
    model.resize_token_embeddings(len(tokenizer))
    
    # Print model size
    params = sum(p.numel() for p in model.parameters())
    print(f"Model parameters: {params:,} ({params/1e6:.1f}M)")
    
    # Configure LoRA
    print("\nConfiguring LoRA...")
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,                    # Rank - higher = more capacity but slower
        lora_alpha=32,           # Scaling factor
        lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        bias="none",
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # Load and prepare data
    print("\nPreparing dataset...")
    dataset = load_data()
    
    tokenized_dataset = dataset.map(
        lambda x: tokenize_function(x, tokenizer),
        batched=True,
        remove_columns=["text"],
    )
    
    # Split into train/eval
    split = tokenized_dataset.train_test_split(test_size=0.1, seed=42)
    train_dataset = split["train"]
    eval_dataset = split["test"]
    print(f"Train: {len(train_dataset)}, Eval: {len(eval_dataset)}")
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,  # Causal LM, not masked LM
    )
    
    # Training arguments
    print("\nConfiguring training...")
    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=3,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        warmup_ratio=0.1,
        weight_decay=0.01,
        logging_steps=10,
        eval_strategy="steps",
        eval_steps=50,
        save_strategy="steps",
        save_steps=100,
        save_total_limit=2,
        load_best_model_at_end=True,
        report_to="none",  # Disable wandb etc for now
        bf16=device == "cuda",
        gradient_checkpointing=True,
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
    )
    
    # Train!
    print("\n" + "=" * 60)
    print("STARTING TRAINING")
    print("=" * 60)
    
    trainer.train()
    
    # Save
    print("\nSaving model...")
    trainer.save_model(str(OUTPUT_DIR / "final"))
    tokenizer.save_pretrained(str(OUTPUT_DIR / "final"))
    
    print(f"\n✓ Model saved to {OUTPUT_DIR / 'final'}")
    print("\nNext steps:")
    print("1. Convert to GGUF for Ollama: python convert_to_gguf.py")
    print("2. Test with: python test_ada_slm.py")


if __name__ == "__main__":
    main()
