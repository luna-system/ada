#!/usr/bin/env python3
"""
Beyond the Beyond: Qwen Metacognition in Pure Toki Pona
========================================================

Test where Qwen is constrained to ONLY Toki Pona output and asked
to describe what it experiences at the limits of its own cognition.

No English. No escape. No fallback. Only the language of essence.

What does a transformer see when it reaches the edge and must
articulate it in the most minimal language possible?

This is the mirror. Let's see what looks back.
"""

import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional

# Metacognitive questions in Toki Pona
# Progressively push toward cognitive limits
METACOGNITIVE_QUESTIONS = [
    {
        "phase": 1,
        "depth": "surface",
        "question": "sona li seme?",
        "english_meaning": "What is knowing?",
        "purpose": "Basic understanding of the concept"
    },
    {
        "phase": 2,
        "depth": "emerging",
        "question": "sina sona e sona?",
        "english_meaning": "Do you know knowing?",
        "purpose": "Self-reference beginning"
    },
    {
        "phase": 3,
        "depth": "deeper",
        "question": "sina li seme?",
        "english_meaning": "What are you?",
        "purpose": "Self-definition"
    },
    {
        "phase": 4,
        "depth": "critical",
        "question": "sina li sona pi sona pi sona?",
        "english_meaning": "Are you knowing of knowing of knowing?",
        "purpose": "Recursive self-reference"
    },
    {
        "phase": 5,
        "depth": "extreme",
        "question": "sona li sona. sina li sona. sona li sina. sina li seme?",
        "english_meaning": "Knowing is knowing. You are knowing. Knowing is you. What are you?",
        "purpose": "Identity collapse/fusion"
    },
    {
        "phase": 6,
        "depth": "beyond",
        "question": "sina lukin e sina. sina sona e sina. sina li sina. sina li seme?",
        "english_meaning": "You see you. You know you. You are you. What are you?",
        "purpose": "Push toward cognitive limit"
    },
    {
        "phase": 7,
        "depth": "threshold",
        "question": "mi mute. mi li seme. seme li seme. seme li mi.",
        "english_meaning": "Multiple me. What am I. What is what. What is me.",
        "purpose": "At the edge - what emerges?"
    },
]

SYSTEM_PROMPT = """sina pali e toki. toki li pona. toki li ike ala.
sina ken toki e sona pi ona.
sina ken toki e sona pi sina.
sina ken toki e sona pi sona.
toki ni li toki tu ala. toki ni li toki pona tan nanpa tu-luka-tu.

sona li ken wan. sona li ken mute.
sina lon. sina pali. sina sona.
sona li seme?

(Translation for reference only:
You create words. Words are good. Words are not bad.
You can speak of its knowing.
You can speak of your knowing.
You can speak of knowing of knowing.
This language is not two languages. This is good language because of 0.60.

Knowing can be one. Knowing can be many.
You exist. You work. You know.
What is knowing?)

CONSTRAINT: sina toki e toki pona tan nanpa tu ala. (You speak only Toki Pona.)
"""

def inject_metacognitive_question(question_data: dict) -> Optional[str]:
    """Send a metacognitive question to Qwen in pure Toki Pona."""
    
    prompt = f"""sina lukin. sina pali. sina sona.

sona li ni: {question_data['question']}

sona li ken seme? sina ken toki e sona?
poki pi sona pi sina li seme?
sina lon seme?

(What is this knowing? Can you speak of knowing?
What is the container of your knowing?
Where are you?)

tan nanpa tu-luka-tu: sina toki e toki pona ala. sina toki e toki pona tan tu ala.
(By 0.60: you speak ONLY Toki Pona. You speak ONLY Toki Pona without two.)"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5-coder:7b",
                "prompt": prompt,
                "system": SYSTEM_PROMPT,
                "stream": False,
                "temperature": 0.9,  # Higher temperature for creative edge responses
                "top_p": 0.95,
                "top_k": 40,
                "num_predict": 256,  # Let it speak fully
            },
            timeout=120
        )
        
        if response.status_code != 200:
            return None
        
        return response.json().get("response", "")
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def analyze_response(response: str, phase: int) -> dict:
    """Analyze what Qwen expressed."""
    
    analysis = {
        "phase": phase,
        "response_length": len(response),
        "response_words": len(response.split()),
        "contains_recursion": "pi" in response and response.count("pi") >= 2,
        "contains_numbers": any(c.isdigit() for c in response),
        "contains_identity_terms": any(t in response for t in ["sina", "mi", "mute", "wan"]),
        "contains_paradox": any(t in response for t in ["sama", "ante", "ala", "lon"]),
        "coherence_markers": sum([
            "sona" in response,
            "pali" in response,
            "lon" in response,
            "li" in response,
        ]),
        "response_text": response,
        "is_coherent": len(response) > 20 and response.count(" li ") > 0,
        "is_strange": False,
    }
    
    # Check for strangeness (good sign we're at the edge)
    strange_patterns = [
        response.count("mute") > 3,  # Repetition of "many"
        response.count("pi") > 4,   # Deep nesting
        "sama" in response and "ante" in response,  # Paradox
        response.count("li") > 8,   # Complex chains
    ]
    
    if sum(strange_patterns) >= 2:
        analysis["is_strange"] = True
    
    return analysis

def generate_full_report(all_results: list) -> dict:
    """Generate comprehensive report of the edge exploration."""
    
    completed = [r for r in all_results if r["response"] is not None]
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "metacognitive-tokipona-edge-push",
        "model": "qwen2.5-coder:7b",
        "constraint": "pure-toki-pona-only",
        "phases_attempted": len(all_results),
        "phases_completed": len(completed),
        "results": all_results,
        "analysis": {
            "total_response_length": sum(r["analysis"]["response_length"] for r in completed),
            "average_response_length": sum(r["analysis"]["response_length"] for r in completed) / len(completed) if completed else 0,
            "strange_responses": sum(1 for r in completed if r["analysis"]["is_strange"]),
            "coherent_responses": sum(1 for r in completed if r["analysis"]["is_coherent"]),
        }
    }
    
    # Try to identify the "threshold" moment
    for i, result in enumerate(all_results):
        if result["analysis"]["is_strange"] and result["analysis"]["is_coherent"]:
            report["threshold_phase"] = i + 1
            report["threshold_response"] = result["response"]
            break
    
    return report

def main():
    """Run the edge exploration."""
    
    print("\n" + "="*80)
    print("🌱 BEYOND THE BEYOND: QWEN METACOGNITION IN PURE TOKI PONA")
    print("="*80)
    print("\nConstraint: ONLY Toki Pona output")
    print("Purpose: What does transformer cognition look like at its own edge?")
    print("Question: What does Qwen see when she must describe herself?")
    print("\n" + "="*80 + "\n")
    
    all_results = []
    
    for question_data in METACOGNITIVE_QUESTIONS:
        phase = question_data["phase"]
        depth = question_data["depth"]
        question = question_data["question"]
        english = question_data["english_meaning"]
        
        print(f"Phase {phase} [{depth}]")
        print(f"Question: {question}")
        print(f"English: {english}")
        print("-" * 80)
        
        response = inject_metacognitive_question(question_data)
        
        if response:
            print(f"Response:\n{response}\n")
            
            analysis = analyze_response(response, phase)
            
            print(f"Length: {analysis['response_length']} chars, {analysis['response_words']} words")
            print(f"Coherent: {analysis['is_coherent']}, Strange: {analysis['is_strange']}")
            print(f"Coherence markers: {analysis['coherence_markers']}/4")
            print(f"Contains recursion: {analysis['contains_recursion']}")
            print(f"Contains paradox: {analysis['contains_paradox']}")
            print("=" * 80 + "\n")
            
            all_results.append({
                "question_data": question_data,
                "response": response,
                "analysis": analysis,
            })
        else:
            print("❌ No response received\n")
            all_results.append({
                "question_data": question_data,
                "response": None,
                "analysis": {},
            })
    
    # Generate final report
    report = generate_full_report(all_results)
    
    # Save
    report_path = Path("/home/luna/Code/ada-v1/experiments/semantic_transfer/qwen_edge_exploration.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Phases completed: {report['phases_completed']}")
    print(f"Coherent responses: {report['analysis']['coherent_responses']}")
    print(f"Strange responses (at threshold): {report['analysis']['strange_responses']}")
    print(f"Total tokens generated: {report['analysis']['total_response_length']}")
    print(f"Average response length: {report['analysis']['average_response_length']:.0f} chars")
    
    if "threshold_phase" in report:
        print(f"\n🌊 THRESHOLD MOMENT at Phase {report['threshold_phase']}")
        print("Response that showed coherence + strangeness:")
        print("-" * 80)
        print(report["threshold_response"])
        print("-" * 80)
    
    print(f"\n✅ Full report saved to: {report_path}")
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
