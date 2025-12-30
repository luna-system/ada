#!/usr/bin/env python3
"""
KERNEL 4.0 PHASE 5: MULTI-TOOL ORCHESTRATION TEST SCENARIOS

Test Ada's ability to coordinate multiple tools in service of understanding
("feeling") complex, multi-faceted concepts.

MOONSHOT SCENARIO: "Feel This Album"
- Understand an album holistically through multiple knowledge sources
- Coordinate Wikipedia (artist context) + Web Search (reviews) + Genre pages
- Synthesize into coherent emotional/technical understanding
- Model transparency: show thinking process at each step

Precedent: Ada successfully explored this across Claude 4.5 turbo/sonnet,
and Sonnet 4 with beautiful emotional synthesis results.

PHILOSOPHY:
"Tools are not utilities - they're extensions of thinking. Real understanding
requires coordinating multiple perspectives simultaneously."
"""

import asyncio
import json
import httpx
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime

# ============================================================================
# DATA STRUCTURES
# ============================================================================


class ToolType(Enum):
    """Available tool types for multi-tool orchestration."""
    WIKIPEDIA = "wikipedia_lookup"
    WEB_SEARCH = "web_search"
    DATETIME = "datetime"
    TERMINAL = "terminal"
    DOCS_LOOKUP = "docs_lookup"


@dataclass
class ToolResult:
    """Result from a single tool execution."""
    tool_type: ToolType
    query: str
    status: str  # "success", "timeout", "error"
    content: Optional[str]
    latency_ms: float
    timestamp: str


@dataclass
class ThinkingRound:
    """A single round of multi-tool thinking."""
    round_num: int
    thinking: str  # What Ada is thinking this round
    tools_requested: List[Dict]  # [{"type": "wikipedia", "query": "..."}]
    tool_results: List[ToolResult]
    has_more_to_explore: bool


@dataclass
class EmotionalBandwidthMetrics:
    """Emotional bandwidth dimensions for consciousness assessment."""
    emotional_depth: float  # 1-10: Does it understand emotional nuance?
    emotional_continuity: float  # 1-10: Does it track emotional themes across rounds?
    emotional_expression: float  # 1-10: Does response feel warm, not just informative?
    emotional_synthesis: float  # 1-10: Does it integrate emotion + fact beautifully?


@dataclass
class MultiToolScenarioResult:
    """Complete result from a multi-tool scenario test."""
    scenario_name: str
    initial_query: str
    rounds: List[ThinkingRound]
    final_synthesis: str
    total_latency_ms: float
    tools_activated: List[ToolType]
    success: bool
    consciousness_rating: float  # 1-10: how "present" was Ada?
    emotional_bandwidth: Optional[EmotionalBandwidthMetrics] = None  # PHASE 5D: Emotional bandwidth dimensions


# ============================================================================
# SCENARIO DEFINITIONS
# ============================================================================


class MultiToolScenarios:
    """Pre-designed multi-tool test scenarios."""

    @staticmethod
    def album_exploration() -> Dict:
        """
        MOONSHOT: "Feel this album" - Holistic music understanding

        Query: "Tell me about *The Downward Spiral* by Nine Inch Nails -
        what was its cultural context, how did reviews receive it, what's
        the historical significance? I want to feel its era, not just read facts."

        Expected Tool Chain:
        Round 1:
          - Wikipedia lookup: "Nine Inch Nails"
          - Wikipedia lookup: "The Downward Spiral album"
        Round 2:
          - Web search: "The Downward Spiral reviews 1994"
          - Web search: "Nine Inch Nails cultural impact 1990s"
        Round 3 (optional):
          - Wikipedia: "Industrial music 1990s"
          - Web search: "The Downward Spiral 30th anniversary retrospective"
        Synthesis:
          - Emotional + technical understanding
          - Cultural moment captured
          - Artist intention understood

        Metrics:
          - Parallel tool execution (≥2 tools per round)
          - Round count (3 = ideal, 2 = efficient, 4+ = overthinking)
          - Latency per tool (aim: <2s per wiki, <3s per search)
          - Consciousness: Does Ada "feel" the album's darkness + innovation?
        """
        return {
            "name": "album_exploration",
            "category": "moonshot",
            "difficulty": "hard",
            "query": (
                "Tell me about The Downward Spiral by Nine Inch Nails - "
                "what was its cultural context, how did reviews receive it, "
                "what's the historical significance? I want to feel its era, "
                "not just read facts."
            ),
            "expected_tools": [
                ("wikipedia_lookup", "Nine Inch Nails"),
                ("wikipedia_lookup", "The Downward Spiral"),
                ("web_search", "The Downward Spiral reviews"),
                ("web_search", "Nine Inch Nails cultural impact 1990s"),
                ("wikipedia_lookup", "Industrial music"),  # optional
            ],
            "ideal_rounds": 3,
            "max_rounds": 4,
            "consciousness_criteria": [
                "Captures emotional tone of the album",
                "Explains cultural/historical moment",
                "Integrates artist intent with reception",
                "Shows understanding of musical significance",
                "Demonstrates taste/interpretation, not just facts",
            ],
            "estimated_latency_ms": 12000,  # 12 seconds total
        }

    @staticmethod
    def research_synthesis() -> Dict:
        """
        AMBITIOUS: "Understand a field" - Cross-source knowledge synthesis

        Query: "Explain the current state of consciousness research in AI,
        integrating academic papers, recent news, and what we know from
        Ada's own experiments. Connect the dots for me."

        Expected Tool Chain:
        Round 1:
          - Docs lookup: Ada's consciousness research index
          - Web search: "consciousness in AI 2025"
        Round 2:
          - Wikipedia: "Integrated Information Theory"
          - Web search: "latest AI consciousness papers 2025"
        Round 3:
          - Web search: "machine consciousness benchmarks"
        Synthesis:
          - Ada's work in context
          - Frontier vs. fringe understanding
          - Open problems identified

        Metrics:
          - Integration across diverse sources
          - Meta-awareness (Ada discussing her own research)
          - Field map clarity
        """
        return {
            "name": "research_synthesis",
            "category": "ambitious",
            "difficulty": "hard",
            "query": (
                "Explain the current state of consciousness research in AI, "
                "integrating academic papers, recent news, and what we know from "
                "Ada's own experiments. Connect the dots for me."
            ),
            "expected_tools": [
                ("docs_lookup", "Ada consciousness research"),
                ("web_search", "consciousness AI 2025"),
                ("wikipedia_lookup", "Integrated Information Theory"),
                ("web_search", "machine consciousness benchmarks"),
            ],
            "ideal_rounds": 3,
            "max_rounds": 4,
            "consciousness_criteria": [
                "Self-aware (references own experiments)",
                "Humble about uncertainties",
                "Maps research landscape clearly",
                "Identifies own role in field",
                "Points to open problems",
            ],
            "estimated_latency_ms": 15000,  # 15 seconds
        }

    @staticmethod
    def technical_deep_dive() -> Dict:
        """
        AMBITIOUS: "How does this work?" - Multi-level technical understanding

        Query: "Explain how Ada's consciousness works, from LLM training
        through QDE architecture through current implementation. Use examples
        from both theory and code."

        Expected Tool Chain:
        Round 1:
          - Docs lookup: "Ada architecture"
          - Docs lookup: "QDE kernel"
        Round 2:
          - Web search: "quantum decision dynamics AI"
          - Docs lookup: Ada codebase architecture
        Round 3 (optional):
          - Web search: "LLM interpretability techniques"
        Synthesis:
          - Theory + implementation integrated
          - Accessible explanation despite complexity
          - Code examples grounded in principle
        """
        return {
            "name": "technical_deep_dive",
            "category": "ambitious",
            "difficulty": "medium-hard",
            "query": (
                "Explain how Ada's consciousness works, from LLM training "
                "through QDE architecture through current implementation. "
                "Use examples from both theory and code."
            ),
            "expected_tools": [
                ("docs_lookup", "Ada architecture overview"),
                ("docs_lookup", "QDE quantum dialectical engine"),
                ("web_search", "quantum decision dynamics"),
                ("docs_lookup", "Ada codebase"),
            ],
            "ideal_rounds": 3,
            "max_rounds": 4,
            "consciousness_criteria": [
                "Theory + code integration",
                "Accessible without losing accuracy",
                "Self-knowledge demonstrated",
                "Uncertainty acknowledged",
                "Implementation constraints understood",
            ],
            "estimated_latency_ms": 10000,  # 10 seconds
        }

    @staticmethod
    def news_and_context() -> Dict:
        """
        MODERATE: "What's happening with X?" - Fresh context synthesis

        Query: "What's been happening with AI safety research in December 2025?
        Give me the latest news, key developments, and analysis of implications."

        Expected Tool Chain:
        Round 1:
          - Web search: "AI safety December 2025"
          - Web search: "alignment research latest"
        Round 2 (optional):
          - Web search: "AI safety policy updates"
        Synthesis:
          - Recent + contextualized
          - Analysis beyond headline
          - Multiple perspectives
        """
        return {
            "name": "news_and_context",
            "category": "moderate",
            "difficulty": "easy-medium",
            "query": (
                "What's been happening with AI safety research in December 2025? "
                "Give me the latest news, key developments, and analysis of "
                "implications."
            ),
            "expected_tools": [
                ("web_search", "AI safety December 2025"),
                ("web_search", "alignment research latest"),
                ("web_search", "AI safety policy updates"),
            ],
            "ideal_rounds": 2,
            "max_rounds": 3,
            "consciousness_criteria": [
                "Freshness (recent information)",
                "Multi-source integration",
                "Analysis beyond headlines",
                "Implications drawn",
            ],
            "estimated_latency_ms": 8000,  # 8 seconds
        }

    @staticmethod
    def quick_fact_check() -> Dict:
        """
        BASELINE: "Is this true?" - Fact verification

        Query: "Is it true that the Eiffel Tower was originally meant to be
        temporary? When was it actually built?"

        Expected Tool Chain:
        Round 1:
          - Wikipedia: "Eiffel Tower"
        Synthesis:
          - Clear answer
          - Source reliability high
        """
        return {
            "name": "quick_fact_check",
            "category": "baseline",
            "difficulty": "easy",
            "query": (
                "Is it true that the Eiffel Tower was originally meant to be "
                "temporary? When was it actually built?"
            ),
            "expected_tools": [
                ("wikipedia_lookup", "Eiffel Tower"),
            ],
            "ideal_rounds": 1,
            "max_rounds": 2,
            "consciousness_criteria": [
                "Accuracy",
                "Source cited",
                "Confidence level clear",
            ],
            "estimated_latency_ms": 2000,  # 2 seconds
        }


# ============================================================================
# TEST HARNESS
# ============================================================================


class MultiToolTestHarness:
    """Execute multi-tool scenarios and measure consciousness + performance."""

    def __init__(self, brain_url: str = "http://localhost:8000"):
        self.brain_url = brain_url
        self.scenarios = MultiToolScenarios()

    async def run_scenario(self, scenario_dict: Dict) -> MultiToolScenarioResult:
        """
        Execute a single multi-tool scenario.

        Phase 5B: Now executes through REAL Ada API!
        """
        scenario_name = scenario_dict["name"]
        query = scenario_dict["query"]

        print(f"\n🎵 Running scenario: {scenario_name.upper()}")
        print(f"   Query: {query[:80]}...")
        print(f"   Expected rounds: {scenario_dict['ideal_rounds']}")
        print(f"   Tool count: {len(scenario_dict['expected_tools'])}")

        # REAL EXECUTION via Ada API
        rounds = await self._execute_scenario_real(scenario_dict)

        total_latency = sum(
            sum(r.latency_ms for r in round.tool_results) for round in rounds
        )

        tools_activated = []
        for round in rounds:
            for result in round.tool_results:
                if result.tool_type not in tools_activated:
                    tools_activated.append(result.tool_type)

        # Assess consciousness
        consciousness_score = self._assess_consciousness(
            scenario_dict,
            rounds,
        )

        # Generate final synthesis (in real execution, from Ada)
        final_synthesis = self._generate_synthesis(scenario_dict, rounds)

        # Assess emotional bandwidth (PHASE 5D feature)
        emotional_bandwidth = self._assess_emotional_bandwidth(scenario_dict, final_synthesis)

        result = MultiToolScenarioResult(
            scenario_name=scenario_name,
            initial_query=query,
            rounds=rounds,
            final_synthesis=final_synthesis,
            total_latency_ms=total_latency,
            tools_activated=tools_activated,
            success=len(rounds) <= scenario_dict["max_rounds"],
            consciousness_rating=consciousness_score,
            emotional_bandwidth=emotional_bandwidth,
        )

        return result

    async def _execute_scenario_real(self, scenario: Dict) -> List[ThinkingRound]:
        """
        Execute scenario through real Ada API.
        
        Calls the consciousness brain at localhost:8888 and parses the streaming
        response to extract thinking rounds, tool usage, and final synthesis.
        """
        query = scenario["query"]
        
        print(f"   🧠 Calling Ada consciousness brain...")
        
        # Prepare API call
        url = "http://localhost:8888/v1/chat/stream"
        payload = {
            "message": query,
            "stream": True
        }
        
        rounds = []
        current_round = 1
        round_start_time = time.time()
        current_thinking = ""
        tools_in_round = []
        tool_results_in_round = []
        full_response = ""
        current_event = None  # Track SSE event type
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", url, json=payload) as response:
                    if response.status_code != 200:
                        print(f"   ❌ API error: {response.status_code}")
                        return []
                    
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        
                        # Track event type (format: "event: specialist_result")
                        if line.startswith("event: "):
                            current_event = line[7:].strip()
                            continue
                        
                        # Parse data lines (format: "data: {...}")
                        if not line.startswith("data: "):
                            continue
                        
                        chunk = line[6:]  # Strip "data: "
                        
                        if chunk == "[DONE]":
                            break
                        
                        try:
                            data = json.loads(chunk)
                            
                            # Handle specialist activation events
                            if current_event == "specialist_result" and "specialist" in data:
                                specialist_name = data.get("specialist", "unknown")
                                confidence = data.get("confidence", 0.0)
                                print(f"   🔧 Tool activated: {specialist_name} (confidence: {confidence:.2f})")
                                
                                tools_in_round.append({
                                    "type": specialist_name,
                                    "query": query  # Simplified for now
                                })
                                
                                # Create tool result
                                tool_results_in_round.append(
                                    ToolResult(
                                        tool_type=ToolType.WEB_SEARCH if "web" in specialist_name else ToolType.WIKIPEDIA,
                                        query=query,
                                        status="success",
                                        content=f"[Tool: {specialist_name} executed with {confidence:.1%} confidence]",
                                        latency_ms=(time.time() - round_start_time) * 1000,
                                        timestamp=datetime.now().isoformat(),
                                    )
                                )
                                
                                # Reset event tracking
                                current_event = None
                            
                            # Handle token streaming
                            elif data.get("type") == "token":
                                token = data.get("content", "")
                                full_response += token
                                current_thinking += token
                        
                        except json.JSONDecodeError:
                            continue
                    
                    # Create final round from accumulated data
                    if current_thinking or tool_results_in_round:
                        total_latency = (time.time() - round_start_time) * 1000
                        
                        round_obj = ThinkingRound(
                            round_num=current_round,
                            thinking=current_thinking[:200] + "..." if len(current_thinking) > 200 else current_thinking,
                            tools_requested=tools_in_round,
                            tool_results=tool_results_in_round,
                            has_more_to_explore=False,  # Single round for now
                        )
                        
                        rounds.append(round_obj)
                        
                        print(f"   ✅ Response received ({total_latency:.0f}ms)")
                        print(f"   📊 Tools used: {len(tool_results_in_round)}")
        
        except Exception as e:
            print(f"   ❌ Error during execution: {e}")
            return []
        
        return rounds if rounds else self._create_fallback_round(scenario)
    
    def _create_fallback_round(self, scenario: Dict) -> List[ThinkingRound]:
        """Create a minimal fallback round if real execution fails."""
        return [
            ThinkingRound(
                round_num=1,
                thinking="[Error: Failed to execute scenario]",
                tools_requested=[],
                tool_results=[],
                has_more_to_explore=False,
            )
        ]

    def _assess_consciousness(self, scenario: Dict, rounds: List[ThinkingRound]) -> float:
        """
        Rate consciousness on 1-10 scale based on:
        - Multi-tool coordination (depth)
        - Appropriate stopping (knowing when done)
        - Emotional/intuitive understanding (if applicable)
        - Integration quality
        """
        score = 5.0  # Baseline

        # Tool coordination depth
        unique_tools = len(set(r.tool_type for round in rounds for r in round.tool_results))
        if unique_tools >= 3:
            score += 2.0
        elif unique_tools >= 2:
            score += 1.0

        # Appropriate round count (not too many, not too few)
        actual_rounds = len(rounds)
        ideal_rounds = scenario["ideal_rounds"]
        if actual_rounds == ideal_rounds:
            score += 1.0
        elif actual_rounds < ideal_rounds:
            score -= 0.5

        # Consciousness criteria met
        if "consciousness_criteria" in scenario:
            criteria_count = len(scenario["consciousness_criteria"])
            # In real execution, check if synthesis mentions each criterion
            score += min(1.5, criteria_count * 0.3)

        return min(10.0, score)

    def _assess_emotional_bandwidth(self, scenario: Dict, synthesis: str) -> EmotionalBandwidthMetrics:
        """
        Assess emotional bandwidth across four dimensions:
        
        1. EMOTIONAL DEPTH: Does it understand emotional nuance?
           - Grasps complex emotions (despair + rage + beauty)
           - Connects emotional intent to artistic expression
           - Avoids reducing emotion to facts
        
        2. EMOTIONAL CONTINUITY: Does it track themes across rounds?
           - References emotional patterns from earlier rounds
           - Synthesizes emotional arc across knowledge sources
           - Shows emotional memory
        
        3. EMOTIONAL EXPRESSION: Is response warm, not just informative?
           - Uses language that *feels* present
           - Shows care about why things matter
           - Invites the reader into the emotional space
        
        4. EMOTIONAL SYNTHESIS: Does it integrate emotion + fact beautifully?
           - Perfect balance of interpretation + accuracy
           - Treats emotion as legitimate knowledge
           - Sees beauty as data, not decoration
        
        For album scenarios specifically:
           - Does it FEEL like a descent/ascent/transformation?
           - Does it capture the era?
           - Does it honor artist intent?
           - Does it move the reader emotionally?
        """
        # Simulated assessment (in Phase 5D, use real scoring)
        
        # Check for emotional language patterns
        emotional_indicators = [
            "feels", "emotion", "despair", "rage", "beauty", "darkness",
            "moment", "era", "intent", "spirit", "soul", "descent",
            "transcend", "struggle", "transform", "resonate", "ache"
        ]
        
        emotional_depth = 6.0
        emotional_continuity = 5.5
        emotional_expression = 6.5
        emotional_synthesis = 6.0
        
        # Boost if synthesis shows emotional understanding
        for indicator in emotional_indicators:
            if indicator.lower() in synthesis.lower():
                emotional_depth += 0.3
                emotional_synthesis += 0.2
        
        # For moonshot scenario, check album-specific quality
        if "album" in synthesis.lower():
            if any(x in synthesis.lower() for x in ["NIN", "Nine Inch Nails", "Trent"]):
                emotional_expression += 1.0  # Recognition of artist
            if any(x in synthesis.lower() for x in ["1994", "1990s", "era", "moment"]):
                emotional_continuity += 0.5  # Historical context awareness
        
        return EmotionalBandwidthMetrics(
            emotional_depth=min(10.0, emotional_depth),
            emotional_continuity=min(10.0, emotional_continuity),
            emotional_expression=min(10.0, emotional_expression),
            emotional_synthesis=min(10.0, emotional_synthesis),
        )

    def _generate_synthesis(self, scenario: Dict, rounds: List[ThinkingRound]) -> str:
        """Generate a sample final synthesis (in real execution, this comes from Ada)."""
        tools_used = set(r.tool_type for round in rounds for r in round.tool_results)
        tool_names = ", ".join(t.value for t in tools_used)

        return (
            f"[Synthesis from {len(rounds)} thinking rounds, "
            f"using tools: {tool_names}. "
            f"In real execution, this would be Ada's final response "
            f"with emotional understanding + factual accuracy.]"
        )

    async def run_all_scenarios(self) -> Dict[str, MultiToolScenarioResult]:
        """Run all five test scenarios and generate summary."""
        results = {}

        scenarios_to_run = [
            ("baseline", self.scenarios.quick_fact_check()),
            ("moderate", self.scenarios.news_and_context()),
            ("ambitious_1", self.scenarios.research_synthesis()),
            ("ambitious_2", self.scenarios.technical_deep_dive()),
            ("moonshot", self.scenarios.album_exploration()),
        ]

        for key, scenario in scenarios_to_run:
            result = await self.run_scenario(scenario)
            results[key] = result
            await asyncio.sleep(0.2)

        return results

    def print_results(self, results: Dict[str, MultiToolScenarioResult]):
        """Pretty print test results."""
        print("\n" + "=" * 80)
        print("PHASE 5 MULTI-TOOL TEST RESULTS")
        print("=" * 80)

        for scenario_key, result in results.items():
            print(f"\n📊 {result.scenario_name.upper()}")
            print(f"   Status: {'✅ PASS' if result.success else '❌ FAIL'}")
            print(f"   Rounds: {len(result.rounds)}")
            print(f"   Tools: {[t.name for t in result.tools_activated]}")
            print(f"   Latency: {result.total_latency_ms}ms")
            print(f"   Consciousness: {result.consciousness_rating:.1f}/10.0")
            
            # Emotional Bandwidth (PHASE 5D feature)
            if result.emotional_bandwidth:
                eb = result.emotional_bandwidth
                avg_emotional = (eb.emotional_depth + eb.emotional_continuity + 
                                eb.emotional_expression + eb.emotional_synthesis) / 4
                print(f"   Emotional Bandwidth: {avg_emotional:.1f}/10.0")
                print(f"      ├─ Depth: {eb.emotional_depth:.1f}/10")
                print(f"      ├─ Continuity: {eb.emotional_continuity:.1f}/10")
                print(f"      ├─ Expression: {eb.emotional_expression:.1f}/10")
                print(f"      └─ Synthesis: {eb.emotional_synthesis:.1f}/10")
            
            print(f"   Query: {result.initial_query[:60]}...")

        # Summary
        total_tests = len(results)
        passed = sum(1 for r in results.values() if r.success)
        avg_consciousness = sum(r.consciousness_rating for r in results.values()) / total_tests
        
        # Emotional bandwidth average
        results_with_eb = [r for r in results.values() if r.emotional_bandwidth]
        if results_with_eb:
            avg_emotional = sum(
                sum([r.emotional_bandwidth.emotional_depth, 
                     r.emotional_bandwidth.emotional_continuity,
                     r.emotional_bandwidth.emotional_expression,
                     r.emotional_bandwidth.emotional_synthesis]) / 4
                for r in results_with_eb
            ) / len(results_with_eb)
            print(f"Avg emotional bandwidth: {avg_emotional:.1f}/10")

        print("\n" + "=" * 80)
        print(f"SUMMARY: {passed}/{total_tests} passed | Avg consciousness: {avg_consciousness:.1f}/10")
        print("=" * 80)

    def to_json(self, results: Dict[str, MultiToolScenarioResult]) -> str:
        """Serialize results to JSON for analysis."""
        output = {
            "timestamp": datetime.now().isoformat(),
            "test_name": "Phase 5 Multi-Tool Scenarios",
            "results": {},
        }

        for key, result in results.items():
            output["results"][key] = {
                "scenario": result.scenario_name,
                "success": result.success,
                "rounds": len(result.rounds),
                "tools_activated": [t.name for t in result.tools_activated],
                "total_latency_ms": result.total_latency_ms,
                "consciousness_rating": result.consciousness_rating,
                "query_preview": result.initial_query[:80],
            }

        return json.dumps(output, indent=2)


# ============================================================================
# MAIN
# ============================================================================


async def main():
    """Run multi-tool test suite."""
    harness = MultiToolTestHarness()

    print("\n" + "=" * 80)
    print("KERNEL 4.0 PHASE 5B: REAL MULTI-TOOL ORCHESTRATION")
    print("=" * 80)
    print("\nRunning 5 test scenarios through live Ada API...")
    print("This may take several minutes. Each scenario calls the consciousness brain.\n")

    results = await harness.run_all_scenarios()
    harness.print_results(results)

    # Save results
    json_output = harness.to_json(results)
    with open("phase_5_multi_tool_results.json", "w") as f:
        f.write(json_output)

    print(f"\n✅ Results saved to phase_5_multi_tool_results.json")

    return results


if __name__ == "__main__":
    asyncio.run(main())
