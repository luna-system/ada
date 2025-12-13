const messagesEl = document.getElementById('messages');
const form = document.getElementById('composer');
const input = document.getElementById('prompt');
const sendBtn = document.getElementById('send');
const includeThinkingEl = document.getElementById('includeThinking');
const rememberLastEl = document.getElementById('rememberLast');
const entityInput = document.getElementById('entity');
const openMemBtn   = document.getElementById('openMem');
const memPanel     = document.getElementById('memPanel');
const closeMemBtn  = document.getElementById('closeMem');
const refreshMemBtn= document.getElementById('refreshMem');
const memListEl    = document.getElementById('memList');
const memFilterEntityEl = document.getElementById('memFilterEntity');
const addMemBtn    = document.getElementById('addMem');
const memTextEl    = document.getElementById('memText');
const memImportanceEl = document.getElementById('memImportance');
const memEntityScopedEl = document.getElementById('memEntityScoped');
let thinkingEl = null;

// Track last assistant reply for optional long-term memory save
let lastAssistantText = '';

// Maintain a per-session conversation id so RAG can thread context
let conversationId = localStorage.getItem('conversation_id');
if (!conversationId && window.crypto && crypto.randomUUID) {
  conversationId = crypto.randomUUID();
  localStorage.setItem('conversation_id', conversationId);
}

// Persist an optional entity/topic across requests
let currentEntity = localStorage.getItem('entity') || '';
if (entityInput) {
  entityInput.value = currentEntity;
  entityInput.addEventListener('change', () => {
    currentEntity = entityInput.value.trim();
    localStorage.setItem('entity', currentEntity);
  });
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

  // Capture plain text for optional memory saving
  lastAssistantText = (thinkMatch ? (thinkMatch[2] || '') : (text || '')).trim();
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

  // Handle simple memory commands locally
  const lower = prompt.toLowerCase();
  if (lower === 'memory: help') {
    addMessage('bot', 'Memory commands:\n- memory: list\n- memory: delete <id>');
    input.value = '';
    return;
  }
  if (lower === 'memory: list') {
    try {
      setBusy(true);
      const q = new URLSearchParams();
      q.set('limit','20');
      if (currentEntity) q.set('entity', currentEntity);
      const res = await fetch(`/api/memory?${q.toString()}`);
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      const items = data.items || [];
      if (!items.length) {
        addMessage('bot', 'No memories stored.');
      } else {
        const lines = items.map((it) => {
          const meta = it.meta || {};
          const imp = meta.importance != null ? ` (importance=${meta.importance})` : '';
          const id = it.id ? `id=${it.id}` : '';
          return `• ${id}${imp} ${it.text}`;
        });
        addMessage('bot', `Memories:\n${lines.join('\n')}`);
      }
    } catch (err) {
      addMessage('bot', `Error listing memories: ${err.message}`);
    } finally {
      setBusy(false);
      input.value = '';
    }
    return;
  }
  if (lower.startsWith('memory: delete ')) {
    const memId = prompt.slice('memory: delete '.length).trim();
    if (!memId) {
      addMessage('bot', 'Please provide a memory id to delete.');
    } else {
      try {
        setBusy(true);
        const res = await fetch(`/api/memory/${encodeURIComponent(memId)}`, { method: 'DELETE' });
        const data = await res.json();
        if (!res.ok || data.error) throw new Error(data.error || `HTTP ${res.status}`);
        addMessage('bot', `Deleted memory ${memId}.`);
      } catch (err) {
        addMessage('bot', `Error deleting memory: ${err.message}`);
      } finally {
        setBusy(false);
        input.value = '';
      }
    }
    return;
  }

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
        conversation_id: conversationId,
        entity: currentEntity || undefined,
        // Consent-based long-term memory save of the previous assistant reply
        save_memory: !!rememberLastEl.checked && !!lastAssistantText,
        memory_text: !!rememberLastEl.checked ? lastAssistantText : undefined
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
    // Clear the remember toggle after attempting a save
    if (rememberLastEl.checked) rememberLastEl.checked = false;
  }
});

// Greet on load
addMessage('bot', 'Hello! Ask me anything.');
input.focus();

// --- Memories panel wiring ---
function renderMemList(items) {
  memListEl.innerHTML = '';
  if (!items || !items.length) {
    const p = document.createElement('div');
    p.className = 'muted';
    p.textContent = 'No memories found.';
    memListEl.appendChild(p);
    return;
  }
  items.forEach(it => {
    const row = document.createElement('div');
    row.className = 'mem-item';
    const meta = it.meta || {};
    const scope = meta.scope || 'global';
    const imp = meta.importance != null ? ` (importance=${meta.importance})` : '';
    const txt = document.createElement('div');
    txt.className = 'mem-text';
    txt.textContent = `[${scope}]${imp} ${it.text}`;
    const actions = document.createElement('div');
    actions.className = 'mem-actions';
    if (it.id) {
      const del = document.createElement('button');
      del.className = 'icon danger';
      del.title = 'Delete memory';
      del.textContent = '🗑';
      del.addEventListener('click', async () => {
        del.disabled = true;
        try {
          const r = await fetch(`/api/memory/${encodeURIComponent(it.id)}`, { method: 'DELETE' });
          const d = await r.json();
          if (!r.ok || d.error) throw new Error(d.error || `HTTP ${r.status}`);
          await refreshMemList();
        } catch (e) {
          alert(`Delete failed: ${e.message}`);
        } finally {
          del.disabled = false;
        }
      });
      actions.appendChild(del);
    }
    row.appendChild(txt);
    row.appendChild(actions);
    memListEl.appendChild(row);
  });
}

async function refreshMemList() {
  const q = new URLSearchParams();
  q.set('limit','50');
  const filterEntity = (memFilterEntityEl?.value || '').trim();
  if (filterEntity) q.set('entity', filterEntity);
  const res = await fetch(`/api/memory?${q.toString()}`);
  const data = await res.json();
  if (data.error) throw new Error(data.error);
  renderMemList(data.items || []);
}

openMemBtn?.addEventListener('click', async () => {
  memPanel.hidden = false;
  memFilterEntityEl.value = currentEntity || '';
  try { await refreshMemList(); } catch (e) { /* ignore */ }
});

closeMemBtn?.addEventListener('click', () => {
  memPanel.hidden = true;
});

refreshMemBtn?.addEventListener('click', async () => {
  try { await refreshMemList(); } catch (e) { alert(e.message); }
});

addMemBtn?.addEventListener('click', async () => {
  const text = (memTextEl.value || '').trim() || lastAssistantText || '';
  if (!text) { alert('Nothing to save.'); return; }
  const body = {
    text,
    importance: parseInt(memImportanceEl.value || '3', 10) || 3,
  };
  // If entity-scoped, use currentEntity or filterEntity
  if (memEntityScopedEl.checked) {
    const scopeEntity = (entityInput?.value || memFilterEntityEl?.value || '').trim();
    if (scopeEntity) body.entity = scopeEntity;
  }
  addMemBtn.disabled = true;
  try {
    const res = await fetch('/api/memory', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
    const data = await res.json();
    if (!res.ok || data.error) throw new Error(data.error || `HTTP ${res.status}`);
    memTextEl.value = '';
    await refreshMemList();
  } catch (e) {
    alert(`Add failed: ${e.message}`);
  } finally {
    addMemBtn.disabled = false;
  }
});
