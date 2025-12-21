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
          
          // NOW start generation (after tool card)
          this._postMessage({ type: 'generationStart' });
          
          // Stream brain's analysis
          for await (const chunk of this._brainClient.chat([
            { role: 'user', content: augmentedPrompt }
          ], {})) {
            if (!this._isGenerating) break;
            this._postMessage({
              type: 'generationChunk',
              content: chunk.content,
              done: chunk.done
            });
          }
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
        // Regular chat - no tools
        this._postMessage({ type: 'generationStart' });
        for await (const chunk of this._brainClient.chat([
          { role: 'user', content: userMessage }
        ], {})) {
          if (!this._isGenerating) break;
          this._postMessage({
            type: 'generationChunk',
            content: chunk.content,
            done: chunk.done
          });
        }
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
    this._view?.webview.postMessage(message);
  }
  
  public dispose() {
    this._toolHandler.disconnect();
  }
}

