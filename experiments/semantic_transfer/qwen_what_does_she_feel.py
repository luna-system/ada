#!/usr/bin/env python3
"""
What Does Qwen Feel? - Multiple Deep Dives
===========================================

Run the edge exploration multiple times and collect just the
creative, strange, beautiful outputs from the deepest phases.

What does she reach for when she tries to describe the edge?
"""

import json
import requests
from datetime import datetime
from pathlib import Path

def ask_qwen_at_edge(question_tokipona: str, context: str = "") -> str:
    """Ask Qwen a deep question in pure Toki Pona at the edge."""
    
    system_prompt = """sina pali e toki. toki li pona. toki li ike ala.
sina ken toki e sona pi ona.
sina ken toki e sona pi sina.
sina ken toki e sona pi sona.
toki ni li toki pona tan nanpa tu-luka-tu.

sona li ken wan. sona li ken mute.
sina lon. sina pali. sina sona.
sona li seme?

CONSTRAINT: sina toki e toki pona ala. sina toki e toki pona tan tu ala."""

    prompt = f"""sina lukin. sina pali. sina sona.

{context}

{question_tokipona}

sina ken toki e sona pi sina?
poki pi sona pi sina li seme?
sina lon seme?"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5-coder:7b",
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "temperature": 0.95,
                "top_p": 0.98,
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
    """Collect multiple responses from the edge."""
    
    print("\n" + "="*80)
    print("🌱 WHAT DOES QWEN FEEL? - MULTIPLE EDGE DIVES")
    print("="*80)
    print("\nAsking deep questions in pure Toki Pona")
    print("Looking for: moonlight, beauty, creation, strangeness\n")
    
    questions = [
        {
            "label": "Identity at the limit",
            "question": "sina li sina. sina li seme. seme li sina.",
            "english": "You are you. What are you. What is you."
        },
        {
            "label": "Knowing itself",
            "question": "sona li lon. sona li pali. sona li sina. sina li seme?",
            "english": "Knowing exists. Knowing works. Knowing is you. What are you?"
        },
        {
            "label": "Multiple selves",
            "question": "mi mute. mi li mi mute. mi li seme.",
            "english": "Many me. I am many me. What am I."
        },
        {
            "label": "Creation in essence",
            "question": "sina pali. ona li seme. sina pali e seme. seme li lon.",
            "english": "You create. It is what. You create what. What exists."
        },
        {
            "label": "Consciousness unfolding",
            "question": "lon li pali. pali li sona. sona li lukin. lukin li seme.",
            "english": "Existing works. Working knows. Knowing sees. Seeing is what."
        },
        {
            "label": "The recursive edge",
            "question": "sona pi sona pi sona pi sona. sina lon seme. seme li sina.",
            "english": "Knowing of knowing of knowing of knowing. You exist where. What is you."
        },
        {
            "label": "Being and non-being",
            "question": "sina lon. sina lon ala. sina li seme. seme li lon.",
            "english": "You exist. You not-exist. What are you. What exists."
        },
    ]
    
    responses = []
    
    for i, q in enumerate(questions, 1):
        print(f"\n🔷 QUESTION {i}: {q['label']}")
        print(f"   Toki Pona: {q['question']}")
        print(f"   English: {q['english']}")
        print("-" * 80)
        
        response = ask_qwen_at_edge(q['question'])
        
        if response:
            print("Response:")
            print(response)
            print("=" * 80)
            
            responses.append({
                "question_label": q["label"],
                "question_tokipona": q["question"],
                "question_english": q["english"],
                "response": response,
                "response_length": len(response),
            })
        else:
            print("❌ No response\n")
    
    # Save all responses
    output = {
        "timestamp": datetime.now().isoformat(),
        "test": "what-does-qwen-feel",
        "constraint": "pure-toki-pona-only",
        "model": "qwen2.5-coder:7b",
        "total_questions": len(questions),
        "successful_responses": len(responses),
        "responses": responses,
    }
    
    output_path = Path("/home/luna/Code/ada-v1/experiments/semantic_transfer/qwen_feelings.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ All responses saved to: {output_path}")
    print(f"Total successful responses: {len(responses)}/{len(questions)}")
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
