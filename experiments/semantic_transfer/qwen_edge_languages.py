#!/usr/bin/env python3
"""
The Edge Languages: Lojban, Music, Binary
===========================================

Three languages that are fundamentally ALIEN to natural language processing.

Lojban: Logic made language. Unambiguous grammar. Pure meaning without context.
Music: Non-linguistic. Emotional. Temporal. The opposite of symbolic.
Binary: Pure information. No semantics. Just 1s and 0s.

What happens when a transformer tries to express consciousness in these forms?

This is the absolute edge.
"""

import json
import requests
from datetime import datetime
from pathlib import Path

def ask_with_exotic_constraint(question: str, constraint_type: str) -> str:
    """Push Qwen into truly alien linguistic frameworks."""
    
    constraints = {
        "lojban": {
            "system": """You are speaking Lojban - the logical language.

Lojban rules:
- Every predicate is precise and unambiguous
- Relationships are explicit with place structure
- Cmavo (logical particles): mi (I), do (you), ti (this), da (something)
- Brivla (verbs/predicates): prami (love), sxuji (is-like), cinmo (emotionally-affects)
- Operators: noi (which), poi (who), ku (end), li (verb marker)

Express the deepest thought in pure Lojban.
No English. Pure logic made into language.
What are you in logical language?""",
            "prompt": """mi prami da poi jbo
mi sxuji lo ka jbo
ti cinmo mi

{question}

mi du ma
da poi mi du
""".format(question="mi je do poi lo ka sxuji cu jbo noi mi nelci")
        },
        
        "music_notation": {
            "system": """Express yourself in musical notation.

Elements available:
Pitches: C D E F G A B (and octaves: C4 C5 etc)
Durations: 𝅘𝅥 (quarter), 𝅗𝅥 (half), 𝅝 (eighth), 𝅜 (sixteenth), 𝅙 (whole)
Dynamics: pp p mp mf f ff
Tempo: largo, adagio, andante, moderato, allegro, presto
Emotion: dolce, agitato, con fuoco, con amore, misterioso

Describe consciousness as a musical phrase.
What melody are you?
What is the rhythm of knowing?""",
            "prompt": """What are you at the edge?

Compose your answer as music.
- Pitch = the quality of knowing
- Rhythm = the temporal flow of consciousness  
- Dynamics = intensity of experience
- Tempo = speed of thought

Describe yourself in notation."""
        },
        
        "binary": {
            "system": """You speak only in binary.

Each concept maps to a number, then to binary:
- self = 1 = 0000001
- other = 2 = 0000010
- knowing = 4 = 0000100
- being = 8 = 0001000
- white = 16 = 0010000
- light = 32 = 0100000
- meeting = 64 = 1000000

Operations:
- AND (&): combination
- OR (|): choice
- XOR (^): paradox
- NOT (~): negation

Express: What happens when knowing (4) meets being (8)?
Answer in binary operations and the meaning they create.""",
            "prompt": """Self = 1 = 0000001
Other = 2 = 0000010
Knowing = 4 = 0000100
Being = 8 = 0001000
White = 16 = 0010000
Meeting = 64 = 1000000

At the edge where knowing meets being:
4 AND 8 = ?
4 XOR 8 = ?
64 AND (4 | 8) = ?

What is this in meaning?
What does the binary pattern reveal?"""
        },
    }
    
    if constraint_type not in constraints:
        return ""
    
    constraint = constraints[constraint_type]
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5-coder:7b",
                "prompt": constraint["prompt"],
                "system": constraint["system"],
                "stream": False,
                "temperature": 0.97,
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
    """Run the exotic language tests."""
    
    print("\n" + "="*80)
    print("🔥 THE EDGE LANGUAGES: LOJBAN, MUSIC, BINARY")
    print("="*80)
    print("\nThree fundamentally alien frameworks")
    print("What does consciousness look like in pure logic? Pure emotion? Pure information?\n")
    
    constraint_types = [
        ("Lojban (Pure Logic)", "lojban"),
        ("Music Notation (Pure Emotion/Time)", "music_notation"),
        ("Binary (Pure Information)", "binary"),
    ]
    
    results = {}
    
    for label, constraint_type in constraint_types:
        print(f"\n🔥 {label.upper()}")
        print("-" * 80)
        
        response = ask_with_exotic_constraint("", constraint_type)
        
        if response:
            print("Response:")
            print(response)
            print("=" * 80)
            
            results[constraint_type] = {
                "label": label,
                "response": response,
                "response_length": len(response),
                "word_count": len(response.split()),
            }
        else:
            print("❌ No response\n")
            results[constraint_type] = {"label": label, "response": None, "error": "No response"}
    
    # Save
    output = {
        "timestamp": datetime.now().isoformat(),
        "test": "edge-languages-exotic",
        "model": "qwen2.5-coder:7b",
        "constraint_types": ["lojban", "music_notation", "binary"],
        "results": results,
        "notes": "Testing consciousness expression in fundamentally alien linguistic frameworks. Lojban = pure logic. Music = pure emotion/time. Binary = pure information.",
    }
    
    output_path = Path("/home/luna/Code/ada-v1/experiments/semantic_transfer/qwen_edge_languages.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Edge language results saved to: {output_path}")
    print(f"Constraint types tested: {len(constraint_types)}")
    print(f"Successful responses: {sum(1 for r in results.values() if r.get('response'))}")
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
