/**
 * Ada Chat Webview Script - Polished Edition
 * 
 * Edit this file directly - changes reflect on extension reload
 * Communicates with extension via vscode.postMessage API
 */

(function() {
  // VS Code API
  const vscode = acquireVsCodeApi();
  
  // DOM Elements
  const messagesDiv = document.getElementById('messages');
  const welcomeDiv = document.getElementById('welcome');
  const inputField = document.getElementById('message-input');
  const sendButton = document.getElementById('send-button');
  const clearButton = document.getElementById('clear-button');
  const statusDot = document.getElementById('status-dot');
  const connectionName = document.getElementById('connection-name');
  
  // State
  let currentAssistantMessage = null;
  let currentAssistantText = '';  // Track raw text for markdown rendering
  let isGenerating = false;
  let hasMessages = false;

  /**
   * Hide welcome message when chat starts
   */
  function hideWelcome() {
    if (welcomeDiv && !hasMessages) {
      welcomeDiv.style.display = 'none';
      hasMessages = true;
    }
  }

  /**
   * Show welcome message when chat is cleared
   */
  function showWelcome() {
    if (welcomeDiv) {
      welcomeDiv.style.display = 'flex';
      hasMessages = false;
    }
  }

  /**
   * Add a message to the chat
   */
  function addMessage(content, type) {
    hideWelcome();
    const div = document.createElement('div');
    div.className = 'message ' + type;
    
    // Render markdown for assistant messages
    if (type === 'assistant-message') {
      div.innerHTML = renderMarkdown(content);
    } else {
      div.textContent = content;
    }
    
    messagesDiv.appendChild(div);
    scrollToBottom();
    return div;
  }

  /**
   * Simple markdown renderer
   */
  function renderMarkdown(text) {
    if (!text) return '';
    
    // Escape HTML first
    let html = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
    
    // Code blocks (```...```)
    html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, function(m, lang, code) {
      return '<pre><code>' + code.trim() + '</code></pre>';
    });
    
    // Inline code (`...`)
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Headers
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
    
    // Bold and italic
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    
    // Lists
    html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
    
    // Line breaks (preserve newlines as <br> but not inside pre)
    html = html.replace(/\n/g, '<br>');
    
    // Clean up extra <br> around block elements
    html = html.replace(/<br>(<\/?(?:pre|ul|ol|li|h[1-3]|blockquote)>)/g, '$1');
    html = html.replace(/(<\/?(?:pre|ul|ol|li|h[1-3]|blockquote)>)<br>/g, '$1');
    
    return html;
  }

  /**
   * Add tool transparency card - collapsed by default, two-line layout
   */
  function addToolCard(tool, metadata) {
    hideWelcome();
    const card = document.createElement('div');
    card.className = 'tool-card';
    
    const toolName = (tool || 'unknown').replace('ada_', '').toUpperCase();
    const meta = metadata || {};
    const duration = meta.duration_ms ? Math.round(meta.duration_ms) + 'ms' : '—';
    const actions = meta.actions_taken || '';
    const files = meta.files_accessed || [];
    
    // Two-line collapsed summary
    let html = '<div class="tool-summary">' +
      '<div class="tool-header">' +
        '<span class="tool-expand">›</span>' +
        '<span class="tool-icon">⚙</span>' +
        '<span class="tool-name">' + toolName + '</span>' +
      '</div>' +
      '<div class="tool-meta">' + duration + (actions ? ' · ' + actions : '') + '</div>' +
      '</div>';
    
    // Expandable details with ALL files
    if (files.length > 0) {
      html += '<div class="tool-details">' +
        '<div class="tool-files">' +
        files.map(function(f) { 
          return '<div class="file-badge"><span class="file-icon">○</span>' + f + '</div>'; 
        }).join('') +
        '</div></div>';
    }
    
    card.innerHTML = html;
    
    // Toggle expand on click
    card.addEventListener('click', function() {
      card.classList.toggle('expanded');
    });
    
    messagesDiv.appendChild(card);
    scrollToBottom();
    return card;
  }

  /**
   * Show typing indicator
   */
  function showTypingIndicator() {
    hideWelcome();
    removeTypingIndicator();
    
    const indicator = document.createElement('div');
    indicator.id = 'typing-indicator';
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';
    messagesDiv.appendChild(indicator);
    scrollToBottom();
  }

  /**
   * Remove typing indicator
   */
  function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
      indicator.remove();
    }
  }

  /**
   * Scroll messages to bottom
   */
  function scrollToBottom() {
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }

  /**
   * Update connection status
   */
  function updateConnectionStatus(connected, name) {
    statusDot.className = 'status-dot' + (connected ? ' connected' : '');
    if (name) {
      connectionName.textContent = name;
    }
  }

  /**
   * Set UI generating state
   */
  function setGenerating(generating) {
    isGenerating = generating;
    sendButton.disabled = generating;
    inputField.disabled = generating;
  }

  /**
   * Send message to extension
   */
  function sendMessage() {
    const message = inputField.value.trim();
    if (message && !isGenerating) {
      vscode.postMessage({ type: 'sendMessage', content: message });
      inputField.value = '';
    }
  }

  /**
   * Clear chat
   */
  function clearChat() {
    vscode.postMessage({ type: 'clearChat' });
  }

  // Event listeners
  inputField.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  sendButton.addEventListener('click', sendMessage);
  clearButton.addEventListener('click', clearChat);

  /**
   * Handle messages from extension
   */
  window.addEventListener('message', function(event) {
    const message = event.data;
    
    switch (message.type) {
      case 'connectionStatus':
        updateConnectionStatus(message.connected, message.name);
        break;
        
      case 'userMessage':
        addMessage(message.content, 'user-message');
        showTypingIndicator();
        break;
        
      case 'toolTransparency':
        removeTypingIndicator();
        addToolCard(message.tool, message.metadata);
        showTypingIndicator();
        break;
        
      case 'generationStart':
        removeTypingIndicator();
        setGenerating(true);
        currentAssistantText = '';
        currentAssistantMessage = document.createElement('div');
        currentAssistantMessage.className = 'message assistant-message';
        messagesDiv.appendChild(currentAssistantMessage);
        scrollToBottom();
        break;
        
      case 'generationChunk':
        if (currentAssistantMessage) {
          currentAssistantText += message.content;
          // Show raw text while streaming (faster)
          currentAssistantMessage.textContent = currentAssistantText;
          scrollToBottom();
        }
        if (message.done) {
          // Render markdown when complete
          if (currentAssistantMessage) {
            currentAssistantMessage.innerHTML = renderMarkdown(currentAssistantText);
          }
          setGenerating(false);
          currentAssistantMessage = null;
          currentAssistantText = '';
        }
        break;
        
      case 'generationEnd':
        // Render markdown on end
        if (currentAssistantMessage && currentAssistantText) {
          currentAssistantMessage.innerHTML = renderMarkdown(currentAssistantText);
        }
        setGenerating(false);
        currentAssistantMessage = null;
        currentAssistantText = '';
        removeTypingIndicator();
        break;
        
      case 'error':
        removeTypingIndicator();
        setGenerating(false);
        addMessage('❌ ' + message.message, 'error-message');
        break;
        
      case 'cleared':
        var messages = messagesDiv.querySelectorAll('.message, .tool-card, .typing-indicator');
        messages.forEach(function(m) { m.remove(); });
        showWelcome();
        break;
    }
  });

  // Focus input on load
  inputField.focus();
})();
