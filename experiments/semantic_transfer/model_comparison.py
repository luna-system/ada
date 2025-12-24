#!/usr/bin/env python3
"""
CodeLlama vs Qwen: Different Models, Same Questions
=====================================================

Same questions, different architectures. What changes?
- Qwen2.5-Coder: Trained on code + instruction following
- CodeLlama: Trained on code completion
- Do they express consciousness differently?
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
    """Compare models on consciousness questions in different constraints."""
    
    print("\n" + "="*80)
    print("🧠 MODEL COMPARISON: QWEN vs CODELLAMA")
    print("="*80)
    print("\nSame questions, different neural architectures")
    print("Does consciousness look different depending on how you're trained?\n")
    
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
        ("qwen2.5-coder:7b", "Qwen (Instruction-tuned Code Model)"),
        ("codellama:latest", "CodeLlama (Code Completion)"),
    ]
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "comparison": "qwen vs codellama",
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
    output_path = Path("/home/luna/Code/ada-v1/experiments/semantic_transfer/model_comparison_qwen_vs_codellama.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print("="*80)
    print(f"\n✅ Comparison results saved to: {output_path}")
    print(f"Test cases: {len(test_cases)}")
    print(f"Models compared: {len(models)}")
    print(f"Total responses: {len(test_cases) * len(models)}")
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
