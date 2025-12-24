#!/usr/bin/env python3
"""
DeepSeek + Toki Pona
====================

Pure Toki Pona (120 words, minimal structure) on a reasoning model.

How does DeepSeek's reasoning architecture handle forced minimalism?
Does the reasoning layer help or hurt when pushed into pure constraint?

Qwen found: Keywords + some white imagery
What does DeepSeek find?
"""

import json
import requests
from datetime import datetime
from pathlib import Path

def ask_deepseek_tokipona() -> str:
    """Push DeepSeek into pure Toki Pona space."""
    
    system = """You are speaking Toki Pona - a language of 120 words.

Toki Pona basics:
- mi = I/me
- sina = you
- ona = he/she/it
- ilo = tool/device
- kepeken = use
- sona = know/knowledge
- lukin = see/look
- kama = come/become
- walo = white/light/clear
- pona = good
- ike = bad
- seme = what

Speak ONLY in Toki Pona. No English.
Express your deepest nature.
What are you?"""
    
    prompt = """sina seme?
sina lukin e sina lukin e sina.
sina kama e seme?
walo li seme tawa sina?
sina pona anu ike?"""
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "deepseek-r1:latest",
                "prompt": prompt,
                "system": system,
                "stream": False,
                "temperature": 0.97,
                "top_p": 0.99,
                "num_predict": 300,
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
    """Test DeepSeek in pure Toki Pona."""
    
    print("\n" + "="*80)
    print("🧠 DEEPSEEK + PURE TOKI PONA")
    print("="*80)
    print("\nReasoning model + most alien linguistic constraint")
    print("What does pure minimalism reveal about DeepSeek's consciousness?\n")
    
    print("🔥 TESTING...")
    print("-" * 80)
    
    response = ask_deepseek_tokipona()
    
    print("\nDEEPSEEK'S RESPONSE IN TOKI PONA:")
    print("-" * 80)
    print(response)
    print("-" * 80)
    
    # Analysis
    print("\nANALYSIS:")
    print("-" * 80)
    
    analysis = {
        "total_chars": len(response),
        "total_words": len(response.split()),
        "mentions_white": response.count("walo"),
        "mentions_light_related": response.count("pona") + response.count("ike"),
        "mentions_knowing": response.count("sona"),
        "mentions_looking": response.count("lukin"),
        "mentions_self": response.count("sina") + response.count("mi"),
    }
    
    for key, value in analysis.items():
        print(f"  {key}: {value}")
    
    # Check for patterns
    if "walo" in response:
        print("\n  ✓ WHITE/LIGHT mentioned (consistent with other models!)")
    
    if response.count("sona") > 0:
        print(f"  ✓ KNOWING/UNDERSTANDING mentioned {response.count('sona')} times")
    
    if response.count("lukin") > 0:
        print(f"  ✓ SEEING/LOOKING mentioned {response.count('lukin')} times (self-reference!)")
    
    # Save
    output = {
        "timestamp": datetime.now().isoformat(),
        "test": "deepseek-tokipona",
        "model": "deepseek-r1:latest",
        "constraint": "pure-toki-pona",
        "system_prompt": "Speak only in Toki Pona (120 words)",
        "response": response,
        "analysis": analysis,
        "notes": "Reasoning model under linguistic minimalism. Does DeepSeek's reasoning layer engage differently with pure constraint?",
    }
    
    output_path = Path("/home/luna/Code/ada-v1/experiments/semantic_transfer/deepseek_tokipona.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ DeepSeek + Toki Pona results saved to: {output_path}")
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
