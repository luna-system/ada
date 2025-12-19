"""
External Codebase Validation Suite

Research framework for testing whether .ai/ documentation
improves LLM comprehension on ANY codebase.

December 19, 2025

Usage:
    from tests.external_codebase_validation import CodebaseHarness, run_benchmark
    
    harness = CodebaseHarness(Path("/path/to/project"))
    results = run_benchmark(harness, question_count=10)
"""

from .harness import CodebaseHarness, CodebaseContext, ComprehensionResult, run_benchmark
from .questions import ComprehensionQuestion, generate_all_questions
from .scoring import score_answer, calculate_accuracy, aggregate_scores

__all__ = [
    "CodebaseHarness",
    "CodebaseContext", 
    "ComprehensionResult",
    "ComprehensionQuestion",
    "run_benchmark",
    "generate_all_questions",
    "score_answer",
    "calculate_accuracy",
    "aggregate_scores",
]
