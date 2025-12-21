/**
 * ChatViewProvider - Manages webview chat UI with MCP tool routing
 * 
 * Architecture:
 * - Uses MCPToolHandler for intent classification
 * - Two-phase pattern: tool execution → brain reasoning
 * - Tool transparency via structured metadata
 * 
 * December 2025 - luna+ada
 */

import * as vscode from 'vscode';
import { AdaBrainClient } from '@ada-code/shared/clients';
import { MCPToolHandler } from './mcpToolHandler';

export class ChatViewProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = 'ada.chatView';
  private _view?: vscode.WebviewView;
  private _toolHandler: MCPToolHandler;
  private _isGenerating = false;

  constructor(
    private readonly _extensionUri: vscode.Uri,
    private readonly _brainClient: AdaBrainClient
  ) {
    this._toolHandler = new MCPToolHandler();
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
    this._postMessage({ type: 'generationStart' });

    try {
      // Classify intent - does this need MCP tools?
      const intent = this._toolHandler.classifyIntent(userMessage);
      
      if (intent.requiresTool) {
        console.log('[Ada Chat] Tool required:', intent.tool);
        
        // Execute tool
        const toolResult = await this._toolHandler.executeTool(intent);
        
        // Show tool transparency
        if (toolResult.metadata.files_accessed.length > 0) {
          this._postMessage({
            type: 'toolFiles',
            files: toolResult.metadata.files_accessed
          });
        }
        
        if (intent.requiresReasoning) {
          // Two-phase: inject tool results into brain for reasoning
          const augmentedPrompt = this._toolHandler.buildAugmentedPrompt(
            userMessage,
            toolResult
          );
          
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
          // Simple tool output - no reasoning needed
          this._postMessage({
            type: 'generationChunk',
            content: toolResult.content,
            done: true
          });
        }
      } else {
        // Regular chat - no tools
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
    // Minimal working HTML for now - will enhance later
    return `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Ada Chat</title>
          <style>
            body {
              font-family: var(--vscode-font-family);
              padding: 10px;
              color: var(--vscode-foreground);
              background-color: var(--vscode-editor-background);
            }
            #chat-container {
              display: flex;
              flex-direction: column;
              height: 100vh;
            }
            #messages {
              flex: 1;
              overflow-y: auto;
              margin-bottom: 10px;
            }
            .message {
              margin-bottom: 10px;
              padding: 8px;
              border-radius: 4px;
            }
            .user-message {
              background-color: var(--vscode-input-background);
            }
            .assistant-message {
              background-color: var(--vscode-editor-background);
            }
            .tool-files {
              background-color: var(--vscode-badge-background);
              color: var(--vscode-badge-foreground);
              padding: 4px 8px;
              border-radius: 3px;
              font-size: 11px;
              margin-bottom: 8px;
              display: inline-block;
            }
            #input-container {
              display: flex;
              gap: 5px;
            }
            #message-input {
              flex: 1;
              padding: 8px;
              background-color: var(--vscode-input-background);
              color: var(--vscode-input-foreground);
              border: 1px solid var(--vscode-input-border);
              border-radius: 3px;
            }
            button {
              padding: 8px 16px;
              background-color: var(--vscode-button-background);
              color: var(--vscode-button-foreground);
              border: none;
              border-radius: 3px;
              cursor: pointer;
            }
            button:hover {
              background-color: var(--vscode-button-hoverBackground);
            }
          </style>
        </head>
        <body>
          <div id="chat-container">
            <div id="messages"></div>
            <div id="input-container">
              <input type="text" id="message-input" placeholder="Ask Ada..." />
              <button id="send-button">Send</button>
            </div>
          </div>
          <script>
            const vscode = acquireVsCodeApi();
            const messagesDiv = document.getElementById('messages');
            const inputField = document.getElementById('message-input');
            const sendButton = document.getElementById('send-button');
            
            let currentAssistantMessage = null;
            
            function addMessage(content, isUser) {
              const div = document.createElement('div');
              div.className = 'message ' + (isUser ? 'user-message' : 'assistant-message');
              div.textContent = content;
              messagesDiv.appendChild(div);
              messagesDiv.scrollTop = messagesDiv.scrollHeight;
              return div;
            }
            
            function sendMessage() {
              const message = inputField.value.trim();
              if (message) {
                vscode.postMessage({ type: 'sendMessage', content: message });
                inputField.value = '';
              }
            }
            
            inputField.addEventListener('keypress', (e) => {
              if (e.key === 'Enter') sendMessage();
            });
            
            sendButton.addEventListener('click', sendMessage);
            
            window.addEventListener('message', (event) => {
              const message = event.data;
              
              switch (message.type) {
                case 'userMessage':
                  addMessage(message.content, true);
                  break;
                  
                case 'toolFiles':
                  const badge = document.createElement('div');
                  badge.className = 'tool-files';
                  badge.textContent = '🔧 Files: ' + message.files.join(', ');
                  messagesDiv.appendChild(badge);
                  break;
                  
                case 'generationStart':
                  currentAssistantMessage = addMessage('', false);
                  break;
                  
                case 'generationChunk':
                  if (currentAssistantMessage) {
                    currentAssistantMessage.textContent += message.content;
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                  }
                  break;
                  
                case 'generationEnd':
                  currentAssistantMessage = null;
                  break;
                  
                case 'error':
                  addMessage('Error: ' + message.message, false);
                  break;
              }
            });
          </script>
        </body>
      </html>
    `;
  }

  private _postMessage(message: any) {
    this._view?.webview.postMessage(message);
  }
  
  public dispose() {
    this._toolHandler.disconnect();
  }
}

