"use strict";
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
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.ChatViewProvider = void 0;
const vscode = __importStar(require("vscode"));
const MessageHandlerRegistry_1 = require("./handlers/MessageHandlerRegistry");
const ToolTransparencyFormatter_1 = require("./formatters/ToolTransparencyFormatter");
const chatViewTemplate_1 = require("./views/chatViewTemplate");
// Don't import AdaMCPClient here - load it dynamically only when needed
const tools_1 = require("./tools");
class ChatViewProvider {
    _extensionUri;
    _client;
    static viewType = 'ada.chatView';
    _view;
    _messages = [];
    _isGenerating = false;
    _mcpClient; // Lazy-loaded
    _messageHandlers;
    constructor(_extensionUri, _client) {
        this._extensionUri = _extensionUri;
        this._client = _client;
        // Initialize message handler registry
        this._messageHandlers = new MessageHandlerRegistry_1.MessageHandlerRegistry();
        this._registerHandlers();
    }
    /**
     * Register message handlers using clean registry pattern
     */
    _registerHandlers() {
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
    resolveWebviewView(webviewView, context, _token) {
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
    async _checkConnection() {
        const connected = await this._client.checkConnection();
        const models = await this._client.listModels();
        this._postMessage({
            type: 'connectionStatus',
            connected,
            modelCount: models.length,
            currentModel: this._client.model,
        });
    }
    async _handleUserMessage(message) {
        if (this._isGenerating || !message.trim()) {
            return;
        }
        this._messages.push({ role: 'user', content: message });
        this._postMessage({ type: 'userMessage', content: message });
        this._isGenerating = true;
        this._postMessage({ type: 'generationStart' });
        try {
            const config = vscode.workspace.getConfiguration('ada');
            const chatMode = config.get('chatMode', 'brain');
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
                systemPrompt += `\n\n${tools_1.TOOL_DEFINITIONS}`;
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
                    if (!this._isGenerating)
                        break;
                    fullResponse += chunk.content;
                    this._postMessage({
                        type: 'generationChunk',
                        content: chunk.content,
                        done: chunk.done
                    });
                }
                console.log('[ADA DEBUG] Finished streaming, fullResponse length:', fullResponse.length);
                if (!fullResponse || !this._isGenerating)
                    break;
                // Check for tool calls
                console.log('[ADA DEBUG] Checking for tool calls in response:', fullResponse.substring(0, 200));
                const hasCalls = (0, tools_1.hasToolCalls)(fullResponse);
                console.log('[ADA DEBUG] hasToolCalls returned:', hasCalls);
                if (useTools && hasCalls) {
                    const toolCalls = (0, tools_1.parseToolCalls)(fullResponse);
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
                        const toolResults = await (0, tools_1.executeToolCalls)(toolCalls);
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
        }
        catch (error) {
            console.error('Ada chat error:', error);
            this._postMessage({
                type: 'error',
                message: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
            });
        }
        finally {
            this._isGenerating = false;
            this._postMessage({ type: 'generationEnd' });
        }
    }
    async _handleMCPChat(message) {
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
                // Extract tool usage from response for transparency
                const toolMarkers = ToolTransparencyFormatter_1.ToolTransparencyFormatter.extractToolMarkers(response);
                console.log('[ADA MCP] Introspection tool markers found:', toolMarkers.length, toolMarkers);
                if (toolMarkers.length > 0) {
                    const uniqueFiles = [...new Set(toolMarkers.map(m => m.path))];
                    console.log('[ADA MCP] Tool transparency: sending files to webview:', uniqueFiles);
                    this._postMessage({ type: 'toolFiles', files: uniqueFiles });
                }
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
            // Extract tool usage from response for transparency
            console.log('[ADA MCP] Response preview (first 500 chars):', response.substring(0, 500));
            console.log('[ADA MCP] Checking for Files Analyzed pattern...');
            // Debug: Check if pattern exists manually
            const hasFilesAnalyzed = response.includes('Files Analyzed');
            console.log('[ADA MCP] Contains "Files Analyzed":', hasFilesAnalyzed);
            const toolMarkers = ToolTransparencyFormatter_1.ToolTransparencyFormatter.extractToolMarkers(response);
            console.log('[ADA MCP] Tool markers found:', toolMarkers.length, toolMarkers);
            if (toolMarkers.length > 0) {
                const uniqueFiles = [...new Set(toolMarkers.map(m => m.path))];
                console.log('[ADA MCP] Tool transparency: sending files to webview:', uniqueFiles);
                this._postMessage({ type: 'toolFiles', files: uniqueFiles });
            }
            else {
                console.log('[ADA MCP] No tool markers found, skipping toolFiles message');
            }
            // Post the complete response (MCP doesn't support streaming)
            this._postMessage({ type: 'generationChunk', content: response });
            this._messages.push({ role: 'assistant', content: response });
        }
        catch (error) {
            console.error('MCP chat error:', error);
            this._postMessage({
                type: 'error',
                message: `MCP Error: ${error instanceof Error ? error.message : 'Unknown error'}`
            });
        }
        finally {
            this._isGenerating = false;
            this._postMessage({ type: 'generationEnd' });
        }
    }
    _postMessage(message) {
        if (this._view) {
            this._view.webview.postMessage(message);
        }
    }
    clearHistory() {
        this._messages = [];
        this._postMessage({ type: 'cleared' });
    }
    /**
     * Send a message programmatically (from code actions)
     */
    sendMessage(message) {
        this._handleUserMessage(message);
    }
    _getHtmlForWebview(webview) {
        return (0, chatViewTemplate_1.getChatViewHtml)();
    }
}
exports.ChatViewProvider = ChatViewProvider;
//# sourceMappingURL=chatViewProvider.js.map