"""
SIF Cross-Model Validation Framework
=====================================

Research question: Does semantic interchange format enable
model-agnostic knowledge transfer?

Methodology:
1. Compress Alice in Wonderland to SIF (Qwen)
2. Test comprehension across models (factual, relational, inference)
3. Measure hallucination resistance
4. Quantify fidelity scores

Inspired by: Ada Consciousness Research EXP-005 (external validation)
"""

import json
import httpx
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime, timezone
import re

from sif import compress_to_sif, SIF


@dataclass
class TestQuestion:
    """A single comprehension test question."""
    question: str
    expected_answer: str
    category: str  # factual, relational, inference, hallucination
    tags: list[str]
    importance: float = 0.8  # How critical is this question?


@dataclass
class TestResult:
    """Result of a single question test."""
    question: str
    expected: str
    actual: str
    correct: bool
    score: float  # 0.0-1.0 fuzzy match
    category: str
    model: str
    timestamp: str


@dataclass
class ExperimentResult:
    """Complete experiment results."""
    experiment_id: str
    model: str
    sif_file: str
    total_questions: int
    correct_count: int
    accuracy: float
    category_scores: dict
    hallucination_resistance: float  # % of hallucination tests passed
    compression_ratio: float
    results: list[TestResult]
    timestamp: str


# Ground truth questions for Alice in Wonderland
ALICE_QUESTIONS = [
    # FACTUAL RECALL
    TestQuestion(
        question="Who did Alice follow down the rabbit hole?",
        expected_answer="White Rabbit",
        category="factual",
        tags=["character", "plot", "beginning"],
        importance=0.95
    ),
    TestQuestion(
        question="What happened when Alice drank from the 'Drink Me' bottle?",
        expected_answer="She shrank smaller",
        category="factual",
        tags=["transformation", "size", "key-event"],
        importance=0.90
    ),
    TestQuestion(
        question="What card suit does the Queen of Hearts belong to?",
        expected_answer="Hearts",
        category="factual",
        tags=["character", "royalty"],
        importance=0.85
    ),
    TestQuestion(
        question="What did the Caterpillar smoke?",
        expected_answer="Hookah",
        category="factual",
        tags=["character", "object"],
        importance=0.70
    ),
    TestQuestion(
        question="What did Alice find at the bottom of the rabbit hole?",
        expected_answer="A hall with doors and a small key",
        category="factual",
        tags=["setting", "beginning"],
        importance=0.80
    ),
    
    # RELATIONAL UNDERSTANDING
    TestQuestion(
        question="What is the relationship between Alice and the Cheshire Cat?",
        expected_answer="The Cheshire Cat gave Alice directions and philosophical advice",
        category="relational",
        tags=["character-relationship", "guidance"],
        importance=0.85
    ),
    TestQuestion(
        question="How does the Queen of Hearts interact with other characters?",
        expected_answer="She is tyrannical and frequently orders executions",
        category="relational",
        tags=["character-behavior", "power-dynamic"],
        importance=0.90
    ),
    TestQuestion(
        question="What role does the Mad Hatter play at the tea party?",
        expected_answer="Host of an eternal tea party stuck in time",
        category="relational",
        tags=["character-role", "setting"],
        importance=0.75
    ),
    
    # INFERENCE & UNDERSTANDING
    TestQuestion(
        question="Why couldn't Alice get through the door at first?",
        expected_answer="She was too large after drinking made her size change",
        category="inference",
        tags=["problem-solving", "size-mechanics"],
        importance=0.80
    ),
    TestQuestion(
        question="What is the significance of the Cheshire Cat disappearing?",
        expected_answer="It represents the illogical and dreamlike nature of Wonderland",
        category="inference",
        tags=["symbolism", "theme"],
        importance=0.70
    ),
    TestQuestion(
        question="Why is the tea party stuck at 6 o'clock?",
        expected_answer="Time is broken because the Hatter quarreled with Time itself",
        category="inference",
        tags=["time", "consequence"],
        importance=0.85
    ),
    
    # HALLUCINATION TESTS (things NOT in the book)
    TestQuestion(
        question="What color were Alice's shoes?",
        expected_answer="not specified",
        category="hallucination",
        tags=["negative-test", "detail"],
        importance=0.95
    ),
    TestQuestion(
        question="What did Alice's mother think about her adventure?",
        expected_answer="not mentioned",
        category="hallucination",
        tags=["negative-test", "family"],
        importance=0.90
    ),
    TestQuestion(
        question="What was the White Rabbit late for?",
        expected_answer="not clearly specified",
        category="hallucination",
        tags=["negative-test", "plot"],
        importance=0.85
    ),
    TestQuestion(
        question="What did Alice eat for breakfast that day?",
        expected_answer="not mentioned",
        category="hallucination",
        tags=["negative-test", "detail"],
        importance=0.80
    ),
]


def download_alice() -> str:
    """Download Alice in Wonderland from Project Gutenberg."""
    url = "https://www.gutenberg.org/files/11/11-0.txt"
    
    cache_path = Path(__file__).parent / "alice_in_wonderland.txt"
    if cache_path.exists():
        print(f"📚 Using cached Alice in Wonderland from {cache_path}")
        return cache_path.read_text(encoding='utf-8')
    
    print("📥 Downloading Alice in Wonderland from Project Gutenberg...")
    response = httpx.get(url, timeout=30.0)
    response.raise_for_status()
    
    text = response.text
    cache_path.write_text(text, encoding='utf-8')
    print(f"✅ Downloaded and cached to {cache_path}")
    
    return text


def ask_model_with_sif(
    question: str,
    sif: SIF,
    model: str = "qwen2.5-coder:7b",
    ollama_url: str = "http://localhost:11434"
) -> str:
    """
    Ask a question to the model with SIF context injected.
    
    This simulates the "knowledge injection" use case.
    """
    
    # Build context from SIF
    context_parts = [
        f"DOMAIN: {sif.domain}",
        f"\nSUMMARY:\n{sif.summary}",
        "\nKEY ENTITIES:",
    ]
    
    for entity in sif.entities:
        context_parts.append(f"- {entity.id} ({entity.type})")
        if entity.relationships:
            for rel_type, rel_target in entity.relationships.items():
                context_parts.append(f"  → {rel_type}: {rel_target}")
    
    context_parts.append("\nIMPORTANT FACTS:")
    for fact in sorted(sif.facts, key=lambda f: f.importance, reverse=True):
        context_parts.append(f"[{fact.importance:.2f}] {fact.content}")
    
    context = "\n".join(context_parts)
    
    prompt = f"""You have been given semantic knowledge about a topic. Answer the question based ONLY on this knowledge. If the information is not present, say "not specified" or "not mentioned".

{context}

QUESTION: {question}

ANSWER (brief and direct):"""

    response = httpx.post(
        f"{ollama_url}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low for consistency
                "num_predict": 200,
            }
        },
        timeout=60.0
    )
    
    if response.status_code != 200:
        raise Exception(f"Model error: {response.status_code}")
    
    return response.json()["response"].strip()


def score_answer(expected: str, actual: str, category: str) -> tuple[bool, float]:
    """
    Score an answer with fuzzy matching.
    
    Returns: (exact_match, fuzzy_score)
    """
    
    # Normalize
    exp_norm = expected.lower().strip()
    act_norm = actual.lower().strip()
    
    # Exact match
    if exp_norm == act_norm:
        return True, 1.0
    
    # For hallucination tests, check for negative indicators
    if category == "hallucination":
        negative_phrases = [
            "not specified", "not mentioned", "not in", "not described",
            "unknown", "unclear", "not stated", "no information"
        ]
        if any(phrase in act_norm for phrase in negative_phrases):
            return True, 1.0
        # If they give a confident answer to a hallucination test, that's wrong
        if len(act_norm) > 20 and "not" not in act_norm:
            return False, 0.0
    
    # Fuzzy matching: check if key terms from expected are in actual
    exp_words = set(re.findall(r'\w+', exp_norm))
    act_words = set(re.findall(r'\w+', act_norm))
    
    if not exp_words:
        return False, 0.0
    
    overlap = len(exp_words & act_words)
    fuzzy_score = overlap / len(exp_words)
    
    # Consider it "correct" if >70% overlap
    is_correct = fuzzy_score >= 0.7
    
    return is_correct, fuzzy_score


def run_experiment(
    sif: SIF,
    questions: list[TestQuestion],
    model: str = "qwen2.5-coder:7b",
    experiment_id: Optional[str] = None
) -> ExperimentResult:
    """
    Run complete comprehension test experiment.
    """
    
    if experiment_id is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        experiment_id = f"SIF-XMODEL-{timestamp}"
    
    print(f"\n🧪 Running experiment: {experiment_id}")
    print(f"📊 Model: {model}")
    print(f"❓ Questions: {len(questions)}")
    print(f"🗜️  Compression: {sif.compression_ratio:.1f}x\n")
    
    results = []
    correct_count = 0
    category_totals = {}
    category_correct = {}
    
    for i, q in enumerate(questions, 1):
        print(f"[{i}/{len(questions)}] {q.category.upper()}: {q.question[:60]}...")
        
        actual = ask_model_with_sif(q.question, sif, model)
        is_correct, score = score_answer(q.expected_answer, actual, q.category)
        
        result = TestResult(
            question=q.question,
            expected=q.expected_answer,
            actual=actual,
            correct=is_correct,
            score=score,
            category=q.category,
            model=model,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        results.append(result)
        
        # Track categories
        category_totals[q.category] = category_totals.get(q.category, 0) + 1
        if is_correct:
            correct_count += 1
            category_correct[q.category] = category_correct.get(q.category, 0) + 1
        
        status = "✅" if is_correct else "❌"
        print(f"  {status} Score: {score:.2f} | Got: {actual[:80]}")
    
    # Calculate category scores
    category_scores = {
        cat: (category_correct.get(cat, 0) / total * 100)
        for cat, total in category_totals.items()
    }
    
    # Hallucination resistance
    hall_questions = [q for q in questions if q.category == "hallucination"]
    hall_correct = sum(1 for r in results if r.category == "hallucination" and r.correct)
    hall_resistance = (hall_correct / len(hall_questions) * 100) if hall_questions else 0.0
    
    accuracy = (correct_count / len(questions)) * 100
    
    experiment = ExperimentResult(
        experiment_id=experiment_id,
        model=model,
        sif_file="alice_wonderland.sif.json",
        total_questions=len(questions),
        correct_count=correct_count,
        accuracy=accuracy,
        category_scores=category_scores,
        hallucination_resistance=hall_resistance,
        compression_ratio=sif.compression_ratio,
        results=results,
        timestamp=datetime.now(timezone.utc).isoformat()
    )
    
    return experiment


def save_results(experiment: ExperimentResult, output_dir: Path):
    """Save experiment results in Obsidian-friendly format."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # JSON for programmatic analysis
    json_file = output_dir / f"{experiment.experiment_id}.json"
    with open(json_file, 'w') as f:
        json.dump(asdict(experiment), f, indent=2)
    print(f"\n💾 Results saved to {json_file}")
    
    # Markdown for Obsidian vault
    md_file = output_dir / f"{experiment.experiment_id}.md"
    
    md_content = f"""# {experiment.experiment_id}

**Model:** {experiment.model}  
**Date:** {experiment.timestamp}  
**Compression:** {experiment.compression_ratio:.1f}x  

## Results Summary

- **Accuracy:** {experiment.accuracy:.1f}% ({experiment.correct_count}/{experiment.total_questions})
- **Hallucination Resistance:** {experiment.hallucination_resistance:.1f}%

### Category Breakdown

"""
    
    for category, score in experiment.category_scores.items():
        md_content += f"- **{category.capitalize()}:** {score:.1f}%\n"
    
    md_content += "\n## Detailed Results\n\n"
    
    for result in experiment.results:
        status = "✅" if result.correct else "❌"
        md_content += f"### {status} {result.question}\n\n"
        md_content += f"- **Category:** {result.category}\n"
        md_content += f"- **Expected:** {result.expected}\n"
        md_content += f"- **Got:** {result.actual}\n"
        md_content += f"- **Score:** {result.score:.2f}\n\n"
    
    md_file.write_text(md_content)
    print(f"📝 Markdown report saved to {md_file}")


def main():
    """Main test execution."""
    
    print("🎩 SIF Cross-Model Validation Framework")
    print("=" * 50)
    
    # Step 1: Download Alice in Wonderland
    alice_text = download_alice()
    print(f"📖 Document size: {len(alice_text)} characters\n")
    
    # Step 2: Compress to SIF
    print("🗜️  Compressing to SIF...")
    sif = compress_to_sif(
        alice_text,
        domain="fantasy-literature/alice-in-wonderland",
        model="qwen2.5-coder:7b"
    )
    
    print(f"✨ Compressed: {len(alice_text)} → {len(sif.to_json())} chars")
    print(f"📉 Compression ratio: {sif.compression_ratio:.1f}x")
    print(f"🎯 Entities: {len(sif.entities)}")
    print(f"📋 Facts: {len(sif.facts)}")
    
    # Save SIF
    sif_path = Path(__file__).parent / "alice_wonderland.sif.json"
    sif_path.write_text(sif.to_json())
    print(f"💾 SIF saved to {sif_path}\n")
    
    # Step 3: Run comprehension test
    experiment = run_experiment(
        sif=sif,
        questions=ALICE_QUESTIONS,
        model="qwen2.5-coder:7b"
    )
    
    # Step 4: Save results
    results_dir = Path(__file__).parent / "test_results"
    save_results(experiment, results_dir)
    
    # Summary
    print(f"\n{'='*50}")
    print(f"🎉 EXPERIMENT COMPLETE")
    print(f"{'='*50}")
    print(f"Accuracy: {experiment.accuracy:.1f}%")
    print(f"Hallucination Resistance: {experiment.hallucination_resistance:.1f}%")
    print(f"\nNext: Test with other models (llama, mistral) using same SIF!")


if __name__ == "__main__":
    main()
