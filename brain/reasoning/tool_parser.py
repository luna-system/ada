"""Parse tool requests from LLM output.

LLMs can request tools mid-generation using either pattern:
    TOOL_REQUEST[tool_name:{"param": "value"}]    (standard)
    ⚡tool_name:{"param": "value"}                  (dense notation)

This module parses these requests and validates them against
available tools.
"""

import re
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class ToolRequest:
    """A parsed tool request from LLM output.
    
    Example LLM output (standard):
        "I need to search the codebase. TOOL_REQUEST[ada_search:{"query":"authentication"}]"
    
    Example LLM output (dense notation):
        "?auth → ⚡brain_search:{\"query\":\"authentication\"}"
    
    Parsed result:
        ToolRequest(
            tool_name="ada_search",
            params={"query": "authentication"},
            raw_text="TOOL_REQUEST[ada_search:{\"query\":\"authentication\"}]"
        )
    """
    tool_name: str
    params: Dict[str, Any]
    raw_text: str


class ToolRequestParser:
    """Parse tool requests from LLM output.
    
    Supports TWO formats:
    1. Standard: TOOL_REQUEST[tool_name:{"param":"value"}]
    2. Dense:    ⚡tool_name:{"param":"value"}
    
    Supports:
    - Single tool requests
    - Multiple tool requests in one output
    - JSON parameter parsing
    - Validation against available tools
    
    Example:
        parser = ToolRequestParser(available_tools=["brain_search", "brain_read_file"])
        
        # Standard format
        llm_output = "I need to search. TOOL_REQUEST[brain_search:{\"query\":\"auth\"}]"
        requests = parser.parse(llm_output)
        
        # Dense format (same result!)
        llm_output = "?auth → ⚡brain_search:{\"query\":\"auth\"}"
        requests = parser.parse(llm_output)
    """
    
    # Pattern 1: TOOL_REQUEST[tool_name:{"param":"value"}]
    STANDARD_PATTERN = r'TOOL_REQUEST\[([a-z_]+):(.*?)\]'
    
    # Pattern 2: ⚡tool_name:{"param":"value"} (dense notation)
    DENSE_PATTERN = r'⚡([a-z_]+):\{([^}]+)\}'
    
    def __init__(self, available_tools: Optional[List[str]] = None):
        """Initialize parser.
        
        Args:
            available_tools: List of valid tool names. If None, all tools are accepted.
        """
        self.available_tools = set(available_tools) if available_tools else None
    
    def parse(self, text: str) -> List[ToolRequest]:
        """Parse all tool requests from text.
        
        Supports both standard TOOL_REQUEST[...] and dense ⚡tool:... formats.
        
        Args:
            text: LLM output that may contain tool request patterns
            
        Returns:
            List of parsed tool requests (may be empty)
        """
        requests = []
        
        # Find standard format matches
        matches = re.finditer(self.STANDARD_PATTERN, text, re.DOTALL)
        
        for match in matches:
            tool_name = match.group(1)
            params_str = match.group(2)
            raw_text = match.group(0)
            
            # Validate tool name
            if self.available_tools and tool_name not in self.available_tools:
                logger.warning(f"Unknown tool requested: {tool_name}")
                continue
            
            # Parse parameters (JSON)
            try:
                params = json.loads(params_str)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse tool params: {params_str} - {e}")
                continue
            
            # Create request
            request = ToolRequest(
                tool_name=tool_name,
                params=params,
                raw_text=raw_text
            )
            requests.append(request)
            
            logger.info(f"Parsed tool request: {tool_name} with params {params}")
        
        return requests
    
    def has_tool_requests(self, text: str) -> bool:
        """Check if text contains any tool requests.
        
        Fast check without full parsing.
        """
        return 'TOOL_REQUEST[' in text
    
    def remove_tool_requests(self, text: str) -> str:
        """Remove all TOOL_REQUEST[...] patterns from text.
        
        Useful for cleaning LLM output after extracting requests.
        """
        return re.sub(self.PATTERN, '', text, flags=re.DOTALL).strip()
