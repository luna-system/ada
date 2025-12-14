<script lang="ts">
  import { onMount, afterUpdate } from 'svelte';
  import { get } from 'svelte/store';
  import {
    messages,
    thinking,
    ensureConversationId,
    setConversationId,
    setThinking,
    pushMessage,
    updateMessage,
    type Message,
    type Role
  } from '../stores/chat';
  import { memList, memLoading, memError, fetchMemories, addMemoryItem, deleteMemoryItem } from '../stores/memory';
  type StreamMessage =
    | { type: 'token'; content: string }
    | { type: 'thinking'; content: string }
    | { type: 'done'; conversation_id?: string }
    | { type: 'error'; error?: string };

  const uuid = () => crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2);

  let prompt = '';
  let includeThinking = false;
  let entity = '';
  let panelOpen: 'none' | 'debug' | 'mem' = 'none';
  let menuOpen = false;

  // Status & client libs
  let health: string = 'Loading…';
  let healthOk: boolean | null = null;
  let clientLibs = '';

  // Memory panel state
  let memFilter = '';
  let memText = '';
  let memImportance = 3;
  let memEntityScoped = false;
  let memEntity = '';

  let messagesContainer: HTMLElement | null = null;

  function scrollMessages() {
    if (!messagesContainer) return;
    const el = messagesContainer;
    requestAnimationFrame(() => {
      try {
        el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
      } catch {
        /* ignore */
      }
    });
  }

  afterUpdate(scrollMessages);

  onMount(() => {
    ensureConversationId(uuid);
    const storedEntity = localStorage.getItem('entity') || '';
    entity = storedEntity;
    refreshHealth();
    updateClientLibStatus();
    refreshMemList();
  });

  async function refreshHealth() {
    try {
      const res = await fetch('/api/health', { cache: 'no-store' });
      const data = await res.json();
      healthOk = !!data.ok;
      const parts: string[] = [];
      parts.push(`Brain: ${data.ok ? 'healthy' : 'unavailable'}`);
      if (data.python) parts.push(`Python: ${data.python}`);
      if (data.config) {
        if (data.config.OLLAMA_MODEL) parts.push(`Model: ${data.config.OLLAMA_MODEL}`);
        if (data.config.OLLAMA_BASE_URL) parts.push(`Ollama: ${data.config.OLLAMA_BASE_URL}`);
      }
      if (data.persona && typeof data.persona.loaded !== 'undefined') {
        parts.push(`Persona: ${data.persona.loaded ? 'loaded' : 'missing'}`);
      }
      health = parts.join(' • ');
    } catch (e) {
      healthOk = false;
      health = 'Brain: unavailable';
    }
  }

  function updateClientLibStatus() {
    const libs: [string, boolean][] = [
      ['marked', typeof (window as any).marked !== 'undefined'],
      ['DOMPurify', typeof (window as any).DOMPurify !== 'undefined'],
      ['hljs', typeof (window as any).hljs !== 'undefined']
    ];
    clientLibs = libs.map(([n, ok]) => `${n}:${ok ? '✓' : '✕'}`).join(' ');
  }

  function renderMarkdown(md: string, allowBlocks = true): string {
    try {
      const marked = (window as any).marked;
      const DOMPurify = (window as any).DOMPurify;
      const hljs = (window as any).hljs;
      let raw = md;
      if (allowBlocks && marked?.parse) {
        if (hljs) {
          marked.setOptions({
            highlight: function (code: string, lang: string) {
              try {
                if (lang && hljs.getLanguage(lang)) return hljs.highlight(code, { language: lang }).value;
                return hljs.highlightAuto(code).value;
              } catch {
                return code;
              }
            }
          });
        }
        raw = marked.parse(md);
      } else if (marked?.parseInline) {
        raw = marked.parseInline(md);
      } else {
        raw = md.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>');
      }
      return DOMPurify ? DOMPurify.sanitize(raw) : raw;
    } catch {
      return md;
    }
  }

  function togglePanel(which: 'debug' | 'mem') {
    panelOpen = panelOpen === which ? 'none' : which;
    menuOpen = false;
    if (which === 'debug') {
      refreshHealth();
      updateClientLibStatus();
    }
    if (which === 'mem') {
      refreshMemList();
      memEntity = entity || memEntity;
    }
  }

  function onEntityChange(val: string) {
    entity = val;
    localStorage.setItem('entity', entity);
  }

  async function handleSubmit() {
    const text = prompt.trim();
    if (!text) return;
    pushMessage({ id: uuid(), role: 'user', text });
    prompt = '';
    await streamReply(text);
  }

  async function streamReply(userText: string) {
    setThinking(true);
    let answerId = uuid();
    let assistantText = '';
    let thinkingText = '';
    pushMessage({ id: answerId, role: 'assistant', text: '' });

    const convId = ensureConversationId(uuid);
    let activeConversationId = convId;

    try {
      const res = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: userText,
          include_thinking: includeThinking,
          conversation_id: activeConversationId,
          entity: entity || undefined
        })
      });
      if (!res.body) throw new Error('No response body');
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const dataStr = line.slice(6);
          let data: StreamMessage;
          try { data = JSON.parse(dataStr); } catch { continue; }
          if (data.type === 'token') {
            assistantText += data.content;
          } else if (data.type === 'thinking' && includeThinking) {
            thinkingText += data.content;
          } else if (data.type === 'done') {
            if (data.conversation_id && data.conversation_id !== activeConversationId) {
              activeConversationId = data.conversation_id;
              setConversationId(activeConversationId);
            }
          } else if (data.type === 'error') {
            throw new Error(data.error || 'Stream error');
          }
          updateMessage(answerId, { text: assistantText, thinking: thinkingText });
        }
      }
    } catch (e: any) {
      updateMessage(answerId, { text: `Error: ${e.message || e}` });
    } finally {
      setThinking(false);
    }
  }

  async function refreshMemList() {
    await fetchMemories(memFilter);
  }

  async function addMemory() {
    const lastAssistant = (() => {
      const list = get(messages);
      for (let i = list.length - 1; i >= 0; i -= 1) {
        if (list[i].role === 'assistant') return list[i];
      }
      return undefined;
    })();
    const text = (memText || lastAssistant?.text || '').trim();
    if (!text) return alert('Nothing to save.');
    const body: Record<string, any> = { text, importance: memImportance };
    if (memEntityScoped && memEntity.trim()) body.entity = memEntity.trim();
    try {
      await addMemoryItem(body);
      memText = '';
      memEntity = '';
      memEntityScoped = false;
      await refreshMemList();
    } catch (e:any) {
      alert(`Add failed: ${e.message}`);
    }
  }

  async function deleteMemory(id: string) {
    try {
      await deleteMemoryItem(id);
      await refreshMemList();
    } catch (e:any) {
      alert(`Delete failed: ${e.message}`);
    }
  }

  function openSaveToMemory(text: string) {
    panelOpen = 'mem';
    memText = text;
    memEntity = entity || memEntity;
    menuOpen = false;
  }
</script>

<svelte:window on:click={(e) => {
  const menuEl = document.getElementById('panelMenu');
  const btnEl = document.getElementById('panelMenuButton');
  if (!menuEl || !btnEl) return;
  if (!menuOpen) return;
  if (menuEl.contains(e.target as Node) || btnEl.contains(e.target as Node)) return;
  menuOpen = false;
}} />

<div class="app">
  <header>
    <div class="brand">
      <div class="dot {healthOk === true ? 'ok' : healthOk === false ? 'bad' : ''}" aria-hidden="true"></div>
      <h1>ADA · Chat</h1>
    </div>
    <div class="grow"></div>
    <label class="field" title="Optional entity/topic to scope memory">
      <span>Entity</span>
      <input value={entity} on:input={(e) => onEntityChange((e.target as HTMLInputElement).value)} placeholder="entity/topic (optional)" />
    </label>
    <label class="toggle" title="Show model's thinking (<think>…</think>)">
      <span>Include thinking</span>
      <span class="switch">
        <input type="checkbox" bind:checked={includeThinking} />
        <span class="knob"></span>
      </span>
    </label>
    <div class="menu" id="panelMenu">
      <button id="panelMenuButton" class="ghost" type="button" aria-haspopup="true" aria-expanded={menuOpen} on:click={() => menuOpen = !menuOpen}>Panels ▾</button>
      {#if menuOpen}
        <div class="menu-list">
          <button type="button" class="menu-item" on:click={() => togglePanel('debug')}>Debug</button>
          <button type="button" class="menu-item" on:click={() => togglePanel('mem')}>Memories</button>
        </div>
      {/if}
    </div>
  </header>

  <main id="messages" bind:this={messagesContainer} aria-live="polite" aria-busy={$thinking}>
    {#each $messages as m}
      <div class={`msg ${m.role === 'user' ? 'me' : 'bot'}`}>
        <div class="avatar">{m.role === 'user' ? '🧑' : '🤖'}</div>
        <div class="stack">
          {#if m.thinking && includeThinking}
            <details class="bubble think" open>
              <summary>Thinking</summary>
              <div class="think-content">{@html renderMarkdown(m.thinking || '', true)}</div>
            </details>
          {/if}
          <div class={`bubble ${m.role === 'assistant' ? 'answer' : ''}`}>{@html renderMarkdown(m.text || '', true)}</div>
          {#if m.role === 'assistant'}
            <button class="ghost save-mem" type="button" on:click={() => openSaveToMemory(m.text)}>Save to memory</button>
          {/if}
        </div>
      </div>
    {/each}
    {#if $thinking}
      <div class="msg thinking"><div class="spinner" aria-hidden="true" title="Thinking..."></div></div>
    {/if}
  </main>
  <div class="hint">Press Enter to send, Shift+Enter for newline</div>

  <form id="composer" on:submit|preventDefault={handleSubmit}>
    <textarea bind:value={prompt} placeholder="Type your message..." autocomplete="off" on:keydown={(e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    }}></textarea>
    <button type="submit" disabled={thinking}>Send</button>
  </form>

  {#if panelOpen === 'debug'}
    <aside class="panel" id="debugPanel">
      <div class="panel-header">
        <strong>Debug</strong>
        <button class="icon" type="button" aria-label="Close" on:click={() => panelOpen = 'none'}>✕</button>
      </div>
      <div class="panel-body">
        <div class="panel-status">
          <div class="row" style="justify-content: space-between;">
            <strong>Status</strong>
            <button class="ghost" type="button" title="Refresh health" on:click={refreshHealth}>Refresh</button>
          </div>
          <div class={`status-box muted ${healthOk === false ? 'bad' : ''}`} aria-live="polite">{health}</div>
        </div>
        <div class="panel-status">
          <div class="row" style="justify-content: space-between;">
            <strong>Client libraries</strong>
            <button class="ghost" type="button" title="Refresh client libraries" on:click={updateClientLibStatus}>Refresh</button>
          </div>
          <div class="status-box muted" aria-live="polite">{clientLibs || 'Loading…'}</div>
        </div>
      </div>
    </aside>
  {/if}

  {#if panelOpen === 'mem'}
    <aside class="panel" id="memPanel">
      <div class="panel-header">
        <strong>Memories</strong>
        <button class="icon" type="button" aria-label="Close" on:click={() => panelOpen = 'none'}>✕</button>
      </div>
      <div class="panel-body">
        <div class="panel-controls">
          <label class="field small">
            <span>Filter by entity</span>
            <input type="text" bind:value={memFilter} placeholder="entity (optional)" />
          </label>
          <button class="ghost" type="button" on:click={refreshMemList}>Refresh</button>
        </div>
        <div class="mem-list" aria-live="polite">
          {#if $memLoading}
            <div class="muted">Loading…</div>
          {:else if $memError}
            <div class="muted">{$memError}</div>
          {:else if !$memList || $memList.length === 0}
            <div class="muted">No memories found.</div>
          {:else}
            {#each $memList as it}
              <div class="mem-item">
                <div class="mem-text">[{it.meta?.scope || 'global'}]{it.meta?.importance ? ` (importance=${it.meta.importance})` : ''} {it.text}</div>
                {#if it.id}
                  <button class="icon danger" title="Delete memory" on:click={() => deleteMemory(it.id)}>🗑</button>
                {/if}
              </div>
            {/each}
          {/if}
        </div>
        <hr />
        <div class="panel-add">
          <label class="field">
            <span>New memory text</span>
            <textarea rows="5" bind:value={memText} placeholder="Enter memory text or leave blank to use last answer..."></textarea>
          </label>
          <div class="row">
            <label class="field small">
              <span>Importance</span>
              <select bind:value={memImportance}>
                <option value="5">5 (high)</option>
                <option value="4">4</option>
                <option value="3">3</option>
                <option value="2">2</option>
                <option value="1">1 (low)</option>
              </select>
            </label>
            <label class="toggle">
              <span>Entity-scoped</span>
              <span class="switch">
                <input type="checkbox" bind:checked={memEntityScoped} />
                <span class="knob"></span>
              </span>
            </label>
          </div>
          {#if memEntityScoped}
            <label class="field">
              <span>Entity</span>
              <input type="text" bind:value={memEntity} placeholder="e.g., project-x" />
            </label>
          {/if}
          <button type="button" on:click={addMemory}>Add memory</button>
        </div>
      </div>
    </aside>
  {/if}
</div>

<style>
  :global(:root) {
    --bg: #0f172a;
    --panel: #111827;
    --muted: #94a3b8;
    --text: #e5e7eb;
    --me: #2563eb;
    --bot: #334155;
    --accent: #10b981;
  }
  :global(html, body) {
    height: 100%;
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji";
  }
  .app { height: 100%; display: grid; grid-template-rows: auto 1fr auto; max-width: 900px; margin: 0 auto; }
  header { padding: 16px; border-bottom: 1px solid #1f2937; display: flex; align-items: center; gap: 12px; justify-content: space-between; }
  .grow { flex: 1; }
  .field { display: flex; flex-direction: column; gap: 4px; font-size: 12px; color: var(--muted); }
  .field input, .field select, .field textarea { height: 28px; border-radius: 8px; border: 1px solid #374151; background: #0b1220; color: var(--text); padding: 4px 8px; }
  .field textarea { height: auto; }
  .field.small input, .field.small select { height: 28px; font-size: 12px; }
  .ghost { background: transparent; color: var(--muted); border: 1px solid #374151; padding: 6px 10px; border-radius: 8px; cursor: pointer; }
  .icon { background: #1f2937; border: 1px solid #374151; color: var(--text); border-radius: 8px; padding: 4px 8px; cursor: pointer; }
  .icon.danger { border-color: #7f1d1d; color: #fca5a5; background: #1f1b1b; }
  .brand { display: flex; align-items: center; gap: 12px; }
  header .dot { width: 10px; height: 10px; border-radius: 50%; background: #6b7280; box-shadow: 0 0 0 2px rgba(0,0,0,0.2) inset; }
  header .dot.ok { background: var(--accent); }
  header .dot.bad { background: #ef4444; }
  header h1 { font-size: 16px; margin: 0; letter-spacing: 0.5px; }
  #clientLibs { font-size: 12px; color: var(--muted); margin-left: 8px; }
  .toggle { display: flex; align-items: center; gap: 8px; color: var(--muted); font-size: 13px; }
  .switch { position: relative; width: 38px; height: 22px; background: #1f2937; border-radius: 999px; border: 1px solid #374151; cursor: pointer; }
  .switch input { display: none; }
  .knob { position: absolute; top: 2px; left: 2px; width: 18px; height: 18px; border-radius: 50%; background: #9ca3af; transition: transform 0.15s ease, background 0.15s ease; }
  .switch input:checked + .knob { transform: translateX(16px); background: var(--accent); }
  #messages { padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; background: radial-gradient(1200px 600px at 50% -200px, rgba(16,185,129,0.08), transparent 60%); }
  .msg { display: flex; gap: 10px; align-items: flex-start; max-width: 85%; }
  .msg .stack { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
  .msg.me { align-self: flex-end; flex-direction: row-reverse; }
  .bubble { padding: 10px 12px; border-radius: 12px; line-height: 1.35; white-space: pre-wrap; word-break: break-word; }
  .me .bubble { background: var(--me); color: white; }
  .bot .bubble { background: var(--bot); }
  .bot .bubble.answer { background: var(--bot); }
  .bot .bubble.think { background: #1f2937; color: var(--muted); border: 1px solid #374151; }
  .bubble.think { padding: 0; overflow: hidden; }
  .bubble.think summary { padding: 10px 12px; cursor: pointer; list-style: none; color: var(--muted); font-weight: 600; }
  .bubble.think summary::-webkit-details-marker { display: none; }
  .bubble.think summary::after { content: '▸'; float: right; color: var(--muted); transition: transform 0.15s ease; }
  .bubble.think[open] summary::after { transform: rotate(90deg); }
  .bubble.think .think-content { padding: 10px 12px; border-top: 1px solid #374151; white-space: pre-wrap; word-break: break-word; font-size: 0.9em; }
  .avatar { width: 28px; height: 28px; border-radius: 50%; background: #1f2937; display: grid; place-items: center; font-size: 14px; }
  .bubble a { color: var(--accent); text-decoration: underline; }
  .bubble code { background: rgba(255,255,255,0.04); padding: 2px 6px; border-radius: 6px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", "Helvetica Neue", monospace; font-size: 0.95em; }
  .bubble pre { background: #091126; border: 1px solid #111827; padding: 10px; border-radius: 8px; overflow: auto; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", "Helvetica Neue", monospace; font-size: 13px; white-space: pre; }
  .bubble pre code { display: block; white-space: pre; }
  .bubble ul, .bubble ol { padding-left: 1.25rem; margin: 0.25rem 0; }
  .bubble h1, .bubble h2, .bubble h3, .bubble h4 { margin: 0.25rem 0; }
  form#composer { display: grid; grid-template-columns: 1fr auto; gap: 8px; padding: 12px; border-top: 1px solid #1f2937; background: linear-gradient(0deg, rgba(17,24,39,0.9), rgba(17,24,39,0.9)); }
  textarea { resize: none; height: 44px; border-radius: 10px; border: 1px solid #374151; background: #0b1220; color: var(--text); padding: 10px 12px; outline: none; }
  button { height: 44px; padding: 0 16px; border: 1px solid #2563eb; border-radius: 10px; background: #1d4ed8; color: white; cursor: pointer; }
  button:disabled, textarea:disabled { opacity: 0.6; cursor: not-allowed; }
  .hint { color: var(--muted); font-size: 12px; padding: 0 12px 12px; }
  .panel { position: fixed; top: 0; right: 0; width: 360px; height: 100%; background: #0b1220; border-left: 1px solid #1f2937; box-shadow: -4px 0 16px rgba(0,0,0,0.4); display: grid; grid-template-rows: auto 1fr; z-index: 20; }
  .panel-header { display: flex; align-items: center; justify-content: space-between; padding: 12px; border-bottom: 1px solid #1f2937; }
  .panel-body { padding: 12px; display: grid; grid-template-rows: auto 1fr auto; gap: 10px; }
  .panel-controls { display: flex; gap: 8px; align-items: end; }
  .panel-status { display: grid; gap: 6px; }
  .status-box { border: 1px solid #1f2937; background: #0f172a; border-radius: 8px; padding: 8px; font-size: 12px; color: var(--text); }
  .status-box.bad { border-color: #7f1d1d; color: #fca5a5; background: #1f1b1b; }
  .mem-list { overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
  .mem-item { display: flex; align-items: start; justify-content: space-between; gap: 8px; background: #0f172a; border: 1px solid #1f2937; border-radius: 8px; padding: 8px; }
  .mem-text { white-space: pre-wrap; word-break: break-word; font-size: 13px; }
  .panel-add { display: grid; gap: 8px; }
  .panel-add textarea { min-height: 120px; }
  .row { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
  .muted { color: var(--muted); }
  .spinner { width: 16px; height: 16px; border-radius: 50%; border: 2px solid #334155; border-top-color: var(--accent); animation: spin 0.9s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .msg.thinking { align-self: stretch; justify-content: center; }
  .menu { position: relative; }
  .menu-list { position: absolute; right: 0; top: calc(100% + 8px); background: #0b1220; border: 1px solid #1f2937; border-radius: 10px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); padding: 8px; display: flex; flex-direction: column; gap: 6px; z-index: 30; }
  .menu-item { text-align: left; background: #111827; color: var(--text); border: 1px solid #1f2937; border-radius: 8px; padding: 6px 10px; cursor: pointer; }
  .menu-item:hover { background: #1f2937; }
  .save-mem { margin-top: 6px; align-self: flex-start; padding: 4px 10px; height: auto; }
</style>
