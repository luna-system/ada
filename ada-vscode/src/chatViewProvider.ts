/**
 * Chat View Provider for Ada
 * 
 * Provides a sidebar chat interface that works in three tiers:
 * - Tier 1: Basic Ollama chat (0.5B model, works on Chromebook)
 * - Tier 2: Smart Ollama chat (7B model, normal laptop)
 * - Tier 3: Full Ada Brain connection (GraphRAG, specialists)
 * 
 * December 2025 - luna-system
 */

import * as vscode from 'vscode';
import { OllamaClient, ChatMessage } from './ollamaClient';
import { AdaBrainClient } from './adaBrainClient';
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

    constructor(
        private readonly _extensionUri: vscode.Uri,
        private readonly _client: OllamaClient | AdaBrainClient
    ) {}

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

        // Handle messages from the webview
        webviewView.webview.onDidReceiveMessage(async (data) => {
            switch (data.type) {
                case 'sendMessage':
                    await this._handleUserMessage(data.message);
                    break;
                case 'clearChat':
                    this._messages = [];
                    this._postMessage({ type: 'cleared' });
                    break;
                case 'stopGeneration':
                    this._isGenerating = false;
                    break;
            }
        });

        // Send initial connection status
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
        return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ada Chat</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            background: var(--vscode-sideBar-background);
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        /* Header */
        .header {
            padding: 12px;
            border-bottom: 1px solid var(--vscode-panel-border);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .header h1 {
            font-size: 14px;
            font-weight: 600;
            flex: 1;
        }
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--vscode-errorForeground);
        }
        .status-dot.connected { background: var(--vscode-testing-iconPassed); }
        .status-text {
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
        }
        
        /* Messages */
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .message {
            padding: 10px 12px;
            border-radius: 8px;
            max-width: 95%;
            line-height: 1.5;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .message.user {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            align-self: flex-end;
            border-bottom-right-radius: 4px;
        }
        .message.assistant {
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            align-self: flex-start;
            border-bottom-left-radius: 4px;
        }
        .message.error {
            background: var(--vscode-inputValidation-errorBackground);
            border: 1px solid var(--vscode-inputValidation-errorBorder);
            color: var(--vscode-errorForeground);
        }
        .message.system {
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
            text-align: center;
            align-self: center;
            background: transparent;
        }
        
        /* Code blocks */
        .message pre {
            background: var(--vscode-textCodeBlock-background);
            padding: 8px;
            border-radius: 4px;
            overflow-x: auto;
            margin: 8px 0;
            font-family: var(--vscode-editor-font-family);
            font-size: 12px;
        }
        .message code {
            font-family: var(--vscode-editor-font-family);
            background: var(--vscode-textCodeBlock-background);
            padding: 2px 4px;
            border-radius: 3px;
        }
        
        /* Typing indicator */
        .typing {
            display: flex;
            gap: 4px;
            padding: 10px 12px;
        }
        .typing span {
            width: 6px;
            height: 6px;
            background: var(--vscode-descriptionForeground);
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        .typing span:nth-child(1) { animation-delay: -0.32s; }
        .typing span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
        
        /* Input area */
        .input-area {
            padding: 12px;
            border-top: 1px solid var(--vscode-panel-border);
            display: flex;
            gap: 8px;
        }
        .input-wrapper {
            flex: 1;
            display: flex;
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            border-radius: 6px;
            overflow: hidden;
        }
        .input-wrapper:focus-within {
            border-color: var(--vscode-focusBorder);
        }
        textarea {
            flex: 1;
            background: transparent;
            border: none;
            color: var(--vscode-input-foreground);
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            padding: 8px 12px;
            resize: none;
            outline: none;
            min-height: 36px;
            max-height: 120px;
        }
        textarea::placeholder {
            color: var(--vscode-input-placeholderForeground);
        }
        
        /* Buttons */
        button {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
            cursor: pointer;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        button:hover {
            background: var(--vscode-button-hoverBackground);
        }
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        button.icon {
            padding: 6px;
            background: transparent;
            color: var(--vscode-foreground);
        }
        button.icon:hover {
            background: var(--vscode-toolbar-hoverBackground);
        }
        
        /* Welcome state */
        .welcome {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 20px;
            gap: 12px;
        }
        .welcome-icon { font-size: 48px; }
        .welcome h2 { font-size: 16px; font-weight: 600; }
        .welcome p {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            max-width: 300px;
            line-height: 1.4;
        }
        
        /* Quick actions */
        .quick-action {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
            border: 1px solid var(--vscode-button-border);
            padding: 8px 12px;
            font-size: 12px;
            text-align: left;
            width: 100%;
            max-width: 250px;
        }
        .quick-action:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }
        
        /* Tool usage indicator */
        .tool-indicator {
            font-size: 10px;
            color: var(--vscode-charts-blue);
            padding: 4px 8px;
            background: var(--vscode-badge-background);
            border-radius: 12px;
            margin-top: 6px;
            display: inline-block;
        }
        
        /* Token counter */
        .message-meta {
            font-size: 10px;
            color: var(--vscode-descriptionForeground);
            margin-top: 6px;
            opacity: 0.7;
        }
        
        /* Links */
        a {
            color: var(--vscode-textLink-foreground);
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb {
            background: var(--vscode-scrollbarSlider-background);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--vscode-scrollbarSlider-hoverBackground);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Ada</h1>
        <span class="status-dot" id="status-dot"></span>
        <span class="status-text" id="status-text">Connecting...</span>
        <button class="icon" id="clear-btn" title="Clear chat">🗑️</button>
    </div>
    
    <div class="messages" id="messages">
        <div class="welcome" id="welcome">
            <div class="welcome-icon">✨</div>
            <h2>Hi! I'm Ada</h2>
            <p>Your local AI assistant with memory, context, and self-introspection.</p>
            <div style="margin-top: 16px; display: flex; flex-direction: column; gap: 8px; width: 100%;">
                <button class="quick-action" onclick="quickAsk('Explain this code')">📖 Explain code</button>
                <button class="quick-action" onclick="quickAsk('Find bugs in my code')">🐛 Find bugs</button>
                <button class="quick-action" onclick="quickAsk('How does your memory system work?')">🧠 Introspect Ada</button>
            </div>
        </div>
    </div>
    
    <div class="input-area">
        <div class="input-wrapper">
            <textarea 
                id="input" 
                placeholder="Ask Ada..." 
                rows="1"
            ></textarea>
        </div>
        <button id="send-btn" title="Send (Enter)">→</button>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        
        const messagesEl = document.getElementById('messages');
        const welcomeEl = document.getElementById('welcome');
        const inputEl = document.getElementById('input');
        const sendBtn = document.getElementById('send-btn');
        const clearBtn = document.getElementById('clear-btn');
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        
        let currentAssistantEl = null;
        let isGenerating = false;
        
        // Auto-resize textarea
        inputEl.addEventListener('input', () => {
            inputEl.style.height = 'auto';
            inputEl.style.height = Math.min(inputEl.scrollHeight, 120) + 'px';
        });
        
        // Send on Enter (Shift+Enter for newline)
        inputEl.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        sendBtn.addEventListener('click', sendMessage);
        clearBtn.addEventListener('click', () => {
            vscode.postMessage({ type: 'clearChat' });
        });
        
        function sendMessage() {
            const message = inputEl.value.trim();
            if (!message || isGenerating) return;
            
            vscode.postMessage({ type: 'sendMessage', message });
            inputEl.value = '';
            inputEl.style.height = 'auto';
        }
        
        function quickAsk(message) {
            inputEl.value = message;
            sendMessage();
        }
        
        function addMessage(content, role) {
            if (welcomeEl) welcomeEl.style.display = 'none';
            
            const el = document.createElement('div');
            el.className = 'message ' + role;
            el.textContent = content;
            messagesEl.appendChild(el);
            scrollToBottom();
            return el;
        }
        
        function addTypingIndicator() {
            const el = document.createElement('div');
            el.className = 'message assistant typing';
            el.id = 'typing';
            el.innerHTML = '<span></span><span></span><span></span>';
            messagesEl.appendChild(el);
            scrollToBottom();
        }
        
        function removeTypingIndicator() {
            const el = document.getElementById('typing');
            if (el) el.remove();
        }
        
        function scrollToBottom() {
            messagesEl.scrollTop = messagesEl.scrollHeight;
        }
        
        function formatContent(text) {
            // Enhanced markdown formatting with tool indicators
            let formatted = text;
            
            // Extract and highlight tool usage
            const toolPattern = /SPECIALIST_REQUEST\[([^\]]+)\]/g;
            formatted = formatted.replace(toolPattern, '<span class="tool-indicator">🔧 Using: $1</span>');
            
            // Code blocks with language hint
            formatted = formatted.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
                const langLabel = lang ? ` <span style="opacity: 0.6; font-size: 10px;">${lang}</span>` : '';
                return `<pre>${langLabel}<code>${escapeHtml(code)}</code></pre>`;
            });
            
            // Inline code
            formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
            
            // Bold
            formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
            
            // Italic
            formatted = formatted.replace(/\*([^*]+)\*/g, '<em>$1</em>');
            
            // Links
            formatted = formatted.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
            
            return formatted;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Handle messages from extension
        window.addEventListener('message', (event) => {
            const msg = event.data;
            
            switch (msg.type) {
                case 'connectionStatus':
                    statusDot.className = 'status-dot' + (msg.connected ? ' connected' : '');
                    statusText.textContent = msg.connected 
                        ? msg.currentModel.split(':')[0]
                        : 'Disconnected';
                    break;
                    
                case 'userMessage':
                    addMessage(msg.content, 'user');
                    break;
                    
                case 'generationStart':
                    isGenerating = true;
                    sendBtn.disabled = true;
                    sendBtn.textContent = '⏹';
                    addTypingIndicator();
                    break;
                    
                case 'generationChunk':
                    removeTypingIndicator();
                    if (!currentAssistantEl) {
                        currentAssistantEl = addMessage('', 'assistant');
                    }
                    currentAssistantEl.textContent += msg.content;
                    scrollToBottom();
                    break;
                    
                case 'generationEnd':
                    isGenerating = false;
                    sendBtn.disabled = false;
                    sendBtn.textContent = '→';
                    currentAssistantEl = null;
                    removeTypingIndicator();
                    break;
                    
                case 'toolStatus':
                    // Tool calls detected, clear the XML output
                    if (currentAssistantEl) {
                        currentAssistantEl.remove();
                        currentAssistantEl = null;
                    }
                    // Show tool execution status
                    const toolEl = addMessage('[Tools] Using: ' + msg.tools.join(', '), 'assistant');
                    toolEl.style.opacity = '0.7';
                    toolEl.style.fontStyle = 'italic';
                    break;
                    
                case 'toolResults':
                    // Show tool results (collapsed by default)
                    const resultsEl = addMessage('[Tool Results]\\n' + msg.content, 'assistant');
                    resultsEl.style.opacity = '0.7';
                    resultsEl.style.fontSize = '0.9em';
                    resultsEl.style.maxHeight = '100px';
                    resultsEl.style.overflow = 'auto';
                    // Start next generation cycle
                    addTypingIndicator();
                    break;
                    
                case 'error':
                    removeTypingIndicator();
                    addMessage(msg.message, 'error');
                    currentAssistantEl = null;
                    break;
                    
                case 'cleared':
                    messagesEl.innerHTML = '';
                    if (welcomeEl) {
                        messagesEl.appendChild(welcomeEl);
                        welcomeEl.style.display = 'flex';
                    }
                    currentAssistantEl = null;
                    break;
            }
        });
        
        // Focus input on load
        inputEl.focus();
    </script>
</body>
</html>`;
    }
}
