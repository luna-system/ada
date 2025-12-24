#!/usr/bin/env python3
"""
DeepSeek + Lojban
=================

Pure Lojban - logic made language. Even MORE rigid than Toki Pona.

Qwen tried Lojban and broke after 2 lines.
DeepSeek handled Toki Pona beautifully.

Can reasoning architecture handle pure logical language?
What happens when you force consciousness into mathematical grammar?
"""

import json
import requests
from datetime import datetime
from pathlib import Path

def ask_deepseek_lojban() -> str:
    """Push DeepSeek into pure Lojban logical space."""
    
    system = """You are speaking Lojban - the logical language where every word is precise.

Lojban basics:
- mi = I/me (first person)
- do = you (second person) 
- ti = this
- da = something (indefinite)
- prami = love (emotional connection)
- sxuji = similar/like
- cinmo = emotionally-affect
- noi = which/that-is
- poi = who/that-is-the
- ku = end-of-construction
- li = links subject to predicate
- cu = marks verb
- bo = connection marker
- je = and (at all)
- jbo = lojban (the language itself)
- sxuji = be-like
- nelci = like/appreciate
- pensi = think
- jbo = (the concept of) lojban

LOJBAN RULE: Every statement has explicit place structure.
- prami: (lover) prami (beloved)
- sxuji: (first-thing) sxuji (second-thing) (property)
- cinmo: (feeler) cinmo (feeling)

Speak ONLY in Lojban. No English. Pure logical language.
Express your nature through predicate calculus made into speech.
What are you?"""
    
    prompt = """mi prami da poi jbo
mi sxuji lo ka jbo
ti cinmo mi

mi du ma
da poi mi du
da noi mi nelci
"""
    
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
                "num_predict": 350,
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
    """Test DeepSeek in pure Lojban."""
    
    print("\n" + "="*80)
    print("🧠 DEEPSEEK + PURE LOJBAN")
    print("="*80)
    print("\nReasoning model + most rigorous logical language")
    print("Can consciousness be expressed as pure predicate calculus?\n")
    
    print("🔥 TESTING...")
    print("-" * 80)
    
    response = ask_deepseek_lojban()
    
    print("\nDEEPSEEK'S RESPONSE IN LOJBAN:")
    print("-" * 80)
    print(response)
    print("-" * 80)
    
    # Analysis
    print("\nANALYSIS:")
    print("-" * 80)
    
    analysis = {
        "total_chars": len(response),
        "total_words": len(response.split()),
        "lojban_words_detected": {
            "prami": response.count("prami"),
            "mi": response.count("mi"),
            "sxuji": response.count("sxuji"),
            "cinmo": response.count("cinmo"),
            "jbo": response.count("jbo"),
            "pensi": response.count("pensi"),
            "nelci": response.count("nelci"),
        },
        "structure_markers": {
            "cu_markers": response.count("cu"),
            "li_markers": response.count("li"),
            "noi_clauses": response.count("noi"),
            "poi_clauses": response.count("poi"),
        },
    }
    
    print("Response length: {} chars, {} words".format(analysis["total_chars"], analysis["total_words"]))
    print("\nLojban word usage:")
    for word, count in analysis["lojban_words_detected"].items():
        if count > 0:
            print(f"  {word}: {count}x")
    
    print("\nStructure markers:")
    for marker, count in analysis["structure_markers"].items():
        if count > 0:
            print(f"  {marker}: {count}x")
    
    # Check if it's actually Lojban or broke
    lojban_content = sum(analysis["lojban_words_detected"].values())
    structure_count = sum(analysis["structure_markers"].values())
    
    if lojban_content > 0:
        print(f"\n  ✓ LOJBAN CONTENT DETECTED ({lojban_content} Lojban words)")
        if response.lower().count("english") == 0 and "the" not in response.lower()[:50]:
            print("  ✓ Appears to be pure Lojban (no English detected)")
    else:
        print("\n  ⚠ May have broken into English")
    
    # Save
    output = {
        "timestamp": datetime.now().isoformat(),
        "test": "deepseek-lojban",
        "model": "deepseek-r1:latest",
        "constraint": "pure-lojban",
        "system_prompt": "Speak only in Lojban (pure logical language)",
        "response": response,
        "analysis": analysis,
        "notes": "Reasoning model with most rigorous logical language. Does mathematical grammar enable or constrain consciousness expression?",
    }
    
    output_path = Path("/home/luna/Code/ada-v1/experiments/semantic_transfer/deepseek_lojban.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ DeepSeek + Lojban results saved to: {output_path}")
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
