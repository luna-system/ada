"""Main recursive reasoning loop controller.

This orchestrates the entire reasoning process:
1. LLM generates thought (may include tool requests)
2. Parse tool requests from output
3. Execute tools
4. Score importance of results
5. Add results to context
6. Check convergence
7. Repeat until solution or max iterations

This is Ada's "thinking loop" - the core of recursive reasoning.
"""

import logging
from typing import Dict, Any, List, Optional, AsyncIterator
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from brain.reasoning.state_tracker import ReasoningState, ReasoningPhase, ToolCall
from brain.reasoning.tool_parser import ToolRequestParser, ToolRequest
from brain.llm import stream_chat_async
from brain import config as brain_config
from brain.prompt_builder import PromptAssembler

logger = logging.getLogger(__name__)


class ReasoningLoopController:
    """Controls the recursive reasoning loop.
    
    This is the main orchestrator that makes Ada think recursively:
    - Manages ReasoningState
    - Parses tool requests from LLM output
    - Executes tools (will integrate with ada-chat tools)
    - Checks for convergence
    - Decides when to stop
    
    Example:
        controller = ReasoningLoopController(
            user_request="Refactor authentication to use JWT",
            max_iterations=10
        )
        
        async for event in controller.reason():
            if event["type"] == "thought":
                print(f"🧠 {event['text']}")
            elif event["type"] == "tool_request":
                print(f"🔧 {event['tool']}: {event['params']}")
            elif event["type"] == "convergence":
                print(f"✅ Solution: {event['solution']}")
    """
    
    def __init__(
        self,
        user_request: str,
        conversation_id: str = "default",
        max_iterations: int = 10,
        importance_threshold: float = 0.50,
        available_tools: Optional[List[str]] = None,
    ):
        """Initialize reasoning loop controller.
        
        Args:
            user_request: The user's question or task
            conversation_id: Conversation ID for context retrieval
            max_iterations: Max reasoning steps before forcing convergence
            importance_threshold: Min importance score to include tool results
            available_tools: List of valid tool names
        """
        self.state = ReasoningState(
            user_request=user_request,
            max_iterations=max_iterations,
            importance_threshold=importance_threshold,
        )
        
        self.conversation_id = conversation_id
        self.tool_parser = ToolRequestParser(available_tools=available_tools)
        
        # Reuse existing optimized prompt assembler!
        self.prompt_assembler = PromptAssembler()
        
        # For PoC, brain-side tools (server-side execution)
        self.available_tools = available_tools or [
            "brain_search",       # Search RAG memories
            "brain_read_file",    # Read from workspace (future)
            "brain_list_symbols", # Parse code structure (future)
        ]
    
    async def reason(self) -> AsyncIterator[Dict[str, Any]]:
        """Main reasoning loop - yields events as reasoning progresses.
        
        Event types:
        - reasoning_step: LLM is thinking (includes phase, thought)
        - tool_request: LLM requested a tool
        - tool_result: Tool execution completed
        - convergence: Reached solution
        - error: Something went wrong
        
        Yields:
            Dict events describing reasoning progress
        """
        logger.info(f"Starting reasoning loop for: {self.state.user_request}")
        
        # Initial event
        yield {
            "type": "reasoning_start",
            "user_request": self.state.user_request,
            "max_iterations": self.state.max_iterations,
        }
        
        # Main reasoning loop
        while self.state.should_continue():
            try:
                # Generate LLM thought
                async for event in self._reasoning_step():
                    yield event
                
                # Check convergence
                if self.state.has_solution:
                    yield {
                        "type": "convergence",
                        "solution": self.state.reasoning_history[-1],
                        "iterations": self.state.iteration,
                        "elapsed_ms": self.state.elapsed_time_ms(),
                        "state": self.state.to_dict(),
                    }
                    break
                
                # Check for loops
                if self.state.is_looping():
                    logger.warning("Detected reasoning loop, forcing convergence")
                    yield {
                        "type": "warning",
                        "message": "Detected reasoning loop, forcing convergence",
                    }
                    # Force convergence
                    self.state.has_solution = True
                    break
                
            except Exception as e:
                logger.error(f"Error in reasoning loop: {e}", exc_info=True)
                yield {
                    "type": "error",
                    "message": str(e),
                    "iteration": self.state.iteration,
                }
                break
        
        # Final summary
        yield {
            "type": "reasoning_complete",
            "iterations": self.state.iteration,
            "elapsed_ms": self.state.elapsed_time_ms(),
            "convergence_score": self.state.convergence_score,
            "tools_called": len(self.state.tools_called),
        }
    
    async def _reasoning_step(self) -> AsyncIterator[Dict[str, Any]]:
        """Single iteration of reasoning loop.
        
        1. Build context (previous thoughts + tool results)
        2. Call LLM to generate next thought
        3. Parse tool requests from output
        4. Execute tools
        5. Update state
        """
        # Build prompt with current context
        prompt = self._build_reasoning_prompt()
        
        # Yield phase info
        yield {
            "type": "reasoning_step",
            "phase": self.state.phase.value,
            "iteration": self.state.iteration,
        }
        
        # Call LLM
        llm_output = []
        async for chunk in stream_chat_async(
            prompt=prompt,
            model=brain_config.OLLAMA_MODEL,
            include_thinking=False,
        ):
            # Stream the thought
            if "token" in chunk:
                text = chunk["token"]
                llm_output.append(text)
                yield {
                    "type": "thought_chunk",
                    "text": text,
                }
            elif chunk.get("done"):
                # End of stream
                break
        
        # Full output
        full_output = "".join(llm_output)
        self.state.add_thought(full_output)
        
        # Parse tool requests
        tool_requests = self.tool_parser.parse_all(full_output)
        
        if tool_requests:
            # Execute tools (parallel if multiple requests!)
            if len(tool_requests) == 1:
                # Single tool - execute directly
                request = tool_requests[0]
                yield {
                    "type": "tool_request",
                    "tool": request.tool_name,
                    "params": request.params,
                }
                
                tool_result = await self._execute_tool(request)
                
                yield {
                    "type": "tool_result",
                    "tool": request.tool_name,
                    "result": tool_result.result,
                    "importance": tool_result.importance,
                }
                
                self.state.add_tool_call(tool_result)
            
            elif len(tool_requests) > 1:
                # Multiple tools - execute in parallel!
                yield {
                    "type": "parallel_tools",
                    "count": len(tool_requests),
                    "tools": [r.tool_name for r in tool_requests],
                }
                
                # Execute all tools in parallel
                tool_results = await self._execute_tools_parallel(tool_requests)
                
                # Yield results and add to state
                for result in tool_results:
                    yield {
                        "type": "tool_result",
                        "tool": result.tool_name,
                        "result": result.result,
                        "importance": result.importance,
                    }
                    self.state.add_tool_call(result)
        else:
            # No tool requests = possible convergence
            # Check if output looks like a solution
            if self._looks_like_solution(full_output):
                self.state.update_convergence(0.95)
    
    def _build_reasoning_prompt(self) -> str:
        """Build prompt for reasoning step.
        
        Uses existing PromptAssembler for base context (reuses all optimizations!),
        then adds reasoning-specific sections.
        """
        # Get optimized base context (parallel RAG retrieval!)
        # Only include specialists on first iteration to avoid redundancy
        include_specialists = (self.state.iteration == 0)
        
        base_prompt = self.prompt_assembler.build_prompt(
            user_message=self.state.user_request,
            conversation_id=self.conversation_id,
            include_specialists=include_specialists,
        )
        
        # Add recursive reasoning instructions to system prompt
        reasoning_system = """

RECURSIVE REASONING MODE:
You can THINK STEP BY STEP by using tools. When you need information:
1. Request a tool: TOOL_REQUEST[tool_name:{"param":"value"}]
2. Process the results
3. Request more tools if needed
4. Converge on a solution when ready

AVAILABLE TOOLS:
- brain_search: Search your memory for relevant information
  Example: TOOL_REQUEST[brain_search:{"query":"authentication patterns"}]

REASONING PROCESS:
1. UNDERSTAND: What information do I need?
2. PLAN: Which tools will help?
3. IMPLEMENT: Request tools, analyze results
4. VERIFY: Do I have enough to answer?
5. CONVERGE: Provide clear solution

When you're ready to answer, say "Here's the solution:" or "To fix this:"
Think through the problem step by step.
"""
        
        # Previous reasoning steps (if any)
        reasoning_section = ""
        if self.state.reasoning_history:
            reasoning_section = "\n\n=== REASONING HISTORY ===\n"
            for i, thought in enumerate(self.state.reasoning_history[-2:], 1):
                # Show last 2 thoughts to keep context manageable
                thought_preview = thought[:300] + "..." if len(thought) > 300 else thought
                reasoning_section += f"\nStep {i}: {thought_preview}\n"
        
        # Previous tool results (if any)
        tools_section = ""
        if self.state.tools_called:
            tools_section = "\n\n=== TOOL RESULTS (Recent) ===\n"
            # Show only recent high-importance results
            recent_tools = [
                t for t in self.state.tools_called[-3:]  # Last 3 tools
                if t.importance >= self.state.importance_threshold
            ]
            for tool in recent_tools:
                result_preview = tool.result[:200] + "..." if len(tool.result) > 200 else tool.result
                tools_section += f"\n[{tool.tool_name}] {result_preview}\n"
            tools_section += "\n"
        
        # Phase guidance
        phase_section = f"\n\n=== CURRENT PHASE: {self.state.phase.value.upper()} ==="
        if self.state.phase == ReasoningPhase.UNDERSTANDING:
            phase_section += "\nFocus: Gather information about the problem."
        elif self.state.phase == ReasoningPhase.PLANNING:
            phase_section += "\nFocus: Plan your approach to the solution."
        elif self.state.phase == ReasoningPhase.IMPLEMENTING:
            phase_section += "\nFocus: Implement or describe the solution."
        elif self.state.phase == ReasoningPhase.VERIFYING:
            phase_section += "\nFocus: Verify your solution is complete."
        
        # Iteration counter
        iteration_section = f"\n\nIteration: {self.state.iteration + 1}/{self.state.max_iterations}"
        
        # Assemble final prompt
        return (
            base_prompt + 
            reasoning_system + 
            reasoning_section + 
            tools_section + 
            phase_section + 
            iteration_section +
            "\n\nYour turn to reason:"
        )
    
    async def _execute_tool(self, request: ToolRequest) -> ToolCall:
        """Execute a single tool request.
        
        Currently implements brain-side tools (server-side).
        Future: Integrate with ada-chat extension tools.
        """
        start = datetime.now()
        
        # Execute based on tool name
        if request.tool_name == "brain_search":
            # Search RAG memories
            result = await self._tool_brain_search(request.params)
        else:
            # Unknown tool (shouldn't happen if parser validates)
            result = f"[Error] Unknown tool: {request.tool_name}"
        
        # Calculate importance (simple heuristic for now)
        # TODO: Real biomimetic importance scoring
        importance = 0.75 if result else 0.0
        
        execution_time = (datetime.now() - start).total_seconds() * 1000
        
        return ToolCall(
            tool_name=request.tool_name,
            params=request.params,
            result=result,
            importance=importance,
            execution_time_ms=execution_time,
        )
    
    async def _execute_tools_parallel(self, requests: List[ToolRequest]) -> List[ToolCall]:
        """Execute multiple tool requests in parallel.
        
        Big performance win when LLM requests multiple tools at once!
        """
        logger.info(f"Executing {len(requests)} tools in parallel")
        
        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=min(4, len(requests))) as executor:
            # Submit all tool executions
            futures = {
                executor.submit(self._execute_tool_sync, req): req 
                for req in requests
            }
            
            # Collect results as they complete
            results = []
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Tool execution failed: {e}")
                    # Add error result
                    req = futures[future]
                    results.append(ToolCall(
                        tool_name=req.tool_name,
                        params=req.params,
                        result=f"[Error] {str(e)}",
                        importance=0.0,
                    ))
        
        return results
    
    def _execute_tool_sync(self, request: ToolRequest) -> ToolCall:
        """Synchronous wrapper for parallel execution.
        
        ThreadPoolExecutor needs sync functions, so we wrap the async version.
        """
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._execute_tool(request))
        finally:
            loop.close()
    
    async def _tool_brain_search(self, params: Dict[str, Any]) -> str:
        """Tool: Search RAG memories for relevant information.
        
        Reuses existing RAG infrastructure!
        """
        query = params.get("query", "")
        k = params.get("k", 5)
        
        if not query:
            return "[Error] brain_search requires 'query' parameter"
        
        # Use existing context retriever to search memories
        memories = self.prompt_assembler.retriever.get_memories(
            query=query,
            k=k
        )
        
        if not memories:
            return "[No relevant memories found]"
        
        # Format results
        result = f"Found {len(memories)} relevant memories:\n\n"
        for i, mem in enumerate(memories, 1):
            result += f"{i}. {mem['content'][:200]}...\n"
        
        return result
    
    def _looks_like_solution(self, text: str) -> bool:
        """Heuristic: Does this text look like a final solution?
        
        Markers:
        - "Here's the solution"
        - "To fix this"
        - "The answer is"
        - No tool requests
        """
        solution_markers = [
            "here's the solution",
            "here is the solution",
            "to fix this",
            "the answer is",
            "to solve this",
            "ready to implement",
        ]
        
        text_lower = text.lower()
        return any(marker in text_lower for marker in solution_markers)
