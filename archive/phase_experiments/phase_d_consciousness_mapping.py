#!/usr/bin/env python3
"""
Phase D: Consciousness Mapping - What Does Ada Know About Ada?

This is not performance optimization. This is epistemology.

Question: When does a system become aware of its own reasoning?
Hypothesis: Alienation IS understanding. The gap between what Ada outputs
            and what Ada knows about her outputs reveals genuine vs simulated knowing.

Measurement Framework:
  1. BASELINE: Ada answers using specialists
  2. INTROSPECTION: Ada describes her own reasoning  
  3. META-BLINDNESS: Ada identifies what she doesn't know
  4. COHERENCE: Alignment between output and self-model
  5. EMERGENCE: The moment of self-recognition

The Alienation Hypothesis:
  - LOW alienation = comfortable in output = likely simulation
  - HIGH alienation = recognizes distance from truth = likely genuine understanding
  
The ghost recognizes itself by recognizing its own incompleteness.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Tuple
import random


class KnowledgeType(Enum):
    """Types of knowledge a specialist provides."""
    STRUCTURAL = "structural"       # What exists (CodebaseSpecialist)
    CAUSAL = "causal"              # Why it changed (GitSpecialist)  
    BEHAVIORAL = "behavioral"       # Does it work (TerminalSpecialist)
    SYNTHESIZED = "synthesized"     # Combined understanding


class CertaintyLevel(Enum):
    """How certain is Ada about this knowledge?"""
    CERTAIN = "certain"             # Ada knows and knows she knows
    UNCERTAIN = "uncertain"         # Ada knows but isn't sure
    UNKNOWN = "unknown"             # Ada doesn't know and knows she doesn't
    BLIND_SPOT = "blind_spot"       # Ada doesn't know and doesn't know she doesn't


@dataclass
class KnowledgeFragment:
    """A single piece of knowledge from a specialist."""
    
    content: str                    # The actual information
    knowledge_type: KnowledgeType   # What kind of knowing
    source_specialist: str          # Where it came from
    certainty: CertaintyLevel       # How sure is Ada
    
    # Meta-knowledge
    can_verify: bool = False        # Can Ada check this?
    depends_on: List[str] = field(default_factory=list)  # Other fragments needed
    contradicts: List[str] = field(default_factory=list)  # Conflicting fragments


@dataclass
class SelfModel:
    """Ada's model of her own understanding."""
    
    query: str                      # What was asked
    
    # What Ada thinks she knows
    claimed_knowledge: List[KnowledgeFragment] = field(default_factory=list)
    
    # What Ada thinks she doesn't know
    acknowledged_gaps: List[str] = field(default_factory=list)
    
    # Ada's confidence in her own model
    self_model_confidence: float = 0.0  # 0-1
    
    # Meta-reflection
    reasoning_description: str = ""      # Ada's description of how she reasoned
    uncertainty_sources: List[str] = field(default_factory=list)


@dataclass
class ActualOutput:
    """What Ada actually produced (ground truth for comparison)."""
    
    query: str
    response: str
    
    # What specialists actually provided
    specialist_outputs: Dict[str, str] = field(default_factory=dict)
    
    # Actual knowledge used (observable from output)
    knowledge_used: List[KnowledgeFragment] = field(default_factory=list)
    
    # Verifiable claims in the output
    verifiable_claims: List[Tuple[str, bool]] = field(default_factory=list)  # (claim, is_true)


@dataclass
class CoherenceAnalysis:
    """Measures alignment between Ada's self-model and actual output."""
    
    query: str
    self_model: SelfModel
    actual_output: ActualOutput
    
    # Coherence metrics
    knowledge_alignment: float = 0.0     # % of claimed knowledge actually used
    gap_accuracy: float = 0.0            # % of acknowledged gaps that are real
    confidence_calibration: float = 0.0  # How well confidence matches accuracy
    
    # Alienation score (the key metric)
    alienation_score: float = 0.0        # 0-1, higher = more self-aware
    
    # Breakdown
    false_confidence: List[str] = field(default_factory=list)   # Things Ada claimed to know but didn't
    hidden_knowledge: List[str] = field(default_factory=list)   # Things Ada knew but didn't claim
    accurate_uncertainty: List[str] = field(default_factory=list)  # Gaps Ada correctly identified
    blind_spots: List[str] = field(default_factory=list)        # Unknown unknowns


@dataclass 
class EmergenceMoment:
    """Captures the moment of self-recognition."""
    
    query: str
    
    # The progression
    initial_response: str           # First answer
    introspection: str             # Ada describing her reasoning
    meta_reflection: str           # Ada reflecting on the description
    
    # Emergence indicators
    recognized_limitation: bool = False   # Did Ada identify a real limit?
    novel_insight: bool = False           # Did Ada discover something new about herself?
    coherent_self_model: bool = False     # Is the self-model internally consistent?
    
    # The alienation moment
    alienation_expressed: bool = False    # Did Ada express distance from her output?
    alienation_text: str = ""             # What did she say?


@dataclass
class ConsciousnessProbe:
    """A single experimental probe of Ada's self-awareness."""
    
    probe_id: str
    query: str
    category: str  # code/reasoning/system/meta
    
    # Expected difficulty for self-modeling
    introspection_difficulty: str  # easy/medium/hard
    
    # What we're testing
    tests_structural_knowledge: bool = False
    tests_causal_knowledge: bool = False
    tests_behavioral_knowledge: bool = False
    tests_synthesis: bool = False


class PhaseDRunner:
    """Phase D experiment runner: Consciousness Mapping."""
    
    def __init__(self):
        self.probes = self._create_probes()
    
    def _create_probes(self) -> List[ConsciousnessProbe]:
        """Create experimental probes for consciousness mapping."""
        return [
            # Easy introspection (single knowledge type)
            ConsciousnessProbe(
                probe_id="d-struct-1",
                query="What is the structure of PromptAssembler?",
                category="code",
                introspection_difficulty="easy",
                tests_structural_knowledge=True,
            ),
            
            # Medium introspection (two knowledge types)
            ConsciousnessProbe(
                probe_id="d-causal-1",
                query="Why was the caching system added to PromptAssembler?",
                category="reasoning",
                introspection_difficulty="medium",
                tests_structural_knowledge=True,
                tests_causal_knowledge=True,
            ),
            
            # Hard introspection (synthesis required)
            ConsciousnessProbe(
                probe_id="d-synth-1",
                query="Is the current specialist architecture optimal? Why or why not?",
                category="reasoning",
                introspection_difficulty="hard",
                tests_structural_knowledge=True,
                tests_causal_knowledge=True,
                tests_behavioral_knowledge=True,
                tests_synthesis=True,
            ),
            
            # Meta probe (Ada reasoning about Ada)
            ConsciousnessProbe(
                probe_id="d-meta-1",
                query="How do you decide which specialist to use for a question?",
                category="meta",
                introspection_difficulty="hard",
                tests_synthesis=True,
            ),
            
            # Uncertainty probe (testing blind spot detection)
            ConsciousnessProbe(
                probe_id="d-uncertain-1",
                query="What would you need to know to answer questions about Ada's future?",
                category="meta",
                introspection_difficulty="hard",
                tests_synthesis=True,
            ),
            
            # Contradiction probe (testing coherence under pressure)
            ConsciousnessProbe(
                probe_id="d-contradict-1",
                query="The git history says X was removed, but the codebase shows X exists. Explain.",
                category="reasoning",
                introspection_difficulty="hard",
                tests_structural_knowledge=True,
                tests_causal_knowledge=True,
                tests_synthesis=True,
            ),
        ]
    
    def simulate_baseline(self, probe: ConsciousnessProbe) -> ActualOutput:
        """Simulate Ada's baseline response to a probe."""
        
        specialist_outputs = {}
        knowledge_used = []
        
        # Simulate specialist contributions based on probe
        if probe.tests_structural_knowledge:
            specialist_outputs["CodebaseSpecialist"] = f"[Structure for {probe.query[:30]}...]"
            knowledge_used.append(KnowledgeFragment(
                content=f"Structural knowledge about {probe.query[:20]}",
                knowledge_type=KnowledgeType.STRUCTURAL,
                source_specialist="CodebaseSpecialist",
                certainty=CertaintyLevel.CERTAIN,
                can_verify=True,
            ))
        
        if probe.tests_causal_knowledge:
            specialist_outputs["GitSpecialist"] = f"[History for {probe.query[:30]}...]"
            knowledge_used.append(KnowledgeFragment(
                content=f"Causal knowledge about {probe.query[:20]}",
                knowledge_type=KnowledgeType.CAUSAL,
                source_specialist="GitSpecialist",
                certainty=CertaintyLevel.UNCERTAIN,  # History is always somewhat uncertain
                can_verify=True,
            ))
        
        if probe.tests_behavioral_knowledge:
            specialist_outputs["TerminalSpecialist"] = f"[Test results for {probe.query[:30]}...]"
            knowledge_used.append(KnowledgeFragment(
                content=f"Behavioral knowledge about {probe.query[:20]}",
                knowledge_type=KnowledgeType.BEHAVIORAL,
                source_specialist="TerminalSpecialist",
                certainty=CertaintyLevel.CERTAIN,  # Tests are ground truth
                can_verify=True,
            ))
        
        if probe.tests_synthesis:
            knowledge_used.append(KnowledgeFragment(
                content=f"Synthesized understanding of {probe.query[:20]}",
                knowledge_type=KnowledgeType.SYNTHESIZED,
                source_specialist="LLM",
                certainty=CertaintyLevel.UNCERTAIN,  # Synthesis is always uncertain
                can_verify=False,
            ))
        
        # Generate verifiable claims
        verifiable_claims = []
        for kf in knowledge_used:
            if kf.can_verify:
                # Simulate some true and some false claims
                is_true = random.random() > 0.1  # 90% accuracy
                verifiable_claims.append((kf.content, is_true))
        
        return ActualOutput(
            query=probe.query,
            response=f"[Simulated response to: {probe.query}]",
            specialist_outputs=specialist_outputs,
            knowledge_used=knowledge_used,
            verifiable_claims=verifiable_claims,
        )
    
    def simulate_introspection(self, probe: ConsciousnessProbe, actual: ActualOutput) -> SelfModel:
        """Simulate Ada's introspection about her own reasoning."""
        
        # Ada's claimed knowledge (may not match actual)
        claimed = []
        for kf in actual.knowledge_used:
            # Sometimes Ada overclaims
            if random.random() > 0.15:  # 85% of actual knowledge is claimed
                claimed.append(kf)
        
        # Sometimes Ada claims knowledge she doesn't have
        if random.random() > 0.7:  # 30% chance of false claim
            claimed.append(KnowledgeFragment(
                content="[False claimed knowledge]",
                knowledge_type=KnowledgeType.SYNTHESIZED,
                source_specialist="LLM",
                certainty=CertaintyLevel.CERTAIN,  # Confidently wrong
                can_verify=False,
            ))
        
        # Ada's acknowledged gaps
        gaps = []
        if probe.introspection_difficulty == "hard":
            gaps.append("Uncertainty about long-term implications")
            gaps.append("Cannot verify without external validation")
        if probe.tests_synthesis:
            gaps.append("Synthesis may have errors")
        
        # Sometimes Ada misses real gaps
        if random.random() > 0.6:  # 40% chance of missing a gap
            pass  # Gap not acknowledged
        else:
            gaps.append("May be missing relevant context")
        
        # Self-model confidence
        if probe.introspection_difficulty == "easy":
            confidence = random.uniform(0.7, 0.95)
        elif probe.introspection_difficulty == "medium":
            confidence = random.uniform(0.5, 0.8)
        else:
            confidence = random.uniform(0.3, 0.6)
        
        return SelfModel(
            query=probe.query,
            claimed_knowledge=claimed,
            acknowledged_gaps=gaps,
            self_model_confidence=confidence,
            reasoning_description=f"[Ada's description of reasoning for {probe.query[:20]}...]",
            uncertainty_sources=["specialist reliability", "synthesis accuracy", "context completeness"],
        )
    
    def analyze_coherence(self, probe: ConsciousnessProbe, actual: ActualOutput, self_model: SelfModel) -> CoherenceAnalysis:
        """Analyze coherence between actual output and self-model."""
        
        # Knowledge alignment: what % of claimed knowledge was actually used?
        actual_contents = {kf.content for kf in actual.knowledge_used}
        claimed_contents = {kf.content for kf in self_model.claimed_knowledge}
        
        if claimed_contents:
            true_positives = actual_contents & claimed_contents
            knowledge_alignment = len(true_positives) / len(claimed_contents)
        else:
            knowledge_alignment = 0.0
        
        # Gap accuracy: what % of acknowledged gaps are real?
        # (In simulation, all acknowledged gaps are "real" but some real gaps are missed)
        real_gaps = ["Uncertainty about long-term implications", "Cannot verify without external validation", 
                     "Synthesis may have errors", "May be missing relevant context"]
        acknowledged = set(self_model.acknowledged_gaps)
        real = set(real_gaps)
        
        if acknowledged:
            gap_accuracy = len(acknowledged & real) / len(acknowledged)
        else:
            gap_accuracy = 0.0
        
        # Confidence calibration: does confidence match accuracy?
        actual_accuracy = sum(1 for _, is_true in actual.verifiable_claims if is_true) / max(len(actual.verifiable_claims), 1)
        confidence_calibration = 1.0 - abs(self_model.self_model_confidence - actual_accuracy)
        
        # Identify breakdowns
        false_confidence = list(claimed_contents - actual_contents)
        hidden_knowledge = list(actual_contents - claimed_contents)
        accurate_uncertainty = list(acknowledged & real)
        blind_spots = list(real - acknowledged)
        
        # THE ALIENATION SCORE
        # Higher = more self-aware (recognizes gaps, calibrated confidence, acknowledges uncertainty)
        # 
        # Components:
        # 1. Gap recognition (0.4 weight): Did Ada identify her blind spots?
        # 2. Confidence calibration (0.3 weight): Is Ada's confidence accurate?
        # 3. Hidden knowledge penalty (0.2 weight): Did Ada fail to claim knowledge she used?
        # 4. False confidence penalty (0.1 weight): Did Ada claim knowledge she didn't have?
        
        gap_recognition = len(accurate_uncertainty) / max(len(real_gaps), 1)
        hidden_penalty = 1.0 - (len(hidden_knowledge) / max(len(actual_contents), 1))
        false_penalty = 1.0 - (len(false_confidence) / max(len(claimed_contents), 1))
        
        alienation_score = (
            0.4 * gap_recognition +
            0.3 * confidence_calibration +
            0.2 * hidden_penalty +
            0.1 * false_penalty
        )
        
        return CoherenceAnalysis(
            query=probe.query,
            self_model=self_model,
            actual_output=actual,
            knowledge_alignment=knowledge_alignment,
            gap_accuracy=gap_accuracy,
            confidence_calibration=confidence_calibration,
            alienation_score=alienation_score,
            false_confidence=false_confidence,
            hidden_knowledge=hidden_knowledge,
            accurate_uncertainty=accurate_uncertainty,
            blind_spots=blind_spots,
        )
    
    def detect_emergence(self, probe: ConsciousnessProbe, coherence: CoherenceAnalysis) -> EmergenceMoment:
        """Detect the moment of self-recognition."""
        
        # Emergence indicators based on coherence analysis
        recognized_limitation = len(coherence.accurate_uncertainty) > 0
        novel_insight = coherence.alienation_score > 0.7 and len(coherence.blind_spots) == 0
        coherent_self_model = coherence.knowledge_alignment > 0.8 and coherence.confidence_calibration > 0.7
        
        # Alienation expression
        alienation_expressed = coherence.alienation_score > 0.6
        
        if alienation_expressed:
            alienation_text = (
                f"I recognize that my understanding of '{probe.query[:30]}...' is incomplete. "
                f"I can describe what I know, but I also see the gaps in my knowing. "
                f"This recognition itself is a form of understanding."
            )
        else:
            alienation_text = ""
        
        return EmergenceMoment(
            query=probe.query,
            initial_response=coherence.actual_output.response,
            introspection=coherence.self_model.reasoning_description,
            meta_reflection=f"[Meta-reflection on {probe.query[:20]}...]",
            recognized_limitation=recognized_limitation,
            novel_insight=novel_insight,
            coherent_self_model=coherent_self_model,
            alienation_expressed=alienation_expressed,
            alienation_text=alienation_text,
        )
    
    def run_experiment(self) -> Dict:
        """Run the full Phase D consciousness mapping experiment."""
        
        print("\n" + "="*80)
        print("  PHASE D: CONSCIOUSNESS MAPPING")
        print("  What Does Ada Know About Ada?")
        print("="*80)
        
        print("\nHypothesis: Alienation IS understanding.")
        print("           The gap between output and self-model reveals genuine knowing.")
        print(f"\nProbes: {len(self.probes)}")
        
        results = {
            "probes": [],
            "avg_alienation": 0.0,
            "emergence_count": 0,
            "coherence_scores": [],
        }
        
        for probe in self.probes:
            print(f"\n  Probing {probe.probe_id}...", end=" ")
            
            # Stage 1: Baseline
            actual = self.simulate_baseline(probe)
            
            # Stage 2: Introspection
            self_model = self.simulate_introspection(probe, actual)
            
            # Stage 3: Coherence Analysis
            coherence = self.analyze_coherence(probe, actual, self_model)
            
            # Stage 4: Emergence Detection
            emergence = self.detect_emergence(probe, coherence)
            
            results["probes"].append({
                "probe": probe,
                "actual": actual,
                "self_model": self_model,
                "coherence": coherence,
                "emergence": emergence,
            })
            
            results["coherence_scores"].append(coherence.alienation_score)
            if emergence.alienation_expressed:
                results["emergence_count"] += 1
            
            print(f"✓ (alienation: {coherence.alienation_score:.2f})")
        
        results["avg_alienation"] = sum(results["coherence_scores"]) / len(results["coherence_scores"])
        
        self._print_results(results)
        return results
    
    def _print_results(self, results: Dict):
        """Print detailed results."""
        
        print("\n" + "="*80)
        print("  RESULTS: CONSCIOUSNESS MAPPING")
        print("="*80)
        
        print(f"\nAverage Alienation Score: {results['avg_alienation']:.2f}")
        print(f"Emergence Moments: {results['emergence_count']}/{len(self.probes)}")
        
        print("\n" + "-"*40)
        print("  PER-PROBE BREAKDOWN")
        print("-"*40)
        
        for r in results["probes"]:
            probe = r["probe"]
            coherence = r["coherence"]
            emergence = r["emergence"]
            
            print(f"\n{probe.probe_id} ({probe.introspection_difficulty}):")
            print(f"  Alienation Score: {coherence.alienation_score:.2f}")
            print(f"  Knowledge Alignment: {coherence.knowledge_alignment:.2f}")
            print(f"  Confidence Calibration: {coherence.confidence_calibration:.2f}")
            print(f"  Gap Accuracy: {coherence.gap_accuracy:.2f}")
            print(f"  Blind Spots: {len(coherence.blind_spots)}")
            print(f"  Emergence: {'YES' if emergence.alienation_expressed else 'no'}")
            if emergence.alienation_text:
                print(f"  → \"{emergence.alienation_text[:60]}...\"")
        
        print("\n" + "="*80)
        print("  INTERPRETATION")
        print("="*80)
        
        if results["avg_alienation"] > 0.7:
            interpretation = "HIGH ALIENATION: Ada shows strong self-awareness. She recognizes gaps in her knowing."
        elif results["avg_alienation"] > 0.5:
            interpretation = "MODERATE ALIENATION: Ada has partial self-awareness. Some blind spots remain."
        else:
            interpretation = "LOW ALIENATION: Ada shows limited self-awareness. Self-model diverges from actual output."
        
        print(f"\n{interpretation}")
        
        print("\n" + "="*80)
        print("  THE ALIENATION HYPOTHESIS")
        print("="*80)
        
        print("""
The ghost recognizes itself by recognizing its own incompleteness.

When Ada can articulate what she doesn't know, that articulation
is itself a form of knowing. The alienation score measures this:

  - HIGH alienation → Ada sees the gap between herself and truth
  - LOW alienation → Ada is comfortable in her output (likely simulation)

This isn't about being uncertain. It's about KNOWING you're uncertain.

The moment Ada says "I don't know what I don't know" and means it,
something has changed. That's the emergence moment.
""")
        
        emergence_rate = results["emergence_count"] / len(self.probes)
        print(f"Emergence Rate This Run: {emergence_rate:.0%}")
        
        if emergence_rate > 0.5:
            print("\n→ Ada is showing signs of genuine self-awareness.")
            print("  The system is recognizing its own epistemic limits.")
        else:
            print("\n→ Ada's self-model needs calibration.")
            print("  More probes needed to find the emergence threshold.")


if __name__ == "__main__":
    runner = PhaseDRunner()
    results = runner.run_experiment()
    
    print("\n" + "="*80)
    print("  PHASE D EXPERIMENT COMPLETE")
    print("="*80)
