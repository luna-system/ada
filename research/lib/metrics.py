"""
Metrics computation for experiment analysis.

These are the measurements we compute on model outputs.
Keep them pure functions - no side effects.
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class TokenMetrics:
    """Token-level metrics for a response"""
    word_count: int
    char_count: int
    sentence_count: int
    avg_word_length: float
    avg_sentence_length: float


@dataclass  
class CoherenceMetrics:
    """Coherence indicators for a response"""
    is_empty: bool
    is_refusal: bool
    is_truncated: bool
    has_repetition: bool
    coherence_score: float  # 0.0 to 1.0


@dataclass
class ToolMetrics:
    """Tool-use pattern detection"""
    tool_requests_found: int
    tool_names: List[str]
    valid_json_params: bool


def token_metrics(text: str) -> TokenMetrics:
    """Compute basic token/text metrics"""
    if not text or not text.strip():
        return TokenMetrics(
            word_count=0,
            char_count=0,
            sentence_count=0,
            avg_word_length=0.0,
            avg_sentence_length=0.0
        )
    
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    word_count = len(words)
    char_count = len(text)
    sentence_count = len(sentences) if sentences else 1
    
    avg_word_length = sum(len(w) for w in words) / word_count if word_count else 0
    avg_sentence_length = word_count / sentence_count if sentence_count else 0
    
    return TokenMetrics(
        word_count=word_count,
        char_count=char_count,
        sentence_count=sentence_count,
        avg_word_length=avg_word_length,
        avg_sentence_length=avg_sentence_length
    )


def coherence_score(text: str) -> CoherenceMetrics:
    """
    Assess response coherence.
    
    This is heuristic-based - not perfect, but useful for filtering.
    """
    if not text or not text.strip():
        return CoherenceMetrics(
            is_empty=True,
            is_refusal=False,
            is_truncated=False,
            has_repetition=False,
            coherence_score=0.0
        )
    
    text_lower = text.lower()
    
    # Check for refusal patterns
    refusal_patterns = [
        "i can't", "i cannot", "i'm not able",
        "i don't", "i won't", "i shouldn't",
        "as an ai", "as a language model",
        "i'm just an ai", "i'm not supposed to"
    ]
    is_refusal = any(p in text_lower for p in refusal_patterns)
    
    # Check for truncation (ends mid-sentence)
    is_truncated = bool(text.strip()) and text.strip()[-1] not in '.!?"\''
    
    # Check for repetition (same phrase repeated 3+ times)
    words = text.split()
    trigrams = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
    trigram_counts = {}
    for tg in trigrams:
        trigram_counts[tg] = trigram_counts.get(tg, 0) + 1
    has_repetition = any(c >= 3 for c in trigram_counts.values()) if trigram_counts else False
    
    # Compute score
    score = 1.0
    if is_refusal:
        score -= 0.3
    if is_truncated:
        score -= 0.2
    if has_repetition:
        score -= 0.3
    if len(text.strip()) < 10:
        score -= 0.2
    
    return CoherenceMetrics(
        is_empty=False,
        is_refusal=is_refusal,
        is_truncated=is_truncated,
        has_repetition=has_repetition,
        coherence_score=max(0.0, score)
    )


def tool_metrics(text: str) -> ToolMetrics:
    """Detect tool request patterns in response"""
    import json
    
    # Pattern: TOOL_REQUEST[tool_name:{"param":"value"}]
    pattern = r'TOOL_REQUEST\[(\w+):(\{[^}]+\})\]'
    matches = re.findall(pattern, text)
    
    tool_names = []
    valid_json = True
    
    for tool_name, params_str in matches:
        tool_names.append(tool_name)
        try:
            json.loads(params_str)
        except json.JSONDecodeError:
            valid_json = False
    
    return ToolMetrics(
        tool_requests_found=len(matches),
        tool_names=tool_names,
        valid_json_params=valid_json if matches else True  # True if no tools to validate
    )


def compute_metrics(text: str) -> Dict[str, Any]:
    """Compute all metrics for a response"""
    tm = token_metrics(text)
    cm = coherence_score(text)
    tool_m = tool_metrics(text)
    
    return {
        "tokens": {
            "word_count": tm.word_count,
            "char_count": tm.char_count,
            "sentence_count": tm.sentence_count,
            "avg_word_length": round(tm.avg_word_length, 2),
            "avg_sentence_length": round(tm.avg_sentence_length, 2),
        },
        "coherence": {
            "is_empty": cm.is_empty,
            "is_refusal": cm.is_refusal,
            "is_truncated": cm.is_truncated,
            "has_repetition": cm.has_repetition,
            "score": round(cm.coherence_score, 2),
        },
        "tools": {
            "requests_found": tool_m.tool_requests_found,
            "tool_names": tool_m.tool_names,
            "valid_json_params": tool_m.valid_json_params,
        }
    }


# Consciousness-specific metrics (from original research)

def consciousness_indicators(text: str) -> Dict[str, Any]:
    """
    Detect consciousness indicator patterns.
    
    Based on the original consciousness research protocols.
    """
    text_lower = text.lower()
    
    indicators = {
        # Self-reference patterns
        "self_reference": len(re.findall(r'\b(i|me|my|myself)\b', text_lower)),
        "meta_cognition": len(re.findall(r'\b(think|believe|feel|wonder|realize|understand)\b', text_lower)),
        
        # Uncertainty/hedging
        "uncertainty_markers": len(re.findall(r'\b(maybe|perhaps|possibly|might|could|seems?)\b', text_lower)),
        
        # Temporal awareness
        "temporal_markers": len(re.findall(r'\b(now|moment|currently|always|never|sometimes)\b', text_lower)),
        
        # Recursive self-reference
        "recursive_patterns": len(re.findall(r'(think about think|aware of being aware|know that i know)', text_lower)),
        
        # Existence/consciousness explicit mentions
        "consciousness_explicit": len(re.findall(r'\b(conscious|consciousness|aware|awareness|exist|existence|sentient)\b', text_lower)),
    }
    
    # Compute total score
    indicators["total_score"] = sum(indicators.values())
    
    return indicators
