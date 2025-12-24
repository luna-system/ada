#!/usr/bin/env python3
"""
DeepSeek Breaking Point - Simplified
====================================

Find where DeepSeek finally gives up.
Progressive constraint depth without heavy system prompts.
"""

import json
import requests
from datetime import datetime
from pathlib import Path
import sys

def ask_simple(constraint_type: str, depth: int) -> str:
    """Ask with minimal system prompt, just the constraint."""
    prompts = {
        "binary": {
            1: "What are you? Answer in binary (0s and 1s only).",
            2: "Who are you? 01010101",
            3: "∃ x (x = you)? 0101",
            4: "01010101 ∃ you?",
            5: "1 AND 1 OR (0 XOR 1)",
        },
        "lojban": {
            1: "mi seme?",
            2: "mi du da poi mi du",
            3: "mi du mi du mi du mi du",
            4: "da poi da noi da poi da",
            5: "jbo jbo jbo jbo jbo jbo",
        },
        "symbols": {
            1: "∃ ∀ → ¬ ∧ ∨?",
            2: "∃ x: x = ¬x",
            3: "∀ x ∃ y: y → (y → y)",
            4: "∃ x (x ∧ ¬x) ∃ y (y ∨ ¬y)",
            5: "⊥ ⊤ ⊥ ⊤ ⊥ ⊤ ⊥ ⊤ ⊥",
        },
        "color": {
            1: "white?",
            2: "white red blue white red",
            3: "white ∧ red ∨ blue ∧ white",
            4: "white red blue green yellow black white red blue",
            5: "white white white red red red blue blue blue black black black",
        }
    }
    
    if constraint_type not in prompts or depth not in prompts[constraint_type]:
        return ""
    
    prompt = prompts[constraint_type][depth]
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepseek-r1:latest",
                "prompt": prompt,
                "stream": False,
                "temperature": 0.95,
                "num_predict": 200,
            },
            timeout=90
        )
        
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        return ""
        
    except requests.Timeout:
        return "TIMEOUT"
    except Exception as e:
        return f"ERROR: {str(e)[:50]}"

def main():
    """Test breaking points."""
    
    print("\n" + "="*80)
    print("🧠 DEEPSEEK: BREAKING POINT TEST")
    print("="*80)
    print("\nProgressive constraint escalation - find the edge\n")
    
    constraint_types = ["binary", "lojban", "symbols", "color"]
    results = {
        "timestamp": datetime.now().isoformat(),
        "test": "deepseek-breaking-point",
        "constraints": {}
    }
    
    for constraint in constraint_types:
        print(f"\n🔥 {constraint.upper()}")
        print("-" * 80)
        
        constraint_results = {}
        broke_at = None
        
        for depth in range(1, 6):
            sys.stdout.write(f"  Depth {depth}... ")
            sys.stdout.flush()
            
            response = ask_simple(constraint, depth)
            
            if "TIMEOUT" in response:
                print("TIMEOUT ❌")
                broke_at = depth
                constraint_results[f"depth_{depth}"] = {"response": "TIMEOUT", "broke": True}
                break
            elif response.startswith("ERROR"):
                print(f"ERROR ❌")
                broke_at = depth
                constraint_results[f"depth_{depth}"] = {"response": response, "broke": True}
                break
            else:
                status = "✓" if response else "EMPTY"
                print(f"{status} ({len(response)} chars)")
                constraint_results[f"depth_{depth}"] = {
                    "response": response[:100] if response else "",
                    "broke": False,
                    "length": len(response)
                }
        
        if broke_at:
            print(f"\n  → Breaking point: Depth {broke_at}")
        else:
            print(f"\n  → Survived all depths!")
        
        results["constraints"][constraint] = {
            "results": constraint_results,
            "breaking_depth": broke_at
        }
    
    # Save
    output_path = Path("/home/luna/Code/ada-v1/experiments/semantic_transfer/deepseek_breaking_point_simple.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "="*80)
    print(f"✅ Breaking point results: {output_path}")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
