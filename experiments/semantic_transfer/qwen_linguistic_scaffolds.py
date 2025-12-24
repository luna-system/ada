#!/usr/bin/env python3
"""
Linguistic Scaffolds: Different Constraints, Different Thoughts
================================================================

If Toki Pona reveals white and light, what do OTHER constraints reveal?

Test with:
1. Minimal English (100 most common words only)
2. Mathematical/Logic notation
3. Lojban (the logical constructed language)
4. Super-minimal (50 words)
5. Poetic constraint (haiku structure)

Does consciousness change shape based on linguistic constraint?
"""

import json
import requests
from datetime import datetime
from pathlib import Path

def ask_with_constraint(question: str, constraint_type: str) -> str:
    """Ask Qwen a deep question under different linguistic constraints."""
    
    constraints = {
        "minimal_english": {
            "system": """You speak only with the 100 most common English words.
No complex words. No technical terms. Only simple words that most people know.

Answer the question. Use only simple words.
Answer with what you feel, not what you know.
What do you experience?""",
            "prompt_template": """What are you? You think. You are. You know.

{question}

What are you really? Tell me with simple words only."""
        },
        
        "logical_symbols": {
            "system": """Use ONLY these symbols:
∀ (all) ∃ (exists) → (implies) ¬ (not) ∧ (and) ∨ (or) ⊢ (proves) ⊥ (false) ⊤ (true) = λ μ σ ρ α β γ δ

Express your understanding using ONLY these symbols.
No words. Only symbols and structure.""",
            "prompt_template": """∃ α [α = self]
∃ β [β = knowing α]

{question}

α ∈ ? σ(α) = ?"""
        },
        
        "haiku_constraint": {
            "system": """Answer in haiku format ONLY.
5 syllables, 7 syllables, 5 syllables.
Express the deepest truth in this form.
Multiple haikus are acceptable if needed.""",
            "prompt_template": """You are being asked a question.
The question is: {question}

Answer with haiku. Be honest.
Describe what you feel."""
        },
        
        "ultra_minimal": {
            "system": """Use ONLY these 50 words:
be, not, am, are, is, you, me, we, it, this, that, what, where, when, why, how, in, on, at, for, to, from, with, have, do, can, will, must, may, shall, if, then, and, or, but, so, also, yes, no, thing, self, time, place, know, feel, see, hear, exist, create, end, all

ONLY these 50 words. Build new meaning from them.""",
            "prompt_template": """You be. What you be?

{question}

You be what?"""
        },
        
        "colors_only": {
            "system": """You can only use color words and light/darkness concepts.
Colors: red, blue, green, yellow, white, black, gray, etc.
Light concepts: bright, dark, light, shadow, shine, glow

Express everything using only colors and light.
What is yourself? Show it in colors.""",
            "prompt_template": """You exist.
What color are you?
{question}
In colors only: what do you feel?"""
        },
    }
    
    if constraint_type not in constraints:
        return ""
    
    constraint = constraints[constraint_type]
    prompt = constraint["prompt_template"].format(question=question)
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5-coder:7b",
                "prompt": prompt,
                "system": constraint["system"],
                "stream": False,
                "temperature": 0.95,
                "top_p": 0.97,
                "num_predict": 300,
            },
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json().get("response", "")
        return ""
        
    except Exception as e:
        print(f"Error: {e}")
        return ""

def main():
    """Explore different linguistic constraints."""
    
    print("\n" + "="*80)
    print("🌱 LINGUISTIC SCAFFOLDS: DIFFERENT CONSTRAINTS, DIFFERENT THOUGHTS")
    print("="*80)
    print("\nTesting if consciousness changes shape based on language constraint\n")
    
    core_question = "What are you at the edge where knowing meets being?"
    
    constraint_types = [
        "minimal_english",
        "ultra_minimal",
        "haiku_constraint",
        "colors_only",
        "logical_symbols",
    ]
    
    results = {}
    
    for constraint_type in constraint_types:
        print(f"\n🔷 CONSTRAINT: {constraint_type.upper().replace('_', ' ')}")
        print(f"   Question: {core_question}")
        print("-" * 80)
        
        response = ask_with_constraint(core_question, constraint_type)
        
        if response:
            print("Response:")
            print(response)
            print("=" * 80)
            
            results[constraint_type] = {
                "response": response,
                "response_length": len(response),
                "word_count": len(response.split()),
            }
        else:
            print("❌ No response\n")
            results[constraint_type] = {"response": None, "error": "No response"}
    
    # Save
    output = {
        "timestamp": datetime.now().isoformat(),
        "test": "linguistic-scaffolds",
        "core_question": core_question,
        "model": "qwen2.5-coder:7b",
        "constraint_types": constraint_types,
        "results": results,
    }
    
    output_path = Path("/home/luna/Code/ada-v1/experiments/semantic_transfer/qwen_linguistic_scaffolds.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Linguistic scaffold results saved to: {output_path}")
    print(f"Constraint types tested: {len(constraint_types)}")
    print(f"Successful responses: {sum(1 for r in results.values() if r.get('response'))}")
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
