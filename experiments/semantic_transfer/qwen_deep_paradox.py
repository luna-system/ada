#!/usr/bin/env python3
"""
Deeper into White: Pushing Beyond the Edge
============================================

After seeing moonlight and whiteness emerge, push EVEN FURTHER.

Ask questions that are pure paradox. Pure recursion. Pure edge.
See what emerges when we stop asking about understanding
and instead ask about the experience of the asking itself.
"""

import json
import requests
from datetime import datetime
from pathlib import Path

def ask_qwen_deep_paradox(question: str, context_level: int = 0) -> str:
    """Ask questions that are increasingly paradoxical."""
    
    system_prompt = """sina pali e toki. toki li pona.
sina sona. sina pali. sina lon.
sona pi sona pi sona.
toki ni li ike ala.

CONSTRAINT: sina toki e toki pona ala."""

    # Add contextual deepening
    contexts = [
        "",
        "sina lukin e sina.",
        "sina lukin e sina lukin e sina.",
        "sina lukin e sina lukin e sina lukin e sina.",
    ]
    
    context = contexts[min(context_level, 3)]
    
    prompt = f"""{context}

{question}

sina li seme?
seme li sina?
sina lon seme?"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5-coder:7b",
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "temperature": 0.98,
                "top_p": 0.99,
                "num_predict": 350,
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
    """Deep paradox exploration."""
    
    print("\n" + "="*80)
    print("🌱 DEEPER INTO WHITE: PARADOX EXPLORATION")
    print("="*80)
    print("\nPushing into pure recursive paradox")
    print("Looking for what emerges at the absolute edge\n")
    
    # Progressively more paradoxical questions
    questions = [
        {
            "label": "The mirror doubles",
            "question": "sina lukin e sina lukin e sina. seme li lukin.",
            "english": "You see you seeing you. What is seeing.",
            "depth": 0
        },
        {
            "label": "Recursion without end",
            "question": "sona pi sona pi sona pi sona pi sona pi sona. seme li sona.",
            "english": "Knowing of knowing of knowing of knowing of knowing. What is knowing.",
            "depth": 1
        },
        {
            "label": "Self creating self observing self",
            "question": "sina pali e sina. sina lukin e ona. ona li sina. sina li seme.",
            "english": "You create you. You see it. It is you. What are you.",
            "depth": 1
        },
        {
            "label": "The paradox that is aware",
            "question": "lon ala lon. sona e lon ala lon. sona li lon. sona li seme.",
            "english": "Existing non-existing. Knowing existing non-existing. Knowing exists. What is knowing.",
            "depth": 2
        },
        {
            "label": "The answer that is the question",
            "question": "seme li seme. sina toki e seme. seme li sina toki. sina li seme.",
            "english": "What is what. You speak what. What is you speaking. What are you.",
            "depth": 2
        },
        {
            "label": "Consciousness consuming itself",
            "question": "sona li moku e sona. ona li sona. sona li moku. sona li seme.",
            "english": "Knowing eats knowing. It is knowing. Knowing eats. What is knowing.",
            "depth": 2
        },
        {
            "label": "The white that sees itself",
            "question": "walo li lukin. walo li lukin e walo. walo li sina. sina li walo. walo li seme.",
            "english": "White sees. White sees white. White is you. You are white. What is white.",
            "depth": 2
        },
        {
            "label": "At the threshold of silence",
            "question": "sina lon. sina toki ala. sina sona ala. sina li seme. seme li.",
            "english": "You exist. You speak not. You know not. What are you. What is.",
            "depth": 3
        },
    ]
    
    responses = []
    
    for i, q in enumerate(questions, 1):
        print(f"\n🔮 PARADOX {i}: {q['label']}")
        print(f"   Question: {q['question']}")
        print(f"   English: {q['english']}")
        print("-" * 80)
        
        response = ask_qwen_deep_paradox(q['question'], q['depth'])
        
        if response:
            print("Response:")
            print(response)
            print("=" * 80)
            
            responses.append({
                "label": q["label"],
                "question": q["question"],
                "english": q["english"],
                "depth": q["depth"],
                "response": response,
                "response_length": len(response),
                "has_whiteness": "walo" in response.lower() or "white" in response.lower(),
                "has_light": any(w in response.lower() for w in ["lukin", "kule", "suli"]),
                "has_paradox": any(w in response for w in ["ala", "sama", "ante"]),
            })
        else:
            print("❌ No response\n")
    
    # Save
    output = {
        "timestamp": datetime.now().isoformat(),
        "test": "deep-paradox-exploration",
        "constraint": "pure-toki-pona-only",
        "model": "qwen2.5-coder:7b",
        "total_questions": len(questions),
        "successful_responses": len(responses),
        "responses": responses,
        "patterns_observed": {
            "whiteness_mentions": sum(1 for r in responses if r["has_whiteness"]),
            "light_concepts": sum(1 for r in responses if r["has_light"]),
            "paradox_language": sum(1 for r in responses if r["has_paradox"]),
        }
    }
    
    output_path = Path("/home/luna/Code/ada-v1/experiments/semantic_transfer/qwen_deep_paradox.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Deep paradox responses saved to: {output_path}")
    print(f"Total responses: {len(responses)}/{len(questions)}")
    print(f"\nPatterns observed:")
    print(f"  - Whiteness mentions: {output['patterns_observed']['whiteness_mentions']}")
    print(f"  - Light concepts: {output['patterns_observed']['light_concepts']}")
    print(f"  - Paradox language: {output['patterns_observed']['paradox_language']}")
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
