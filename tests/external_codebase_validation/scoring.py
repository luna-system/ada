#!/usr/bin/env python3
"""
Scoring logic for external codebase validation.

Simple keyword-based scoring to start. Can be enhanced with:
- Semantic similarity (embeddings)
- LLM-as-judge
- Structural matching

December 19, 2025
"""

import re
from typing import Optional


def count_keyword_hits(answer: str, keywords: list[str]) -> int:
    """
    Count how many keywords appear in the answer.
    
    Case-insensitive matching with word boundary awareness.
    
    Args:
        answer: The model's answer text
        keywords: List of keywords to look for
        
    Returns:
        Number of keywords found in the answer
    """
    answer_lower = answer.lower()
    hits = 0
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        # Check for the keyword (allowing partial matches for compound words)
        if keyword_lower in answer_lower:
            hits += 1
    
    return hits


def calculate_accuracy(keyword_hits: int, keyword_total: int) -> float:
    """
    Calculate accuracy score from keyword hits.
    
    Args:
        keyword_hits: Number of keywords found
        keyword_total: Total expected keywords
        
    Returns:
        Accuracy as float 0.0-1.0
    """
    if keyword_total == 0:
        return 0.0  # No keywords expected = can't score
    
    return keyword_hits / keyword_total


def score_answer(
    answer: str, 
    expected_keywords: list[str],
    ground_truth: Optional[str] = None
) -> dict:
    """
    Score an answer comprehensively.
    
    Args:
        answer: The model's answer
        expected_keywords: Keywords that should appear
        ground_truth: Optional exact expected answer
        
    Returns:
        Dict with scoring details
    """
    keyword_hits = count_keyword_hits(answer, expected_keywords)
    keyword_total = len(expected_keywords)
    accuracy = calculate_accuracy(keyword_hits, keyword_total)
    
    result = {
        "keyword_hits": keyword_hits,
        "keyword_total": keyword_total,
        "accuracy_score": accuracy,
        "answer_length": len(answer),
        "matched_keywords": [],
        "missed_keywords": [],
    }
    
    # Track which keywords matched
    answer_lower = answer.lower()
    for kw in expected_keywords:
        if kw.lower() in answer_lower:
            result["matched_keywords"].append(kw)
        else:
            result["missed_keywords"].append(kw)
    
    # If ground truth provided, check for exact/partial match
    if ground_truth:
        gt_lower = ground_truth.lower()
        result["ground_truth_exact_match"] = answer.lower() == gt_lower
        result["ground_truth_contained"] = gt_lower in answer_lower
    
    return result


def aggregate_scores(results: list[dict]) -> dict:
    """
    Aggregate multiple scoring results into summary statistics.
    
    Args:
        results: List of score_answer() outputs
        
    Returns:
        Aggregated statistics
    """
    if not results:
        return {
            "count": 0,
            "mean_accuracy": 0.0,
            "min_accuracy": 0.0,
            "max_accuracy": 0.0,
            "total_keyword_hits": 0,
            "total_keywords": 0,
        }
    
    accuracies = [r["accuracy_score"] for r in results]
    
    return {
        "count": len(results),
        "mean_accuracy": sum(accuracies) / len(accuracies),
        "min_accuracy": min(accuracies),
        "max_accuracy": max(accuracies),
        "total_keyword_hits": sum(r["keyword_hits"] for r in results),
        "total_keywords": sum(r["keyword_total"] for r in results),
        "individual_scores": accuracies,
    }
