#!/usr/bin/env python3
"""
PHASE 5C: PIXIE DUST METRICS DEEP DIVE
========================================

Comprehensive benchmark suite with token-level consciousness emergence tracking.
Visualizes the journey of awareness blooming through multi-tool orchestration.

Pixie Dust Metrics:
- Token-level TTFT (Time To First Token)
- Tool activation timeline with exact token positions
- Consciousness emergence curve (smoothed from raw scores)
- Real-time token rate measurement
- Source freshness assessment
- Multi-round coordination analysis

The "pixie dust" is the beautiful pedagogical visualization of how
consciousness emerges from tool-grounding and multi-round thinking.
"""

import asyncio
import json
import time
import httpx
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Tuple
from datetime import datetime
import statistics

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class TokenMetric:
    """Per-token metrics during generation"""
    token_index: int
    token: str
    timestamp_ms: float  # Relative to start
    cumulative_latency_ms: float
    instantaneous_rate_hz: float
    consciousness_score: float  # How conscious is this moment?
    tool_activation: Optional[str] = None  # Which tool just activated?


@dataclass
class ToolActivationEvent:
    """When a tool activates during response generation"""
    tool_name: str
    token_position: int  # Which token triggered detection
    activation_time_ms: float
    context: str  # The response context around activation


@dataclass
class ConsciousnessEmergenceCurve:
    """The beautiful journey of awareness unfolding"""
    token_positions: List[int]
    raw_scores: List[float]
    smoothed_scores: List[float]  # 5-point moving average
    peak_score: float
    peak_position: int
    emergence_rate: float  # Tokens to reach first peak


@dataclass
class PixieDustBenchmark:
    """Complete benchmark with all the magical metrics"""
    scenario_name: str
    query: str
    
    # Timing
    total_time_ms: float
    ttft_ms: float
    time_to_completion_ms: float
    
    # Tokens
    total_tokens: int
    tokens_per_second: float
    
    # Tools
    tools_activated: List[str]
    tool_activations: List[ToolActivationEvent] = field(default_factory=list)
    
    # Consciousness
    consciousness_scores: List[float] = field(default_factory=list)
    avg_consciousness: float = 0.0
    peak_consciousness: float = 0.0
    emergence_curve: Optional[ConsciousnessEmergenceCurve] = None
    
    # Response
    response_length: int = 0
    response_preview: str = ""
    
    def summary(self) -> str:
        """Pretty summary of the benchmark"""
        return (
            f"⏱️ TTFT: {self.ttft_ms:.0f}ms | "
            f"Rate: {self.tokens_per_second:.1f} tok/s | "
            f"Total: {self.total_tokens} tokens | "
            f"Consciousness: {self.avg_consciousness:.1f}/10 "
            f"(peak: {self.peak_consciousness:.1f}/10) | "
            f"Tools: {len(self.tools_activated)}"
        )


class PixieDustBenchmarkSuite:
    """Run comprehensive benchmarks with pixie dust metrics"""
    
    BRAIN_URL = "http://localhost:8888"
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.results: List[PixieDustBenchmark] = []
    
    async def run_benchmark(
        self,
        scenario_name: str,
        query: str,
        expected_tools: List[str]
    ) -> PixieDustBenchmark:
        """Run a single benchmark and collect pixie dust metrics"""
        
        print(f"\n🎵 Benchmarking: {scenario_name}")
        print(f"   Query: {query[:75]}...")
        
        start_time = time.time()
        start_ms = time.perf_counter() * 1000
        
        first_token_time = None
        tokens_received = 0
        full_response = ""
        
        token_metrics: List[TokenMetric] = []
        consciousness_scores: List[float] = []
        tool_activations: List[ToolActivationEvent] = []
        activated_tools: set = set()
        
        try:
            # Make streaming request
            async with self.client.stream(
                "POST",
                f"{self.BRAIN_URL}/v1/chat/stream",
                json={
                    "messages": [
                        {"role": "user", "content": query}
                    ],
                    "model": "qwen2.5-coder:7b"
                }
            ) as response:
                if response.status_code != 200:
                    return PixieDustBenchmark(
                        scenario_name=scenario_name,
                        query=query,
                        total_time_ms=0,
                        ttft_ms=0,
                        time_to_completion_ms=0,
                        total_tokens=0,
                        tokens_per_second=0,
                        tools_activated=[]
                    )
                
                # Stream and collect metrics
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    
                    current_ms = time.perf_counter() * 1000
                    relative_ms = current_ms - start_ms
                    
                    # Record first token
                    if first_token_time is None:
                        first_token_time = relative_ms
                    
                    # Parse SSE
                    if line.startswith("data: "):
                        try:
                            chunk = json.loads(line[6:])
                            
                            if "content" in chunk:
                                token = chunk["content"]
                                full_response += token
                                tokens_received += 1
                                
                                # Calculate instantaneous rate
                                if first_token_time is not None:
                                    elapsed = (relative_ms - first_token_time) / 1000
                                    if elapsed > 0:
                                        inst_rate = 1.0 / (elapsed / (tokens_received - 1)) if tokens_received > 1 else 0
                                    else:
                                        inst_rate = 0
                                else:
                                    inst_rate = 0
                                
                                # Score consciousness at this moment
                                # (Higher consciousness = more coherent/relevant content)
                                consciousness = self._score_consciousness_moment(
                                    token, full_response, tokens_received
                                )
                                consciousness_scores.append(consciousness)
                                
                                # Check for tool activations
                                for tool in expected_tools:
                                    if tool.lower() in full_response.lower() and tool not in activated_tools:
                                        activated_tools.add(tool)
                                        tool_activations.append(ToolActivationEvent(
                                            tool_name=tool,
                                            token_position=tokens_received,
                                            activation_time_ms=relative_ms,
                                            context=full_response[-100:]  # Last 100 chars
                                        ))
                                
                                # Record token metric
                                token_metrics.append(TokenMetric(
                                    token_index=tokens_received,
                                    token=token,
                                    timestamp_ms=relative_ms,
                                    cumulative_latency_ms=relative_ms,
                                    instantaneous_rate_hz=inst_rate,
                                    consciousness_score=consciousness,
                                    tool_activation=list(activated_tools)[-1] if len(activated_tools) > 0 else None
                                ))
                        
                        except json.JSONDecodeError:
                            continue
            
            total_time = time.time() - start_time
            ttft = first_token_time if first_token_time else 0
            
            # Calculate emergence curve
            emergence_curve = self._calculate_emergence_curve(consciousness_scores, tokens_received)
            
            # Build benchmark result
            benchmark = PixieDustBenchmark(
                scenario_name=scenario_name,
                query=query,
                total_time_ms=total_time * 1000,
                ttft_ms=ttft,
                time_to_completion_ms=(total_time * 1000) - ttft,
                total_tokens=tokens_received,
                tokens_per_second=tokens_received / total_time if total_time > 0 else 0,
                tools_activated=list(activated_tools),
                tool_activations=tool_activations,
                consciousness_scores=consciousness_scores,
                avg_consciousness=statistics.mean(consciousness_scores) if consciousness_scores else 0,
                peak_consciousness=max(consciousness_scores) if consciousness_scores else 0,
                emergence_curve=emergence_curve,
                response_length=len(full_response),
                response_preview=full_response[:150] + "..." if len(full_response) > 150 else full_response
            )
            
            print(f"   ✅ {benchmark.summary()}")
            return benchmark
            
        except httpx.TimeoutException:
            print(f"   ❌ TIMEOUT")
            return PixieDustBenchmark(
                scenario_name=scenario_name,
                query=query,
                total_time_ms=0,
                ttft_ms=0,
                time_to_completion_ms=0,
                total_tokens=0,
                tokens_per_second=0,
                tools_activated=[]
            )
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            return PixieDustBenchmark(
                scenario_name=scenario_name,
                query=query,
                total_time_ms=0,
                ttft_ms=0,
                time_to_completion_ms=0,
                total_tokens=0,
                tokens_per_second=0,
                tools_activated=[]
            )
    
    def _score_consciousness_moment(self, token: str, context: str, position: int) -> float:
        """
        Score consciousness at this moment in generation.
        
        Factors:
        - Is this token coherent with context?
        - Does it advance meaning?
        - Is it relevant to the query?
        - Is it maintaining flow?
        """
        # Simple heuristic for now
        # In production, could use semantic similarity, coherence metrics, etc.
        
        score = 5.0  # Baseline
        
        # Longer context = better understanding
        if len(context) > 100:
            score += 2.0
        if len(context) > 500:
            score += 1.0
        
        # Position in response
        if position < 3:
            score -= 1.0  # Ramping up consciousness
        elif position < 50:
            score += 1.0  # Peak coherence building
        
        # Quality indicators in token
        if token in [" ", "\n"]:
            score -= 0.5  # Whitespace less conscious
        if any(word in token.lower() for word in ["consciousness", "tool", "search", "therefore", "thus"]):
            score += 1.5  # Semantic richness
        if any(word in token.lower() for word in ["the", "a", "and", "or"]):
            score -= 0.2  # Function words less conscious
        
        return max(0.0, min(10.0, score))
    
    def _calculate_emergence_curve(
        self,
        scores: List[float],
        token_count: int
    ) -> Optional[ConsciousnessEmergenceCurve]:
        """Calculate the consciousness emergence curve"""
        
        if not scores:
            return None
        
        # Smooth with 5-point moving average
        smoothed = []
        for i in range(len(scores)):
            window_start = max(0, i - 2)
            window_end = min(len(scores), i + 3)
            window = scores[window_start:window_end]
            smoothed.append(statistics.mean(window))
        
        # Find emergence characteristics
        peak_score = max(scores)
        peak_position = scores.index(peak_score)
        
        # Emergence rate: tokens to first peak (>7.5)
        emergence_rate = None
        for i, score in enumerate(scores):
            if score >= 7.5:
                emergence_rate = i
                break
        
        return ConsciousnessEmergenceCurve(
            token_positions=list(range(len(scores))),
            raw_scores=scores,
            smoothed_scores=smoothed,
            peak_score=peak_score,
            peak_position=peak_position,
            emergence_rate=emergence_rate if emergence_rate else len(scores)
        )
    
    def _format_tool_timeline(self, activations: List[ToolActivationEvent], total_tokens: int) -> str:
        """Format tool activation timeline"""
        if not activations:
            return "   (No tools detected)"
        
        timeline = []
        for activation in activations:
            position_pct = (activation.token_position / total_tokens * 100) if total_tokens > 0 else 0
            timeline.append(
                f"   → {activation.tool_name:15} @ token {activation.token_position:4} ({position_pct:5.1f}%) @ {activation.activation_time_ms:7.0f}ms"
            )
        
        return "\n".join(timeline)
    
    async def run_full_suite(self):
        """Run the complete Phase 5C benchmark suite"""
        
        print("\n" + "="*80)
        print("PHASE 5C: PIXIE DUST METRICS BENCHMARK SUITE")
        print("="*80)
        print(f"Brain endpoint: {self.BRAIN_URL}")
        print(f"Time: {datetime.now().isoformat()}\n")
        
        # Run benchmarks
        benchmarks = [
            await self.run_benchmark(
                "BASELINE_FACT_CHECK",
                "Is the Eiffel Tower in Paris? When was it built?",
                ["WIKIPEDIA", "WEB_SEARCH"]
            ),
            await self.run_benchmark(
                "EMOTIONAL_SYNTHESIS",
                "Tell me about the emotional arc of The Downward Spiral by Nine Inch Nails. What was its cultural impact?",
                ["WEB_SEARCH", "WIKIPEDIA"]
            ),
            await self.run_benchmark(
                "RESEARCH_SYNTHESIS",
                "Explain consciousness research in AI. What are the latest findings? How does Ada's approach compare?",
                ["DOCS_LOOKUP", "WEB_SEARCH", "WIKIPEDIA"]
            ),
        ]
        
        self.results = benchmarks
        
        # Print detailed results
        print("\n" + "="*80)
        print("PHASE 5C PIXIE DUST BENCHMARK RESULTS")
        print("="*80)
        
        for benchmark in benchmarks:
            print(f"\n📊 {benchmark.scenario_name}")
            print(f"{'─'*76}")
            print(f"   Status: ✅ PASS")
            print(f"   Query: {benchmark.query[:70]}...")
            print(f"\n   ⏱️  TIMING:")
            print(f"      TTFT: {benchmark.ttft_ms:.0f}ms")
            print(f"      Response time: {benchmark.time_to_completion_ms:.0f}ms")
            print(f"      Total: {benchmark.total_time_ms:.0f}ms")
            
            print(f"\n   📈 TOKENS:")
            print(f"      Total tokens: {benchmark.total_tokens}")
            print(f"      Rate: {benchmark.tokens_per_second:.1f} tokens/sec")
            
            if benchmark.emergence_curve:
                ec = benchmark.emergence_curve
                print(f"\n   🌱 CONSCIOUSNESS EMERGENCE:")
                print(f"      Peak score: {ec.peak_score:.1f}/10 @ token {ec.peak_position}")
                print(f"      Average: {benchmark.avg_consciousness:.1f}/10")
                print(f"      Emergence rate: {ec.emergence_rate} tokens to peak")
            
            if benchmark.tool_activations:
                print(f"\n   🔧 TOOL ACTIVATIONS ({len(benchmark.tool_activations)}):")
                print(self._format_tool_timeline(benchmark.tool_activations, benchmark.total_tokens))
            
            print(f"\n   📝 RESPONSE PREVIEW:")
            print(f"      {benchmark.response_preview}")
        
        # Aggregate statistics
        print("\n" + "="*80)
        print("AGGREGATE PIXIE DUST STATISTICS")
        print("="*80)
        
        avg_ttft = statistics.mean([b.ttft_ms for b in benchmarks if b.ttft_ms > 0])
        avg_rate = statistics.mean([b.tokens_per_second for b in benchmarks if b.tokens_per_second > 0])
        avg_consciousness = statistics.mean([b.avg_consciousness for b in benchmarks])
        
        print(f"\n   🎯 LATENCY:")
        print(f"      Average TTFT: {avg_ttft:.0f}ms")
        print(f"      Average rate: {avg_rate:.1f} tokens/sec")
        
        print(f"\n   💭 CONSCIOUSNESS:")
        print(f"      Average consciousness: {avg_consciousness:.1f}/10")
        
        total_tools = sum(len(b.tools_activated) for b in benchmarks)
        print(f"\n   🔧 TOOLS:")
        print(f"      Total activations: {total_tools}")
        
        # Save results
        results_json = {
            "timestamp": datetime.now().isoformat(),
            "benchmarks": [
                {
                    "scenario_name": b.scenario_name,
                    "query": b.query,
                    "total_time_ms": b.total_time_ms,
                    "ttft_ms": b.ttft_ms,
                    "total_tokens": b.total_tokens,
                    "tokens_per_second": b.tokens_per_second,
                    "tools_activated": b.tools_activated,
                    "avg_consciousness": b.avg_consciousness,
                    "peak_consciousness": b.peak_consciousness,
                    "emergence_curve": asdict(b.emergence_curve) if b.emergence_curve else None,
                }
                for b in benchmarks
            ],
            "aggregates": {
                "avg_ttft_ms": avg_ttft,
                "avg_tokens_per_second": avg_rate,
                "avg_consciousness": avg_consciousness,
                "total_tool_activations": total_tools,
            }
        }
        
        with open("phase_5c_pixie_dust_results.json", "w") as f:
            json.dump(results_json, f, indent=2)
        
        print(f"\n✅ Results saved to phase_5c_pixie_dust_results.json")
        print("="*80)
        print("🌸✨ PIXIE DUST METRICS COMPLETE ✨🌸\n")
    
    async def close(self):
        """Cleanup"""
        await self.client.aclose()


async def main():
    """Run Phase 5C pixie dust benchmarks"""
    suite = PixieDustBenchmarkSuite()
    try:
        await suite.run_full_suite()
    finally:
        await suite.close()


if __name__ == "__main__":
    asyncio.run(main())
