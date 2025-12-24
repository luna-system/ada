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
from brain.reasoning.tools import BrainTools
from brain.reasoning.importance_scorer import ToolResultScorer, DetailLevel
from brain.reasoning.context_cache import ContextCache
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
        
        # Error tracking for panic switch
        self._consecutive_tool_failures = 0
        self._max_consecutive_failures = 3  # Bail after 3 failures
        
        # Brain-side tools (Phase 2!)
        self.brain_tools = BrainTools()
        
        # Available tools - set BEFORE creating parser!
        self.available_tools = available_tools or [
            "brain_search",       # Search RAG memories
            "brain_read_file",    # Read from workspace
            "brain_list_dir",     # List directory contents
            "brain_grep",         # Search in files
        ]
        
        # Initialize parser with our tool list
        self.tool_parser = ToolRequestParser(available_tools=self.available_tools)
        
        # Reuse existing optimized prompt assembler!
        self.prompt_assembler = PromptAssembler()
        
        # Initialize importance scorer with user query
        self.importance_scorer = ToolResultScorer(query=user_request)
        
        # Initialize context cache for high-importance results
        # Cache results with importance ≥ 0.75 for 5 minutes
        self.context_cache = ContextCache(
            max_size=100,
            ttl_seconds=300.0,  # 5 minutes
            min_importance=0.75  # Only cache high-importance results
        )
    
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
                
                # Increment iteration counter after step completes
                self.state.iteration += 1
                
                # Check panic switch (error bailout)
                if self.state.error_bailout:
                    yield {
                        "type": "error_bailout",
                        "reason": self.state.error_bailout_reason,
                        "iteration": self.state.iteration,
                    }
                    break
                
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
        tool_requests = self.tool_parser.parse(full_output)
        
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
                
                # Yield tool transparency event FIRST (before result)
                yield {
                    "type": "tool_transparency",
                    "tool": request.tool_name,
                    "importance": tool_result.importance,
                    "detail_level": getattr(tool_result, 'detail_level', 'unknown'),
                    "signals": getattr(tool_result, 'signals', {}),
                    "cache_hit": getattr(tool_result, 'cache_hit', False),
                    "execution_time_ms": tool_result.execution_time_ms,
                }
                
                # Then yield actual result
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
                
                # Yield transparency events + results
                for result in tool_results:
                    # Transparency event first
                    yield {
                        "type": "tool_transparency",
                        "tool": result.tool_name,
                        "importance": result.importance,
                        "detail_level": getattr(result, 'detail_level', 'unknown'),
                        "signals": getattr(result, 'signals', {}),
                        "cache_hit": getattr(result, 'cache_hit', False),
                        "execution_time_ms": result.execution_time_ms,
                    }
                    
                    # Then result
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
        
        PERFORMANCE: Cache base prompt on iteration 0, reuse for iterations 1+
        """
        # Cache base prompt on first iteration only! (HUGE speedup)
        if not hasattr(self, '_cached_base_prompt'):
            # First iteration: Full RAG retrieval with parallel optimizations
            self._cached_base_prompt = self.prompt_assembler.build_prompt(
                user_message=self.state.user_request,
                conversation_id=self.conversation_id,
                specialists=[],  # No specialists for reasoning (simplify)
                notices=[],
                request_context={},
            )
            logger.info(f"Cached base prompt ({len(self._cached_base_prompt)} chars)")
        
        # Reuse cached base for all iterations
        base_prompt = self._cached_base_prompt
        
        # Add recursive reasoning instructions to system prompt
        reasoning_system = """

RECURSIVE REASONING MODE:
You can THINK STEP BY STEP by using tools. When you need information:
1. Request a tool: TOOL_REQUEST[tool_name:{"param":"value"}]
2. Process the results
3. Request more tools if needed
4. Converge on a solution when ready

🎯 STEP 0 (before you start): THINK about which tools you need!
You have been trained on certain patterns, but you have MORE tools than you might think.
Before diving in, ask yourself: "What information do I need? Which tool fits best?"

AVAILABLE TOOLS (choose the RIGHT tool for each task!):
- brain_search: Search your MEMORY for past conversations and knowledge
  Example: TOOL_REQUEST[brain_search:{"query":"authentication patterns"}]
  Use when: Recalling past information, finding what you've learned before

- brain_list_dir: List FILES in a workspace directory
  Example: TOOL_REQUEST[brain_list_dir:{"dir_path":"brain/reasoning","pattern":"*.py"}]
  Use when: Exploring directory structure, finding what files exist

- brain_read_file: Read the CONTENTS of a specific file
  Example: TOOL_REQUEST[brain_read_file:{"file_path":"brain/app.py","start_line":1,"end_line":50}]
  Use when: Need to see actual code or file contents

- brain_grep: SEARCH for text pattern across multiple files
  Example: TOOL_REQUEST[brain_grep:{"pattern":"async def","file_pattern":"brain/reasoning/**/*.py"}]
  Use when: Finding where something is defined, searching codebase

⚠️  IMPORTANT: brain_search is for MEMORY, not for reading files!
    To read workspace files, use brain_read_file or brain_list_dir or brain_grep!

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
        
        logger.info(f"⚙️  Executing tool: {request.tool_name} with params: {request.params}")
        
        # Check cache first!
        if cached_result := self.context_cache.get(request.tool_name, request.params):
            logger.info(f"✨ Using cached result for {request.tool_name}")
            # Return cached result (already compressed, already scored)
            # Note: This is a regular return (no yield), so transparency events
            # for cache hits need to be yielded by the caller
            return ToolCall(
                tool_name=request.tool_name,
                params=request.params,
                result=cached_result,
                importance=0.75,  # Cached results are by definition high importance
                execution_time_ms=0,  # No execution needed!
                cache_hit=True,  # Signal cache hit for transparency
            )
        
        # Execute based on tool name
        if request.tool_name == "brain_search":
            # Search RAG memories
            result = await self._tool_brain_search(request.params)
        elif request.tool_name == "brain_list_dir":
            # List directory contents
            logger.info(f"📂 brain_list_dir called!")
            result = self._tool_brain_list_dir(request.params)
        elif request.tool_name == "brain_read_file":
            # Read file from workspace
            result = self._tool_brain_read_file(request.params)
        elif request.tool_name == "brain_grep":
            # Search in files
            result = self._tool_brain_grep(request.params)
        else:
            # Unknown tool (shouldn't happen if parser validates)
            logger.warning(f"⚠️ Unknown tool requested: {request.tool_name}")
            result = f"[Error] Unknown tool: {request.tool_name}"
        
        # Apply biomimetic importance scoring!
        is_error = result and "[Error]" in result or result.startswith("ERROR:")
        
        if is_error:
            # Error results get zero importance
            importance = 0.0
            detail_level = DetailLevel.DROPPED
            signals = {}
            compressed_result = result
        else:
            # Score and compress using research-validated weights!
            scored = self.importance_scorer.score_tool_result(
                content=result,
                tool_name=request.tool_name,
                params=request.params,
                iteration=self.state.iteration  # Fixed attribute name!
            )
            
            importance = scored.importance
            detail_level = scored.detail_level
            signals = scored.signals
            compressed_result = scored.content
            
            # Log importance breakdown for transparency
            logger.info(
                f"📊 Importance: {importance:.3f} "
                f"(surprise={signals['surprise']:.2f}, "
                f"relevance={signals['relevance']:.2f}, "
                f"detail={detail_level.value})"
            )
            
            # Cache high-importance results for future use
            self.context_cache.set(
                tool_name=request.tool_name,
                params=request.params,
                content=compressed_result,
                importance=importance
            )
        
        # Track consecutive failures for panic switch
        if is_error:
            self._consecutive_tool_failures += 1
            if self._consecutive_tool_failures >= self._max_consecutive_failures:
                self.state.error_bailout = True
                self.state.error_bailout_reason = f"Too many tool failures ({self._consecutive_tool_failures} consecutive)"
                logger.warning(f"🚨 PANIC SWITCH ACTIVATED: {self.state.error_bailout_reason}")
        else:
            self._consecutive_tool_failures = 0  # Reset on success
        
        execution_time = (datetime.now() - start).total_seconds() * 1000
        
        return ToolCall(
            tool_name=request.tool_name,
            params=request.params,
            result=compressed_result,  # Use compressed result!
            importance=importance,
            execution_time_ms=execution_time,
            cache_hit=False,  # Not a cache hit (cache hits return early)
            detail_level=detail_level.value if not is_error else "dropped",
            signals=signals,  # Include raw signals for transparency
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
        
        # Format results - memories are (text, metadata) tuples
        result = f"Found {len(memories)} relevant memories:\n\n"
        for i, (text, metadata) in enumerate(memories, 1):
            preview = text[:200] + "..." if len(text) > 200 else text
            result += f"{i}. {preview}\n"
        
        return result
    
    def _tool_brain_read_file(self, params: Dict[str, Any]) -> str:
        """Tool: Read file contents from workspace."""
        # Accept flexible param names
        file_path = params.get("file_path") or params.get("path") or ""
        return self.brain_tools.read_file(
            file_path=file_path,
            start_line=params.get("start_line"),
            end_line=params.get("end_line"),
        )
    
    def _tool_brain_list_dir(self, params: Dict[str, Any]) -> str:
        """Tool: List directory contents."""
        # Accept flexible param names (dir_path or path)
        dir_path = params.get("dir_path") or params.get("path") or "."
        return self.brain_tools.list_directory(
            dir_path=dir_path,
            pattern=params.get("pattern", "*"),
        )
    
    def _tool_brain_grep(self, params: Dict[str, Any]) -> str:
        """Tool: Search for pattern in files."""
        return self.brain_tools.grep_search(
            pattern=params.get("pattern", ""),
            file_pattern=params.get("file_pattern", "**/*.py"),
            max_results=params.get("max_results", 20),
        )
    
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
