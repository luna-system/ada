const messagesEl = document.getElementById('messages');
const form = document.getElementById('composer');
const input = document.getElementById('prompt');
const sendBtn = document.getElementById('send');
const includeThinkingEl = document.getElementById('includeThinking');
let thinkingEl = null;

// Maintain a per-session conversation id so RAG can thread context
let conversationId = localStorage.getItem('conversation_id');
if (!conversationId && window.crypto && crypto.randomUUID) {
  conversationId = crypto.randomUUID();
  localStorage.setItem('conversation_id', conversationId);
}

function addMessage(role, text) {
  const wrap = document.createElement('div');
  wrap.className = `msg ${role}`;

  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.textContent = role === 'me' ? '🧑' : '🤖';

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;

  wrap.appendChild(avatar);
  wrap.appendChild(bubble);
  messagesEl.appendChild(wrap);
  messagesEl.scrollTo({ top: messagesEl.scrollHeight, behavior: 'smooth' });
}

function showThinking() {
  if (thinkingEl) return;
  thinkingEl = document.createElement('div');
  thinkingEl.className = 'msg thinking';
  const spin = document.createElement('div');
  spin.className = 'spinner';
  spin.setAttribute('aria-hidden', 'true');
  spin.title = 'Thinking...';
  thinkingEl.appendChild(spin);
  messagesEl.appendChild(thinkingEl);
  messagesEl.scrollTo({ top: messagesEl.scrollHeight, behavior: 'smooth' });
}

function hideThinking() {
  if (thinkingEl) {
    thinkingEl.remove();
    thinkingEl = null;
  }
}

function replaceThinkingWithBot(text) {
  const wrap = document.createElement('div');
  wrap.className = 'msg bot';

  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.textContent = '🤖';

  // Stack to place bubbles vertically so thinking flows above the answer
  const stack = document.createElement('div');
  stack.className = 'stack';

  // If the model returns a <think>...</think> block and the toggle is ON,
  // render it as a collapsible bubble above the final answer.
  const thinkMatch = /<think>([\s\S]*?)<\/think>([\s\S]*)/i.exec(text || '');
  if (includeThinkingEl.checked && thinkMatch) {
    const thinkDetails = document.createElement('details');
    thinkDetails.className = 'bubble think';

    const summary = document.createElement('summary');
    summary.textContent = 'Thinking';

    const content = document.createElement('div');
    content.className = 'think-content';
    content.textContent = thinkMatch[1].trim();

    thinkDetails.appendChild(summary);
    thinkDetails.appendChild(content);
    stack.appendChild(thinkDetails);

    const answerBubble = document.createElement('div');
    answerBubble.className = 'bubble answer';
    answerBubble.textContent = (thinkMatch[2] || '').trim();
    stack.appendChild(answerBubble);
  } else {
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = (thinkMatch ? thinkMatch[2] : text) || '';
    stack.appendChild(bubble);
  }

  wrap.appendChild(avatar);
  wrap.appendChild(stack);

  if (thinkingEl && thinkingEl.parentNode) {
    thinkingEl.replaceWith(wrap);
    thinkingEl = null;
  } else {
    messagesEl.appendChild(wrap);
  }
  messagesEl.scrollTo({ top: messagesEl.scrollHeight, behavior: 'smooth' });
}

function setBusy(busy) {
  form.querySelectorAll('textarea,button').forEach(el => el.disabled = busy);
  messagesEl.setAttribute('aria-busy', String(busy));
  if (busy) showThinking(); else hideThinking();
}

input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const prompt = input.value.trim();
  if (!prompt) return;

  addMessage('me', prompt);
  input.value = '';
  setBusy(true);

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt,
        include_thinking: !!includeThinkingEl.checked,
        conversation_id: conversationId
      })
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || `Request failed: ${res.status}`);
    }

    // Update local conversation id if backend generated one
    if (data.conversation_id && data.conversation_id !== conversationId) {
      conversationId = data.conversation_id;
      localStorage.setItem('conversation_id', conversationId);
    }

    // If the API returns a separate 'thinking' field and the toggle is ON,
    // prepend it wrapped in <think>...</think> so existing rendering logic
    // shows a muted thinking bubble followed by the answer.
    let displayText = data.response || '';
    if (includeThinkingEl.checked && data.thinking) {
      displayText = `<think>${data.thinking}</think>` + (data.response || '');
    }

    replaceThinkingWithBot(displayText);
  } catch (err) {
    console.error(err);
    replaceThinkingWithBot(`Error: ${err.message}`);
  } finally {
    setBusy(false);
    input.focus();
  }
});

// Greet on load
addMessage('bot', 'Hello! Ask me anything.');
input.focus();
