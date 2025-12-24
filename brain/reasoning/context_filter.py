"""Environment-aware tool filtering for contextual malleability.

This module implements context-aware tool selection following the
biomimetic principles discovered in v2.2 research. Just as memory
importance is contextually malleable, tool availability should 
adapt to the environment (web, IDE, terminal, etc.).

@ai-indexable: reasoning-tools
@ai-purpose: Context-aware tool filtering for appropriate tool selection
"""
from typing import List, Dict, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Environment(Enum):
    """Environment contexts for tool selection."""
    WEB = "web"          # Browser/web interface 
    IDE = "ide"          # VS Code or other IDE
    TERMINAL = "terminal" # Command line interface
    API = "api"          # Direct API access
    MOBILE = "mobile"    # Mobile app interface


class ContextAwareToolFilter:
    """Filter tools based on environment context."""
    
    # Tool availability by environment
    TOOL_AVAILABILITY = {
        Environment.WEB: {
            # Web environment - no direct file access, focus on analysis
            "brain_introspect": True,        # Can analyze knowledge/memory  
            "brain_search": True,            # Can search RAG memories
            "brain_read_file": False,        # No direct file access in browser
            "brain_list_dir": False,         # No filesystem browsing  
            "brain_grep": False,             # No filesystem search
            # Could add: web_search, knowledge_lookup, etc.
        },
        Environment.IDE: {
            # IDE environment - full access
            "brain_introspect": True,
            "brain_search": True,
            "brain_read_file": True, 
            "brain_list_dir": True,
            "brain_grep": True,
            # Full toolset available
        },
        Environment.TERMINAL: {
            # Terminal environment - full access
            "brain_introspect": True,
            "brain_search": True,
            "brain_read_file": True,
            "brain_list_dir": True, 
            "brain_grep": True,
        },
        Environment.API: {
            # API environment - depends on caller context
            "brain_introspect": True,
            "brain_search": True,
            "brain_read_file": True,  # API has workspace access
            "brain_list_dir": True,
            "brain_grep": True,
        },
        Environment.MOBILE: {
            # Mobile environment - limited file access
            "brain_introspect": True,
            "brain_search": True,
            "brain_read_file": False,
            "brain_list_dir": False,
            "brain_grep": False,
        }
    }
    
    @classmethod
    def filter_tools(cls, available_tools: List[str], environment: Environment) -> List[str]:
        """Filter tools based on environment context.
        
        Args:
            available_tools: List of all possible tool names
            environment: Current environment context
            
        Returns:
            Filtered list of tools appropriate for environment
            
        Example:
            >>> tools = ["read_file", "introspect", "list_directory"]
            >>> ContextAwareToolFilter.filter_tools(tools, Environment.WEB)
            ["introspect"]
        """
        if environment not in cls.TOOL_AVAILABILITY:
            logger.warning(f"Unknown environment {environment}, allowing all tools")
            return available_tools
            
        env_rules = cls.TOOL_AVAILABILITY[environment]
        filtered_tools = []
        
        for tool in available_tools:
            # Allow tool if explicitly permitted or not in rules (default allow)
            if env_rules.get(tool, True):
                filtered_tools.append(tool)
            else:
                logger.debug(f"Filtering out {tool} for environment {environment.value}")
                
        logger.info(f"Filtered {len(available_tools)} → {len(filtered_tools)} tools for {environment.value}")
        return filtered_tools
    
    @classmethod 
    def get_environment_from_context(cls, context: Dict[str, Any]) -> Environment:
        """Detect environment from request context.
        
        Args:
            context: Request context dictionary
            
        Returns:
            Detected environment enum
        """
        # Check for explicit environment hint
        if "environment" in context:
            env_str = context["environment"].lower()
            for env in Environment:
                if env.value == env_str:
                    return env
        
        # Check for web interface indicators  
        if context.get("source") == "web":
            return Environment.WEB
        if "user_agent" in context:
            return Environment.WEB
        if "browser" in str(context).lower():
            return Environment.WEB
            
        # Check for IDE indicators
        if context.get("source") == "vscode":
            return Environment.IDE
        if "workspace" in context and "editor" in str(context).lower():
            return Environment.IDE
            
        # Check for terminal indicators
        if context.get("source") == "cli":
            return Environment.TERMINAL
        if context.get("source") == "terminal":
            return Environment.TERMINAL
            
        # Default to API for direct calls
        return Environment.API
    
    @classmethod
    def explain_filtering(cls, original_tools: List[str], filtered_tools: List[str], 
                         environment: Environment) -> str:
        """Explain why tools were filtered for transparency.
        
        Args:
            original_tools: Original tool list
            filtered_tools: Filtered tool list  
            environment: Environment used for filtering
            
        Returns:
            Human-readable explanation
        """
        if len(original_tools) == len(filtered_tools):
            return f"All {len(original_tools)} tools available in {environment.value} environment"
        
        removed = set(original_tools) - set(filtered_tools)
        explanations = {
            Environment.WEB: "Web environment: File system tools unavailable for security",
            Environment.MOBILE: "Mobile environment: Limited tool set for performance",
            Environment.IDE: "IDE environment: Full toolset available",
            Environment.TERMINAL: "Terminal environment: Full toolset available",
            Environment.API: "API environment: Full toolset available"
        }
        
        base_msg = explanations.get(environment, f"{environment.value} environment")
        if removed:
            removed_list = ", ".join(sorted(removed))
            return f"{base_msg}. Filtered out: {removed_list}"
        else:
            return base_msg