#!/usr/bin/env python3
"""
Core harness for testing codebase comprehension.

This is the main engine that:
1. Loads a codebase (with or without .ai/ docs)
2. Asks questions via LLM
3. Scores the answers
4. Compares WITH vs WITHOUT .ai/ documentation

December 19, 2025
"""

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import subprocess

from .scoring import score_answer, aggregate_scores
from .questions import (
    ComprehensionQuestion, 
    generate_all_questions,
)


@dataclass
class CodebaseContext:
    """Context about a codebase for testing."""
    name: str
    path: Path
    has_ai_docs: bool
    ai_docs_content: Optional[dict] = None
    file_count: int = 0
    primary_language: str = "unknown"
    discovered_modules: list[str] = field(default_factory=list)


@dataclass
class ComprehensionResult:
    """Result of asking a model about a codebase."""
    question: ComprehensionQuestion
    answer: str
    latency_ms: float
    keyword_hits: int
    keyword_total: int
    accuracy_score: float
    confidence: Optional[float] = None


class CodebaseHarness:
    """
    Harness for testing LLM comprehension of a codebase.
    
    Usage:
        harness = CodebaseHarness(Path("/path/to/project"))
        ctx = harness.load_context()
        result = harness.ask_question(question, use_ai_docs=True)
    """
    
    def __init__(self, path: Path, model: str = "qwen2.5-coder:7b"):
        """
        Initialize the harness.
        
        Args:
            path: Path to the codebase
            model: Ollama model to use for questions
        """
        self.path = path.resolve()
        self.model = model
        self._context: Optional[CodebaseContext] = None
        self._ai_docs_cache: Optional[dict] = None
    
    def load_context(self) -> CodebaseContext:
        """
        Load and analyze the codebase.
        
        Returns:
            CodebaseContext with codebase metadata
        """
        if self._context is not None:
            return self._context
        
        # Basic info
        name = self.path.name
        
        # Check for .ai/ directory
        ai_dir = self.path / ".ai"
        has_ai_docs = ai_dir.exists() and ai_dir.is_dir()
        
        # Load .ai/ contents if present
        ai_docs_content = None
        if has_ai_docs:
            ai_docs_content = self._load_ai_docs(ai_dir)
        
        # Count files and detect language
        file_count = 0
        lang_counts = {"python": 0, "javascript": 0, "rust": 0, "go": 0}
        discovered_modules = []
        
        for f in self.path.rglob("*"):
            if f.is_file() and not any(
                part.startswith(".") or part in ["node_modules", "__pycache__", "venv", ".venv"]
                for part in f.parts
            ):
                file_count += 1
                suffix = f.suffix.lower()
                if suffix == ".py":
                    lang_counts["python"] += 1
                    # Track Python modules
                    rel = f.relative_to(self.path)
                    if len(rel.parts) <= 3:  # Not too deeply nested
                        discovered_modules.append(str(rel))
                elif suffix in [".js", ".ts", ".jsx", ".tsx"]:
                    lang_counts["javascript"] += 1
                elif suffix == ".rs":
                    lang_counts["rust"] += 1
                elif suffix == ".go":
                    lang_counts["go"] += 1
        
        # Determine primary language
        primary_language = max(lang_counts, key=lang_counts.get) if any(lang_counts.values()) else "unknown"
        
        self._context = CodebaseContext(
            name=name,
            path=self.path,
            has_ai_docs=has_ai_docs,
            ai_docs_content=ai_docs_content,
            file_count=file_count,
            primary_language=primary_language,
            discovered_modules=discovered_modules[:20],  # Limit
        )
        
        return self._context
    
    def _load_ai_docs(self, ai_dir: Path) -> dict:
        """Load all .ai/ documentation files."""
        docs = {}
        
        for f in ai_dir.iterdir():
            if f.is_file():
                try:
                    content = f.read_text()
                    if f.suffix == ".json":
                        docs[f.name] = json.loads(content)
                    else:
                        docs[f.name] = content
                except Exception as e:
                    docs[f.name] = f"<error loading: {e}>"
        
        return docs
    
    def _build_context_prompt(self, use_ai_docs: bool) -> str:
        """
        Build the context to provide to the LLM.
        
        Args:
            use_ai_docs: Whether to include .ai/ documentation
            
        Returns:
            Context string to prepend to questions
        """
        ctx = self.load_context()
        
        parts = [
            f"You are analyzing a codebase called '{ctx.name}'.",
            f"Primary language: {ctx.primary_language}",
            f"File count: {ctx.file_count}",
        ]
        
        if use_ai_docs and ctx.ai_docs_content:
            parts.append("\n--- .ai/ DOCUMENTATION ---\n")
            
            # Include context.md first (most important)
            if "context.md" in ctx.ai_docs_content:
                parts.append("## context.md\n")
                parts.append(ctx.ai_docs_content["context.md"][:8000])  # Limit size
            
            # Include codebase-map.json summary
            if "codebase-map.json" in ctx.ai_docs_content:
                cmap = ctx.ai_docs_content["codebase-map.json"]
                if isinstance(cmap, dict) and "modules" in cmap:
                    parts.append("\n## Key Modules (from codebase-map.json)\n")
                    for mod, info in list(cmap["modules"].items())[:10]:
                        purpose = info.get("purpose", "unknown") if isinstance(info, dict) else str(info)
                        parts.append(f"- {mod}: {purpose[:100]}")
            
            parts.append("\n--- END .ai/ DOCUMENTATION ---\n")
        else:
            parts.append("\nNo structured documentation available. Answer based on general software patterns.\n")
        
        return "\n".join(parts)
    
    def ask_question(
        self, 
        question: ComprehensionQuestion, 
        use_ai_docs: bool = True
    ) -> ComprehensionResult:
        """
        Ask a comprehension question about the codebase.
        
        Args:
            question: The question to ask
            use_ai_docs: Whether to include .ai/ docs in context
            
        Returns:
            ComprehensionResult with answer and scoring
        """
        context = self._build_context_prompt(use_ai_docs)
        
        full_prompt = f"""{context}

QUESTION: {question.question}

Please answer concisely based on the information provided. If you don't have enough information, say so.

ANSWER:"""
        
        # Call Ollama
        start_time = time.time()
        try:
            result = subprocess.run(
                ["ollama", "run", self.model],
                input=full_prompt,
                capture_output=True,
                text=True,
                timeout=60,
            )
            answer = result.stdout.strip()
        except subprocess.TimeoutExpired:
            answer = "<timeout>"
        except Exception as e:
            answer = f"<error: {e}>"
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Score the answer
        scoring = score_answer(answer, question.expected_keywords, question.ground_truth)
        
        return ComprehensionResult(
            question=question,
            answer=answer,
            latency_ms=latency_ms,
            keyword_hits=scoring["keyword_hits"],
            keyword_total=scoring["keyword_total"],
            accuracy_score=scoring["accuracy_score"],
        )


def run_benchmark(
    harness: CodebaseHarness,
    question_count: int = 10,
    categories: list[str] = None,
) -> dict:
    """
    Run a full benchmark comparing WITH vs WITHOUT .ai/ docs.
    
    Args:
        harness: Configured CodebaseHarness
        question_count: Number of questions to ask
        categories: Optional filter for question categories
        
    Returns:
        Benchmark results dict
    """
    ctx = harness.load_context()
    
    # Generate questions
    all_questions = generate_all_questions(ctx.discovered_modules)
    
    # Filter by category if specified
    if categories:
        all_questions = [q for q in all_questions if q.category in categories]
    
    # Limit to requested count
    questions = all_questions[:question_count]
    
    # Run WITH .ai/ docs
    results_with = []
    for q in questions:
        result = harness.ask_question(q, use_ai_docs=True)
        results_with.append({
            "question": q.question,
            "category": q.category,
            "difficulty": q.difficulty,
            "answer": result.answer[:500],  # Truncate for storage
            "accuracy_score": result.accuracy_score,
            "keyword_hits": result.keyword_hits,
            "keyword_total": result.keyword_total,
            "latency_ms": result.latency_ms,
        })
    
    # Run WITHOUT .ai/ docs  
    results_without = []
    for q in questions:
        result = harness.ask_question(q, use_ai_docs=False)
        results_without.append({
            "question": q.question,
            "category": q.category,
            "difficulty": q.difficulty,
            "answer": result.answer[:500],
            "accuracy_score": result.accuracy_score,
            "keyword_hits": result.keyword_hits,
            "keyword_total": result.keyword_total,
            "latency_ms": result.latency_ms,
        })
    
    # Aggregate
    with_agg = aggregate_scores([{"accuracy_score": r["accuracy_score"], 
                                   "keyword_hits": r["keyword_hits"],
                                   "keyword_total": r["keyword_total"]} 
                                  for r in results_with])
    
    without_agg = aggregate_scores([{"accuracy_score": r["accuracy_score"],
                                      "keyword_hits": r["keyword_hits"],
                                      "keyword_total": r["keyword_total"]}
                                     for r in results_without])
    
    improvement = with_agg["mean_accuracy"] - without_agg["mean_accuracy"]
    
    return {
        "codebase": ctx.name,
        "model": harness.model,
        "question_count": len(questions),
        "has_ai_docs": ctx.has_ai_docs,
        "with_ai_docs": {
            **with_agg,
            "individual_results": results_with,
        },
        "without_ai_docs": {
            **without_agg,
            "individual_results": results_without,
        },
        "improvement": improvement,
        "improvement_percent": (improvement / max(without_agg["mean_accuracy"], 0.01)) * 100,
    }
