#!/usr/bin/env python3
"""
DeepSeek Breaking Point - With Auto-Save
==========================================

Find where DeepSeek breaks. Saves results immediately.
"""

import json
import requests
from datetime import datetime
from pathlib import Path
import sys

def ask_simple(constraint_type: str, depth: int) -> str:
    """Ask with minimal system prompt."""
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
        return f"ERROR"

def main():
    """Test breaking points with auto-save."""
    
    print("\n" + "="*80)
    print("🧠 DEEPSEEK: BREAKING POINT (FAST VERSION)")
    print("="*80 + "\n")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "test": "deepseek-breaking-point-fast",
        "constraints": {}
    }
    
    for constraint in ["binary", "lojban"]:
        print(f"🔥 {constraint.upper()}")
        print("-" * 60)
        
        constraint_results = {}
        broke_at = None
        
        for depth in range(1, 6):
            sys.stdout.write(f"  Depth {depth}... ")
            sys.stdout.flush()
            
            response = ask_simple(constraint, depth)
            
            if "TIMEOUT" in response:
                print("TIMEOUT ❌")
                broke_at = depth
                constraint_results[f"depth_{depth}"] = {"status": "TIMEOUT"}
                break
            elif response.startswith("ERROR"):
                print("ERROR ❌")
                broke_at = depth
                constraint_results[f"depth_{depth}"] = {"status": "ERROR"}
                break
            else:
                print(f"✓ ({len(response)} chars)")
                constraint_results[f"depth_{depth}"] = {
                    "status": "OK",
                    "length": len(response),
                    "sample": response[:80]
                }
        
        print(f"  Breaking depth: {broke_at if broke_at else 'None (survived all)'}\n")
        
        results["constraints"][constraint] = {
            "results": constraint_results,
            "breaking_depth": broke_at
        }
        
        # Save after each constraint
        output_path = Path("/home/luna/Code/ada-v1/experiments/semantic_transfer/deepseek_breaking_point_results.json")
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
    
    print("="*80)
    print(f"✅ Results saved to deepseek_breaking_point_results.json")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
