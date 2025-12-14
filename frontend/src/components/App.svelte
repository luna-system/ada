<script lang="ts">
  import { onMount, afterUpdate } from 'svelte';
  import { get } from 'svelte/store';
  import '../styles/app.css';
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
  import { streamChat, type StreamMessage } from '../services/chat';

  const uuid = () => crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2);

  let prompt = '';
  let includeThinking = false;
  let showEntityInput = false;
  let shareListenBrainz = false;
  let listenBrainzPreview: any = null;
  let listenBrainzLoading = false;
  let entity = '';
  let panelOpen: 'none' | 'debug' | 'mem' | 'prompt' = 'none';
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

  let promptDebug: any = null;
  let promptDebugError: string | null = null;
  let promptDebugLoading = false;

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

    // Set up auto-refresh for ListenBrainz every 2 minutes
    const listenBrainzInterval = setInterval(() => {
      if (shareListenBrainz) {
        fetchListenBrainzNowPlaying();
      }
    }, 2 * 60 * 1000); // 2 minutes

    return () => clearInterval(listenBrainzInterval);
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

  async function fetchListenBrainzNowPlaying() {
    if (!shareListenBrainz) {
      listenBrainzPreview = null;
      listenBrainzLoading = false;
      return null;
    }
    listenBrainzLoading = true;
    try {
      const res = await fetch('/api/media/listenbrainz', { cache: 'no-store' });
      const data = await res.json();
      if (!res.ok || data.error) {
        listenBrainzPreview = null;
        listenBrainzLoading = false;
        return null;
      }
      listenBrainzPreview = data;
      listenBrainzLoading = false;
      return data;
    } catch (e) {
      listenBrainzPreview = null;
      listenBrainzLoading = false;
      return null;
    }
  }

  // Re-fetch ListenBrainz data when toggle changes
  $: if (shareListenBrainz) {
    fetchListenBrainzNowPlaying();
  } else {
    listenBrainzPreview = null;
    listenBrainzLoading = false;
  }

  function mediaSummary(data: any): string {
    if (!data) return '';
    const artist = data.artist || 'Unknown';
    const track = data.track || 'Unknown';
    const release = data.release ? ` • album: ${data.release}` : '';
    const status = data.status ? ` • status: ${data.status}` : '';
    return `${artist} — ${track}${release}${status}`;
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

  function togglePanel(which: 'debug' | 'mem' | 'prompt') {
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
    if (which === 'prompt') {
      fetchPromptDebug();
    }
  }

  function onEntityChange(val: string) {
    entity = val;
    localStorage.setItem('entity', entity);
  }

  function lastOfRole(role: Role) {
    const list = get(messages);
    for (let i = list.length - 1; i >= 0; i -= 1) {
      if (list[i].role === role) return list[i];
    }
    return undefined;
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
      const media = await fetchListenBrainzNowPlaying();
      await streamChat({
        prompt: userText,
        includeThinking,
        conversationId: activeConversationId,
        entity: entity || undefined,
        media,
        onToken: (content) => {
          assistantText += content;
          updateMessage(answerId, { text: assistantText, thinking: thinkingText });
        },
        onThinking: (content) => {
          if (!includeThinking) return;
          thinkingText += content;
          updateMessage(answerId, { text: assistantText, thinking: thinkingText });
        },
        onDone: (newConvId) => {
          setThinking(false);
          if (newConvId && newConvId !== activeConversationId) {
            activeConversationId = newConvId;
            setConversationId(activeConversationId);
          }
        }
      });
    } catch (e: any) {
      updateMessage(answerId, { text: `Error: ${e.message || e}` });
    } finally {
      setThinking(false);
    }
  }

  async function refreshMemList() {
    await fetchMemories(memFilter);
  }

  async function fetchPromptDebug() {
    promptDebugLoading = true;
    promptDebugError = null;
    try {
      const params = new URLSearchParams();
      const convId = ensureConversationId(uuid);
      if (convId) params.set('conversation_id', convId);
      if (entity.trim()) params.set('entity', entity.trim());
      if (shareListenBrainz) params.set('share_listenbrainz', 'true');
      const lastUser = lastOfRole('user');
      if (lastUser?.text) params.set('prompt', lastUser.text);
      const res = await fetch(`/api/debug/prompt?${params.toString()}`);
      const data = await res.json();
      if (!res.ok || data.error) throw new Error(data.error || `HTTP ${res.status}`);
      promptDebug = data;
    } catch (e: any) {
      promptDebugError = e.message || 'Failed to load prompt debug';
      promptDebug = null;
    } finally {
      promptDebugLoading = false;
    }
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
    <div class="menu" id="panelMenu">
      <button id="panelMenuButton" class="ghost" type="button" aria-haspopup="true" aria-expanded={menuOpen} on:click={() => menuOpen = !menuOpen}>Panels ▾</button>
      {#if menuOpen}
        <div class="menu-list">
          <button type="button" class="menu-item" on:click={() => togglePanel('debug')}>Debug</button>
          <button type="button" class="menu-item" on:click={() => togglePanel('mem')}>Memories</button>
          <button type="button" class="menu-item" on:click={() => togglePanel('prompt')}>Prompt Debug</button>
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
    <button type="submit" disabled={$thinking || !prompt.trim()}>Send</button>
    <div class="controls-row">
      <label class="toggle-control" title="Include thinking">
        <span class="emoji">🧠</span>
        <span class="switch">
          <input type="checkbox" bind:checked={includeThinking} />
          <span class="knob"></span>
        </span>
      </label>
      <label class="toggle-control" title="Share ListenBrainz now playing/last track">
        <span class="emoji">🎧</span>
        <span class="switch">
          <input type="checkbox" bind:checked={shareListenBrainz} />
          <span class="knob"></span>
        </span>
      </label>
      <label class="toggle-control" title="Filter memory by entity">
        <span class="emoji">🏷️</span>
        <span class="switch">
          <input type="checkbox" bind:checked={showEntityInput} />
          <span class="knob"></span>
        </span>
      </label>
      {#if showEntityInput}
        <input class="entity-input" value={entity} on:input={(e) => onEntityChange((e.target as HTMLInputElement).value)} placeholder="entity/topic" />
      {/if}
      <div class="spacer"></div>
      {#if shareListenBrainz && listenBrainzLoading}
        <span class="media-pill loading" title="Loading now playing...">
          🎧 <span class="load-dots"><span>.</span><span>.</span><span>.</span></span>
        </span>
      {:else if shareListenBrainz && listenBrainzPreview}
        <span class="media-pill" title={mediaSummary(listenBrainzPreview)}>
          🎧 {mediaSummary(listenBrainzPreview)}
        </span>
      {/if}
    </div>
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

  {#if panelOpen === 'prompt'}
    <aside class="panel" id="promptPanel">
      <div class="panel-header">
        <strong>Prompt Debug</strong>
        <button class="icon" type="button" aria-label="Close" on:click={() => panelOpen = 'none'}>✕</button>
      </div>
      <div class="panel-body">
        <div class="panel-status">
          <div class="row" style="justify-content: space-between;">
            <strong>Most recent turn</strong>
            <button class="ghost" type="button" on:click={fetchPromptDebug}>Refresh</button>
          </div>
          <div class="status-box muted">
            <div><strong>User:</strong> {lastOfRole('user')?.text || '—'}</div>
            <div><strong>Assistant:</strong> {lastOfRole('assistant')?.text || '—'}</div>
          </div>
        </div>
        <div class="panel-status">
          <div class="row" style="justify-content: space-between;">
            <strong>Prompt context</strong>
            {#if promptDebugLoading}<span class="muted">Loading…</span>{/if}
          </div>
          {#if promptDebugError}
            <div class="status-box bad">{promptDebugError}</div>
          {:else if promptDebug}
            <div class="status-box" style="max-height: 28vh; overflow:auto; white-space: pre-wrap;">
              <strong>Context counts</strong>
              <div class="muted">persona: {promptDebug.used_context?.persona?.included ? 'yes' : 'no'},
                faqs: {promptDebug.used_context?.faqs?.length || 0},
                memories: {promptDebug.used_context?.memories?.length || 0},
                turns: {promptDebug.used_context?.turns?.length || 0},
                summaries: {promptDebug.used_context?.summaries?.length || 0}
              </div>
              <strong>Sections</strong>
              <pre style="white-space: pre-wrap; overflow:auto; margin: 8px 0;">{(promptDebug.sections || []).join('\n\n')}</pre>
            </div>
            <div class="status-box" style="max-height: 28vh; overflow:auto; white-space: pre-wrap;">
              <strong>Final prompt</strong>
              <pre style="white-space: pre-wrap; overflow:auto; margin: 8px 0;">{promptDebug.final_prompt}</pre>
            </div>
          {:else}
            <div class="status-box muted">No prompt debug data yet. Refresh to load.</div>
          {/if}
        </div>
      </div>
    </aside>
  {/if}
</div>

