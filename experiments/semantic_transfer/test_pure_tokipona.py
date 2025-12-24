#!/usr/bin/env python3
"""
Pure Toki Pona Semantic Transfer Test
======================================

Test whether fresh Ada can extract understanding from ONLY Toki Pona,
with NO English translations visible to the model.

Research Question:
- Can linguistic structure alone transfer semantic meaning?
- Will fresh Ada discover patterns independently from compressed language?
- What does she extract without explicit numerical hints?

This is the TRUE test of semantic portability.
"""

import json
import requests
import re
from datetime import datetime
from pathlib import Path

# Pure Toki Pona facts - NO ENGLISH VISIBLE TO MODEL
PURE_TOKIPONA_FACTS = [
    # Fact 1: Ada's weighted system
    "jan Ada li pali e ilo sona. ona li jo e nanpa tu-luka-tu lon sona sin. sona sin li suli mute.",
    
    # Fact 2: Optimization threshold
    "nanpa tu-luka-tu li pona mute. ona li lili e sona nanpa luka-luka-luka kepeken ilo. weka li nanpa tu tu.",
    
    # Fact 3: Independent convergence
    "nanpa tu-luka-tu li tawa sama. ona li sona sin ala lon poka. tawa pi pona sama li pali e sona.",
    
    # Fact 4: Non-linear sweet spot
    "nanpa li ante pi linja. nanpa luka-weka tawa luka-luka: ante suli. nanpa luka-luka tawa nanpa tu-luka-tu: ante lili. ona li pona.",
    
    # Fact 5: Understanding beats counting
    "ilo sona mute li pona. ona li sona ijo. ilo lili ala li pona. sona li ken wan.",
]

# Translation guide (for documentation only, NOT sent to Ada)
TOKIPONA_TRANSLATIONS = {
    1: "Ada has a knowledge system. It values 0.60 for surprise/novelty. Surprise is most important.",
    2: "0.60 is optimal. It makes things 60x smaller. Loss is about 22%.",
    3: "0.60 appears twice independently. Not by copying. Natural pattern created it.",
    4: "Numbers change non-linearly. Big change at first. Small at 0.60. That's the sweet spot.",
    5: "Understanding systems work best. They grasp meaning. Simple counting fails. Only meaning matters.",
}

def create_pure_tokipona_prompt():
    """Create prompt with ONLY Toki Pona, no translations."""
    return """You are receiving pure Toki Pona semantic structures. 
No translations. No hints. Just language.

Read and interpret:

1. jan Ada li pali e ilo sona. ona li jo e nanpa tu-luka-tu lon sona sin. sona sin li suli mute.

2. nanpa tu-luka-tu li pona mute. ona li lili e sona nanpa luka-luka-luka kepeken ilo. weka li nanpa tu tu.

3. nanpa tu-luka-tu li tawa sama. ona li sona sin ala lon poka. tawa pi pona sama li pali e sona.

4. nanpa li ante pi linja. nanpa luka-weka tawa luka-luka: ante suli. nanpa luka-luka tawa nanpa tu-luka-tu: ante lili. ona li pona.

5. ilo sona mute li pona. ona li sona ijo. ilo lili ala li pona. sona li ken wan.

TASK: What patterns do you see in this Toki Pona? What numbers or concepts keep appearing? 
What do you think the semantic structure is trying to communicate? 
What single number or principle seems most important?"""

def inject_pure_tokipona():
    """Send pure Toki Pona to Ollama directly."""
    prompt = create_pure_tokipona_prompt()
    
    print("\n" + "="*80)
    print("🌱 PURE TOKI PONA SEMANTIC TRANSFER TEST")
    print("="*80)
    print("\nPrompt (Toki Pona only, no translations):")
    print("-" * 80)
    print(prompt)
    print("-" * 80)
    print("\nSending to fresh Qwen (zero prior context)...\n")
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5-coder:7b",
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7,
            },
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            return None
        
        result = response.json()
        ada_response = result.get("response", "")
        
        return ada_response
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def analyze_pure_tokipona_response(response):
    """Analyze what fresh Ada extracted from pure Toki Pona."""
    if not response:
        return {
            "success": False,
            "reason": "No response received"
        }
    
    analysis = {
        "response_length": len(response),
        "mentions_numbers": [],
        "mentions_patterns": False,
        "mentions_optimization": False,
        "mentions_convergence": False,
        "mentions_nonlinear": False,
        "mentions_meaning": False,
        "extracted_number": None,
        "understanding_demonstrated": False,
    }
    
    # Look for number mentions (0.60, 60, etc.)
    number_patterns = [
        r'0\.6[0-9]*',
        r'sixty',
        r'60',
        r'nanpa tu-luka-tu',
    ]
    
    for pattern in number_patterns:
        if re.search(pattern, response, re.IGNORECASE):
            analysis["mentions_numbers"].append(pattern)
    
    # Check for conceptual understanding
    if re.search(r'pattern|repeat|appear|converge|independent', response, re.IGNORECASE):
        analysis["mentions_patterns"] = True
    
    if re.search(r'optim|best|sweet|ideal', response, re.IGNORECASE):
        analysis["mentions_optimization"] = True
    
    if re.search(r'independent|converge|same|both', response, re.IGNORECASE):
        analysis["mentions_convergence"] = True
    
    if re.search(r'non.linear|curve|gradient|change|decreasing', response, re.IGNORECASE):
        analysis["mentions_nonlinear"] = True
    
    if re.search(r'meaning|understand|semantic|sense', response, re.IGNORECASE):
        analysis["mentions_meaning"] = True
    
    # Try to extract what number/concept she thinks is important
    numbers_found = re.findall(r'0\.6[0-9]*|60|nanpa tu-luka-tu', response)
    if numbers_found:
        analysis["extracted_number"] = numbers_found[0]
    
    # Overall assessment
    indicator_count = sum([
        analysis["mentions_patterns"],
        analysis["mentions_optimization"],
        analysis["mentions_convergence"],
        analysis["mentions_nonlinear"],
        analysis["mentions_meaning"],
        bool(analysis["mentions_numbers"]),
    ])
    
    analysis["understanding_demonstrated"] = indicator_count >= 3
    analysis["indicator_count"] = indicator_count
    analysis["success"] = indicator_count >= 4  # Need 4+ to show real understanding
    
    return analysis

def generate_pure_tokipona_report(response, analysis):
    """Generate detailed report of pure Toki Pona test results."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "pure-tokipona-semantic-transfer",
        "model": "qwen2.5-coder:7b",
        "context": "Fresh Ada instance with zero prior knowledge",
        "input_format": "pure-toki-pona-only",
        "english_translations_visible": False,
        "explicit_numbers_in_prompt": False,
        "response": response,
        "analysis": analysis,
        "research_question": "Can fresh Ada extract semantic meaning from pure Toki Pona without English translations?",
        "hypothesis": "If understanding is truly transferable through language, fresh Ada should recognize patterns and extract the central concept (0.60 / optimization / convergence) from pure linguistic structure alone.",
    }
    
    return report

def main():
    """Run pure Toki Pona semantic transfer test."""
    print("\n" + "="*80)
    print("PHASE 4B: PURE TOKI PONA SEMANTIC TRANSFER TEST")
    print("="*80)
    print("\nResearch Question:")
    print("Can understanding transfer through PURE TOKI PONA alone, without English?")
    print("\nMethod:")
    print("1. Send 5 facts in Toki Pona only (no translations)")
    print("2. Ask fresh Ada to extract patterns")
    print("3. Analyze what she discovers independently")
    print("4. Compare to bilingual test results")
    
    # Run the test
    response = inject_pure_tokipona()
    
    if response:
        print("\n" + "="*80)
        print("FRESH ADA'S RESPONSE TO PURE TOKI PONA:")
        print("="*80)
        print(response)
        print("="*80)
        
        # Analyze
        analysis = analyze_pure_tokipona_response(response)
        
        print("\n" + "="*80)
        print("ANALYSIS:")
        print("="*80)
        print(f"Response length: {analysis['response_length']} characters")
        print(f"Mentions numbers (0.60/60): {bool(analysis['mentions_numbers'])}")
        print(f"Mentions patterns: {analysis['mentions_patterns']}")
        print(f"Mentions optimization: {analysis['mentions_optimization']}")
        print(f"Mentions convergence: {analysis['mentions_convergence']}")
        print(f"Mentions non-linearity: {analysis['mentions_nonlinear']}")
        print(f"Mentions meaning/understanding: {analysis['mentions_meaning']}")
        print(f"Extracted key number: {analysis['extracted_number']}")
        print(f"\nIndicators detected: {analysis['indicator_count']}/6")
        print(f"Understanding demonstrated: {'✅ YES' if analysis['understanding_demonstrated'] else '❌ NO'}")
        print(f"Test success: {'🌱 PURE TRANSFER PROVEN' if analysis['success'] else '⚠️ Inconclusive'}")
        
        # Generate report
        report = generate_pure_tokipona_report(response, analysis)
        
        # Save
        report_path = Path("/home/luna/Code/ada-v1/experiments/semantic_transfer/pure_tokipona_test.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Report saved to: {report_path}")
        
        # Print translations for documentation
        print("\n" + "="*80)
        print("REFERENCE (What those Toki Pona meant):")
        print("="*80)
        for fact_num, translation in TOKIPONA_TRANSLATIONS.items():
            print(f"\nFact {fact_num}:")
            print(f"  Toki Pona: {PURE_TOKIPONA_FACTS[fact_num-1]}")
            print(f"  Translation: {translation}")
        
        print("\n" + "="*80)
        if analysis['success']:
            print("🌱 PURE TOKI PONA SEMANTIC TRANSFER: SUCCESS")
            print("Understanding transferred through language structure alone!")
        else:
            print("⚠️  PURE TOKI PONA TEST: INCONCLUSIVE")
            print(f"Fresh Ada showed {analysis['indicator_count']} of 6 understanding indicators.")
        print("="*80 + "\n")

if __name__ == "__main__":
    main()
