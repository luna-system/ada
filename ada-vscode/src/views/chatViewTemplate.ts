/**
 * Chat View HTML Template
 * Extracted for better maintainability and syntax highlighting
 */

export function getChatViewHtml(): string {
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
        
        /* Tool transparency */
        .tool-results {
            margin-top: 8px;
            padding: 8px;
            background: var(--vscode-textCodeBlock-background);
            border-left: 3px solid var(--vscode-charts-blue);
            border-radius: 4px;
            font-size: 11px;
        }
        .tool-results details {
            cursor: pointer;
        }
        .tool-results summary {
            font-weight: 600;
            color: var(--vscode-charts-blue);
            user-select: none;
        }
        .tool-file-list {
            margin-top: 8px;
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
        }
        .tool-file-badge {
            display: inline-block;
            padding: 2px 6px;
            background: var(--vscode-charts-green);
            color: var(--vscode-editor-background);
            border-radius: 3px;
            font-size: 10px;
            font-family: var(--vscode-editor-font-family);
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
            if (role === 'assistant' && content) {
                el.innerHTML = formatContent(content);
            } else {
                el.textContent = content;
            }
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
            let formatted = text;
            let toolMarkers = [];
            
            // Extract tool markers: [🔧 tool: path]
            const toolRegex = /\\[🔧 ([^:]+): ([^\\]]+)\\]/g;
            let match;
            while ((match = toolRegex.exec(text)) !== null) {
                toolMarkers.push({ tool: match[1], path: match[2] });
            }
            
            // Remove tool markers from content
            formatted = formatted.replace(toolRegex, '');
            
            // Code blocks
            formatted = formatted.replace(/\`\`\`(\\w*)\\n([\\s\\S]*?)\`\`\`/g, (match, lang, code) => {
                const langLabel = lang ? ' <span style="opacity: 0.6; font-size: 10px;">' + lang + '</span>' : '';
                return '<pre>' + langLabel + '<code>' + escapeHtml(code) + '</code></pre>';
            });
            
            // Inline code
            formatted = formatted.replace(/\`([^\`]+)\`/g, '<code>$1</code>');
            
            // Bold
            formatted = formatted.replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>');
            
            // Italic
            formatted = formatted.replace(/\\*([^*]+)\\*/g, '<em>$1</em>');
            
            // Links
            formatted = formatted.replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, '<a href="$2" target="_blank">$1</a>');
            
            // Add tool results if tools were used
            if (toolMarkers.length > 0) {
                const uniqueFiles = [...new Set(toolMarkers.map(m => m.path))];
                const badges = uniqueFiles
                    .map(file => '<span class="tool-file-badge">' + file + '</span>')
                    .join(' ');
                
                const toolSection = 
                    '<div class="tool-results">' +
                    '<details>' +
                    '<summary>🔧 Tools Used (' + uniqueFiles.length + ' files)</summary>' +
                    '<div class="tool-file-list">' + badges + '</div>' +
                    '</details>' +
                    '</div>';
                
                formatted = toolSection + formatted;
            }
            
            return formatted;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Buffer for tool files received before message element exists
        let pendingToolFiles = [];
        
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
                    pendingToolFiles = []; // Clear pending on new generation
                    addTypingIndicator();
                    break;
                    
                case 'generationChunk':
                case 'assistantChunk':
                    removeTypingIndicator();
                    if (!currentAssistantEl) {
                        currentAssistantEl = addMessage('', 'assistant');
                        currentAssistantEl.dataset.rawContent = '';
                        
                        // Apply any pending tool files
                        if (pendingToolFiles.length > 0) {
                            const toolSection = 
                                '<div class="tool-results">' +
                                '<details>' +
                                '<summary>🔧 Files Analyzed (' + pendingToolFiles.length + ')</summary>' +
                                '<div class="tool-file-list">' +
                                pendingToolFiles.map(f => '<span class="tool-file-badge">' + f + '</span>').join(' ') +
                                '</div>' +
                                '</details>' +
                                '</div>';
                            currentAssistantEl.innerHTML = toolSection;
                            pendingToolFiles = [];
                        }
                    }
                    currentAssistantEl.dataset.rawContent += msg.content;
                    // Preserve tool section if it exists
                    const existingToolSection = currentAssistantEl.querySelector('.tool-results');
                    const toolHtml = existingToolSection ? existingToolSection.outerHTML : '';
                    currentAssistantEl.innerHTML = toolHtml + formatContent(currentAssistantEl.dataset.rawContent);
                    scrollToBottom();
                    break;
                    
                case 'toolFiles':
                    // Tool transparency - show which files Ada read
                    if (msg.files.length > 0) {
                        if (currentAssistantEl) {
                            // Apply immediately to existing message
                            const toolSection = 
                                '<div class="tool-results">' +
                                '<details>' +
                                '<summary>🔧 Files Analyzed (' + msg.files.length + ')</summary>' +
                                '<div class="tool-file-list">' +
                                msg.files.map(f => '<span class="tool-file-badge">' + f + '</span>').join(' ') +
                                '</div>' +
                                '</details>' +
                                '</div>';
                            // Only add if not already present
                            if (!currentAssistantEl.querySelector('.tool-results')) {
                                currentAssistantEl.innerHTML = toolSection + currentAssistantEl.innerHTML;
                            }
                        } else {
                            // Buffer for when message element is created
                            pendingToolFiles = msg.files;
                        }
                    }
                    break;
                    
                case 'finalResult':
                    if (currentAssistantEl) {
                        currentAssistantEl.dataset.rawContent = msg.content;
                        currentAssistantEl.innerHTML = formatContent(msg.content);
                    }
                    break;
                    
                case 'generationEnd':
                    isGenerating = false;
                    sendBtn.disabled = false;
                    sendBtn.textContent = '→';
                    currentAssistantEl = null;
                    removeTypingIndicator();
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
