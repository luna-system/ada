const messagesEl = document.getElementById('messages');
const healthDot = document.querySelector('header .brand .dot');
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
const refreshStatusBtn = document.getElementById('refreshStatus');
const statusBoxEl = document.getElementById('statusBox');
const clientLibsEl = document.getElementById('clientLibs');
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

// --- Health indicator ---
async function refreshHealth() {
  if (!healthDot) return;
  try {
    const res = await fetch('/api/health', { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const ok = !!data.ok;
    healthDot.classList.toggle('ok', ok);
    healthDot.classList.toggle('bad', !ok);
    healthDot.title = ok ? 'Brain: healthy' : 'Brain: unavailable';
    healthDot.setAttribute('aria-label', healthDot.title);
  } catch (err) {
    healthDot.classList.remove('ok');
    healthDot.classList.add('bad');
    healthDot.title = 'Brain: unavailable';
    healthDot.setAttribute('aria-label', healthDot.title);
  }
}

// Kick off periodic health checks
refreshHealth();
setInterval(refreshHealth, 10000);

function addMessage(role, text) {
  const wrap = document.createElement('div');
  wrap.className = `msg ${role}`;

  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.textContent = role === 'me' ? '🧑' : '🤖';

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  // Render markdown into the bubble (sanitized via DOMPurify)
  // Always render full markdown for all messages.
  renderMarkdownToElement(bubble, String(text || ''), { allowBlocks: true });

  wrap.appendChild(avatar);
  wrap.appendChild(bubble);
  messagesEl.appendChild(wrap);
  messagesEl.scrollTo({ top: messagesEl.scrollHeight, behavior: 'smooth' });
  updateClientLibStatus();
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
    // Render thinking content with full markdown as well
    renderMarkdownToElement(content, (thinkMatch[1] || '').trim(), { allowBlocks: true });

    thinkDetails.appendChild(summary);
    thinkDetails.appendChild(content);
    stack.appendChild(thinkDetails);

    const answerBubble = document.createElement('div');
    answerBubble.className = 'bubble answer';
    // Allow the assistant's final answers to render full block markdown (headers, lists, code fences)
    renderMarkdownToElement(answerBubble, (thinkMatch[2] || '').trim(), { allowBlocks: true });
    stack.appendChild(answerBubble);
  } else {
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    renderMarkdownToElement(bubble, (thinkMatch ? (thinkMatch[2] || '') : (text || '')) || '', { allowBlocks: true });
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

// Convert a markdown string to sanitized HTML and set it inside an element
// Uses 'marked' to convert markdown -> HTML and 'DOMPurify' to sanitize.
function renderMarkdownToElement(el, markdownText, options = { allowBlocks: false }) {
  const { allowBlocks = false } = options || {};
  if (!el) return;
  const md = String(markdownText || '');
  try {
    // Detect if there are fenced code blocks. If allowBlocks is true we will allow
    // all block-level markdown; otherwise, only inline markup with optional code fences
    // is supported.
    const fencedRegex = /(^|\n)```(\w+)?\n([\s\S]*?)\n```/m;
    const hasFenced = fencedRegex.test(md);
    if (typeof console !== 'undefined' && console.debug) console.debug('renderMarkdownToElement: hasFenced=', hasFenced, 'mdSnippet=', md.slice(0, 200));
    // Detect other block-level elements (excluding fenced code blocks)
    const otherBlockRegex = /(^|\n)( {4,}|\#{1,6}\s+|>\s+|[-*+]\s+|\d+\.\s+)/m;
    if (typeof console !== 'undefined' && console.debug) console.debug('renderMarkdownToElement: hasOtherBlocks=', otherBlockRegex.test(md));
    const hasOtherBlocks = otherBlockRegex.test(md);
    let rawHtml;

    if (allowBlocks) {
      // Allow full markdown rendering when explicitly requested (e.g., for bot messages)
      if (typeof marked !== 'undefined' && typeof marked.parse === 'function') {
        try {
          if (typeof hljs !== 'undefined' && typeof hljs.highlight !== 'undefined') {
            marked.setOptions({
              highlight: function(code, lang) {
                try {
                  if (lang && hljs.getLanguage(lang)) {
                    return hljs.highlight(code, { language: lang }).value;
                  }
                  return hljs.highlightAuto(code).value;
                } catch (e) {
                  return code;
                }
              }
            });
          }
          rawHtml = marked.parse(md);
        } catch (e) {
          rawHtml = md.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>');
        }
      } else {
        rawHtml = md.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>');
      }
    } else if (hasFenced && !hasOtherBlocks) {
      // We allow fenced code blocks plus inline content and paragraphs; use marked.parse
      // with a highlight function if highlight.js is available.
      if (typeof marked !== 'undefined' && typeof marked.parse === 'function') {
        try {
          // Configure highlight function for marked
          if (typeof hljs !== 'undefined' && typeof hljs.highlight !== 'undefined') {
            marked.setOptions({
              highlight: function(code, lang) {
                try {
                  if (lang && hljs.getLanguage(lang)) {
                    return hljs.highlight(code, { language: lang }).value;
                  }
                  return hljs.highlightAuto(code).value;
                } catch (e) {
                  return code;
                }
              }
            });
          }
          rawHtml = marked.parse(md);
        } catch (e) {
          rawHtml = md.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>');
        }
      } else {
        rawHtml = md.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>');
      }
    } else if (!hasOtherBlocks) {
      // No block-level content other than potential inline markdown -> parse inline
      if (typeof marked !== 'undefined' && typeof marked.parseInline === 'function') {
        rawHtml = marked.parseInline(md);
      } else if (typeof marked !== 'undefined' && typeof marked.parse === 'function') {
        rawHtml = marked.parse(md);
        rawHtml = rawHtml.replace(/^<p>([\s\S]*)<\/p>\s*$/i, '$1');
      } else {
        rawHtml = md.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>');
      }
    } else {
      // Has block-level constructs we don't render; escape and keep newlines
      rawHtml = md.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>');
    }
    // Sanitize and set the HTML
    // Sanitize and allow limited tags including <pre> and <code> for code blocks
    const sanitizeConfig = (typeof DOMPurify !== 'undefined') ? (
      allowBlocks ? {
        ALLOWED_TAGS: ['a','b','i','strong','em','del','code','pre','p','br','ul','ol','li','span','h1','h2','h3','h4','h5','h6','blockquote','img'],
        ALLOWED_ATTR: ['href','title','class','src','alt']
      } : {
        ALLOWED_TAGS: ['a','b','i','strong','em','code','pre','p','br','ul','ol','li','span'],
        ALLOWED_ATTR: ['href','title','class']
      }
    ) : undefined;
    const clean = (typeof DOMPurify !== 'undefined') ? DOMPurify.sanitize(rawHtml, sanitizeConfig) : rawHtml;
    el.innerHTML = clean;
    // Force external links to open safely in a new tab
    const anchors = el.querySelectorAll('a');
    anchors.forEach(a => {
      a.setAttribute('target', '_blank');
      a.setAttribute('rel', 'noopener noreferrer');
    });

    // Run syntax highlighting on any code blocks if highlight.js loaded
    if (typeof hljs !== 'undefined' && typeof hljs.highlightElement === 'function') {
      el.querySelectorAll('pre code').forEach((codeEl) => {
        try { hljs.highlightElement(codeEl); } catch (e) { /* ignore */ }
      });
    }
  } catch (e) {
    // Fallback to plain text if anything goes wrong
    el.textContent = markdownText;
  }
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
// Update client libs status once when DOM content is ready in case scripts loaded after run
if (typeof window !== 'undefined') {
  window.addEventListener('DOMContentLoaded', updateClientLibStatus);
}
input.focus();

// --- Memories panel wiring ---
function renderStatusBox(data) {
  if (!statusBoxEl) return;
  try {
    const ok = !!data.ok;
    const parts = [];
    parts.push(`Brain: ${ok ? 'healthy' : 'unavailable'}`);
    if (data.python) parts.push(`Python: ${data.python}`);
    if (data.config) {
      if (data.config.OLLAMA_MODEL) parts.push(`Model: ${data.config.OLLAMA_MODEL}`);
      if (data.config.OLLAMA_BASE_URL) parts.push(`Ollama: ${data.config.OLLAMA_BASE_URL}`);
      if (data.config.CHROMA_URL) parts.push(`Chroma: ${data.config.CHROMA_URL}`);
    }
    if (data.persona && typeof data.persona.loaded !== 'undefined') {
      parts.push(`Persona: ${data.persona.loaded ? 'loaded' : 'missing'}`);
    }
    if (data.chroma) {
      const cOK = data.chroma.ok;
      parts.push(`Chroma heartbeat: ${cOK === null ? 'n/a' : (cOK ? 'ok' : 'fail')}`);
    }
    statusBoxEl.textContent = parts.join(' \u2022 ');
    statusBoxEl.classList.toggle('bad', !ok);
  } catch (e) {
    statusBoxEl.textContent = `Status error: ${e.message}`;
    statusBoxEl.classList.add('bad');
  }
}

// Reflect presence/absence of client-side libraries into the small header status
function updateClientLibStatus() {
  if (!clientLibsEl) return;
  const libs = [
    ['marked', typeof marked !== 'undefined'],
    ['DOMPurify', typeof DOMPurify !== 'undefined'],
    ['hljs', typeof hljs !== 'undefined']
  ];
  clientLibsEl.textContent = libs.map(([n, ok]) => `${n}:${ok ? '✓' : '✕'}`).join(' ');
  if (typeof console !== 'undefined' && console.debug) console.debug('Client libs:', libs);
}

async function refreshStatusPanel() {
  if (!statusBoxEl) return;
  statusBoxEl.textContent = 'Loading…';
  statusBoxEl.classList.remove('bad');
  try {
    const res = await fetch('/api/health', { cache: 'no-store' });
    const data = await res.json();
    renderStatusBox(data);
  } catch (e) {
    renderStatusBox({ ok: false });
  }
}
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
  try { await refreshStatusPanel(); } catch (e) { /* ignore */ }
});

closeMemBtn?.addEventListener('click', () => {
  memPanel.hidden = true;
});

refreshMemBtn?.addEventListener('click', async () => {
  try { await refreshMemList(); } catch (e) { alert(e.message); }
});

refreshStatusBtn?.addEventListener('click', async () => {
  try { await refreshStatusPanel(); } catch (e) { alert(e.message); }
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
