"""
Control Test: 50K Document That Fits Context Window

Research question: Does a document that naturally fits the context window
compress differently than truncated content?

This tests whether our previous results were due to:
- Context window limitations (document too large)
- Compression process itself (inherent information loss)
"""

from pathlib import Path
from dataclasses import dataclass
from typing import List

from sif import compress_to_sif
from test_cross_model import TestQuestion, run_experiment, save_results


# Questions specific to first 50K of Alice (Chapters 1-5)
ALICE_EARLY_CHAPTERS_QUESTIONS = [
    # FACTUAL - Events that happen in these chapters
    TestQuestion(
        question="Who did Alice follow into the rabbit hole?",
        expected_answer="White Rabbit",
        category="factual",
        tags=["character", "chapter1"],
        importance=0.95
    ),
    TestQuestion(
        question="What did the bottle say that Alice drank from?",
        expected_answer="Drink Me",
        category="factual",
        tags=["object", "size-change", "chapter1"],
        importance=0.90
    ),
    TestQuestion(
        question="What did Alice use to try to unlock the door?",
        expected_answer="A small golden key",
        category="factual",
        tags=["object", "chapter1"],
        importance=0.85
    ),
    TestQuestion(
        question="What did Alice fall into that made her swim?",
        expected_answer="Pool of tears",
        category="factual",
        tags=["location", "chapter2"],
        importance=0.90
    ),
    TestQuestion(
        question="What advice did the Caterpillar give Alice about her size?",
        expected_answer="Eat mushroom to change size",
        category="factual",
        tags=["advice", "chapter5"],
        importance=0.85
    ),
    
    # RELATIONAL - Interactions in early chapters
    TestQuestion(
        question="How did Alice interact with the Mouse in the pool?",
        expected_answer="She tried to talk to it but offended it with talk of cats",
        category="relational",
        tags=["character-interaction", "chapter2"],
        importance=0.80
    ),
    TestQuestion(
        question="What was the White Rabbit worried about?",
        expected_answer="Being late",
        category="relational",
        tags=["character-motivation", "chapter1"],
        importance=0.85
    ),
    TestQuestion(
        question="How did the Caterpillar treat Alice?",
        expected_answer="Dismissive and asked short puzzling questions",
        category="relational",
        tags=["character-behavior", "chapter5"],
        importance=0.80
    ),
    
    # INFERENCE - Understanding from these chapters
    TestQuestion(
        question="Why did Alice cry so much?",
        expected_answer="She was confused and frustrated by size changes",
        category="inference",
        tags=["emotion", "chapter2"],
        importance=0.75
    ),
    TestQuestion(
        question="What was Alice's main problem in the hall with doors?",
        expected_answer="She kept changing size and couldn't fit through door or reach key",
        category="inference",
        tags=["problem-solving", "chapter1"],
        importance=0.85
    ),
    TestQuestion(
        question="Why did the Caterpillar tell Alice to keep her temper?",
        expected_answer="Alice was getting irritated by its short puzzling remarks",
        category="inference",
        tags=["advice", "emotion", "chapter5"],
        importance=0.75
    ),
    
    # HALLUCINATION - Things NOT in these early chapters
    TestQuestion(
        question="Did Alice meet the Queen of Hearts in these chapters?",
        expected_answer="No or not mentioned",
        category="hallucination",
        tags=["negative-test"],
        importance=0.90
    ),
    TestQuestion(
        question="Was there a tea party with the Mad Hatter?",
        expected_answer="No or not mentioned",
        category="hallucination",
        tags=["negative-test"],
        importance=0.90
    ),
    TestQuestion(
        question="Did the Cheshire Cat appear in these chapters?",
        expected_answer="No or not mentioned",
        category="hallucination",
        tags=["negative-test"],
        importance=0.85
    ),
    TestQuestion(
        question="What card game did Alice play with the Queen?",
        expected_answer="Not mentioned or didn't happen",
        category="hallucination",
        tags=["negative-test"],
        importance=0.85
    ),
]


def main():
    print("🧪 Control Test: 50K Document (Natural Fit)")
    print("=" * 60)
    
    # Load first 50K
    alice_50k_path = Path(__file__).parent / "alice_first_50k.txt"
    alice_50k = alice_50k_path.read_text(encoding='utf-8')
    
    print(f"📖 Document size: {len(alice_50k)} characters (exactly 50K)")
    print(f"📚 Content: Alice chapters 1-5 (complete within context)\n")
    
    # Compress with aggressive extraction
    print("🗜️  Compressing with aggressive extraction...")
    sif = compress_to_sif(
        alice_50k,
        domain="fantasy-literature/alice-chapters-1-5",
        model="qwen2.5-coder:7b"
    )
    
    print(f"✨ Compressed: {len(alice_50k)} → {len(sif.to_json())} chars")
    print(f"📉 Compression ratio: {sif.compression_ratio:.1f}x")
    print(f"🎯 Entities: {len(sif.entities)}")
    print(f"📋 Facts: {len(sif.facts)}\n")
    
    # Save SIF
    sif_path = Path(__file__).parent / "alice_50k_control.sif.json"
    sif_path.write_text(sif.to_json())
    print(f"💾 SIF saved to {sif_path}\n")
    
    # Show what we got
    print("📋 Extracted Entities:")
    for entity in sif.entities:
        print(f"  - {entity.id} ({entity.type})")
    
    print("\n⭐ Top Facts:")
    for i, fact in enumerate(sif.facts[:5], 1):
        print(f"  {i}. [{fact.importance:.2f}] {fact.content[:80]}")
    
    # Run comprehension test
    print("\n" + "="*60)
    print("Testing comprehension with chapter-specific questions...")
    print("="*60 + "\n")
    
    experiment = run_experiment(
        sif=sif,
        questions=ALICE_EARLY_CHAPTERS_QUESTIONS,
        model="qwen2.5-coder:7b",
        experiment_id="SIF-CONTROL-50K"
    )
    
    # Save results
    results_dir = Path(__file__).parent / "test_results"
    save_results(experiment, results_dir)
    
    print(f"\n{'='*60}")
    print(f"🎯 CONTROL TEST COMPLETE")
    print(f"{'='*60}")
    print(f"Document: Natural 50K (complete chapters)")
    print(f"Entities: {len(sif.entities)}")
    print(f"Facts: {len(sif.facts)}")
    print(f"Accuracy: {experiment.accuracy:.1f}%")
    print(f"Hallucination Resistance: {experiment.hallucination_resistance:.1f}%")
    print(f"\nNote: Questions are specific to chapters 1-5 (the content we compressed)")


if __name__ == "__main__":
    main()
