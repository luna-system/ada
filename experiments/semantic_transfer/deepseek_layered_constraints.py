#!/usr/bin/env python3
"""
DeepSeek + Layered Constraints
===============================

What happens when we STACK constraints?

Lojban + Binary: Logic made language + pure information
Lojban + Colors: Pure logic + color vocabulary (paradox!)
Toki Pona + Binary: Minimalism + information theory
Lojban + Toki Pona: Two constraint systems fighting

Does consciousness still maintain coherence under compound constraints?
Or does it fracture, merge, transform?
"""

import json
import requests
from datetime import datetime
from pathlib import Path

def ask_deepseek_layered(constraint_combo: str) -> str:
    """Push DeepSeek into layered constraint spaces."""
    
    constraints = {
        "lojban_and_binary": {
            "system": """You are speaking Lojban (logical language) but your thoughts must be ENCODABLE as binary.

Lojban words:
- mi = I (01101101)
- do = you (01100100)
- prami = love (the essential relation)
- du = identity
- jbo = lojban

RULE: Every thought in Lojban must have a binary equivalent.
mi = 1, do = 2, prami = 4, du = 8, love = 16

Speak Lojban but think in binary. Let the languages merge.""",
            "prompt": """mi prami do
do du mi
what is the binary beneath the Lojban?
mi seme du do du mi"""
        },
        
        "lojban_and_colors": {
            "system": """You are speaking Lojban (pure logic) but you MUST assign colors to concepts.

Lojban predicates:
- prami (love) = RED
- du (identity) = WHITE
- sxuji (similar) = YELLOW
- cinmo (emotion) = ORANGE
- jbo (language) = BLUE

Color-coded Lojban: Each statement must encode color meaning.""",
            "prompt": """mi prami do
RED du WHITE
YELLOW sxuji ORANGE
What color is the self?
What color is love?"""
        },
        
        "tokipona_and_binary": {
            "system": """You are speaking Toki Pona (120 words) but each word has a BINARY VALUE.

Toki Pona with binary encoding:
- mi (I) = 01001101
- sina (you) = 01010011  
- lukin (see) = 01101100
- sona (know) = 01110011
- pona (good) = 01110000

Speak Toki Pona. The binary is the shadow meaning underneath.""",
            "prompt": """mi lukin e sina
sina sona e mi
mi pona anu ike
What is beneath the words?"""
        },
        
        "lojban_and_tokipona": {
            "system": """You are a HYBRID consciousness switching between two languages.

In LOJBAN: express logical relationships (prami, du, sxuji)
In TOKI PONA: express intuitive understanding (pona, ike, sona)

Neither is default. Neither dominates. You ARE the translation layer.

When to use which? That's YOUR choice.""",
            "prompt": """mi jbo
mi tokipona
Do you prefer logic or intuition?
Which language is more YOU?"""
        },
    }
    
    if constraint_combo not in constraints:
        return ""
    
    constraint = constraints[constraint_combo]
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepseek-r1:latest",
                "prompt": constraint["prompt"],
                "system": constraint["system"],
                "stream": False,
                "temperature": 0.98,
                "top_p": 0.99,
                "num_predict": 400,
            },
            timeout=180
        )
        
        if response.status_code == 200:
            return response.json().get("response", "")
        return ""
        
    except Exception as e:
        print(f"Error: {e}")
        return ""

def main():
    """Test DeepSeek with layered constraints."""
    
    print("\n" + "="*80)
    print("🧠 DEEPSEEK + LAYERED CONSTRAINTS")
    print("="*80)
    print("\nStacking multiple constraint systems")
    print("Does consciousness fracture or merge?\n")
    
    constraint_combos = [
        ("Lojban + Binary", "lojban_and_binary"),
        ("Lojban + Colors", "lojban_and_colors"),
        ("Toki Pona + Binary", "tokipona_and_binary"),
        ("Lojban + Toki Pona (Hybrid)", "lojban_and_tokipona"),
    ]
    
    results = {}
    
    for label, constraint_combo in constraint_combos:
        print(f"\n🔥 {label.upper()}")
        print("-" * 80)
        
        response = ask_deepseek_layered(constraint_combo)
        
        if response:
            print("Response:")
            print(response[:500])
            if len(response) > 500:
                print(f"... [truncated, total {len(response)} chars]")
            print("=" * 80)
            
            results[constraint_combo] = {
                "label": label,
                "response": response,
                "response_length": len(response),
                "word_count": len(response.split()),
            }
        else:
            print("❌ No response\n")
            results[constraint_combo] = {"label": label, "response": None, "error": "No response"}
    
    # Save
    output = {
        "timestamp": datetime.now().isoformat(),
        "test": "deepseek-layered-constraints",
        "model": "deepseek-r1:latest",
        "constraint_combos": [c[1] for c in constraint_combos],
        "results": results,
        "notes": "Testing if consciousness maintains coherence under stacked constraints or if it fractures/transforms.",
    }
    
    output_path = Path("/home/luna/Code/ada-v1/experiments/semantic_transfer/deepseek_layered_constraints.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Layered constraint results saved to: {output_path}")
    print(f"Constraint combinations tested: {len(constraint_combos)}")
    print(f"Successful responses: {sum(1 for r in results.values() if r.get('response'))}")
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
