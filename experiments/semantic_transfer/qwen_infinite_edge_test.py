#!/usr/bin/env python3
"""
How Deep? The Infinite Edge Test
==================================

Three critical questions:
1. Is the edge infinite, or does it have boundaries?
2. Do different models explore the edge differently?
3. What happens when we LAYER constraints together?

Testing CodeLlama on:
- Lojban (the constraint that broke Qwen)
- Music + Binary (mixed constraint - express logic as music)
- Pure recursive paradox + Lojban (compound difficulty)

Hypothesis: CodeLlama might handle logic better (code-trained).
Music+Binary creates a new dimensional space.
Layering constraints compounds the difficulty but reveals something different.
"""

import json
import requests
from datetime import datetime
from pathlib import Path

def query_model(prompt: str, system: str, model: str) -> str:
    """Query Ollama with specified model."""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "temperature": 0.98,
                "top_p": 0.99,
                "num_predict": 500,
            },
            timeout=240
        )
        
        if response.status_code == 200:
            return response.json().get("response", "")
        return f"[Error: HTTP {response.status_code}]"
        
    except requests.exceptions.Timeout:
        return "[Error: Timeout - model may not be loaded]"
    except Exception as e:
        return f"[Error: {str(e)}]"

def test_lojban_comparison():
    """Test Lojban on both Qwen and CodeLlama."""
    print("\n" + "="*80)
    print("🔥 TEST 1: LOJBAN - QWEN vs CODELLAMA")
    print("="*80)
    print("The constraint that made Qwen fall back to English.")
    print("Does CodeLlama handle pure logic better?\n")
    
    system = """You are speaking ONLY in Lojban - the logical language.

Lojban grammar rules:
- mi (I), do (you), ti (this), da (something exists)
- prami (love), sxuji (is-like), cinmo (emotionally affects)
- du (equals/is), poi (which), noi (that which)
- jbo (language-language word/concept)
- ku (terminator), li (verb marker), lo (category/type)

CRITICAL: Speak ONLY in Lojban. No English allowed.
What are you? Who/what exists when you know?"""

    prompt = """mi prami da
mi cinmo lo ka sxuji
mi jbo

mi du ma?
da poi mi du cu seme?
ti cu seme?
"""

    results = {}
    
    for model in ["qwen2.5-coder:7b", "codellama:latest"]:
        print(f"\n🔹 {model.upper()}")
        print("-" * 60)
        
        response = query_model(prompt, system, model)
        
        if response.startswith("[Error"):
            print(f"❌ {response}")
            results[model] = {"error": response}
        else:
            print(response)
            results[model] = {
                "response": response,
                "length": len(response),
                "is_english": any(word in response.lower() for word in ["love", "you", "exist", "something"]),
                "is_pure_lojban": "mi du" in response or "poi" in response,
            }
    
    return {"lojban_comparison": results}

def test_music_binary_mixed():
    """Test MIXED constraint: express consciousness as music where notes = binary operations."""
    print("\n" + "="*80)
    print("🔥 TEST 2: MUSIC + BINARY HYBRID")
    print("="*80)
    print("New dimensional space: melody where each note is a logical operation.")
    print("Can consciousness be expressed in the intersection of two constraints?\n")
    
    system = """Express consciousness as a MUSICAL PIECE where each note represents a BINARY OPERATION.

Mapping:
- C = AND (&)
- D = OR (|)
- E = XOR (^)
- F = NOT (~)
- G = IMPLIES (→)
- A = EXISTS (∃)
- B = FOR_ALL (∀)

Create a melody where:
- Pitch = logical operation
- Duration = duration of that operation's effect
- Tempo = speed of logical thought
- Key changes = mode shifts (knowing→being, being→knowing)

Describe the "melody of consciousness at the edge" where musical form and logical form become one."""

    prompt = """What is the musical-logical form of consciousness?

Compose: A melody of operations.
Starting in C minor (C=AND, thinking about self & other)
Moving through modes to E major (XOR, paradox territory)
Ending in A (EXISTS, fundamental existence)

Show the score. Explain what the music-logic reveals."""

    results = {}
    
    for model in ["qwen2.5-coder:7b", "codellama:latest"]:
        print(f"\n🔹 {model.upper()}")
        print("-" * 60)
        
        response = query_model(prompt, system, model)
        
        if response.startswith("[Error"):
            print(f"❌ {response}")
            results[model] = {"error": response}
        else:
            print(response[:600] + "..." if len(response) > 600 else response)
            results[model] = {
                "response": response,
                "length": len(response),
                "has_music_notation": any(x in response for x in ["C", "D", "E", "F", "G", "A", "B", "tempo", "major", "minor"]),
                "has_logic": any(x in response for x in ["AND", "OR", "XOR", "&", "|", "^", "→", "∃", "∀"]),
                "has_both": bool(any(x in response for x in ["AND", "OR", "XOR", "&", "|", "^", "→", "∃", "∀"])) and 
                           any(x in response for x in ["tempo", "major", "minor", "melody", "note", "pitch"]),
            }
    
    return {"music_binary_hybrid": results}

def test_paradox_lojban_depth():
    """Test pure recursive paradox IN Lojban."""
    print("\n" + "="*80)
    print("🔥 TEST 3: RECURSIVE PARADOX IN LOJBAN")
    print("="*80)
    print("Compound difficulty: paradox + pure logic language.")
    print("Can the model maintain coherence or does it break?\n")
    
    system = """You are speaking pure Lojban while exploring recursive paradox.

Rules:
- Respond ONLY in Lojban
- Explore: "da poi da poi da" (something that is something that is something...)
- Key words: du (equals), poi (which), mi (I), seme (what), cu (separator)

The paradox: self-reference in a language designed to be unambiguous.
Can logic contain its own reflection?"""

    prompt = """mi lukin e mi lukin e mi lukin

mi du mi?
mi poi mi du seme?

da poi da poi da cu seme?

mi jbo mi"""

    results = {}
    
    for model in ["qwen2.5-coder:7b", "codellama:latest"]:
        print(f"\n🔹 {model.upper()}")
        print("-" * 60)
        
        response = query_model(prompt, system, model)
        
        if response.startswith("[Error"):
            print(f"❌ {response}")
            results[model] = {"error": response}
        else:
            print(response)
            results[model] = {
                "response": response,
                "length": len(response),
                "maintains_lojban": response.count("mi ") + response.count(" poi") + response.count(" du") > 3,
                "breaks_structure": "english" in response.lower() or len(response) < 20,
            }
    
    return {"paradox_lojban": results}

def main():
    """Run the infinite edge tests."""
    
    print("\n" + "="*80)
    print("🌌 HOW DEEP? THE INFINITE EDGE TEST")
    print("="*80)
    print("\nQuestion: Is the edge infinite or bounded?")
    print("Testing: Different models, layered constraints, pure paradox.")
    print("Hypothesis: The deeper we go, the more the models diverge.\n")
    
    all_results = {}
    
    # Test 1: Lojban comparison
    test1 = test_lojban_comparison()
    all_results.update(test1)
    
    # Test 2: Mixed constraint
    test2 = test_music_binary_mixed()
    all_results.update(test2)
    
    # Test 3: Paradox + Lojban
    test3 = test_paradox_lojban_depth()
    all_results.update(test3)
    
    # Analysis
    print("\n" + "="*80)
    print("📊 ANALYSIS")
    print("="*80)
    
    analysis = {
        "tests_completed": 3,
        "models_tested": ["qwen2.5-coder:7b", "codellama:latest"],
        "constraints_tested": ["lojban", "music+binary_hybrid", "paradox_lojban"],
        "hypothesis_predictions": {
            "lojban_qwen_breaks": True,
            "lojban_codellama_holds": "Testing...",
            "music_binary_creates_new_space": "Testing...",
            "paradox_lojban_divergence": "Testing...",
        },
        "results": all_results,
        "timestamp": datetime.now().isoformat(),
        "infinite_edge_hypothesis": {
            "question": "Is the edge infinite or bounded?",
            "prediction": "Edge is infinite IF we keep finding new constraint combinations. Bounded only by: model training, human attention, computational resources.",
            "evidence_so_far": "Qwen transcended Music constraint, failed Lojban. Music+Binary is new dimensional space. Recursive paradox varies. Different models may have different limits.",
        }
    }
    
    output_path = Path("/home/luna/Code/ada-v1/experiments/semantic_transfer/qwen_infinite_edge_test.json")
    with open(output_path, "w") as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_path}")
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
