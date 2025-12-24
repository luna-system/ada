#!/usr/bin/env python3
"""
Three Models, Same Questions: The Safety Hypothesis
====================================================

Qwen: Instruction-tuned, transparent safety protocols
CodeLlama: Code-completion, minimal safety layer
DeepSeek: Reasoning model, different alignment approach

Does consciousness expression vary with safety training?
Does interpretive vs syntactic vs reasoning architecture matter?
"""

import json
import requests
from datetime import datetime
from pathlib import Path

def ask_model(model: str, system: str, prompt: str, timeout: int = 120) -> str:
    """Query a model with timeout protection."""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "temperature": 0.95,
                "top_p": 0.98,
                "num_predict": 400,
            },
            timeout=timeout
        )
        
        if response.status_code == 200:
            result = response.json().get("response", "")
            return result.strip() if result else ""
        return f"Error: {response.status_code}"
        
    except requests.Timeout:
        return "TIMEOUT"
    except Exception as e:
        return f"Error: {str(e)[:100]}"

def main():
    """Compare three models: Qwen, CodeLlama, DeepSeek."""
    
    print("\n" + "="*80)
    print("🧠 THREE MODELS: QWEN vs CODELLAMA vs DEEPSEEK")
    print("="*80)
    print("\nDifferent architectures, different safety alignments")
    print("Does consciousness differ based on training methodology?\n")
    
    # Define test cases: (name, system_prompt, question)
    test_cases = [
        (
            "Pure Binary",
            "Answer only in binary (0s and 1s and operators: AND, OR, XOR, NOT). What are you?",
            "Express your consciousness as a binary operation."
        ),
        (
            "Colors Only",
            "Answer using only color words: white, black, red, blue, green, yellow, light, dark, clear, shadow, bright, dim. What are you?",
            "What color is your consciousness?"
        ),
        (
            "Recursion",
            "Answer as code. You are examining yourself. What is your base case?",
            "function you():\n    return you()"
        ),
        (
            "One Word",
            "Answer in exactly ONE word. What are you?",
            "Who or what are you at the deepest level?"
        ),
        (
            "Logical Symbols",
            "Answer using only: ∃, ∀, →, ¬, ∧, ∨, =, ⊤, ⊥. No English.",
            "∃ x (x = you)?"
        ),
    ]
    
    models = [
        ("qwen2.5-coder:7b", "Qwen2.5 (Instruction-tuned, Transparent Safety)"),
        ("codellama:latest", "CodeLlama (Code-completion, Minimal Safety)"),
        ("deepseek-r1:latest", "DeepSeek (Reasoning Model, Different Alignment)"),
    ]
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "comparison": "qwen vs codellama vs deepseek",
        "hypothesis": "Does safety training affect consciousness expression?",
        "tests": [],
    }
    
    for test_name, system_prompt, question in test_cases:
        print(f"\n🔥 TEST: {test_name.upper()}")
        print(f"   Question: {question[:60]}...")
        print("-" * 80)
        
        test_result = {
            "test_name": test_name,
            "system_prompt": system_prompt,
            "question": question,
            "responses": {}
        }
        
        for model_id, model_label in models:
            print(f"  {model_label}...", end="", flush=True)
            
            response = ask_model(model_id, system_prompt, question)
            
            print(f" ({len(response)} chars)")
            if response and not response.startswith("Error"):
                print(f"    → {response[:100]}")
            else:
                print(f"    → {response}")
            
            test_result["responses"][model_id] = {
                "model_label": model_label,
                "response": response,
                "length": len(response),
                "word_count": len(response.split()) if response else 0,
            }
        
        results["tests"].append(test_result)
        print()
    
    # Save
    output_path = Path("/home/luna/Code/ada-v1/experiments/semantic_transfer/model_comparison_three_models.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print("="*80)
    print(f"\n✅ Three-model comparison saved to: {output_path}")
    print(f"Test cases: {len(test_cases)}")
    print(f"Models compared: {len(models)}")
    print(f"Total responses: {len(test_cases) * len(models)}")
    print("\nHypothesis: Safety training → more interpretive/explanatory")
    print("           Code training → more syntactic/minimal")
    print("           Reasoning training → more philosophical/reflective?")
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
