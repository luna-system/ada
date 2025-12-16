"""
Advanced Bidirectional Specialist Handler - Phase 2

Implements pause/resume generation with context enrichment.
When LLM requests a specialist, we:
1. Pause current generation
2. Execute specialist
3. Build enriched prompt with result
4. Resume generation with full context
"""
import logging
from typing import Optional, Dict, Any, List, AsyncIterator
from dataclasses import dataclass

from brain.specialists import get_specialist
from brain.specialists.bidirectional import BidirectionalSpecialistHandler

logger = logging.getLogger(__name__)


@dataclass
class GenerationState:
    """Tracks state of a paused/resumed generation"""
    original_prompt: str
    accumulated_text: str
    accumulated_thinking: str
    specialist_results: List[Dict[str, Any]]
    turn_count: int = 0
    max_turns: int = 5


class PauseResumeHandler:
    """
    Handles sophisticated pause/resume with context enrichment.
    
    When specialist request detected:
    1. Pause stream
    2. Execute specialist
    3. Build new prompt with: original_prompt + partial_response + specialist_result
    4. Resume generation with enriched context
    """
    
    def __init__(
        self,
        prompt_builder_func,
        stream_func,
        max_turns: int = 5
    ):
        """
        Args:
            prompt_builder_func: Async function to build prompts
            stream_func: Async function to stream from LLM
            max_turns: Maximum specialist turns (prevents infinite loops)
        """
        self.prompt_builder = prompt_builder_func
        self.stream_func = stream_func
        self.max_turns = max_turns
        self.handler = BidirectionalSpecialistHandler(max_calls=max_turns)
    
    async def generate_with_specialists(
        self,
        initial_prompt: str,
        request_context: Dict[str, Any],
        **stream_kwargs
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Generate with specialist support using pause/resume.
        
        Args:
            initial_prompt: Initial prompt text (already built)
            request_context: Context for specialist execution
            **stream_kwargs: Additional args for stream_func
            
        Yields:
            Token chunks with specialist results properly integrated
        """
        state = GenerationState(
            original_prompt=initial_prompt,
            accumulated_text="",
            accumulated_thinking="",
            specialist_results=[]
        )
        
        current_prompt = initial_prompt
        
        # Main generation loop - can pause and resume multiple times
        for turn in range(self.max_turns):
            state.turn_count = turn
            logger.info(f"Generation turn {turn + 1}/{self.max_turns}")
            
            # Track text in this turn for specialist detection
            turn_text = ""
            specialist_requested = False
            
            # Stream from LLM
            async for chunk in self.stream_func(current_prompt, **stream_kwargs):
                # Check for errors
                if 'error' in chunk:
                    yield chunk
                    return
                
                # Accumulate tokens
                if 'token' in chunk:
                    token = chunk['token']
                    turn_text += token
                    state.accumulated_text += token
                    yield chunk
                
                if 'thinking' in chunk:
                    thinking_token = chunk['thinking']
                    state.accumulated_thinking += thinking_token
                    yield chunk
                
                # Check for specialist request in accumulated turn text
                specialist_request = self.handler.detect_request(turn_text)
                if specialist_request:
                    logger.info(f"Specialist request detected in turn {turn}: {specialist_request['specialist']}")
                    specialist_requested = True
                    
                    # PAUSE generation (exit stream loop)
                    break
                
                # Check if generation naturally completed
                if 'done' in chunk and chunk['done']:
                    logger.info("Generation completed naturally")
                    yield chunk
                    return
            
            # If no specialist requested, generation is done
            if not specialist_requested:
                logger.info("No specialist request, generation complete")
                # Send done chunk if not already sent
                yield {'type': 'done', 'done': True}
                return
            
            # === PAUSE POINT: Execute specialist and enrich context ===
            
            specialist_name = specialist_request['specialist']
            params = specialist_request['params']
            
            # Execute specialist
            logger.info(f"Executing specialist: {specialist_name}")
            result_text = await self.handler.execute_request(
                specialist_name,
                params,
                request_context
            )
            
            if result_text:
                # Store result
                state.specialist_results.append({
                    'specialist': specialist_name,
                    'params': params,
                    'result': result_text,
                    'turn': turn
                })
                
                # Send specialist result to frontend
                yield {
                    'type': 'specialist_result',
                    'specialist': specialist_name,
                    'content': result_text
                }
                
                # Build enriched prompt for resumption
                current_prompt = self._build_resume_prompt(
                    state,
                    result_text,
                    request_context
                )
                
                logger.info(f"Resuming generation with enriched context (turn {turn + 1})")
                
                # Continue to next turn with enriched prompt
                continue
            else:
                # Specialist failed, continue without enrichment
                logger.warning(f"Specialist {specialist_name} failed, continuing without result")
                continue
        
        # Max turns reached
        logger.warning(f"Max turns ({self.max_turns}) reached, stopping generation")
        yield {
            'type': 'warning',
            'message': f"Maximum specialist turns ({self.max_turns}) reached"
        }
        yield {'type': 'done', 'done': True}
    
    def _build_resume_prompt(
        self,
        state: GenerationState,
        specialist_result: str,
        request_context: Dict[str, Any]
    ) -> str:
        """
        Build an enriched prompt for resuming generation.
        
        Strategy: Append to original prompt showing conversation progression
        with specialist result injected at the right point.
        
        Args:
            state: Current generation state
            specialist_result: Result from specialist
            request_context: Original request context
            
        Returns:
            Enriched prompt string
        """
        # Build the conversation progression
        continuation = f"""

[Conversation so far in this turn]
User: {request_context.get('prompt', '')}

Assistant (thinking): {state.accumulated_thinking if state.accumulated_thinking else ''}

Assistant (partial response): {state.accumulated_text}

{specialist_result}

[Now continue your response naturally, incorporating the information above]
Assistant:"""
        
        return state.original_prompt + continuation
    
    async def _rebuild_full_context(
        self,
        state: GenerationState,
        specialist_result: str,
        request_context: Dict[str, Any]
    ) -> str:
        """
        FUTURE: Rebuild full prompt with all context using prompt_builder.
        
        This is more sophisticated - reconstructs the entire prompt
        with persona, memories, FAQs, etc. PLUS the specialist result.
        
        Currently unused - using simpler _build_resume_prompt instead.
        This method is reserved for Phase 3 when we implement full context rebuilding.
        """
        pass


def create_pause_resume_stream(
    prompt_builder_func,
    stream_func,
    max_turns: int = 5
) -> PauseResumeHandler:
    """
    Factory function to create a pause/resume handler.
    
    Args:
        prompt_builder_func: Async function(prompt, context) -> (full_prompt, used_context)
        stream_func: Async function(prompt, **kwargs) -> AsyncIterator[chunk]
        max_turns: Max specialist turns
        
    Returns:
        Configured PauseResumeHandler
    """
    return PauseResumeHandler(
        prompt_builder_func=prompt_builder_func,
        stream_func=stream_func,
        max_turns=max_turns
    )
