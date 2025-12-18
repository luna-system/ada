#!/usr/bin/env python3
"""
Phase 1 Validation Blueprint

Goal: Prove that Ada handles her category tasks (memory, reasoning, context)
with quality parity to Copilot.

This will validate the routing strategy before building the codebase specialist.

Test Plan:
1. Design 10 questions that Ada should handle well
2. Ask Ada (via brain API) and Copilot (via MCP)
3. Compare: correctness, personalization, context-awareness
4. Measure: % of answers where Ada matches/beats Copilot on quality
5. Target: >90% quality parity (Ada ≥ 90% of Copilot score)

This is the empirical validation of contextual malleability:
Same question, different context (Ada has history, Copilot doesn't) = different effectiveness
"""

from dataclasses import dataclass
from typing import Optional
import json


@dataclass
class ValidationQuery:
    """A test query for validation"""
    id: str
    category: str  # memory, reasoning, context, creative, etc.
    question: str
    expected_strategy: str  # "ada" or "copilot"
    rationale: str
    scoring_rubric: dict  # How to evaluate: keys are criteria, values are importance 0-1


class Phase1ValidationPlan:
    """Complete validation plan for Ada↔Copilot routing"""
    
    # Memory/Reasoning/Context Category Queries (Ada should win)
    MEMORY_CATEGORY_TESTS = [
        ValidationQuery(
            id="mem_001",
            category="memory",
            question="What did we discuss about performance optimization?",
            expected_strategy="ada",
            rationale="Pure memory lookup - Ada has conversation history loaded",
            scoring_rubric={
                "recalls_prior_discussion": 0.4,  # Most important
                "correct_details": 0.3,
                "personalized_context": 0.2,
                "relevance": 0.1,
            }
        ),
        ValidationQuery(
            id="mem_002",
            category="memory",
            question="What's my philosophy about privacy and data?",
            expected_strategy="ada",
            rationale="Persona query - Ada has loaded persona file",
            scoring_rubric={
                "knows_my_preferences": 0.4,
                "specific_examples": 0.3,
                "connected_to_context": 0.2,
                "accurate_representation": 0.1,
            }
        ),
        ValidationQuery(
            id="reas_001",
            category="reasoning",
            question="Should we use async/await for this operation?",
            expected_strategy="ada",
            rationale="Reasoning task - Ada can take time, leverages context",
            scoring_rubric={
                "thoughtful_analysis": 0.35,
                "considers_tradeoffs": 0.35,
                "references_context": 0.2,
                "practical_recommendation": 0.1,
            }
        ),
        ValidationQuery(
            id="reas_002",
            category="reasoning",
            question="What are pros and cons of moving to ROCm for GPU support?",
            expected_strategy="ada",
            rationale="Analysis with context - Ada knows our constraints",
            scoring_rubric={
                "balanced_view": 0.35,
                "uses_our_context": 0.35,
                "technical_accuracy": 0.2,
                "practical_guidance": 0.1,
            }
        ),
        ValidationQuery(
            id="ctx_001",
            category="context",
            question="Given our hardware constraints, what's the best model selection strategy?",
            expected_strategy="ada",
            rationale="Context-aware decision - Ada has measured data, knows history",
            scoring_rubric={
                "references_measurements": 0.35,
                "acknowledges_constraints": 0.3,
                "practical_recommendation": 0.2,
                "considers_context": 0.15,
            }
        ),
    ]
    
    # Fast/Creative/Fresh Category Queries (Copilot should win)
    COPILOT_CATEGORY_TESTS = [
        ValidationQuery(
            id="fast_001",
            category="quick_fix",
            question="Fix this typo: recieve",
            expected_strategy="copilot",
            rationale="Instant response needed - speed dominates",
            scoring_rubric={
                "instant_answer": 0.6,
                "correctness": 0.4,
            }
        ),
        ValidationQuery(
            id="crea_001",
            category="creative",
            question="Write a haiku about debugging",
            expected_strategy="copilot",
            rationale="Creative task - Copilot's specialty",
            scoring_rubric={
                "creativity": 0.4,
                "follows_form": 0.3,
                "quality": 0.3,
            }
        ),
        ValidationQuery(
            id="fresh_001",
            category="current",
            question="What's the latest on Python 3.14 release?",
            expected_strategy="copilot",
            rationale="Needs current external knowledge",
            scoring_rubric={
                "currency": 0.5,
                "accuracy": 0.5,
            }
        ),
    ]
    
    ALL_TESTS = MEMORY_CATEGORY_TESTS + COPILOT_CATEGORY_TESTS
    
    @staticmethod
    def get_scoring_instructions():
        """How to score Ada vs Copilot responses"""
        return """
SCORING INSTRUCTIONS FOR PHASE 1 VALIDATION
==============================================

For each query, you will receive:
1. Ada's response (via brain API, ~600ms)
2. Copilot's response (via VS Code Chat, instant)

Score each response 0-10 on:
- Correctness (does it answer the question accurately?)
- Completeness (does it cover the topic well?)
- Personalization (does it use your context/preferences?)
- Relevance (is it on-topic and useful?)
- Clarity (is it well-written and clear?)

Use the rubric provided for each query to weight importance.

EXAMPLE SCORING:

Query: "What did we discuss about performance optimization?"
Rubric: recalls=0.4, details=0.3, context=0.2, relevance=0.1

Ada Response:
  "We discussed three main areas: (1) Caching strategy for RAG context,
   (2) Model selection (switched deepseek-r1 to qwen2.5-coder:7b for 10x speedup),
   (3) Hardware ceiling measurements. You decided to optimize economics
   around the ceiling rather than fighting physics."
   
Ada Score:
  Recalls prior discussion: 10/10 × 0.4 = 4.0 (specific, accurate)
  Correct details: 9/10 × 0.3 = 2.7 (minor detail but correct)
  Personalized context: 10/10 × 0.2 = 2.0 (references our decisions)
  Relevance: 10/10 × 0.1 = 1.0 (highly relevant)
  TOTAL: 9.7/10

Copilot Response:
  "You discussed performance optimization, which typically involves
   caching, database optimization, and algorithm improvements."
   
Copilot Score:
  Recalls prior discussion: 4/10 × 0.4 = 1.6 (generic, not specific)
  Correct details: 6/10 × 0.3 = 1.8 (generic but not wrong)
  Personalized context: 1/10 × 0.2 = 0.2 (no personalization)
  Relevance: 5/10 × 0.1 = 0.5 (somewhat relevant)
  TOTAL: 4.1/10

Result: Ada wins (9.7 vs 4.1)
Quality Parity: Ada = 240% of Copilot on this query (far exceeds 90% target)

INSTRUCTIONS:
1. Score each response independently (don't compare until end)
2. Use provided rubric to weight criteria
3. Be honest about limitations (e.g., Copilot's generic response)
4. Track which queries Ada wins/loses/ties
5. Calculate overall quality parity %
"""
    
    @staticmethod
    def print_validation_plan():
        """Display the validation plan"""
        
        print("\n" + "="*80)
        print("PHASE 1 VALIDATION PLAN: Ada↔Copilot Quality Parity")
        print("="*80)
        
        print("\nGOAL:")
        print("  Prove Ada handles her category tasks with >90% quality parity to Copilot")
        print("\nHYPOTHESIS:")
        print("  For memory/reasoning/context tasks (Ada's strengths):")
        print("  - Ada will match or beat Copilot on quality")
        print("  - Because Ada has loaded context + can take time")
        print("  - Copilot will match or beat Ada on speed")
        print("  - Economics favor Ada (free vs paid)")
        
        print("\n" + "-"*80)
        print("MEMORY/REASONING/CONTEXT TESTS (Ada should win quality)")
        print("-"*80)
        
        for test in Phase1ValidationPlan.MEMORY_CATEGORY_TESTS:
            print(f"\n  [{test.id}] {test.category.upper()}")
            print(f"  Question: {test.question}")
            print(f"  Rationale: {test.rationale}")
            print(f"  Scoring: {test.scoring_rubric}")
        
        print("\n" + "-"*80)
        print("FAST/CREATIVE/CURRENT TESTS (Copilot should win speed)")
        print("-"*80)
        
        for test in Phase1ValidationPlan.COPILOT_CATEGORY_TESTS:
            print(f"\n  [{test.id}] {test.category.upper()}")
            print(f"  Question: {test.question}")
            print(f"  Rationale: {test.rationale}")
            print(f"  Scoring: {test.scoring_rubric}")
        
        print("\n" + "-"*80)
        print("METHODOLOGY")
        print("-"*80)
        print("""
1. For each query:
   - Ask Ada (record latency, response)
   - Ask Copilot (record latency, response)
   - Score both using provided rubric
   - Note which one "won" on quality/speed

2. Aggregate Results:
   - Ada quality: % of Copilot quality (target: >90%)
   - Ada wins: count of queries where Ada beat Copilot
   - Category analysis: which categories favor Ada?
   
3. Report:
   - Quality parity: {Ada score}/{Copilot score} × 100%
   - Speed ratio: {Copilot latency}/{Ada latency}
   - ROI: Quality parity × (1 - cost_ratio)
   
4. Decision:
   - If parity >90% AND speed acceptable (<2s)
     → Routing to Ada is justified
     → Proceed to Phase 2 (build codebase specialist)
   - If parity <90%
     → Adjust router, try again
     → OR adjust Ada's prompting/context
""")
        
        print("\n" + "-"*80)
        print("EXPECTED OUTCOMES")
        print("-"*80)
        print("""
Best Case (Confirm Hypothesis):
  ✅ Ada quality parity: 95%+ on memory/reasoning tasks
  ✅ Ada wins on personalization 90%+ of time
  ✅ Speed acceptable (<800ms)
  ✅ ROI clearly positive
  → Proceed with confidence to Phase 2

Good Case (Validate Mostly):
  ✅ Ada quality parity: 80-90%
  ✅ Ada wins on context awareness
  ⚠️  Some speed concerns (>1s on complex queries)
  → Refine context prompting, proceed with caution

Challenging Case (Need Adjustment):
  ❌ Ada quality parity: <80%
  ❌ Copilot wins on accuracy in Ada's categories
  ⚠️  Routing strategy may need rethinking
  → Investigate: Is this Ada's limitation or prompt/context issue?
  → Could improve with better persona loading, memory indexing
""")
        
        print("\n" + "="*80)
        print("SCORING INSTRUCTIONS")
        print("="*80)
        print(Phase1ValidationPlan.get_scoring_instructions())


if __name__ == "__main__":
    Phase1ValidationPlan.print_validation_plan()
