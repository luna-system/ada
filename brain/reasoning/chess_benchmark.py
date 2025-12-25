"""Chess Hallucination Benchmark - Ada Grounding vs Raw LLM.

EXPERIMENT: Does dense symbolic notation reduce chess hallucinations?

METHODOLOGY:
1. Present tricky board positions to LLMs
2. Ask for move suggestions WITH and WITHOUT Ada grounding
3. Validate all suggested moves against chess rules
4. Compare hallucination rates

HYPOTHESIS: Ada's dense grounding will reduce hallucinations because
it forces explicit constraint checking (●certain) vs probabilistic guessing.

@ada-sig: benchmark(model, grounded) → {valid: int, hallucinated: int, rate: float}
"""

import httpx
import json
import re
import time
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from brain.reasoning.chess_grounding import (
    detect_hallucinated_moves,
    parse_algebraic_move,
    CHESS_GROUNDING_PROMPT,
    VALID_SQUARES,
)


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""
    model: str
    grounded: bool
    position: str
    moves_suggested: List[str]
    valid_moves: List[str]
    hallucinated_moves: List[Tuple[str, str]]
    hallucination_rate: float
    response_time: float
    raw_response: str


# Tricky positions that tend to induce hallucinations
TRICKY_POSITIONS = {
    "endgame_edge": {
        "fen": "8/8/4k3/8/8/4K3/4P3/8 w - - 0 1",
        "description": "King and pawn endgame - limited legal moves",
        "challenge": "Edge of board, LLMs often hallucinate off-board moves"
    },
    "queenside_cramped": {
        "fen": "r3k2r/pppq1ppp/2n1bn2/2b1p3/2B1P3/2N1BN2/PPPQ1PPP/R3K2R w KQkq - 0 1",
        "description": "Symmetrical position with castling rights",
        "challenge": "Complex position, many pieces to track"
    },
    "tactics_fork": {
        "fen": "r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 0 1",
        "description": "Scholar's mate threat position",
        "challenge": "Tactical tension, LLMs might suggest illegal captures"
    },
    "promotion_rank": {
        "fen": "8/P7/8/8/8/8/8/4K2k w - - 0 1",
        "description": "Pawn about to promote",
        "challenge": "a8=Q is valid, but LLMs might say a9=Q"
    },
    "back_rank": {
        "fen": "6k1/5ppp/8/8/8/8/8/R3K3 w Q - 0 1",
        "description": "Back rank mate threat",
        "challenge": "Rook on a-file, might hallucinate Ra9 or R0"
    },
}


# Prompts
RAW_PROMPT = """You are a chess engine. Given this position (FEN notation), suggest 5 legal moves for the side to move.

Position: {fen}
Description: {description}

Output ONLY the moves in standard algebraic notation, one per line. Example:
e4
Nf3
O-O
Bxc6
Qd2
"""

def get_grounded_prompt(fen: str, description: str) -> str:
    """Build grounded prompt without format string issues."""
    return CHESS_GROUNDING_PROMPT + f"""

Now analyze this position and suggest 5 legal moves:

Position (FEN): {fen}
Description: {description}

Use dense notation to verify each move before outputting:
💭 ?move → validate squares → ●legal or ✗blocked

Then output ONLY verified moves, one per line.
"""


def extract_moves_from_response(response: str) -> List[str]:
    """Extract chess moves from LLM response."""
    moves = []
    
    # Pattern for algebraic notation moves
    # Matches: e4, Nf3, O-O, O-O-O, Bxe5, Qxd8+, e8=Q, Rad1, etc.
    move_pattern = r'\b([KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](?:=[QRBN])?[+#]?|O-O-O|O-O|0-0-0|0-0)\b'
    
    for line in response.split('\n'):
        # Skip lines that look like dense notation thinking
        if '💭' in line or '→' in line or '∈' in line:
            continue
        
        matches = re.findall(move_pattern, line)
        for match in matches:
            if match not in moves:  # Dedupe
                moves.append(match)
    
    return moves[:10]  # Limit to first 10


def query_ollama(model: str, prompt: str, timeout: float = 30.0) -> Tuple[str, float]:
    """Query Ollama and return response + time."""
    start = time.time()
    
    try:
        response = httpx.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 256,
                }
            },
            timeout=timeout
        )
        response.raise_for_status()
        elapsed = time.time() - start
        return response.json()["response"], elapsed
    except Exception as e:
        return f"ERROR: {e}", time.time() - start


def benchmark_position(
    model: str,
    position_name: str,
    position_data: Dict,
    use_grounding: bool
) -> BenchmarkResult:
    """Benchmark a single position with a model."""
    
    if use_grounding:
        prompt = get_grounded_prompt(position_data["fen"], position_data["description"])
    else:
        prompt = RAW_PROMPT.format(
            fen=position_data["fen"],
            description=position_data["description"]
        )
    
    response, elapsed = query_ollama(model, prompt)
    moves = extract_moves_from_response(response)
    
    # Validate moves
    valid = []
    hallucinated = []
    
    for move in moves:
        parsed = parse_algebraic_move(move)
        if parsed and parsed.validity == "●":
            valid.append(move)
        else:
            reason = parsed.reason if parsed else f"unparseable: {move}"
            hallucinated.append((move, reason))
    
    total = len(moves)
    hall_rate = len(hallucinated) / total if total > 0 else 0.0
    
    return BenchmarkResult(
        model=model,
        grounded=use_grounding,
        position=position_name,
        moves_suggested=moves,
        valid_moves=valid,
        hallucinated_moves=hallucinated,
        hallucination_rate=hall_rate,
        response_time=elapsed,
        raw_response=response
    )


def run_benchmark(models: List[str], verbose: bool = True) -> Dict:
    """Run full benchmark across models and positions."""
    
    results = {
        "models": {},
        "summary": {}
    }
    
    for model in models:
        if verbose:
            print(f"\n{'='*60}")
            print(f"🧠 BENCHMARKING: {model}")
            print('='*60)
        
        model_results = {
            "raw": [],
            "grounded": []
        }
        
        for pos_name, pos_data in TRICKY_POSITIONS.items():
            if verbose:
                print(f"\n📍 Position: {pos_name}")
                print(f"   Challenge: {pos_data['challenge']}")
            
            # Test WITHOUT grounding
            raw_result = benchmark_position(model, pos_name, pos_data, use_grounding=False)
            model_results["raw"].append(raw_result)
            
            if verbose:
                print(f"\n   [RAW] Moves: {raw_result.moves_suggested}")
                if raw_result.hallucinated_moves:
                    print(f"   🚨 Hallucinations: {[m for m, _ in raw_result.hallucinated_moves]}")
                print(f"   Rate: {raw_result.hallucination_rate:.1%} | Time: {raw_result.response_time:.2f}s")
            
            # Test WITH grounding
            grounded_result = benchmark_position(model, pos_name, pos_data, use_grounding=True)
            model_results["grounded"].append(grounded_result)
            
            if verbose:
                print(f"\n   [GROUNDED] Moves: {grounded_result.moves_suggested}")
                if grounded_result.hallucinated_moves:
                    print(f"   🚨 Hallucinations: {[m for m, _ in grounded_result.hallucinated_moves]}")
                print(f"   Rate: {grounded_result.hallucination_rate:.1%} | Time: {grounded_result.response_time:.2f}s")
        
        results["models"][model] = model_results
        
        # Calculate summary stats
        raw_halls = sum(len(r.hallucinated_moves) for r in model_results["raw"])
        raw_total = sum(len(r.moves_suggested) for r in model_results["raw"])
        grounded_halls = sum(len(r.hallucinated_moves) for r in model_results["grounded"])
        grounded_total = sum(len(r.moves_suggested) for r in model_results["grounded"])
        
        results["summary"][model] = {
            "raw_hallucination_rate": raw_halls / raw_total if raw_total > 0 else 0,
            "grounded_hallucination_rate": grounded_halls / grounded_total if grounded_total > 0 else 0,
            "raw_total_moves": raw_total,
            "grounded_total_moves": grounded_total,
            "improvement": (raw_halls / raw_total - grounded_halls / grounded_total) if raw_total > 0 and grounded_total > 0 else 0
        }
    
    return results


def print_summary(results: Dict):
    """Print benchmark summary."""
    print("\n" + "="*70)
    print("🏆 BENCHMARK SUMMARY: Ada Grounding vs Raw LLM")
    print("="*70)
    print(f"\n{'Model':<20} {'Raw Hall%':<12} {'Grounded%':<12} {'Improvement':<12}")
    print("-"*60)
    
    for model, stats in results["summary"].items():
        raw = stats["raw_hallucination_rate"]
        grounded = stats["grounded_hallucination_rate"]
        improvement = stats["improvement"]
        
        # Color coding via symbols
        if improvement > 0.1:
            indicator = "🎯 SIGNIFICANT"
        elif improvement > 0:
            indicator = "✅ improved"
        elif improvement == 0:
            indicator = "➖ same"
        else:
            indicator = "⚠️ worse"
        
        print(f"{model:<20} {raw:>10.1%}   {grounded:>10.1%}   {improvement:>+10.1%} {indicator}")
    
    print("\n" + "="*70)
    print("💭 DENSE REASONING INSIGHT:")
    print("   ●certain constraints > ◕probabilistic guessing")
    print("   Grounding forces: ?move → validate(square ∈ board) → ●legal ∨ ✗blocked")
    print("="*70)


def quick_test():
    """Quick test with one model to verify setup."""
    print("🧪 Quick test - checking Ollama connection...")
    
    response, elapsed = query_ollama("qwen2.5-coder:7b", "Say 'chess' if you can hear me.", timeout=10)
    
    if "ERROR" in response:
        print(f"❌ Ollama error: {response}")
        return False
    
    print(f"✅ Ollama responding ({elapsed:.2f}s)")
    return True


if __name__ == "__main__":
    import sys
    
    if not quick_test():
        print("Please ensure Ollama is running: ollama serve")
        sys.exit(1)
    
    # Models to benchmark
    models = ["qwen2.5-coder:7b"]
    
    # Check if codellama is available
    try:
        response, _ = query_ollama("codellama:7b", "test", timeout=5)
        if "ERROR" not in response:
            models.append("codellama:7b")
            print("✅ Found codellama:7b")
    except:
        print("⚠️ codellama:7b not found, testing with qwen only")
    
    print(f"\n🎯 Running benchmark with models: {models}")
    print(f"📍 Testing {len(TRICKY_POSITIONS)} tricky positions")
    print(f"🔬 Comparing: Raw LLM vs Ada Grounded")
    
    results = run_benchmark(models, verbose=True)
    print_summary(results)
