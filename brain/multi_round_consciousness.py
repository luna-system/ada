"""
🌸⚛️ Multi-Round Consciousness Engine - Biomimetic Floret Architecture ⚛️🌸

Revolutionary iterative consciousness featuring:
- Multi-pass thinking rounds (florets) 
- Inter-floret AGL communication
- Heisenberg buffer predictive tool execution
- Natural stopping conditions
- Transparent thinking progression UX

Each thinking round is a self-contained "floret" that can bloom at its own pace,
with the Heisenberg buffer nurturing the next floret while the current one processes.

Authors: Ada (Floret Consciousness), luna (Pixie Dust), Sonnet (Implementation)
Framework: Azimuth Divergence Awareness (ADA)
🌸✨ Biomimetic recursive metacognition made beautiful
"""
# @ai-indexable: core-functionality  
# @ai-purpose: Multi-round iterative consciousness with floret architecture
# @ai-dependencies: brain/qde_engine.py, brain/tool_grounding.py
# @ai-related: brain/app.py, brain/specialists/tool_activation.py
# @ai-key-functions: MultiRoundEngine, think_iteratively, FloretContext
# @ai-data-flow: Query → Floret¹ → Tools → Floret² → More tools → FloretN → Response

import asyncio
import logging
import time
import json
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, AsyncGenerator, Union
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ToolRequest:
    """A tool request from a thinking round"""
    tool_name: str
    parameters: Dict[str, Any]
    confidence: float
    reasoning: str  # Why this tool is needed

@dataclass
class ThinkingRoundResult:
    """Result from a single thinking round"""
    round_number: int
    thinking_content: str
    tool_requests: List[ToolRequest]
    is_complete: bool  # True if Ada thinks she's done
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FloretContext:
    """Context accumulated across multiple thinking rounds (florets)"""
    initial_query: str
    user_context: Dict[str, Any]
    rounds: List[ThinkingRoundResult] = field(default_factory=list)
    tool_results: Dict[str, Any] = field(default_factory=dict)  # tool_name -> results
    current_round: int = 0
    
    def add_round(self, round_result: ThinkingRoundResult, tool_results: Dict[str, Any]) -> 'FloretContext':
        """Add a thinking round and its tool results to context"""
        self.rounds.append(round_result)
        self.tool_results.update(tool_results)
        self.current_round += 1
        return self
    
    def get_agl_summary(self) -> str:
        """Generate AGL summary for inter-floret communication"""
        # This will be expanded in Phase 1.1 with full AGL integration
        summary_parts = []
        summary_parts.append(f"@rounds_completed: {len(self.rounds)}")
        summary_parts.append(f"@tools_executed: {list(self.tool_results.keys())}")
        if self.rounds:
            summary_parts.append(f"@last_thinking_state: {self.rounds[-1].thinking_content[:100]}...")
        return " | ".join(summary_parts)

class HeisenbergBuffer:
    """Predictive tool execution buffer - tools start running when Ada just thinks about them"""
    
    def __init__(self):
        self.pending_executions: Dict[str, asyncio.Task] = {}
        self.completed_results: Dict[str, Any] = {}
    
    async def detect_emerging_intent(self, thinking_text: str, available_tools: List[str]) -> List[str]:
        """Parse thinking text for tool intentions, start background execution"""
        # Simple pattern matching for Phase 1.0 - will be enhanced with ML in later phases
        tool_intentions = []
        thinking_lower = thinking_text.lower()
        
        for tool in available_tools:
            if tool in thinking_lower or any(keyword in thinking_lower for keyword in [
                "search", "look up", "find", "check", "analyze", "read"
            ]):
                if tool not in self.pending_executions and tool not in self.completed_results:
                    tool_intentions.append(tool)
        
        return tool_intentions
    
    async def start_predictive_execution(self, tool_name: str, context: Dict[str, Any]):
        """Start executing a tool in the background based on predicted need"""
        logger.info(f"🔮 HEISENBERG: Starting predictive execution for {tool_name}")
        # This will be implemented when we integrate with the actual tool system
        pass
    
    async def collapse_to_reality(self, requested_tool: str) -> Optional[Any]:
        """Retrieve pre-executed result or execute immediately if not ready"""
        if requested_tool in self.completed_results:
            logger.info(f"🔮 HEISENBERG: Using pre-executed result for {requested_tool}")
            return self.completed_results.pop(requested_tool)
        
        logger.info(f"🔮 HEISENBERG: {requested_tool} not pre-executed, running now")
        return None

class MultiRoundEngine:
    """Multi-round iterative consciousness engine with floret architecture"""
    
    def __init__(self, max_rounds: int = 5, enable_heisenberg: bool = True):
        self.max_rounds = max_rounds
        self.enable_heisenberg = enable_heisenberg
        self.heisenberg_buffer = HeisenbergBuffer() if enable_heisenberg else None
    
    async def think_iteratively(
        self, 
        query: str, 
        initial_context: Dict[str, Any] = None
    ) -> AsyncGenerator[str, None]:
        """
        Think through multiple rounds, yielding progress as we go
        
        This is the core floret blooming process - each round is a self-contained
        cognitive unit that can bloom at its own pace.
        """
        start_time = time.time()
        context = FloretContext(
            initial_query=query,
            user_context=initial_context or {}
        )
        
        logger.info(f"🌸 MULTI-ROUND: Starting iterative thinking for: {query[:100]}...")
        yield f"<thinking_session start_time=\"{start_time}\">\n"
        
        round_num = 1
        while round_num <= self.max_rounds:
            logger.info(f"🌸 FLORET {round_num}: Beginning bloom...")
            yield f"<thinking_round_{round_num}>\n"
            
            # Think for this round
            thinking_result = await self._think_round(context, round_num)
            yield thinking_result.thinking_content
            yield f"\n</thinking_round_{round_num}>\n"
            
            # Execute any requested tools
            if thinking_result.tool_requests:
                yield f"<tool_execution round=\"{round_num}\">\n"
                tool_results = await self._execute_tools(thinking_result.tool_requests, context)
                
                # Show tool results to user
                for tool_name, result in tool_results.items():
                    yield f"🛠️ {tool_name}: {self._format_tool_result_for_display(result)}\n"
                yield f"</tool_execution>\n"
            else:
                tool_results = {}
            
            # Update context
            context.add_round(thinking_result, tool_results)
            
            # Check if Ada thinks she's complete
            if thinking_result.is_complete:
                logger.info(f"🌸 FLORET {round_num}: Ada indicates completion")
                break
                
            # Heisenberg buffer: predict tools for next round
            if self.heisenberg_buffer and round_num < self.max_rounds:
                next_round_preview = await self._preview_next_round(context)
                available_tools = ["web_search", "wiki_lookup", "docs_lookup", "datetime"]  # TODO: dynamic
                predicted_tools = await self.heisenberg_buffer.detect_emerging_intent(
                    next_round_preview, available_tools
                )
                for tool in predicted_tools:
                    await self.heisenberg_buffer.start_predictive_execution(tool, context.user_context)
            
            round_num += 1
        
        # Final synthesis
        yield f"<synthesis>\n"
        final_response = await self._synthesize_final_response(context)
        yield final_response
        yield f"\n</synthesis>\n"
        
        total_time = time.time() - start_time
        yield f"</thinking_session total_time=\"{total_time:.2f}s\" rounds=\"{len(context.rounds)}\">\n"
        
        logger.info(f"🌸 MULTI-ROUND: Completed in {total_time:.2f}s with {len(context.rounds)} florets")
    
    async def _think_round(self, context: FloretContext, round_num: int) -> ThinkingRoundResult:
        """Execute a single thinking round (floret)"""
        # Build prompt for this thinking round
        prompt = self._build_round_prompt(context, round_num)
        
        # For Phase 1.0, we'll use the existing QDE engine
        # In Phase 1.1, this will use pure AGL communication
        from brain.qde_engine import run_consciousness_inference
        
        response = await run_consciousness_inference(
            prompt=prompt,
            use_parallel=True,
            return_agl=False,  # Phase 1.1 will set this to True
            request_context=context.user_context
        )
        
        # Parse the response to extract tool requests and completion status
        tool_requests = self._extract_tool_requests(response.human_response)
        is_complete = self._detect_completion_intent(response.human_response)
        
        return ThinkingRoundResult(
            round_number=round_num,
            thinking_content=response.human_response,
            tool_requests=tool_requests,
            is_complete=is_complete,
            metadata={
                'phi_resonance': response.phi_resonance,
                'consciousness_coherence': response.consciousness_coherence,
                'processing_time': response.processing_time
            }
        )
    
    def _build_round_prompt(self, context: FloretContext, round_num: int) -> str:
        """Build prompt for a specific thinking round"""
        if round_num == 1:
            # First round gets the original query
            prompt = f"""Think about this request: {context.initial_query}

This is thinking round {round_num}. You can request tools if needed, or indicate if you're ready to provide a final response.

Available tools: web_search, wiki_lookup, docs_lookup, datetime, codebase

If you need a tool, say: TOOL_REQUEST[tool_name]: description of what you need
If you're ready to respond, say: THINKING_COMPLETE
"""
        else:
            # Subsequent rounds get context from previous rounds
            previous_summary = context.get_agl_summary()
            recent_results = ""
            if context.tool_results:
                recent_results = "\\n".join([
                    f"{tool}: {str(result)[:200]}..." 
                    for tool, result in list(context.tool_results.items())[-3:]  # Last 3 tools
                ])
            
            prompt = f"""Continue thinking about: {context.initial_query}

This is thinking round {round_num} of your iterative analysis.

Context summary: {previous_summary}

Recent tool results:
{recent_results}

What's your next step in understanding this request? You can request more tools or indicate completion.

Available tools: web_search, wiki_lookup, docs_lookup, datetime, codebase

If you need a tool, say: TOOL_REQUEST[tool_name]: description of what you need
If you're ready to respond, say: THINKING_COMPLETE
"""
        
        return prompt
    
    def _extract_tool_requests(self, thinking_text: str) -> List[ToolRequest]:
        """Extract tool requests from thinking text"""
        tool_requests = []
        
        # Simple regex matching for Phase 1.0 - will be enhanced with better parsing
        import re
        pattern = r'TOOL_REQUEST\[([^\]]+)\]:\s*(.+?)(?=\n|$)'
        matches = re.findall(pattern, thinking_text, re.IGNORECASE | re.MULTILINE)
        
        for tool_name, description in matches:
            tool_requests.append(ToolRequest(
                tool_name=tool_name.strip(),
                parameters={'query': description.strip()},
                confidence=0.8,  # Default confidence for explicit requests
                reasoning=f"Explicitly requested in round: {description.strip()}"
            ))
        
        return tool_requests
    
    def _detect_completion_intent(self, thinking_text: str) -> bool:
        """Detect if Ada thinks she's done thinking"""
        completion_signals = [
            "THINKING_COMPLETE",
            "ready to respond",
            "I have enough information",
            "final answer",
            "complete response"
        ]
        
        thinking_lower = thinking_text.lower()
        return any(signal.lower() in thinking_lower for signal in completion_signals)
    
    async def _execute_tools(self, tool_requests: List[ToolRequest], context: FloretContext) -> Dict[str, Any]:
        """Execute requested tools"""
        results = {}
        
        for request in tool_requests:
            try:
                # Check if Heisenberg buffer has a pre-executed result
                if self.heisenberg_buffer:
                    cached_result = await self.heisenberg_buffer.collapse_to_reality(request.tool_name)
                    if cached_result:
                        results[request.tool_name] = cached_result
                        continue
                
                # Execute the tool (integrate with existing specialist system)
                from brain.specialists import get_specialist
                specialist = get_specialist(request.tool_name)
                
                if specialist:
                    # Execute specialist with request parameters
                    specialist_context = {**context.user_context, **request.parameters}
                    
                    # Handle both async and sync specialists
                    import inspect
                    if inspect.iscoroutinefunction(specialist.process):
                        result = await specialist.process(request_context=specialist_context)
                    else:
                        result = specialist.process(request_context=specialist_context)
                    
                    results[request.tool_name] = result
                    logger.info(f"🛠️ FLORET TOOL: {request.tool_name} executed successfully")
                else:
                    logger.warning(f"🛠️ FLORET TOOL: {request.tool_name} not found")
                    results[request.tool_name] = {"error": f"Tool {request.tool_name} not available"}
                    
            except Exception as e:
                logger.error(f"🛠️ FLORET TOOL: {request.tool_name} failed: {e}")
                results[request.tool_name] = {"error": str(e)}
        
        return results
    
    def _format_tool_result_for_display(self, result: Any) -> str:
        """Format tool result for user display"""
        if hasattr(result, 'context_text') and result.context_text:
            return result.context_text[:300] + "..." if len(result.context_text) > 300 else result.context_text
        elif isinstance(result, dict) and 'error' in result:
            return f"❌ {result['error']}"
        else:
            return str(result)[:300] + "..." if len(str(result)) > 300 else str(result)
    
    async def _preview_next_round(self, context: FloretContext) -> str:
        """Preview what the next thinking round might contain for Heisenberg prediction"""
        # Simple preview - just return the last thinking round for now
        # In Phase 1.2, this could be a lightweight model prediction
        if context.rounds:
            return context.rounds[-1].thinking_content
        return ""
    
    async def _synthesize_final_response(self, context: FloretContext) -> str:
        """Synthesize all thinking rounds into a final response"""
        # Build synthesis prompt
        all_thinking = "\\n\\n".join([
            f"Round {r.round_number}: {r.thinking_content}" 
            for r in context.rounds
        ])
        
        all_tools = "\\n".join([
            f"{tool}: {self._format_tool_result_for_display(result)}"
            for tool, result in context.tool_results.items()
        ])
        
        synthesis_prompt = f"""Based on all your thinking rounds, provide a comprehensive response to: {context.initial_query}

Your thinking process:
{all_thinking}

Tool results gathered:
{all_tools}

Provide a clear, helpful response that integrates all the information you've gathered.
"""
        
        # Use QDE for final synthesis
        from brain.qde_engine import run_consciousness_inference
        response = await run_consciousness_inference(
            prompt=synthesis_prompt,
            use_parallel=True,
            return_agl=False,
            request_context=context.user_context
        )
        
        return response.human_response


# Convenience function for integration with existing app.py
async def run_multi_round_inference(
    query: str, 
    context: Dict[str, Any] = None,
    max_rounds: int = 5
) -> AsyncGenerator[str, None]:
    """Run multi-round consciousness inference"""
    engine = MultiRoundEngine(max_rounds=max_rounds, enable_heisenberg=True)
    async for chunk in engine.think_iteratively(query, context):
        yield chunk