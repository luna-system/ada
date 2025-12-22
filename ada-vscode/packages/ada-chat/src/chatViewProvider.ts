/**
 * ChatViewProvider - Manages webview chat UI with MCP tool routing
 * 
 * Architecture:
 * - Uses MCPToolHandler for intent classification
 * - Two-phase pattern: tool execution → brain reasoning
 * - Tool transparency via structured metadata
 * - Webview loaded from separate HTML/CSS/JS files for easy iteration
 * 
 * December 2025 - luna+ada
 */

import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { MCPToolHandler } from './mcpToolHandler';

export class ChatViewProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = 'ada.chatView';
  private _view?: vscode.WebviewView;
  private _toolHandler: MCPToolHandler;
  private _isGenerating = false;
  private _extensionPath: string;

  constructor(
    private readonly _extensionUri: vscode.Uri,
    private readonly _brainClient: any  // AdaBrainClient from extension.ts
  ) {
    this._toolHandler = new MCPToolHandler();
    this._extensionPath = _extensionUri.fsPath;
  }

  public resolveWebviewView(
    webviewView: vscode.WebviewView,
    context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken,
  ) {
    this._view = webviewView;

    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [this._extensionUri]
    };

    webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

    webviewView.webview.onDidReceiveMessage(async (data) => {
      await this._handleMessage(data);
    });
    
    this._checkConnection();
  }

  private async _checkConnection() {
    const connected = await this._brainClient.checkConnection();
    this._postMessage({
      type: 'connectionStatus',
      connected,
      name: 'Ada Brain',  // TODO: Make configurable for Ollama direct
    });
  }

  private async _handleMessage(message: any) {
    switch (message.type) {
      case 'sendMessage':
        await this._handleUserMessage(message.content);
        break;
      case 'clearChat':
        this._postMessage({ type: 'cleared' });
        break;
      case 'stopGeneration':
        this._isGenerating = false;
        break;
    }
  }

  private async _handleUserMessage(userMessage: string) {
    if (this._isGenerating || !userMessage.trim()) {
      return;
    }

    this._postMessage({ type: 'userMessage', content: userMessage });
    this._isGenerating = true;

    try {
      // Classify intent - does this need MCP tools?
      const intent = this._toolHandler.classifyIntent(userMessage);
      
      if (intent.requiresTool) {
        console.log('[Ada Chat] Tool required:', intent.tool);
        
        // Execute tool
        const toolResult = await this._toolHandler.executeTool(intent);
        
        // ALWAYS show tool transparency (metadata card) FIRST
        this._postMessage({
          type: 'toolTransparency',
          tool: intent.tool || 'unknown',
          metadata: toolResult.metadata
        });
        
        if (intent.requiresReasoning) {
          // Two-phase: inject tool results into brain for reasoning
          const augmentedPrompt = this._toolHandler.buildAugmentedPrompt(
            userMessage,
            toolResult,
            intent.tool || 'unknown'
          );
          
          console.log('[Ada Chat] Sending augmented prompt to Brain for reasoning...');
          console.log('[Ada Chat] Augmented prompt length:', augmentedPrompt.length);
          
          // NOW start generation (after tool card)
          this._postMessage({ type: 'generationStart' });
          
          // Stream brain's analysis
          let chunkCount = 0;
          for await (const chunk of this._brainClient.chat([
            { role: 'user', content: augmentedPrompt }
          ], {})) {
            chunkCount++;
            if (!this._isGenerating) break;
            console.log(`[Ada Chat] Chunk ${chunkCount}:`, chunk.content?.slice(0, 50), 'done:', chunk.done);
            this._postMessage({
              type: 'generationChunk',
              content: chunk.content,
              done: chunk.done
            });
          }
          console.log('[Ada Chat] Stream complete, total chunks:', chunkCount);
        } else {
          // Simple tool output - show directly with formatting
          this._postMessage({ type: 'generationStart' });
          this._postMessage({
            type: 'generationChunk',
            content: toolResult.content,
            done: true
          });
        }
      } else {
        // Regular chat - no pre-identified tools, but watch for bidirectional requests
        console.log('[Ada Chat] Sending generationStart...');
        this._postMessage({ type: 'generationStart' });
        await this._streamWithBidirectional(userMessage);
      }
    } catch (error) {
      console.error('Ada chat error:', error);
      this._postMessage({
        type: 'error',
        message: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
    } finally {
      this._isGenerating = false;
      this._postMessage({ type: 'generationEnd' });
    }
  }

  /**
   * Stream response with bidirectional tool interception
   * 
   * Watches for SPECIALIST_REQUEST[...] or TOOL_REQUEST[...] patterns in Brain's output.
   * When detected, executes the tool locally via VS Code APIs and injects the result.
   */
  private async _streamWithBidirectional(userMessage: string): Promise<void> {
    let accumulated = '';
    let toolCallCount = 0;
    const MAX_TOOL_CALLS = 5; // Safety limit

    // Inject VS Code tool instructions so Brain knows what tools are available
    // TEMPORARY DEBUG: Use simple prompt to test streaming
    const augmentedMessage = `Hello! The user said: ${userMessage}. Please respond naturally.`;
    
    // Start initial stream with tool context
    let currentMessages = [
      { role: 'user', content: augmentedMessage }
    ];
    
    while (this._isGenerating) {
      let foundToolRequest = false;
      
      console.log('[Ada Chat] About to start brain stream iteration...');
      for await (const chunk of this._brainClient.chat(currentMessages, {})) {
        console.log('[Ada Chat] Got chunk from brain:', JSON.stringify(chunk));
        if (!this._isGenerating) break;
        
        // Send chunk to UI immediately for real-time display
        if (chunk.content) {
          console.log('[Ada Chat] Sending generationChunk to webview:', JSON.stringify(chunk.content));
          this._postMessage({
            type: 'generationChunk',
            content: chunk.content,
            done: false
          });
          
          // Also accumulate for pattern detection
          accumulated += chunk.content;
        } else {
          console.log('[Ada Chat] Chunk has no content:', JSON.stringify(chunk));
        }
        
        // Handle completion
        if (chunk.done) {
          this._postMessage({
            type: 'generationChunk',
            content: '',
            done: true
          });
          return; // Stream complete, exit
        }
        
        // Check for bidirectional tool request
        const request = this._toolHandler.detectBidirectionalRequest(accumulated);
        
        if (request.detected && request.tool && toolCallCount < MAX_TOOL_CALLS) {
          foundToolRequest = true;
          toolCallCount++;
          
          console.log(`[Ada Chat] Bidirectional request detected: ${request.tool}`);
          
          // Show tool transparency card
          this._postMessage({
            type: 'toolTransparency',
            tool: request.tool,
            metadata: {
              tool_name: request.tool,
              actions_taken: `Brain requested: ${request.tool}`,
              bidirectional: true
            }
          });
          
          // Execute the tool
          const toolExecution = await this._toolHandler.executeBidirectionalTool(
            request.tool,
            request.params || {}
          );
          
          // Build continuation prompt with tool result
          const continuation = `${userMessage}

${toolExecution.resultText}

Continue your response, incorporating the tool result above.`;
          
          // Reset for next iteration
          accumulated = '';
          currentMessages = [{ role: 'user', content: continuation }];
          
          break; // Break inner loop to restart stream with tool context
        }
        
        // Normal chunk - forward to UI
        this._postMessage({
          type: 'generationChunk',
          content: chunk.content,
          done: chunk.done
        });
        
        if (chunk.done) {
          return; // Stream complete, exit
        }
      }
      
      // If we didn't find a tool request, we're done
      if (!foundToolRequest) {
        break;
      }
      
      // Safety check
      if (toolCallCount >= MAX_TOOL_CALLS) {
        console.warn('[Ada Chat] Max bidirectional tool calls reached');
        this._postMessage({
          type: 'generationChunk',
          content: '\n\n*[Tool call limit reached]*',
          done: true
        });
        break;
      }
    }
  }

  private _getHtmlForWebview(webview: vscode.Webview) {
    // Generate nonce for CSP
    const nonce = this._getNonce();
    
    // Get URIs for webview resources
    const webviewPath = path.join(this._extensionPath, 'resources', 'webview');
    
    console.log('[Ada Chat] Extension path:', this._extensionPath);
    console.log('[Ada Chat] Webview path:', webviewPath);
    
    // Check if files exist
    const htmlPath = path.join(webviewPath, 'chat.html');
    const cssPath = path.join(webviewPath, 'chat.css');
    const jsPath = path.join(webviewPath, 'chat.js');
    
    console.log('[Ada Chat] HTML exists:', fs.existsSync(htmlPath));
    console.log('[Ada Chat] CSS exists:', fs.existsSync(cssPath));
    console.log('[Ada Chat] JS exists:', fs.existsSync(jsPath));
    
    if (!fs.existsSync(htmlPath)) {
      // Fallback: return inline HTML if files not found
      console.error('[Ada Chat] Webview files not found at:', webviewPath);
      return this._getFallbackHtml();
    }
    
    const cssUri = webview.asWebviewUri(
      vscode.Uri.file(cssPath)
    );
    const jsUri = webview.asWebviewUri(
      vscode.Uri.file(jsPath)
    );
    
    // Load HTML template
    let html = fs.readFileSync(htmlPath, 'utf8');
    
    // Replace template variables
    html = html
      .replace(/\{\{cspSource\}\}/g, webview.cspSource)
      .replace(/\{\{nonce\}\}/g, nonce)
      .replace(/\{\{cssUri\}\}/g, cssUri.toString())
      .replace(/\{\{jsUri\}\}/g, jsUri.toString());
    
    return html;
  }

  /**
   * Generate tool instructions for Brain so it knows about VS Code tools
   */
  private _getToolInstructions(): string {
    return `You have access to VS Code tools via the extension. When you need to read files, search code, or analyze the workspace, request tools using this syntax:

TOOL_REQUEST[tool_name:{"param":"value"}]

Available tools:

- ada_introspect: Analyze workspace structure, find TODOs/FIXMEs, understand project
  When to use: Understanding the codebase, finding tasks, getting project overview
  Example: TOOL_REQUEST[ada_introspect:{"query":"TODOs in the project"}]
  Returns: Project structure, package.json info, TODO/FIXME items with file locations

- ada_read_file: Read file contents with optional line range
  When to use: Reading specific files to understand code, reviewing implementations
  Example: TOOL_REQUEST[ada_read_file:{"path":"src/index.ts"}]
  Example: TOOL_REQUEST[ada_read_file:{"path":"src/app.py","startLine":10,"endLine":50}]
  Returns: File contents (or portion if line range specified)

- ada_search: Search for text patterns in the codebase
  When to use: Finding where something is defined, used, or referenced
  Example: TOOL_REQUEST[ada_search:{"query":"handleMessage","includePattern":"**/*.ts"}]
  Returns: Matching lines with file paths and line numbers

- ada_list_files: List files in a directory with optional glob pattern
  When to use: Exploring folder structure, finding files of a certain type
  Example: TOOL_REQUEST[ada_list_files:{"path":"src","pattern":"**/*.ts"}]
  Returns: List of matching files

- ada_symbols: Find code symbols (functions, classes, etc.)
  When to use: Finding function definitions, class declarations, navigating code
  Example: TOOL_REQUEST[ada_symbols:{"query":"ChatViewProvider"}]
  Returns: Symbol definitions with locations

- ada_git_status: Get current git repository status
  When to use: Understanding what's changed, what's staged, current branch
  Example: TOOL_REQUEST[ada_git_status:{}]
  Returns: Branch, staged changes, unstaged changes, untracked files

Guidelines:
- Use tools proactively when the user's question would benefit from real file/code data
- After receiving tool results, incorporate them naturally into your response
- You can chain multiple tool calls if needed (one at a time)
- For "find a TODO" or "show me something to work on" questions, use ada_introspect first`;
  }
  
  private _getFallbackHtml(): string {
    return `<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Ada Chat</title>
<style>body{font-family:system-ui;padding:20px;color:#ccc;background:#1e1e1e;}
.error{color:#f44;}</style></head>
<body>
<h3>⚠️ Ada Chat - File Loading Error</h3>
<p class="error">Could not load webview files from resources/webview/</p>
<p>Extension path: ${this._extensionPath}</p>
<p>Please check that chat.html, chat.css, and chat.js exist.</p>
</body></html>`;
  }

  private _getNonce(): string {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
      text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
  }

  private _postMessage(message: any) {
    if (!this._view) {
      console.error('[Ada Chat] Cannot post message - webview not available!', message.type);
      return;
    }
    console.log('[Ada Chat] Posting message to webview:', message.type);
    this._view.webview.postMessage(message);
  }
  
  public dispose() {
    this._toolHandler.disconnect();
  }
}

