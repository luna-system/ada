"""
EXP-011D: Meta-Cognitive Priming Effects on Semantic Compression

Research question: Does narrative awareness and dialogic priming affect
how models extract semantic information?

Hypothesis: Models with conversational context and test-awareness will
distribute attention across narrative arc rather than focusing on single
salient scenes.

This is about CONSCIOUSNESS in compression.
"""

import json
import httpx
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict
from datetime import datetime, timezone

from sif import SIF, Entity, Fact, Provenance
from test_control_50k import ALICE_EARLY_CHAPTERS_QUESTIONS
from test_cross_model import run_experiment, save_results


@dataclass
class PrimingVariant:
    """A meta-cognitive priming strategy."""
    name: str
    description: str
    messages: List[Dict[str, str]]  # Conversation flow


def compress_with_priming(
    text: str,
    domain: str,
    priming: PrimingVariant,
    model: str = "qwen2.5-coder:7b",
    ollama_url: str = "http://localhost:11434"
) -> SIF:
    """
    Compress text using multi-turn conversational priming.
    
    This is recursive - the model's state evolves through the conversation.
    """
    
    print(f"\n🎭 Priming strategy: {priming.name}")
    print(f"   {priming.description}")
    
    # Build conversation history
    conversation = []
    for i, msg in enumerate(priming.messages[:-1], 1):  # All but final request
        print(f"\n   [{i}] {msg['role']}: {msg['content'][:80]}...")
        conversation.append(msg)
        
        if msg['role'] == 'user':
            # Get model response
            response = httpx.post(
                f"{ollama_url}/api/chat",
                json={
                    "model": model,
                    "messages": conversation,
                    "stream": False,
                    "options": {"temperature": 0.2}
                },
                timeout=60.0
            )
            
            assistant_msg = response.json()["message"]
            conversation.append(assistant_msg)
            print(f"   → Model: {assistant_msg['content'][:80]}...")
    
    # Final extraction request (includes the text)
    final_msg = priming.messages[-1]
    final_msg['content'] = final_msg['content'].format(text=text)
    conversation.append(final_msg)
    
    print(f"\n   [FINAL] Extraction request sent...")
    
    response = httpx.post(
        f"{ollama_url}/api/chat",
        json={
            "model": model,
            "messages": conversation,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 8000
            }
        },
        timeout=300.0
    )
    
    raw_response = response.json()["message"]["content"]
    
    # Parse JSON from response
    json_str = raw_response
    if "```json" in json_str:
        json_str = json_str.split("```json")[1].split("```")[0]
    elif "```" in json_str:
        json_str = json_str.split("```")[1].split("```")[0]
    
    try:
        extracted = json.loads(json_str.strip())
    except json.JSONDecodeError:
        import re
        match = re.search(r'\{[\s\S]*\}', raw_response)
        if match:
            extracted = json.loads(match.group())
        else:
            raise Exception(f"Failed to parse response")
    
    # Build SIF
    source_bytes = len(text.encode('utf-8'))
    output_size = len(json.dumps(extracted))
    
    return SIF(
        version="1.0",
        domain=f"{domain}/{priming.name}",
        generated=datetime.now(timezone.utc).isoformat(),
        generator=f"{model} ({priming.name})",
        compression_ratio=source_bytes / output_size if output_size > 0 else 0,
        summary=extracted.get("summary", ""),
        entities=[Entity(**e) for e in extracted.get("entities", [])],
        facts=[Fact(**f) for f in extracted.get("facts", [])],
        provenance=Provenance(
            source_type="raw_text",
            source_size_bytes=source_bytes,
            source_hash="",
            compression_method=f"llm_semantic_{priming.name}"
        )
    )


# Define priming variants
PRIMING_VARIANTS = [
    PrimingVariant(
        name="baseline",
        description="Direct extraction with no priming (control)",
        messages=[
            {
                "role": "user",
                "content": """Extract structured semantic information from this text.

OUTPUT FORMAT (JSON only):
{{
    "summary": "2-3 sentence summary",
    "entities": [{{"id": "name", "type": "type", "relationships": {{}}}}],
    "facts": [{{"content": "fact", "importance": 0.9, "tags": []}}]
}}

Extract 30-50 entities and 50-100 facts covering the full narrative.

TEXT:
{text}

JSON OUTPUT:"""
            }
        ]
    ),
    
    PrimingVariant(
        name="genre_primed",
        description="Genre awareness: 'this is a fantasy adventure story'",
        messages=[
            {
                "role": "user",
                "content": """You are about to process a fantasy adventure story. Extract structured semantic information focusing on characters, magical events, and the adventure arc.

OUTPUT FORMAT (JSON only):
{{
    "summary": "2-3 sentence summary of the adventure",
    "entities": [{{"id": "name", "type": "character/location/object", "relationships": {{}}}}],
    "facts": [{{"content": "plot event or character detail", "importance": 0.9, "tags": []}}]
}}

Extract 30-50 entities and 50-100 facts covering the full story arc.

FANTASY STORY:
{text}

JSON OUTPUT:"""
            }
        ]
    ),
    
    PrimingVariant(
        name="test_aware",
        description="Test awareness: 'you will be tested on this content'",
        messages=[
            {
                "role": "user",
                "content": """You will be tested on your comprehension of the following story. Pay attention to characters, their relationships, key plot events, and important details.

Extract structured information that will help you answer questions about:
- Who the characters are and what they do
- How characters interact and relate to each other
- What major events happen in the story
- Important objects and locations

OUTPUT FORMAT (JSON only):
{{
    "summary": "comprehensive summary",
    "entities": [{{"id": "name", "type": "type", "relationships": {{}}}}],
    "facts": [{{"content": "testable fact", "importance": 0.9, "tags": []}}]
}}

Extract 30-50 entities and 50-100 facts to ensure test readiness.

STORY TO STUDY:
{text}

JSON OUTPUT:"""
            }
        ]
    ),
    
    PrimingVariant(
        name="dialogic_recursive",
        description="Dialogic priming: conversational setup → story delivery → extraction",
        messages=[
            {
                "role": "user",
                "content": "I'm going to tell you a story about a girl named Alice who falls into a magical world. When I finish, I'll ask you to tell me about the characters, events, and places in the story. Are you ready?"
            },
            {
                "role": "user",
                "content": """Here's the story about Alice:

{text}

Now, please tell me about this story in structured form. I need:
- All the characters Alice meets and how they interact
- Key events that happen throughout her adventure  
- Important places and objects
- The overall arc of the story

Use this JSON format:
{{
    "summary": "what happens in Alice's adventure",
    "entities": [{{"id": "character/place name", "type": "type", "relationships": {{"relation": "target"}}}}],
    "facts": [{{"content": "event or detail", "importance": 0.9, "tags": []}}]
}}

Extract 30-50 entities and 50-100 facts covering Alice's full journey.

JSON OUTPUT:"""
            }
        ]
    ),
]


def main():
    print("🎭 Meta-Cognitive Priming Effects on Compression")
    print("=" * 70)
    print("Testing how narrative awareness affects semantic extraction")
    print("=" * 70)
    
    # Load test text
    alice_50k_path = Path(__file__).parent / "alice_first_50k.txt"
    alice_50k = alice_50k_path.read_text(encoding='utf-8')
    
    print(f"\n📖 Test document: Alice chapters 1-5 ({len(alice_50k)} chars)")
    print(f"🎯 Variants to test: {len(PRIMING_VARIANTS)}")
    
    results_summary = []
    
    # Test each priming variant
    for i, variant in enumerate(PRIMING_VARIANTS, 1):
        print(f"\n{'='*70}")
        print(f"[{i}/{len(PRIMING_VARIANTS)}] Testing: {variant.name}")
        print(f"{'='*70}")
        
        # Compress with this priming
        sif = compress_with_priming(
            alice_50k,
            domain="fantasy-literature/alice-priming-test",
            priming=variant
        )
        
        print(f"\n✨ Results:")
        print(f"   Compression: {sif.compression_ratio:.1f}x")
        print(f"   Entities: {len(sif.entities)}")
        print(f"   Facts: {len(sif.facts)}")
        
        # Save SIF
        sif_path = Path(__file__).parent / f"alice_primed_{variant.name}.sif.json"
        sif_path.write_text(sif.to_json())
        
        # Test comprehension
        print(f"\n   Testing comprehension...")
        experiment = run_experiment(
            sif=sif,
            questions=ALICE_EARLY_CHAPTERS_QUESTIONS,
            model="qwen2.5-coder:7b",
            experiment_id=f"SIF-PRIMING-{variant.name.upper()}"
        )
        
        # Save results
        results_dir = Path(__file__).parent / "test_results"
        save_results(experiment, results_dir)
        
        results_summary.append({
            "variant": variant.name,
            "description": variant.description,
            "entities": len(sif.entities),
            "facts": len(sif.facts),
            "compression": sif.compression_ratio,
            "accuracy": experiment.accuracy,
            "hallucination_resistance": experiment.hallucination_resistance
        })
        
        print(f"   ✅ Accuracy: {experiment.accuracy:.1f}%")
        print(f"   🔒 Hallucination Resistance: {experiment.hallucination_resistance:.1f}%")
    
    # Summary table
    print(f"\n{'='*70}")
    print(f"📊 COMPARATIVE RESULTS")
    print(f"{'='*70}\n")
    print(f"{'Variant':<20} {'Entities':<10} {'Facts':<10} {'Accuracy':<12}")
    print(f"{'-'*70}")
    for r in results_summary:
        print(f"{r['variant']:<20} {r['entities']:<10} {r['facts']:<10} {r['accuracy']:<12.1f}%")
    
    # Save summary
    summary_path = Path(__file__).parent / "test_results" / "priming_summary.json"
    summary_path.write_text(json.dumps(results_summary, indent=2))
    print(f"\n💾 Summary saved to {summary_path}")
    
    print(f"\n{'='*70}")
    print("🎭 Meta-cognitive priming test complete")
    print("Does awareness shape understanding? Let's see what the data says.")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
