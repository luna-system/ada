import logging
import os
from typing import Dict, Any, List
from brain.tools.protocol import BaseTool, ToolCapability, ToolResult

logger = logging.getLogger(__name__)

class DocsTool(BaseTool):
    def __init__(self):
        super().__init__(
            capability=ToolCapability(
                name="docs_lookup",
                description="Look up information from Ada's local documentation and research files",
                version="4.0.0",
                input_schema={
                    "query": "The search terms to find in documentation"
                }
            )
        )
        # Search path: Project root
        self.doc_path = "/home/luna/Code/ada"

    async def process(self, request_context: Dict[str, Any]) -> ToolResult:
        query = request_context.get("query", "")
        if not query:
            return ToolResult(
                success=False, 
                tool_name="docs_lookup",
                context_text="Error: Empty query",
                error="No query provided"
            )

        logger.info(f"📚 DocsTool: Searching for '{query}' in {self.doc_path}")
        
        # Simple implementation: grep for the query in markdown files
        import subprocess
        try:
            # Use ripgrep if available, else standard grep
            cmd = [
                "rg", "-i", "-t", "md", "--max-count", "3", "--context", "2", 
                query, self.doc_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout:
                output = f"Found relevant documentation for '{query}':\n\n{result.stdout}"
                return ToolResult(
                    success=True, 
                    tool_name="docs_lookup",
                    context_text=output,
                    data={"results": result.stdout}
                )
            else:
                return ToolResult(
                    success=False, 
                    tool_name="docs_lookup",
                    context_text=f"No documentation found for '{query}'",
                    error="No results"
                )
                
        except Exception as e:
            logger.error(f"DocsTool error: {e}")
            return ToolResult(
                success=False, 
                tool_name="docs_lookup",
                context_text=f"Error executing search: {e}",
                error=str(e)
            )

