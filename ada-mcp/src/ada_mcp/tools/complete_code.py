"""Code completion tool for MCP server.

Provides intelligent code completion based on context, using Ada's brain
to generate contextually-aware suggestions.
"""
# @ai-indexable: mcp-tool
# @ai-purpose: Code completion for editors via MCP
# @ai-dependencies: ada_client, httpx

import logging
from typing import Any

from ada_mcp.tools.base import ToolResult

logger = logging.getLogger(__name__)


async def complete_code(
    code_before: str,
    code_after: str,
    language: str = "python",
    max_tokens: int = 150,
    **kwargs: Any
) -> ToolResult:
    """Complete code based on surrounding context.
    
    This tool generates code completion suggestions by analyzing:
    - Code before the cursor (for context)
    - Code after the cursor (for continuation patterns)
    - File language/syntax
    - Common patterns in the language
    
    Args:
        code_before: Code before cursor position
        code_after: Code after cursor position (helps with context)
        language: Programming language (python, javascript, rust, etc.)
        max_tokens: Maximum tokens to generate (default: 150)
        **kwargs: Additional context (filename, project_type, etc.)
        
    Returns:
        ToolResult with suggested completion
        
    Examples:
        Complete a function definition:
        
        code_before = 'def calculate_importance(memory: dict, signals: dict) -> float:\\n    # '
        result = await complete_code(code_before, "", "python")
        # Returns code completing the function body
    """
    from ada_mcp.client import get_ada_client
    
    # Build specialized completion prompt
    prompt = _build_completion_prompt(
        code_before=code_before,
        code_after=code_after,
        language=language,
        **kwargs
    )
    
    try:
        # For code completion, bypass Ada brain and hit Ollama directly
        # This avoids RAG overhead and special token encoding issues with FIM syntax
        import httpx
        
        ollama_url = "http://localhost:11434/api/generate"
        
        async with httpx.AsyncClient(timeout=30.0) as http_client:
            # Stream from Ollama using FIM format
            response = await http_client.post(
                ollama_url,
                json={
                    "model": "qwen2.5-coder:7b",
                    "prompt": prompt,
                    "stream": False,  # Non-streaming for simplicity
                    "options": {
                        "temperature": 0.2,  # Low temperature for focused completions
                        "top_p": 0.95,
                        "num_predict": max_tokens,
                    }
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama returned {response.status_code}: {response.text}")
            
            result = response.json()
            completion_text = result.get("response", "")
        
        # Extract just the code from response
        completion = _extract_code(completion_text, language)
        
        return ToolResult(
            success=True,
            content=completion,
            metadata={
                "language": language,
                "tokens_used": len(completion.split()),
                "has_code_after": bool(code_after)
            }
        )
        
    except Exception as e:
        logger.error(f"Code completion failed: {e}")
        return ToolResult(
            success=False,
            error=f"Completion error: {str(e)}",
            content=""
        )


def _build_completion_prompt(
    code_before: str,
    code_after: str,
    language: str,
    **kwargs: Any
) -> str:
    """Build specialized prompt for code completion using FIM (Fill-In-Middle) format.
    
    Uses the qwen2.5-coder FIM syntax for precise, explanation-free completions:
    <|fim_prefix|>code_before<|fim_suffix|>code_after<|fim_middle|>
    
    This format is specifically designed for code completion models and prevents
    verbose explanations that slow down completion.
    """
    # Use FIM (Fill-In-Middle) format for qwen2.5-coder
    # This is what the model was trained on and produces MUCH faster, terser completions
    if code_after:
        # Fill-in-middle case
        return f"<|fim_prefix|>{code_before}<|fim_suffix|>{code_after}<|fim_middle|>"
    else:
        # Continue from cursor (no suffix)
        return f"<|fim_prefix|>{code_before}<|fim_suffix|><|fim_middle|>"


def _extract_code(response: str, language: str) -> str:
    """Extract just the code from LLM response.
    
    Handles various response formats:
    - Markdown code blocks
    - Plain code
    - Explanations + code
    """
    import re
    
    # Try to find code block
    code_block_pattern = rf"```(?:{language})?\s*\n(.*?)```"
    match = re.search(code_block_pattern, response, re.DOTALL)
    
    if match:
        code = match.group(1).strip()
    else:
        # No code block, treat entire response as code
        code = response.strip()
    
    # Remove common explanation markers
    for marker in ["# Completion:", "// Completion:", "# Here's", "// Here's"]:
        if code.startswith(marker):
            code = code.split('\n', 1)[1] if '\n' in code else ""
    
    # Clean up
    code = code.strip()
    
    # Ensure proper indentation is preserved
    # (Don't strip leading spaces if it's part of the code structure)
    
    return code


# MCP Tool Registration
TOOL_SCHEMA = {
    "name": "complete_code",
    "description": "Generate code completion based on surrounding context",
    "inputSchema": {
        "type": "object",
        "properties": {
            "code_before": {
                "type": "string",
                "description": "Code before cursor position"
            },
            "code_after": {
                "type": "string",
                "description": "Code after cursor position (optional)",
                "default": ""
            },
            "language": {
                "type": "string",
                "description": "Programming language",
                "default": "python"
            },
            "max_tokens": {
                "type": "integer",
                "description": "Maximum tokens to generate",
                "default": 150
            },
            "filename": {
                "type": "string",
                "description": "Current filename (optional)"
            },
            "project_type": {
                "type": "string",
                "description": "Type of project (optional)"
            }
        },
        "required": ["code_before"]
    }
}
