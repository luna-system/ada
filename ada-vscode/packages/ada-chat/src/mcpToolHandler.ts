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

    // Introspection: analyze Ada's own architecture
    if (lower.includes('introspect') || 
        (lower.includes('analyze') && lower.includes('your') && 
         (lower.includes('architecture') || lower.includes('yourself')))) {
      
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

    // Memory search: recall previous information
    if (lower.includes('remember') && lower.includes('when') ||
        lower.includes('what did we') ||
        lower.includes('recall') ||
        lower.includes('search memory') ||
        lower.includes('find in memory')) {
      
      return {
        requiresTool: true,
        requiresReasoning: true,
        tool: 'ada_search_memory',
        params: { query: message }
      };
    }

    // Memory add: store new information
    if (lower.startsWith('remember this') ||
        lower.startsWith('save this') ||
        lower.startsWith('store this') ||
        lower.includes('add to memory')) {
      
      // Extract what to remember (after the command)
      const content = message.replace(/^(remember|save|store) this:?\s*/i, '');
      
      return {
        requiresTool: true,
        requiresReasoning: false,
        tool: 'ada_add_memory',
        params: { content }
      };
    }

    // File read: access file contents
    if (lower.startsWith('read file') ||
        lower.startsWith('show me') && lower.includes('file') ||
        lower.startsWith('cat ') ||
        lower.startsWith('open ')) {
      
      // Extract file path
      const fileMatch = message.match(/(?:read|show|cat|open)\s+(?:file\s+)?(.+)/i);
      const filePath = fileMatch ? fileMatch[1].trim() : '';
      
      return {
        requiresTool: true,
        requiresReasoning: false,
        tool: 'ada_read_file',
        params: { file_path: filePath }
      };
    }

    // Code completion: fill in the middle
    if (lower.includes('complete this') ||
        lower.includes('fill in') && lower.includes('code') ||
        lower.includes('finish this function')) {
      
      return {
        requiresTool: true,
        requiresReasoning: false,
        tool: 'ada_complete_code',
        params: { prefix: message }  // Will be refined
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
    
    switch (intent.tool) {
      case 'ada_introspect':
        return await this.mcpClient!.callTool('ada_introspect', {
          ...intent.params,
          workspace_root: workspace
        });
      
      case 'ada_search_memory':
        return await this.mcpClient!.callTool('ada_search_memory', intent.params);
      
      case 'ada_add_memory':
        return await this.mcpClient!.callTool('ada_add_memory', intent.params);
      
      case 'ada_read_file':
        return await this.mcpClient!.callTool('ada_read_file', {
          ...intent.params,
          workspace_root: workspace
        });
      
      case 'ada_complete_code':
        return await this.mcpClient!.callTool('ada_complete_code', intent.params);
      
      default:
        throw new Error(`Unknown tool: ${intent.tool}`);
    }
  }

  /**
   * Build augmented prompt that includes tool results for brain to reason about
   */
  buildAugmentedPrompt(originalMessage: string, toolResult: ToolResult, toolName: string): string {
    switch (toolName) {
      case 'ada_introspect':
        return `Based on this introspection of Ada's codebase:

${toolResult.content}

---

User's question: ${originalMessage}`;

      case 'ada_search_memory':
        return `Here are relevant memories from past conversations:

${toolResult.content}

---

User's question: ${originalMessage}`;

      case 'ada_read_file':
        return `File contents:

${toolResult.content}

---

User's question: ${originalMessage}`;

      default:
        return `Tool result:

${toolResult.content}

---

User's question: ${originalMessage}`;
    }
  }

  async disconnect(): Promise<void> {
    if (this.mcpClient) {
      await this.mcpClient.disconnect();
      this.mcpClient = undefined;
    }
  }
}
