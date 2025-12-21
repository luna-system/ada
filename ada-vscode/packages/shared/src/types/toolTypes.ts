/**
 * Tool Result Types - Structured metadata for MCP tool transparency
 * 
 * Every MCP tool returns:
 * - content: The actual answer/data
 * - metadata: HOW it was produced (files, actions, timing)
 * 
 * This enables:
 * - Transparency: UI shows "🔧 Files: context.md, codebase-map.json"
 * - Routing: Extension can see what tool accessed, decide how to use it
 * - Performance: Timing data for optimization
 */

export interface ToolMetadata {
  tool_name: string;
  files_accessed: string[];
  actions_taken: string[];
  duration_ms?: number;
}

export interface ToolResult {
  content: string;
  metadata: ToolMetadata;
  success: boolean;
  error?: string;
}

/**
 * Intent classification for compound queries
 */
export interface QueryIntent {
  requiresTool: boolean;
  requiresReasoning: boolean;
  tool?: string;
  params?: any;
}
