"""Parse tool requests from LLM output.

LLMs can request tools mid-generation using the pattern:
    TOOL_REQUEST[tool_name:{"param": "value"}]

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
    
    Example LLM output:
        "I need to search the codebase. TOOL_REQUEST[ada_search:{"query":"authentication"}]"
    
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
    """Parse TOOL_REQUEST[...] patterns from LLM output.
    
    Supports:
    - Single tool requests
    - Multiple tool requests in one output
    - JSON parameter parsing
    - Validation against available tools
    
    Example:
        parser = ToolRequestParser(available_tools=["ada_search", "ada_read_file"])
        
        llm_output = "I need to search. TOOL_REQUEST[ada_search:{\"query\":\"auth\"}]"
        requests = parser.parse(llm_output)
        # [ToolRequest(tool_name="ada_search", params={"query": "auth"})]
    """
    
    # Pattern: TOOL_REQUEST[tool_name:{"param":"value"}]
    PATTERN = r'TOOL_REQUEST\[([a-z_]+):(.*?)\]'
    
    def __init__(self, available_tools: Optional[List[str]] = None):
        """Initialize parser.
        
        Args:
            available_tools: List of valid tool names. If None, all tools are accepted.
        """
        self.available_tools = set(available_tools) if available_tools else None
    
    def parse(self, text: str) -> List[ToolRequest]:
        """Parse all tool requests from text.
        
        Args:
            text: LLM output that may contain TOOL_REQUEST[...] patterns
            
        Returns:
            List of parsed tool requests (may be empty)
        """
        requests = []
        
        # Find all matches
        matches = re.finditer(self.PATTERN, text, re.DOTALL)
        
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
