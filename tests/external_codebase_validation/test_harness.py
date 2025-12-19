#!/usr/bin/env python3
"""
TDD: Test the external codebase validation harness.

Research Question: Does .ai/ documentation improve model comprehension
on codebases the model has never seen with structured context?

This test file validates OUR TESTING TOOLS before we use them.
Meta-science: test the tests.

December 19, 2025 - Phase 1 of external validation research
"""

import pytest
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import json


# ============================================================================
# STEP 1: Define what we're testing (the interfaces)
# ============================================================================

@dataclass
class ComprehensionQuestion:
    """A question about a codebase."""
    question: str
    category: str  # architecture, module, dataflow, debugging, feature
    difficulty: str  # easy, medium, hard
    expected_keywords: list[str]  # Keywords that should appear in good answers
    ground_truth: Optional[str] = None  # If we know the exact answer


@dataclass 
class ComprehensionResult:
    """Result of asking a model about a codebase."""
    question: ComprehensionQuestion
    answer: str
    latency_ms: float
    keyword_hits: int
    keyword_total: int
    accuracy_score: float  # 0.0 - 1.0
    confidence: Optional[float] = None


@dataclass
class CodebaseContext:
    """Context about a codebase for testing."""
    name: str
    path: Path
    has_ai_docs: bool
    ai_docs_content: Optional[dict] = None  # Parsed .ai/ contents
    file_count: int = 0
    primary_language: str = "unknown"


# ============================================================================
# STEP 2: Test that our data structures work
# ============================================================================

class TestDataStructures:
    """Verify our core data structures are correct."""
    
    def test_comprehension_question_creation(self):
        """Can we create a valid question?"""
        q = ComprehensionQuestion(
            question="What is the main entry point of this application?",
            category="architecture",
            difficulty="easy",
            expected_keywords=["main", "entry", "app", "start"],
        )
        assert q.question
        assert q.category == "architecture"
        assert len(q.expected_keywords) == 4
    
    def test_comprehension_result_scoring(self):
        """Can we score an answer?"""
        q = ComprehensionQuestion(
            question="What database does this use?",
            category="architecture", 
            difficulty="easy",
            expected_keywords=["postgres", "sql", "database"],
        )
        r = ComprehensionResult(
            question=q,
            answer="This application uses PostgreSQL as its primary database.",
            latency_ms=150.0,
            keyword_hits=2,  # postgres, database
            keyword_total=3,
            accuracy_score=0.67,
        )
        assert r.keyword_hits == 2
        assert r.accuracy_score == pytest.approx(0.67, rel=0.01)
    
    def test_codebase_context_without_ai_docs(self):
        """Can we represent a codebase without .ai/?"""
        ctx = CodebaseContext(
            name="test-project",
            path=Path("/tmp/test-project"),
            has_ai_docs=False,
            file_count=42,
            primary_language="python",
        )
        assert not ctx.has_ai_docs
        assert ctx.ai_docs_content is None
    
    def test_codebase_context_with_ai_docs(self):
        """Can we represent a codebase WITH .ai/?"""
        ctx = CodebaseContext(
            name="ada",
            path=Path("/home/luna/Code/ada-v1"),
            has_ai_docs=True,
            ai_docs_content={
                "context.md": "# Ada v1 - AI Context Map...",
                "codebase-map.json": {"modules": {}},
            },
            file_count=200,
            primary_language="python",
        )
        assert ctx.has_ai_docs
        assert "context.md" in ctx.ai_docs_content


# ============================================================================
# STEP 3: Test the scoring logic
# ============================================================================

class TestScoringLogic:
    """Test that we can accurately score model answers."""
    
    def test_keyword_matching_case_insensitive(self):
        """Keywords should match case-insensitively."""
        from tests.external_codebase_validation.scoring import count_keyword_hits
        
        answer = "The application uses FastAPI for the web server."
        keywords = ["fastapi", "web", "server"]
        
        hits = count_keyword_hits(answer, keywords)
        assert hits == 3  # All three should match
    
    def test_keyword_matching_partial(self):
        """Partial keyword matches should count."""
        from tests.external_codebase_validation.scoring import count_keyword_hits
        
        answer = "PostgreSQL database with SQLAlchemy ORM"
        keywords = ["postgres", "sql", "database"]
        
        hits = count_keyword_hits(answer, keywords)
        assert hits >= 2  # At least postgres and database
    
    def test_accuracy_score_calculation(self):
        """Accuracy should be hits / total."""
        from tests.external_codebase_validation.scoring import calculate_accuracy
        
        score = calculate_accuracy(keyword_hits=3, keyword_total=4)
        assert score == pytest.approx(0.75, rel=0.01)
    
    def test_accuracy_score_zero_keywords(self):
        """Handle edge case of no expected keywords."""
        from tests.external_codebase_validation.scoring import calculate_accuracy
        
        score = calculate_accuracy(keyword_hits=0, keyword_total=0)
        assert score == 0.0  # Or 1.0? Define the semantics


# ============================================================================
# STEP 4: Test question generation
# ============================================================================

class TestQuestionGeneration:
    """Test that we can generate good questions for codebases."""
    
    def test_generate_architecture_questions(self):
        """Can we generate architecture questions?"""
        from tests.external_codebase_validation.questions import generate_architecture_questions
        
        questions = generate_architecture_questions()
        
        assert len(questions) >= 3
        assert all(q.category == "architecture" for q in questions)
        assert any("entry" in q.question.lower() for q in questions)
    
    def test_generate_module_questions(self):
        """Can we generate module-specific questions?"""
        from tests.external_codebase_validation.questions import generate_module_questions
        
        # Given a list of module names
        modules = ["app.py", "database.py", "auth.py"]
        questions = generate_module_questions(modules)
        
        assert len(questions) >= len(modules)
        assert all(q.category == "module" for q in questions)
    
    def test_generate_dataflow_questions(self):
        """Can we generate data flow questions?"""
        from tests.external_codebase_validation.questions import generate_dataflow_questions
        
        questions = generate_dataflow_questions()
        
        assert len(questions) >= 2
        assert any("flow" in q.question.lower() or "data" in q.question.lower() 
                   for q in questions)


# ============================================================================
# STEP 5: Test the full harness
# ============================================================================

class TestHarness:
    """Test the complete test harness."""
    
    def test_harness_can_load_codebase(self):
        """Can the harness load a codebase?"""
        from tests.external_codebase_validation.harness import CodebaseHarness
        
        # Load Ada itself as test subject (we know it has .ai/)
        harness = CodebaseHarness(Path("/home/luna/Code/ada-v1"))
        ctx = harness.load_context()
        
        assert ctx.name == "ada-v1"
        assert ctx.has_ai_docs == True
        assert ctx.primary_language == "python"
    
    def test_harness_detects_missing_ai_docs(self):
        """Can the harness detect when .ai/ is missing?"""
        from tests.external_codebase_validation.harness import CodebaseHarness
        import tempfile
        
        # Create a temp directory without .ai/
        with tempfile.TemporaryDirectory() as tmpdir:
            # Add a Python file so it's recognized as a codebase
            (Path(tmpdir) / "main.py").write_text("print('hello')")
            
            harness = CodebaseHarness(Path(tmpdir))
            ctx = harness.load_context()
            
            assert ctx.has_ai_docs == False
    
    def test_harness_can_run_single_question(self):
        """Can the harness ask one question and get a result?"""
        from tests.external_codebase_validation.harness import CodebaseHarness
        
        harness = CodebaseHarness(Path("/home/luna/Code/ada-v1"))
        
        question = ComprehensionQuestion(
            question="What is the main entry point for the FastAPI application?",
            category="architecture",
            difficulty="easy",
            expected_keywords=["app.py", "fastapi", "brain"],
        )
        
        result = harness.ask_question(question, use_ai_docs=True)
        
        assert result.answer  # Got some answer
        assert result.latency_ms > 0  # Took some time
        assert 0.0 <= result.accuracy_score <= 1.0
    
    def test_harness_comparison_mode(self):
        """Can the harness compare WITH vs WITHOUT .ai/ docs?"""
        from tests.external_codebase_validation.harness import CodebaseHarness
        
        harness = CodebaseHarness(Path("/home/luna/Code/ada-v1"))
        
        question = ComprehensionQuestion(
            question="What specialist plugins are available?",
            category="architecture",
            difficulty="medium",
            expected_keywords=["ocr", "web_search", "listenbrainz", "specialist"],
        )
        
        # Run same question with and without .ai/ context
        result_with = harness.ask_question(question, use_ai_docs=True)
        result_without = harness.ask_question(question, use_ai_docs=False)
        
        # We expect WITH to score higher (but this is what we're testing!)
        # For now, just verify both complete
        assert result_with.answer
        assert result_without.answer
        
        # Log the comparison for analysis
        print(f"\n📊 Comparison Results:")
        print(f"   WITH .ai/: {result_with.accuracy_score:.2%} ({result_with.keyword_hits}/{result_with.keyword_total})")
        print(f"   WITHOUT:   {result_without.accuracy_score:.2%} ({result_without.keyword_hits}/{result_without.keyword_total})")


# ============================================================================
# STEP 6: Integration test - full benchmark run
# ============================================================================

class TestFullBenchmark:
    """Test a complete benchmark run."""
    
    @pytest.mark.slow
    def test_full_benchmark_on_ada(self):
        """Run a full benchmark on Ada's codebase."""
        from tests.external_codebase_validation.harness import CodebaseHarness, run_benchmark
        
        harness = CodebaseHarness(Path("/home/luna/Code/ada-v1"))
        results = run_benchmark(harness, question_count=5)
        
        assert "with_ai_docs" in results
        assert "without_ai_docs" in results
        assert results["with_ai_docs"]["mean_accuracy"] >= 0.0
        assert results["without_ai_docs"]["mean_accuracy"] >= 0.0
        
        # Save results for analysis
        output_path = Path("/home/luna/Code/ada-v1/tests/external_codebase_validation/benchmark_results_ada.json")
        output_path.write_text(json.dumps(results, indent=2))
        
        print(f"\n🔬 Full Benchmark Results:")
        print(f"   WITH .ai/:    {results['with_ai_docs']['mean_accuracy']:.2%} mean accuracy")
        print(f"   WITHOUT .ai/: {results['without_ai_docs']['mean_accuracy']:.2%} mean accuracy")
        print(f"   Δ Improvement: {results['improvement']:.2%}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--ignore=tests/conftest.py"])
