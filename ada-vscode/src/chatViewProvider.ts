/**
 * Chat View Provider for Ada
 * 
 * Provides a sidebar chat interface that works in three tiers:
 * - Tier 1: Basic Ollama chat (0.5B model, works on Chromebook)
 * - Tier 2: Smart Ollama chat (7B model, normal laptop)
 * - Tier 3: Full Ada Brain connection (GraphRAG, specialists)
 * 
 * ARCHITECTURE NOTES:
 * - Uses message handler registry for clean routing
 * - HTML template extracted to separate file for maintainability
 * - Tool transparency via ToolTransparencyFormatter
 * - Type-safe message contracts in types/messages.ts
 * 
 * WEBVIEW LIFECYCLE:
 * VS Code webviews execute scripts SYNCHRONOUSLY when HTML is set.
 * No need for "ready" signal - initialization happens in resolveWebviewView().
 * Do NOT add ready handlers - causes race conditions with caching!
 * 
 * December 2025 - luna-system
 */

import * as vscode from 'vscode';
import { OllamaClient, ChatMessage } from './ollamaClient';
import { AdaBrainClient } from './adaBrainClient';
import { MessageHandlerRegistry } from './handlers/MessageHandlerRegistry';
import { ToolTransparencyFormatter } from './formatters/ToolTransparencyFormatter';
import { getChatViewHtml } from './views/chatViewTemplate';
// Don't import AdaMCPClient here - load it dynamically only when needed
import { 
    TOOL_DEFINITIONS, 
    parseToolCalls, 
    hasToolCalls, 
    executeToolCalls,
    extractNonToolText 
} from './tools';

export class ChatViewProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'ada.chatView';
    
    private _view?: vscode.WebviewView;
    private _messages: ChatMessage[] = [];
    private _isGenerating: boolean = false;
    private _mcpClient?: any; // Lazy-loaded
    private _messageHandlers: MessageHandlerRegistry;

    constructor(
        private readonly _extensionUri: vscode.Uri,
        private readonly _client: OllamaClient | AdaBrainClient
    ) {
        // Initialize message handler registry
        this._messageHandlers = new MessageHandlerRegistry();
        this._registerHandlers();
    }
    
    /**
     * Register message handlers using clean registry pattern
     */
    private _registerHandlers() {
        this._messageHandlers.register('sendMessage', async (data) => {
            await this._handleUserMessage(data.message);
        });
        
        this._messageHandlers.register('clearChat', () => {
            this._messages = [];
            this._postMessage({ type: 'cleared' });
        });
        
        this._messageHandlers.register('stopGeneration', () => {
            this._isGenerating = false;
        });
    }

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        // Route messages through handler registry
        webviewView.webview.onDidReceiveMessage(async (data) => {
            await this._messageHandlers.handle(data);
        });
        
        // IMPORTANT: Check connection immediately after HTML set
        // Webview scripts execute synchronously - no need for "ready" signal
        this._checkConnection();
    }

    private async _checkConnection() {
        const connected = await this._client.checkConnection();
        const models = await this._client.listModels();
        
        this._postMessage({
            type: 'connectionStatus',
            connected,
            modelCount: models.length,
            currentModel: this._client.model,
        });
    }

    private async _handleUserMessage(message: string) {
        if (this._isGenerating || !message.trim()) {
            return;
        }

        this._messages.push({ role: 'user', content: message });
        this._postMessage({ type: 'userMessage', content: message });

        this._isGenerating = true;
        this._postMessage({ type: 'generationStart' });

        try {
            const config = vscode.workspace.getConfiguration('ada');
            const chatMode = config.get<string>('chatMode', 'brain');
            
            // Route to appropriate backend
            if (chatMode === 'mcp') {
                await this._handleMCPChat(message);
                return;
            }
            
            // Fallback to original logic (ollama or brain)
            const useTools = config.get('enableTools', true);
            
            const editor = vscode.window.activeTextEditor;
            let systemPrompt = `You are Ada, a helpful AI coding assistant. You run locally and respect user privacy. Be concise but helpful.`;
            
            // Add tool definitions if enabled
            if (useTools) {
                systemPrompt += `\n\n${TOOL_DEFINITIONS}`;
            }
            
            if (editor) {
                const fileName = editor.document.fileName.split('/').pop();
                const language = editor.document.languageId;
                systemPrompt += `\n\nThe user is currently editing: ${fileName} (${language})`;
                
                const selection = editor.selection;
                if (!selection.isEmpty) {
                    const selectedText = editor.document.getText(selection);
                    if (selectedText.length < 500) {
                        systemPrompt += `\n\nSelected code:\n\`\`\`${language}\n${selectedText}\n\`\`\``;
                    }
                }
            }

            // Add workspace info
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (workspaceFolders) {
                systemPrompt += `\n\nWorkspace: ${workspaceFolders[0].name}`;
            }

            // Agent loop - continue until no more tool calls
            const MAX_ITERATIONS = 10;
            let iteration = 0;
            
            while (iteration < MAX_ITERATIONS && this._isGenerating) {
                iteration++;
                
                let fullResponse = '';
                
                console.log('[ADA DEBUG] Starting chat iteration', iteration);
                console.log('[ADA DEBUG] Client type:', this._client.constructor.name);
                console.log('[ADA DEBUG] Messages:', this._messages.length);
                
                for await (const chunk of this._client.chat(this._messages, {
                    systemPrompt,
                    temperature: config.get('chatTemperature', 0.7),
                    maxTokens: config.get('chatMaxTokens', 2048),
                })) {
                    console.log('[ADA DEBUG] Got chunk:', chunk);
                    if (!this._isGenerating) break;
                    
                    fullResponse += chunk.content;
                    this._postMessage({ 
                        type: 'generationChunk', 
                        content: chunk.content,
                        done: chunk.done
                    });
                }
                
                console.log('[ADA DEBUG] Finished streaming, fullResponse length:', fullResponse.length);

                if (!fullResponse || !this._isGenerating) break;

                // Check for tool calls
                console.log('[ADA DEBUG] Checking for tool calls in response:', fullResponse.substring(0, 200));
                const hasCalls = hasToolCalls(fullResponse);
                console.log('[ADA DEBUG] hasToolCalls returned:', hasCalls);
                
                if (useTools && hasCalls) {
                    const toolCalls = parseToolCalls(fullResponse);
                    console.log('[ADA DEBUG] parseToolCalls returned:', toolCalls.length, 'calls:', toolCalls);
                    
                    if (toolCalls.length > 0) {
                        // Add assistant's response with tool calls to history
                        this._messages.push({ role: 'assistant', content: fullResponse });
                        
                        // Show tool execution status
                        this._postMessage({
                            type: 'toolStatus',
                            tools: toolCalls.map(t => t.name)
                        });
                        
                        // Execute tools
                        const toolResults = await executeToolCalls(toolCalls);
                        
                        // Show tool results in chat (cleaned for display)
                        const displayResults = toolResults
                            .replace(/<tool_result name="([^"]+)"[^>]*>/g, '**[$1 Results]**\n')
                            .replace(/<\/tool_result>/g, '')
                            .replace(/Now answer the user's question using the above results\./, '');
                        
                        this._postMessage({
                            type: 'toolResults',
                            content: displayResults
                        });
                        
                        // Add tool results to messages for next iteration
                        this._messages.push({ role: 'user', content: toolResults });
                        
                        // Continue loop for next iteration
                        continue;
                    }
                }
                
                // No tool calls - we're done
                this._messages.push({ role: 'assistant', content: fullResponse });
                break;
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

    private async _handleMCPChat(message: string) {
        try {
            // Lazy-load MCP client only when needed
            if (!this._mcpClient) {
                console.log('[ADA MCP] Loading MCP client module...');
                const { AdaMCPClient } = await import('./mcpClient.js');
                this._mcpClient = new AdaMCPClient();
                console.log('[ADA MCP] Connecting...');
                await this._mcpClient.connect();
            }

            // Detect if user is requesting a specific tool
            const lowerMessage = message.toLowerCase();
            
            // Pytest/testing request - add smart defaults
            if ((lowerMessage.includes('pytest') || lowerMessage.includes('run test') || lowerMessage.includes('run the test')) && 
                !lowerMessage.includes('directory') && !lowerMessage.includes('folder')) {
                console.log('[ADA MCP] Detected pytest request, adding workspace context');
                const workspace = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
                const enhancedMessage = `${message}\n\n[Context: Workspace root is ${workspace}. If no specific test path is mentioned, default to running 'pytest tests/' from the workspace root.]`;
                const response = await this._mcpClient.chat({ message: enhancedMessage });
                this._postMessage({ type: 'generationChunk', content: response });
                this._messages.push({ role: 'assistant', content: response });
                return;
            }
            
            // Introspection request
            if (lowerMessage.includes('introspect') || 
                (lowerMessage.includes('analyze') && lowerMessage.includes('your') && 
                 (lowerMessage.includes('architecture') || lowerMessage.includes('yourself')))) {
                console.log('[ADA MCP] Detected introspection request, calling tool directly');
                const workspace = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
                const response = await this._mcpClient.callTool('ada_introspect', {
                    focus: 'general',
                    workspace_root: workspace
                });
                this._postMessage({ type: 'generationChunk', content: response });
                this._messages.push({ role: 'assistant', content: response });
                return;
            }

            // Default: regular chat
            // Add workspace context to help Ada understand "this project"
            const workspace = vscode.workspace.workspaceFolders?.[0];
            let contextualMessage = message;
            
            if (workspace && !message.toLowerCase().includes('workspace') && !message.toLowerCase().includes('directory')) {
                const workspaceName = workspace.name;
                const workspacePath = workspace.uri.fsPath;
                
                // Add context for first-person references to project
                if (message.toLowerCase().match(/\b(this project|these modules|this codebase|here)\b/)) {
                    contextualMessage = `[Context: User is in workspace "${workspaceName}" at ${workspacePath}]\n\n${message}`;
                }
            }
            
            const response = await this._mcpClient.chat({ message: contextualMessage });

            // Post the complete response (MCP doesn't support streaming)
            this._postMessage({ type: 'generationChunk', content: response });

            this._messages.push({ role: 'assistant', content: response });
        } catch (error) {
            console.error('MCP chat error:', error);
            this._postMessage({ 
                type: 'error', 
                message: `MCP Error: ${error instanceof Error ? error.message : 'Unknown error'}`
            });
        } finally {
            this._isGenerating = false;
            this._postMessage({ type: 'generationEnd' });
        }
    }

    private _postMessage(message: any) {
        if (this._view) {
            this._view.webview.postMessage(message);
        }
    }

    public clearHistory() {
        this._messages = [];
        this._postMessage({ type: 'cleared' });
    }

    /**
     * Send a message programmatically (from code actions)
     */
    public sendMessage(message: string) {
        this._handleUserMessage(message);
    }


    private _getHtmlForWebview(webview: vscode.Webview): string {
        return getChatViewHtml();
    }
}
