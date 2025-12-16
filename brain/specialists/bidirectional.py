"""
Bidirectional Specialist Handler

Enables LLM → Specialist communication during inference.
LLM can request specialist execution mid-stream by emitting special syntax.
"""
import re
import json
import logging
from typing import Optional, Dict, Any, AsyncIterator

from brain.specialists import get_specialist, execute_specialists

logger = logging.getLogger(__name__)

# Specialist request syntax patterns
# Format: SPECIALIST_REQUEST[name:{"param":"value"}]
SPECIALIST_REQUEST_PATTERN = re.compile(
    r'SPECIALIST_REQUEST\[(\w+):(.*?)\]',
    re.DOTALL
)

# Alternative simpler syntax: @specialist_name(param=value)
SPECIALIST_MENTION_PATTERN = re.compile(
    r'@(\w+)_specialist\((.*?)\)',
    re.DOTALL
)


class BidirectionalSpecialistHandler:
    """
    Handles LLM-initiated specialist requests during streaming.
    
    Monitors streaming output, detects specialist request syntax,
    executes specialists, and injects results back into the stream.
    """
    
    def __init__(self, max_calls: int = 5):
        """
        Args:
            max_calls: Maximum specialist calls per request (prevents loops)
        """
        self.max_calls = max_calls
        self.call_count = 0
    
    def detect_request(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Detect if text contains a specialist request.
        
        Returns:
            Dict with 'specialist', 'params', 'match_obj' if found, else None
        """
        # Try primary syntax
        match = SPECIALIST_REQUEST_PATTERN.search(text)
        if match:
            specialist_name = match.group(1)
            params_json = match.group(2).strip()
            
            try:
                params = json.loads(params_json) if params_json else {}
                return {
                    'specialist': specialist_name,
                    'params': params,
                    'match': match,
                    'syntax': 'request'
                }
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON in specialist request: {params_json} - {e}")
                return None
        
        # Try mention syntax
        match = SPECIALIST_MENTION_PATTERN.search(text)
        if match:
            specialist_name = match.group(1)
            params_str = match.group(2).strip()
            
            # Simple param parsing: key=value pairs
            params = self._parse_simple_params(params_str)
            return {
                'specialist': specialist_name,
                'params': params,
                'match': match,
                'syntax': 'mention'
            }
        
        return None
    
    def _parse_simple_params(self, params_str: str) -> Dict[str, Any]:
        """Parse simple key=value param string"""
        params = {}
        if not params_str:
            return params
        
        # Basic parsing: key=value, key="value"
        for pair in params_str.split(','):
            if '=' in pair:
                key, value = pair.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                params[key] = value
        
        return params
    
    async def execute_request(
        self,
        specialist_name: str,
        params: Dict[str, Any],
        base_context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Execute a specialist request.
        
        Args:
            specialist_name: Name of specialist to invoke
            params: Parameters from LLM request
            base_context: Base request context to merge with params
            
        Returns:
            Formatted result text to inject back into stream, or None on error
        """
        if self.call_count >= self.max_calls:
            logger.warning(f"Max specialist calls ({self.max_calls}) reached, ignoring request")
            return None
        
        self.call_count += 1
        
        try:
            # Get specialist
            specialist = get_specialist(specialist_name)
            if not specialist:
                error_msg = f"Specialist '{specialist_name}' not found"
                logger.warning(error_msg)
                return f"\n[SPECIALIST_ERROR: {error_msg}]\n"
            
            # Merge params with base context
            execution_context = {**base_context, **params}
            
            # Check if specialist should activate
            if not specialist.should_activate(execution_context):
                logger.debug(f"Specialist {specialist_name} declined activation")
                return None
            
            # Execute
            logger.info(f"Executing bidirectional specialist: {specialist_name}")
            result = await specialist.process(**execution_context)
            
            if result.success:
                # Format result for injection
                formatted = self._format_result(specialist_name, result)
                return formatted
            else:
                error_msg = result.error or "Unknown error"
                logger.error(f"Specialist {specialist_name} failed: {error_msg}")
                return f"\n[SPECIALIST_ERROR: {specialist_name} failed - {error_msg}]\n"
        
        except Exception as e:
            logger.error(f"Exception executing specialist {specialist_name}: {e}", exc_info=True)
            return f"\n[SPECIALIST_ERROR: {specialist_name} exception - {str(e)}]\n"
    
    def _format_result(self, specialist_name: str, result) -> str:
        """
        Format specialist result for injection into LLM context.
        
        Returns:
            Formatted string that LLM will see as specialist output
        """
        lines = [
            f"\n[SPECIALIST_RESULT: {specialist_name}]",
            result.context_text,
            "[/SPECIALIST_RESULT]",
            ""  # Blank line for readability
        ]
        return "\n".join(lines)


async def stream_with_specialists(
    base_stream: AsyncIterator[Dict[str, Any]],
    request_context: Dict[str, Any],
    max_specialist_calls: int = 5
) -> AsyncIterator[Dict[str, Any]]:
    """
    Wrap a streaming response to handle bidirectional specialist calls.
    
    Args:
        base_stream: Original token stream from LLM
        request_context: Base context for specialist execution
        max_specialist_calls: Safety limit on specialist invocations
        
    Yields:
        Token chunks, with specialist results injected when requested
    """
    handler = BidirectionalSpecialistHandler(max_calls=max_specialist_calls)
    accumulated = ""
    
    async for chunk in base_stream:
        # Forward token
        yield chunk
        
        # Accumulate for pattern detection
        if 'token' in chunk:
            accumulated += chunk['token']
            
            # Check for specialist request
            request = handler.detect_request(accumulated)
            if request:
                specialist_name = request['specialist']
                params = request['params']
                
                logger.info(f"Detected specialist request: {specialist_name} with params {params}")
                
                # Execute specialist
                result_text = await handler.execute_request(
                    specialist_name,
                    params,
                    request_context
                )
                
                if result_text:
                    # Inject result as tokens
                    yield {
                        'type': 'token',
                        'content': result_text
                    }
                    accumulated += result_text
                
                # Note: We don't restart the stream - just inject and continue
                # For more sophisticated "pause and resume" you'd need to:
                # 1. Stop current stream
                # 2. Build new prompt with specialist result
                # 3. Resume generation
                # That's Phase 2!
