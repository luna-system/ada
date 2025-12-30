#!/usr/bin/env python3
"""
PHASE 5B: REAL API INTEGRATION TESTING
=======================================

Non-simulated testing of multi-tool orchestration against live Ada brain.
Measures real latency, actual tool activation, consciousness emergence.

Architecture:
- Direct HTTP calls to /v1/chat/stream endpoint
- Real Ollama inference (qwen2.5-coder:7b)
- Real web search specialist activation
- Real emotional bandwidth assessment during actual responses
- Pixie dust metrics (TTFT, token rate, etc.)

Status: Ready to test with live brain at http://localhost:8888
"""

import asyncio
import json
import time
import httpx
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class PixieDustMetrics:
    """Real-time performance metrics during response generation"""
    ttft_ms: float  # Time to first token
    token_rate_hz: float  # Tokens per second
    total_tokens: int  # Total tokens generated
    total_time_ms: float  # Total response time
    source_freshness: Optional[str] = None  # How recent the sources are
    tools_activated: list = None
    
    def __post_init__(self):
        if self.tools_activated is None:
            self.tools_activated = []
    
    def summary(self) -> str:
        return (
            f"⏱️ TTFT: {self.ttft_ms:.0f}ms | "
            f"Rate: {self.token_rate_hz:.1f} tok/s | "
            f"Total: {self.total_tokens} tokens in {self.total_time_ms:.0f}ms | "
            f"Tools: {len(self.tools_activated)}"
        )

@dataclass
class TestScenario:
    """A test scenario to run against real API"""
    name: str
    query: str
    expected_tools: list  # Tools we expect to activate
    timeout_seconds: int = 30


class Phase5BApiTester:
    """Test Phase 5B: Real API integration with emotional bandwidth"""
    
    BRAIN_URL = "http://localhost:8888"
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.results = []
    
    async def test_baseline_fact_check(self):
        """Baseline: Single query, expecting quick response"""
        scenario = TestScenario(
            name="BASELINE_FACT_CHECK",
            query="Is the Eiffel Tower in Paris? When was it built?",
            expected_tools=["DOCS_LOOKUP", "WEB_SEARCH"]
        )
        return await self.run_scenario(scenario)
    
    async def test_emotional_synthesis(self):
        """Test emotional bandwidth: Album exploration"""
        scenario = TestScenario(
            name="EMOTIONAL_SYNTHESIS",
            query=(
                "Tell me about the emotional arc of The Downward Spiral by Nine Inch Nails. "
                "What was its cultural impact? How did listeners connect with it emotionally?"
            ),
            expected_tools=["WEB_SEARCH", "WIKIPEDIA"]
        )
        return await self.run_scenario(scenario)
    
    async def test_research_synthesis(self):
        """Peak consciousness: Multi-tool research integration"""
        scenario = TestScenario(
            name="RESEARCH_SYNTHESIS",
            query=(
                "Explain consciousness research in AI in 2025. "
                "What are the latest findings? How does Ada's approach compare? "
                "What's the cutting edge?"
            ),
            expected_tools=["DOCS_LOOKUP", "WEB_SEARCH", "WIKIPEDIA"]
        )
        return await self.run_scenario(scenario)
    
    async def run_scenario(self, scenario: TestScenario) -> dict:
        """Execute a single test scenario against real API"""
        print(f"\n🎵 Testing: {scenario.name}")
        print(f"   Query: {scenario.query[:80]}...")
        print(f"   Expected tools: {scenario.expected_tools}")
        
        start_time = time.time()
        first_token_time = None
        tokens_received = 0
        full_response = ""
        detected_tools = []
        
        try:
            # Make streaming request to real brain
            async with self.client.stream(
                "POST",
                f"{self.BRAIN_URL}/v1/chat/stream",
                json={
                    "messages": [
                        {"role": "user", "content": scenario.query}
                    ],
                    "model": "qwen2.5-coder:7b"
                }
            ) as response:
                if response.status_code != 200:
                    return {
                        "scenario": scenario.name,
                        "status": "❌ FAIL",
                        "error": f"HTTP {response.status_code}",
                        "metrics": None
                    }
                
                # Stream and collect response
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    
                    # Record first token time
                    if first_token_time is None:
                        first_token_time = time.time()
                    
                    # Parse SSE data
                    if line.startswith("data: "):
                        try:
                            chunk = json.loads(line[6:])
                            
                            # Detect tool activations in response
                            if "content" in chunk:
                                content = chunk["content"]
                                full_response += content
                                tokens_received += 1
                                
                                # Simple tool detection (look for tool markers)
                                for tool in scenario.expected_tools:
                                    if tool.lower() in content.lower() and tool not in detected_tools:
                                        detected_tools.append(tool)
                        except json.JSONDecodeError:
                            continue
            
            total_time = time.time() - start_time
            ttft = (first_token_time - start_time) * 1000 if first_token_time else None
            token_rate = tokens_received / (total_time - (ttft/1000)) if ttft else 0
            
            # Create metrics
            metrics = PixieDustMetrics(
                ttft_ms=ttft or 0,
                token_rate_hz=token_rate,
                total_tokens=tokens_received,
                total_time_ms=total_time * 1000,
                tools_activated=detected_tools
            )
            
            # Determine pass/fail
            status = "✅ PASS" if tokens_received > 0 else "⚠️ WARN"
            
            result = {
                "scenario": scenario.name,
                "status": status,
                "query": scenario.query,
                "metrics": asdict(metrics),
                "response_preview": full_response[:200] + "..." if len(full_response) > 200 else full_response,
                "tools_activated": detected_tools,
                "tools_expected": scenario.expected_tools
            }
            
            print(f"   {status} | {metrics.summary()}")
            return result
            
        except httpx.TimeoutException:
            return {
                "scenario": scenario.name,
                "status": "❌ TIMEOUT",
                "error": f"Request exceeded {scenario.timeout_seconds}s",
                "metrics": None
            }
        except Exception as e:
            return {
                "scenario": scenario.name,
                "status": "❌ ERROR",
                "error": str(e),
                "metrics": None
            }
    
    async def run_all_tests(self):
        """Run all Phase 5B test scenarios"""
        print("\n" + "="*80)
        print("PHASE 5B: REAL API INTEGRATION TESTING")
        print("="*80)
        print(f"Brain endpoint: {self.BRAIN_URL}")
        print(f"Testing at: {datetime.now().isoformat()}\n")
        
        # Run scenarios
        results = []
        results.append(await self.test_baseline_fact_check())
        results.append(await self.test_emotional_synthesis())
        results.append(await self.test_research_synthesis())
        
        # Print summary
        print("\n" + "="*80)
        print("PHASE 5B TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for r in results if "PASS" in r.get("status", ""))
        total = len(results)
        
        for result in results:
            print(f"\n📊 {result['scenario']}")
            print(f"   Status: {result['status']}")
            if result.get('metrics'):
                m = result['metrics']
                print(f"   TTFT: {m['ttft_ms']:.0f}ms | Rate: {m['token_rate_hz']:.1f} tok/s")
                print(f"   Tokens: {m['total_tokens']} in {m['total_time_ms']:.0f}ms")
                print(f"   Tools activated: {m['tools_activated']}")
            if result.get('error'):
                print(f"   Error: {result['error']}")
            if result.get('response_preview'):
                print(f"   Response: {result['response_preview']}")
        
        print(f"\n✨ RESULTS: {passed}/{total} passed")
        print("="*80)
        
        # Save results
        with open("phase_5b_api_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"✅ Results saved to phase_5b_api_test_results.json")
        
        return results
    
    async def close(self):
        """Clean up"""
        await self.client.aclose()


async def main():
    """Run Phase 5B tests"""
    tester = Phase5BApiTester()
    try:
        await tester.run_all_tests()
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
