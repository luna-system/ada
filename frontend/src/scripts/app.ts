// Globals provided via scripts in BaseLayout
/* eslint-disable @typescript-eslint/no-explicit-any */
declare const marked: any;
declare const DOMPurify: any;
declare const hljs: any;

type StreamMessage =
  | { type: 'token'; content: string }
  | { type: 'thinking'; content: string }
  | { type: 'done'; conversation_id?: string }
  | { type: 'error'; error?: string };

type Nullable<T> = T | null;

const messagesEl = document.getElementById('messages') as HTMLDivElement;
const healthDot = document.querySelector('header .brand .dot') as Nullable<HTMLElement>;
const form = document.getElementById('composer') as HTMLFormElement;
const input = document.getElementById('prompt') as HTMLTextAreaElement;
const includeThinkingEl = document.getElementById('includeThinking') as HTMLInputElement;
const entityInput = document.getElementById('entity') as Nullable<HTMLInputElement>;
const panelMenuBtn = document.getElementById('panelMenuButton') as Nullable<HTMLButtonElement>;
const panelMenu = document.getElementById('panelMenu') as Nullable<HTMLDivElement>;
const debugPanel = document.getElementById('debugPanel') as Nullable<HTMLDivElement>;
const closeDebugBtn = document.getElementById('closeDebug') as Nullable<HTMLButtonElement>;
const memPanel = document.getElementById('memPanel') as Nullable<HTMLDivElement>;
const closeMemBtn = document.getElementById('closeMem') as Nullable<HTMLButtonElement>;
const refreshMemBtn = document.getElementById('refreshMem') as Nullable<HTMLButtonElement>;
const memListEl = document.getElementById('memList') as HTMLDivElement;
const memFilterEntityEl = document.getElementById('memFilterEntity') as HTMLInputElement;
const addMemBtn = document.getElementById('addMem') as Nullable<HTMLButtonElement>;
const memTextEl = document.getElementById('memText') as HTMLTextAreaElement;
const memImportanceEl = document.getElementById('memImportance') as HTMLSelectElement;
const memEntityScopedEl = document.getElementById('memEntityScoped') as Nullable<HTMLInputElement>;
const memEntityRow = document.getElementById('memEntityRow') as Nullable<HTMLLabelElement>;
const memEntityInput = document.getElementById('memEntityInput') as Nullable<HTMLInputElement>;
const refreshStatusBtn = document.getElementById('refreshStatus') as Nullable<HTMLButtonElement>;
const statusBoxEl = document.getElementById('statusBox') as Nullable<HTMLDivElement>;
const clientLibsEl = document.getElementById('clientLibs') as Nullable<HTMLDivElement>;
const refreshClientLibsBtn = document.getElementById('refreshClientLibs') as Nullable<HTMLButtonElement>;

let thinkingEl: Nullable<HTMLDivElement> = null;
let lastAssistantText = '';
let conversationId: string | null = localStorage.getItem('conversation_id');

if (!conversationId && window.crypto && crypto.randomUUID) {
  conversationId = crypto.randomUUID();
  localStorage.setItem('conversation_id', conversationId);
}

let currentEntity = localStorage.getItem('entity') || '';
if (entityInput) {
  entityInput.value = currentEntity;
  entityInput.addEventListener('change', () => {
    currentEntity = entityInput.value.trim();
    localStorage.setItem('entity', currentEntity);
  });
}

function hidePanels() {
  if (memPanel) memPanel.hidden = true;
  if (debugPanel) debugPanel.hidden = true;
}

function hideMenu() {
  if (panelMenu) panelMenu.hidden = true;
  if (panelMenuBtn) panelMenuBtn.setAttribute('aria-expanded', 'false');
}

function wireEntityToggle() {
  if (!memEntityScopedEl) return;
  if (memEntityRow) memEntityRow.hidden = !memEntityScopedEl.checked;
  memEntityScopedEl.addEventListener('change', () => {
    if (!memEntityRow) return;
    memEntityRow.hidden = !memEntityScopedEl.checked;
    if (memEntityScopedEl.checked && memEntityInput) {
      const scopeEntity = (entityInput?.value || memFilterEntityEl?.value || '').trim();
      memEntityInput.value = scopeEntity;
      memEntityInput.focus();
    }
  });
}

function attachSaveMemoryButton(stackEl: HTMLElement, text: string) {
  if (!stackEl || !text) return;
  const btn = document.createElement('button');
  btn.className = 'ghost save-mem';
  btn.type = 'button';
  btn.textContent = 'Save to memory';
  btn.addEventListener('click', () => {
    if (memTextEl) memTextEl.value = text;
    if (memFilterEntityEl) memFilterEntityEl.value = currentEntity || '';
    if (memEntityInput) memEntityInput.value = currentEntity || '';
    if (memEntityScopedEl) memEntityScopedEl.checked = !!currentEntity;
    if (memEntityRow) memEntityRow.hidden = !(memEntityScopedEl?.checked ?? false);
    hidePanels();
    hideMenu();
    if (memPanel) memPanel.hidden = false;
  });
  stackEl.appendChild(btn);
}

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

refreshHealth();
setInterval(refreshHealth, 10000);

function addMessage(role: 'me' | 'bot', text: string) {
  const wrap = document.createElement('div');
  wrap.className = `msg ${role}`;

  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.textContent = role === 'me' ? '🧑' : '🤖';

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
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

function replaceThinkingWithBot(text: string) {
  const wrap = document.createElement('div');
  wrap.className = 'msg bot';

  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.textContent = '🤖';

  const stack = document.createElement('div');
  stack.className = 'stack';

  const thinkMatch = /<think>([\s\S]*?)<\/think>([\s\S]*)/i.exec(text || '');
  if (includeThinkingEl.checked && thinkMatch) {
    const thinkDetails = document.createElement('details');
    thinkDetails.className = 'bubble think';

    const summary = document.createElement('summary');
    summary.textContent = 'Thinking';

    const content = document.createElement('div');
    content.className = 'think-content';
    renderMarkdownToElement(content, (thinkMatch[1] || '').trim(), { allowBlocks: true });

    thinkDetails.appendChild(summary);
    thinkDetails.appendChild(content);
    stack.appendChild(thinkDetails);

    const answerBubble = document.createElement('div');
    answerBubble.className = 'bubble answer';
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

  lastAssistantText = (thinkMatch ? (thinkMatch[2] || '') : (text || '')).trim();
  attachSaveMemoryButton(stack, lastAssistantText);
}

function renderMarkdownToElement(el: HTMLElement, markdownText: string, options: { allowBlocks?: boolean } = { allowBlocks: false }) {
  const { allowBlocks = false } = options || {};
  if (!el) return;
  const md = String(markdownText || '');
  try {
    const fencedRegex = /(^|\n)```(\w+)?\n([\s\S]*?)\n```/m;
    const hasFenced = fencedRegex.test(md);
    const otherBlockRegex = /(^|\n)( {4,}|\#{1,6}\s+|>\s+|[-*+]\s+|\d+\.\s+)/m;
    const hasOtherBlocks = otherBlockRegex.test(md);
    let rawHtml: string;

    if (allowBlocks) {
      if (typeof marked !== 'undefined' && typeof marked.parse === 'function') {
        try {
          if (typeof hljs !== 'undefined' && typeof hljs.highlight !== 'undefined') {
            marked.setOptions({
              highlight: function (code: string, lang: string) {
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
      if (typeof marked !== 'undefined' && typeof marked.parse === 'function') {
        try {
          if (typeof hljs !== 'undefined' && typeof hljs.highlight !== 'undefined') {
            marked.setOptions({
              highlight: function (code: string, lang: string) {
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
      if (typeof marked !== 'undefined' && typeof marked.parseInline === 'function') {
        rawHtml = marked.parseInline(md);
      } else if (typeof marked !== 'undefined' && typeof marked.parse === 'function') {
        rawHtml = marked.parse(md);
        rawHtml = rawHtml.replace(/^<p>([\s\S]*)<\/p>\s*$/i, '$1');
      } else {
        rawHtml = md.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>');
      }
    } else {
      rawHtml = md.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>');
    }

    const sanitizeConfig = typeof DOMPurify !== 'undefined'
      ? (allowBlocks
        ? {
            ALLOWED_TAGS: ['a','b','i','strong','em','del','code','pre','p','br','ul','ol','li','span','h1','h2','h3','h4','h5','h6','blockquote','img'],
            ALLOWED_ATTR: ['href','title','class','src','alt']
          }
        : {
            ALLOWED_TAGS: ['a','b','i','strong','em','code','pre','p','br','ul','ol','li','span'],
            ALLOWED_ATTR: ['href','title','class']
          })
      : undefined;
    const clean = typeof DOMPurify !== 'undefined' ? DOMPurify.sanitize(rawHtml, sanitizeConfig) : rawHtml;
    el.innerHTML = clean;

    const anchors = el.querySelectorAll('a');
    anchors.forEach((a) => {
      a.setAttribute('target', '_blank');
      a.setAttribute('rel', 'noopener noreferrer');
    });

    if (typeof hljs !== 'undefined' && typeof hljs.highlightElement === 'function') {
      el.querySelectorAll('pre code').forEach((codeEl) => {
        try { hljs.highlightElement(codeEl as HTMLElement); } catch (e) { /* ignore */ }
      });
    }
  } catch (e) {
    el.textContent = markdownText;
  }
}

function setBusy(busy: boolean) {
  form.querySelectorAll('textarea,button').forEach((el) => ((el as HTMLInputElement).disabled = busy));
  messagesEl.setAttribute('aria-busy', String(busy));
  if (busy) showThinking(); else hideThinking();
}

input.addEventListener('keydown', (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});

form.addEventListener('submit', async (e: SubmitEvent) => {
  e.preventDefault();
  const prompt = input.value.trim();
  if (!prompt) return;

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
        const lines = items.map((it: any) => {
          const meta = it.meta || {};
          const imp = meta.importance != null ? ` (importance=${meta.importance})` : '';
          const id = it.id ? `id=${it.id}` : '';
          return `• ${id}${imp} ${it.text}`;
        });
        addMessage('bot', `Memories:\n${lines.join('\n')}`);
      }
    } catch (err: any) {
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
      } catch (err: any) {
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
    const res = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt,
        include_thinking: !!includeThinkingEl.checked,
        conversation_id: conversationId,
        entity: currentEntity || undefined
      })
    });

    if (!res.ok) {
      throw new Error(`Request failed: ${res.status}`);
    }

    hideThinking();

    const wrap = document.createElement('div');
    wrap.className = 'msg bot';

    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = '🤖';

    const stack = document.createElement('div');
    stack.className = 'stack';

    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    spinner.setAttribute('aria-hidden', 'true');
    spinner.title = 'Generating...';
    stack.appendChild(spinner);

    wrap.appendChild(avatar);
    wrap.appendChild(stack);
    messagesEl.appendChild(wrap);
    messagesEl.scrollTop = messagesEl.scrollHeight;

    let thinkDetailsEl: Nullable<HTMLDetailsElement> = null;
    let thinkContentEl: Nullable<HTMLDivElement> = null;
    let answerBubbleEl: Nullable<HTMLDivElement> = null;
    let spinnerRef: Nullable<HTMLDivElement> = spinner;

    let accumulatedText = '';
    let accumulatedThinking = '';

    const reader = res.body?.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (reader) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() ?? '';

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const dataStr = line.slice(6);
        try {
          const data = JSON.parse(dataStr) as StreamMessage;

          if (data.type === 'token') {
            if (spinnerRef && spinnerRef.parentNode) {
              spinnerRef.remove();
              spinnerRef = null;
            }

            if (!answerBubbleEl) {
              answerBubbleEl = document.createElement('div');
              answerBubbleEl.className = 'bubble answer';
              stack.appendChild(answerBubbleEl);
            }

            accumulatedText += data.content;
            renderMarkdownToElement(answerBubbleEl, accumulatedText, { allowBlocks: true });
            messagesEl.scrollTop = messagesEl.scrollHeight;
          } else if (data.type === 'thinking' && includeThinkingEl.checked) {
            if (spinnerRef && spinnerRef.parentNode) {
              spinnerRef.remove();
              spinnerRef = null;
            }

            if (!thinkDetailsEl) {
              thinkDetailsEl = document.createElement('details');
              thinkDetailsEl.className = 'bubble think';
              thinkDetailsEl.open = true;

              const summary = document.createElement('summary');
              summary.textContent = 'Thinking';
              thinkDetailsEl.appendChild(summary);

              thinkContentEl = document.createElement('div');
              thinkContentEl.className = 'think-content';
              thinkDetailsEl.appendChild(thinkContentEl);

              if (answerBubbleEl) {
                stack.insertBefore(thinkDetailsEl, answerBubbleEl);
              } else {
                stack.appendChild(thinkDetailsEl);
              }
            }

            accumulatedThinking += data.content;
            if (thinkContentEl) {
              renderMarkdownToElement(thinkContentEl, accumulatedThinking, { allowBlocks: true });
            }
            messagesEl.scrollTop = messagesEl.scrollHeight;
          } else if (data.type === 'done') {
            if (data.conversation_id && data.conversation_id !== conversationId) {
              conversationId = data.conversation_id;
              localStorage.setItem('conversation_id', conversationId);
            }
            lastAssistantText = accumulatedText;
          } else if (data.type === 'error') {
            throw new Error(data.error || 'Stream error');
          }
        } catch (err) {
          console.error('Error parsing SSE data:', err);
        }
      }
    }

    if (thinkContentEl && accumulatedThinking) {
      renderMarkdownToElement(thinkContentEl, accumulatedThinking, { allowBlocks: true });
    }
    if (answerBubbleEl && accumulatedText) {
      renderMarkdownToElement(answerBubbleEl, accumulatedText, { allowBlocks: true });
    }
    messagesEl.scrollTop = messagesEl.scrollHeight;

    attachSaveMemoryButton(stack, accumulatedText.trim());

    if (spinnerRef && spinnerRef.parentNode) {
      spinnerRef.remove();
    }
  } catch (err: any) {
    console.error(err);
    replaceThinkingWithBot(`Error: ${err.message}`);
  } finally {
    setBusy(false);
    input.focus();
  }
});

addMessage('bot', 'Hello! Ask me anything.');
if (typeof window !== 'undefined') {
  window.addEventListener('DOMContentLoaded', updateClientLibStatus);
}
input.focus();

function renderStatusBox(data: any) {
  if (!statusBoxEl) return;
  try {
    const ok = !!data.ok;
    const parts: string[] = [];
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
  } catch (e: any) {
    statusBoxEl.textContent = `Status error: ${e.message}`;
    statusBoxEl.classList.add('bad');
  }
}

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

refreshClientLibsBtn?.addEventListener('click', () => {
  updateClientLibStatus();
});

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
function renderMemList(items: any[]) {
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
        } catch (e: any) {
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

closeMemBtn?.addEventListener('click', () => {
  hidePanels();
});

closeDebugBtn?.addEventListener('click', () => {
  hidePanels();
});

panelMenuBtn?.addEventListener('click', () => {
  if (!panelMenu) return;
  const willOpen = !!panelMenu.hidden;
  panelMenu.hidden = !willOpen;
  panelMenuBtn.setAttribute('aria-expanded', String(willOpen));
});

panelMenu?.addEventListener('click', async (e) => {
  const target = e.target;
  if (!(target instanceof HTMLElement)) return;
  const which = target.getAttribute('data-target');
  if (which === 'debug') {
    hidePanels();
    hideMenu();
    if (debugPanel) debugPanel.hidden = false;
    try { await refreshStatusPanel(); } catch (err) { /* ignore */ }
    try { updateClientLibStatus(); } catch (err) { /* ignore */ }
  } else if (which === 'mem') {
    hidePanels();
    hideMenu();
    if (memPanel) {
      memPanel.hidden = false;
      memFilterEntityEl.value = currentEntity || '';
      try { await refreshMemList(); } catch (err) { /* ignore */ }
    }
  }
});

document.addEventListener('click', (e) => {
  if (!panelMenu || !panelMenuBtn) return;
  if (panelMenu.hidden) return;
  const inside = panelMenu.contains(e.target as Node) || panelMenuBtn.contains(e.target as Node);
  if (!inside) hideMenu();
});

refreshMemBtn?.addEventListener('click', async () => {
  try { await refreshMemList(); } catch (e: any) { alert(e.message); }
});

refreshStatusBtn?.addEventListener('click', async () => {
  try { await refreshStatusPanel(); } catch (e: any) { alert(e.message); }
});

addMemBtn?.addEventListener('click', async () => {
  const text = (memTextEl.value || '').trim() || lastAssistantText || '';
  if (!text) { alert('Nothing to save.'); return; }
  const body: Record<string, any> = {
    text,
    importance: parseInt(memImportanceEl.value || '3', 10) || 3,
  };
  if (memEntityScopedEl?.checked) {
    const scopeEntity = (memEntityInput?.value || entityInput?.value || memFilterEntityEl?.value || '').trim();
    if (scopeEntity) body.entity = scopeEntity;
  }
  if (addMemBtn) addMemBtn.disabled = true;
  try {
    const res = await fetch('/api/memory', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
    const data = await res.json();
    if (!res.ok || data.error) throw new Error(data.error || `HTTP ${res.status}`);
    memTextEl.value = '';
    if (memEntityInput) memEntityInput.value = '';
    if (memEntityScopedEl) memEntityScopedEl.checked = false;
    if (memEntityRow) memEntityRow.hidden = true;
    await refreshMemList();
  } catch (e: any) {
    alert(`Add failed: ${e.message}`);
  } finally {
    if (addMemBtn) addMemBtn.disabled = false;
  }
});

wireEntityToggle();

export {};
