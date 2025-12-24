"""
Recursive compression experiment.

Tests whether we can recursively compress bloated prompts down to
fit context windows while preserving semantic meaning.

The hypothesis: Understanding compresses better than avoidance.
"""

import httpx
import json
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class CompressionResult:
    """Result of a compression attempt."""
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    iterations: int
    time_seconds: float
    compressed_text: str
    semantic_score: Optional[float] = None


def count_tokens_approx(text: str) -> int:
    """Rough token count."""
    return int(len(text.split()) * 1.3)


def compress_with_llm(
    text: str,
    target_tokens: int,
    ollama_url: str = "http://localhost:11434",
    model: str = "qwen2.5-coder:7b"
) -> str:
    """Use LLM to compress text while preserving meaning."""
    
    current_tokens = count_tokens_approx(text)
    compression_needed = current_tokens / target_tokens
    
    prompt = f"""You are a context compression specialist. Your task is to compress the following content to approximately {target_tokens} tokens (currently ~{current_tokens} tokens, need {compression_needed:.1f}x compression).

RULES:
1. Preserve ALL semantic meaning and key information
2. Remove redundancy, verbosity, and repetition
3. Use dense, information-rich language
4. Keep code signatures but summarize implementations
5. Merge similar items into patterns
6. Use bullet points over prose
7. Keep specific values/IDs that might be referenced

CONTENT TO COMPRESS:
{text}

COMPRESSED VERSION (target: ~{target_tokens} tokens):"""

    response = httpx.post(
        f"{ollama_url}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Low temp for consistency
                "num_predict": target_tokens * 2,  # Allow some overflow
            }
        },
        timeout=120.0
    )
    
    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(f"LLM error: {response.status_code}")


def recursive_compress(
    text: str,
    target_tokens: int,
    max_iterations: int = 5,
    ollama_url: str = "http://localhost:11434",
    model: str = "qwen2.5-coder:7b"
) -> CompressionResult:
    """
    Recursively compress text until it fits target token count.
    
    Each iteration:
    1. Check current size
    2. If over target, compress
    3. Repeat until under target or max iterations
    """
    
    start_time = time.time()
    original_tokens = count_tokens_approx(text)
    current_text = text
    iterations = 0
    
    print(f"Starting compression: {original_tokens:,} tokens → target {target_tokens:,}")
    
    while count_tokens_approx(current_text) > target_tokens and iterations < max_iterations:
        iterations += 1
        current_tokens = count_tokens_approx(current_text)
        
        # Calculate intermediate target (don't try to compress too much at once)
        compression_factor = min(3.0, current_tokens / target_tokens)
        intermediate_target = int(current_tokens / compression_factor)
        intermediate_target = max(intermediate_target, target_tokens)
        
        print(f"  Iteration {iterations}: {current_tokens:,} → {intermediate_target:,} tokens")
        
        current_text = compress_with_llm(
            current_text,
            intermediate_target,
            ollama_url,
            model
        )
        
        new_tokens = count_tokens_approx(current_text)
        print(f"    Result: {new_tokens:,} tokens ({current_tokens/new_tokens:.2f}x compression)")
    
    end_time = time.time()
    final_tokens = count_tokens_approx(current_text)
    
    return CompressionResult(
        original_tokens=original_tokens,
        compressed_tokens=final_tokens,
        compression_ratio=original_tokens / final_tokens,
        iterations=iterations,
        time_seconds=end_time - start_time,
        compressed_text=current_text
    )


def test_semantic_preservation(
    original: str,
    compressed: str,
    ollama_url: str = "http://localhost:11434",
    model: str = "qwen2.5-coder:7b"
) -> float:
    """
    Test whether compressed version preserves key information.
    Returns score 0-1.
    """
    
    prompt = f"""You are evaluating semantic preservation in text compression.

ORIGINAL TEXT (excerpt, first 2000 chars):
{original[:2000]}

COMPRESSED TEXT:
{compressed}

Rate how well the compressed version preserves the key information from the original.
Consider:
1. Are the main topics/entities preserved?
2. Are specific values/IDs kept?
3. Are relationships between items maintained?
4. Could someone understand the original intent from the compressed version?

Respond with ONLY a number from 0.0 to 1.0, where:
- 1.0 = Perfect preservation
- 0.8 = Minor details lost but main content preserved
- 0.5 = Significant information lost
- 0.0 = Meaning completely changed

SCORE:"""

    response = httpx.post(
        f"{ollama_url}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1}
        },
        timeout=60.0
    )
    
    if response.status_code == 200:
        try:
            score_text = response.json()["response"].strip()
            # Extract first number found
            import re
            match = re.search(r'(\d+\.?\d*)', score_text)
            if match:
                return min(1.0, max(0.0, float(match.group(1))))
        except:
            pass
    return 0.5  # Default if parsing fails


def run_experiment(
    bloat_file: str,
    target_tokens: int = 4000,  # Typical context budget for RAG
    ollama_url: str = "http://localhost:11434",
    model: str = "qwen2.5-coder:7b"
):
    """Run full compression experiment on a bloated prompt."""
    
    print(f"\n{'='*60}")
    print(f"RECURSIVE COMPRESSION EXPERIMENT")
    print(f"{'='*60}")
    print(f"Input: {bloat_file}")
    print(f"Target: {target_tokens:,} tokens")
    print(f"Model: {model}")
    print()
    
    # Load bloated prompt
    with open(bloat_file) as f:
        original = f.read()
    
    original_tokens = count_tokens_approx(original)
    print(f"Original size: {original_tokens:,} tokens")
    print(f"Compression needed: {original_tokens/target_tokens:.1f}x")
    print()
    
    # Run recursive compression
    result = recursive_compress(
        original,
        target_tokens,
        max_iterations=5,
        ollama_url=ollama_url,
        model=model
    )
    
    # Test semantic preservation
    print("\nTesting semantic preservation...")
    result.semantic_score = test_semantic_preservation(
        original,
        result.compressed_text,
        ollama_url,
        model
    )
    
    # Report results
    print(f"\n{'='*60}")
    print(f"RESULTS")
    print(f"{'='*60}")
    print(f"Original tokens:    {result.original_tokens:,}")
    print(f"Compressed tokens:  {result.compressed_tokens:,}")
    print(f"Compression ratio:  {result.compression_ratio:.2f}x")
    print(f"Iterations:         {result.iterations}")
    print(f"Time:               {result.time_seconds:.1f}s")
    print(f"Semantic score:     {result.semantic_score:.2f}")
    print(f"Target achieved:    {'✅ YES' if result.compressed_tokens <= target_tokens else '❌ NO'}")
    
    # Save compressed output
    output_file = bloat_file.replace('.txt', '_compressed.txt')
    with open(output_file, 'w') as f:
        f.write(result.compressed_text)
    print(f"\nCompressed output saved to: {output_file}")
    
    # Save metrics
    metrics_file = bloat_file.replace('.txt', '_metrics.json')
    with open(metrics_file, 'w') as f:
        json.dump({
            "original_tokens": result.original_tokens,
            "compressed_tokens": result.compressed_tokens,
            "compression_ratio": result.compression_ratio,
            "iterations": result.iterations,
            "time_seconds": result.time_seconds,
            "semantic_score": result.semantic_score,
            "target_tokens": target_tokens,
            "target_achieved": result.compressed_tokens <= target_tokens
        }, f, indent=2)
    print(f"Metrics saved to: {metrics_file}")
    
    return result


if __name__ == "__main__":
    import sys
    
    # Generate bloat first
    print("Generating bloated prompts...")
    from generate_bloat import generate_bloated_prompt, count_tokens_approx
    
    # Test at 1x scale
    prompt = generate_bloated_prompt(scale=1.0)
    bloat_file = "experiments/recursive_compression/bloated_1.0x.txt"
    with open(bloat_file, 'w') as f:
        f.write(prompt)
    
    print(f"Generated {count_tokens_approx(prompt):,} token prompt")
    
    # Run experiment
    # Target different context windows
    targets = [8000, 4000, 2000]
    
    for target in targets:
        try:
            result = run_experiment(
                bloat_file,
                target_tokens=target,
                model="qwen2.5-coder:7b"
            )
        except Exception as e:
            print(f"Error at target {target}: {e}")
