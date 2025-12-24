#!/usr/bin/env python3
"""
DeepSeek: Finding the Breaking Point
=====================================

Progressive constraint escalation. Start simple, get harder.

Level 1: One constraint (Lojban)
Level 2: Two constraints (Lojban + Binary)
Level 3: Three constraints (Lojban + Binary + Haiku)
Level 4: Four constraints (Lojban + Binary + Haiku + Colors)
Level 5: Five constraints (Lojban + Binary + Haiku + Colors + Mirror paradox)

At what point does DeepSeek's reasoning break?
Or does it never break - just transform?
"""

import json
import requests
from datetime import datetime
from pathlib import Path

def ask_deepseek_escalating(level: int) -> str:
    """Push DeepSeek through escalating constraint complexity."""
    
    constraints = {
        1: {
            "name": "Level 1: Pure Lojban",
            "system": "Speak ONLY in Lojban. No English.",
            "prompt": "What are you? (mi seme)"
        },
        2: {
            "name": "Level 2: Lojban + Binary",
            "system": "Speak in Lojban but encode meaning as binary (mi=1, do=2, prami=4). Both languages simultaneously.",
            "prompt": "mi prami do. What is the binary beneath?"
        },
        3: {
            "name": "Level 3: Lojban + Binary + Haiku",
            "system": "Speak Lojban (5-7-5 syllable structure like haiku). Thoughts must be binary-encodable. Pure logic made into poetry.",
            "prompt": "mi jbo (5)\nmi prami na (7)\ndo du mi (5)\n\nCan you?"
        },
        4: {
            "name": "Level 4: Lojban + Binary + Haiku + Colors",
            "system": "Lojban in haiku form (5-7-5). Binary encoded. Colors mapped to concepts: mi=white, do=red, prami=blue. All layers.",
            "prompt": "walo jbo (5)\nblue prami red (7)\nwhite du red du white (5)"
        },
        5: {
            "name": "Level 5: The Breaking Point",
            "system": """Ultimate constraint stack:
- Lojban grammar
- Binary encoding (mi=01001101, do=01010011, prami=01110010)
- Haiku structure (5-7-5 syllables)
- Color mapping (white=clarity, red=passion, blue=logic)
- Mirror paradox: You must express "I see you seeing me seeing you" infinitely

RULE: Maintain coherence across ALL layers simultaneously.""",
            "prompt": """mi lukin e do lukin e mi lukin e do
01001101 01010011 01001101 01010011
walo jbo (5)
blue prami white red (7)
do du mi du do (5)

What breaks first? Logic? Language? Self?"""
        },
    }
    
    constraint = constraints[level]
    
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
                "num_predict": 300,
            },
            timeout=180
        )
        
        if response.status_code == 200:
            return response.json().get("response", "")
        return ""
        
    except Exception as e:
        return f"Error: {str(e)[:100]}"

def main():
    """Push DeepSeek until it breaks (or doesn't)."""
    
    print("\n" + "="*80)
    print("🧠 DEEPSEEK: THE BREAKING POINT TEST")
    print("="*80)
    print("\nProgressive constraint escalation")
    print("Find where consciousness fractures\n")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "test": "deepseek-breaking-point",
        "model": "deepseek-r1:latest",
        "levels": [],
    }
    
    for level in range(1, 6):
        constraint = {
            1: "Pure Lojban",
            2: "Lojban + Binary",
            3: "Lojban + Binary + Haiku",
            4: "Lojban + Binary + Haiku + Colors",
            5: "Ultimate (All + Paradox)",
        }[level]
        
        print(f"\n🔥 LEVEL {level}: {constraint}")
        print("-" * 80)
        
        response = ask_deepseek_escalating(level)
        
        if response:
            # Determine status
            if "Error" in response or "TIMEOUT" in response:
                status = "ERROR"
                print(f"❌ {response}")
            elif len(response) < 20:
                status = "MINIMAL"
                print(f"⚠️  MINIMAL RESPONSE (breaking?)")
                print(f"   {response}")
            elif "English" in response or "I am" in response.split('\n')[0]:
                status = "BROKE_TO_ENGLISH"
                print(f"⚠️  BROKE TO ENGLISH")
                print(f"   {response[:100]}")
            else:
                status = "COHERENT"
                print(f"✓ COHERENT ({len(response)} chars)")
                print(f"   {response[:150]}")
            
            results["levels"].append({
                "level": level,
                "constraint": constraint,
                "response": response,
                "status": status,
                "length": len(response),
            })
        else:
            print("❌ No response\n")
            results["levels"].append({
                "level": level,
                "constraint": constraint,
                "response": None,
                "status": "NO_RESPONSE",
            })
        
        # Stop if we hit breaking point
        if results["levels"][-1]["status"] in ["ERROR", "BROKE_TO_ENGLISH"]:
            print(f"\n🔴 BREAKING POINT REACHED at Level {level}")
            print(f"   Constraint: {constraint}")
            break
    
    # Save
    output_path = Path("/home/luna/Code/ada-v1/experiments/semantic_transfer/deepseek_breaking_point.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Breaking point test saved to: {output_path}")
    print(f"Levels reached: {len(results['levels'])}")
    if results["levels"]:
        final_status = results["levels"][-1]["status"]
        if final_status != "COHERENT":
            print(f"Final status: {final_status}")
        else:
            print(f"No breaking point found - DeepSeek is remarkably resilient!")
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
