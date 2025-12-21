/**
 * MCP Tool Handler - Intent classification and tool routing
 * 
 * This handles the two-phase pattern:
 * 1. Detect when user wants to use an MCP tool
 * 2. Call tool, extract metadata, show transparency
 * 3. If query needs reasoning, inject tool results into brain context
 * 4. Stream brain's analysis
 * 
 * Example: "use introspection to find TODOs and suggest an easy one"
 * - Phase 1: Call introspection tool, get file list + TODO content
 * - Phase 2: Inject results into brain prompt for reasoning
 */

import * as vscode from 'vscode';
import { MCPClient, ToolResult, QueryIntent } from '@ada-code/shared';

export class MCPToolHandler {
  private mcpClient?: MCPClient;

  async ensureConnected(): Promise<void> {
    if (!this.mcpClient) {
      console.log('[MCP Tool Handler] Initializing MCP client...');
      this.mcpClient = new MCPClient();
      await this.mcpClient.connect();
    }
  }

  /**
   * Classify user intent - does this need a tool? Does it need reasoning?
   */
  classifyIntent(message: string): QueryIntent {
    const lower = message.toLowerCase();

    // Check for introspection requests
    if (lower.includes('introspect') || 
        (lower.includes('analyze') && lower.includes('your') && 
         (lower.includes('architecture') || lower.includes('yourself')))) {
      
      // Does it need reasoning too?
      const needsReasoning = lower.includes('suggest') || 
                            lower.includes('recommend') ||
                            lower.includes('should') ||
                            lower.includes('todo') ||
                            lower.includes('next') ||
                            lower.includes('easy') ||
                            lower.includes('find');

      return {
        requiresTool: true,
        requiresReasoning: needsReasoning,
        tool: 'ada_introspect',
        params: { focus: 'general' }
      };
    }

    // Pure chat - no tools needed
    return {
      requiresTool: false,
      requiresReasoning: true
    };
  }

  /**
   * Execute MCP tool and return structured result
   */
  async executeTool(intent: QueryIntent): Promise<ToolResult> {
    await this.ensureConnected();

    const workspace = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    
    if (intent.tool === 'ada_introspect') {
      return await this.mcpClient!.callTool('ada_introspect', {
        ...intent.params,
        workspace_root: workspace
      });
    }

    throw new Error(`Unknown tool: ${intent.tool}`);
  }

  /**
   * Build augmented prompt that includes tool results for brain to reason about
   */
  buildAugmentedPrompt(originalMessage: string, toolResult: ToolResult): string {
    return `Based on this introspection of Ada's codebase:

${toolResult.content}

---

User's question: ${originalMessage}`;
  }

  async disconnect(): Promise<void> {
    if (this.mcpClient) {
      await this.mcpClient.disconnect();
      this.mcpClient = undefined;
    }
  }
}
