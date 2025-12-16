<script lang="ts">
  import { onMount, afterUpdate } from 'svelte';
  import { get } from 'svelte/store';
  import '../styles/app.css';
  import {
    messages,
    thinking,
    conversationId,
    ensureConversationId,
    setConversationId,
    setThinking,
    pushMessage,
    updateMessage,
    type Message,
    type Role
  } from '../stores/chat';
  import { memList, memLoading, memError, fetchMemories, addMemoryItem, deleteMemoryItem } from '../stores/memory';
  import { conversations, conversationsLoading, conversationsError, fetchConversations, loadConversation } from '../stores/conversations';
  import ConversationsPanel from './ConversationsPanel.svelte';
  import PanelMenu from './PanelMenu.svelte';
  import DebugPanel from './DebugPanel.svelte';
  import MemoriesPanel from './MemoriesPanel.svelte';
  import PromptPanel from './PromptPanel.svelte';
  import NoticesPanel from './NoticesPanel.svelte';
  import { streamChat, type StreamMessage } from '../services/chat';
  import { panelOpen as panelOpenStore, menuOpen as menuOpenStore } from '../stores/ui';
  import { extractTextFromImage, type OCRResult } from '../services/ocr';

  const uuid = () => crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2);

  let prompt = '';
  let includeThinking = false;
  let showEntityInput = false;
  let shareListenBrainz = false;
  let showAddMemory = false;
  let showComposerControls = true;
  let listenBrainzPreview: any = null;
  let listenBrainzLoading = false;
  let entity = '';
  let ocrContext: OCRResult | null = null;
  let ocrProcessing = false;
  let panelOpen: 'none' | 'debug' | 'mem' | 'prompt' | 'conversations' | 'notices' = 'none';
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
  let conversationIdInput = '';
  let conversationIdError = '';
  let conversationIdEditing = false;

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
    fetchConversations();

    // Set up auto-refresh for ListenBrainz every 2 minutes
    const listenBrainzInterval = setInterval(() => {
      if (shareListenBrainz) {
        fetchListenBrainzNowPlaying();
      }
    }, 2 * 60 * 1000); // 2 minutes

    const unsubPanel = panelOpenStore.subscribe((v) => panelOpen = v);
    const unsubMenu = menuOpenStore.subscribe((v) => menuOpen = v);
    return () => { clearInterval(listenBrainzInterval); unsubPanel(); unsubMenu(); };
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

  function togglePanel(which: 'debug' | 'mem' | 'prompt' | 'conversations') {
    panelOpenStore.set(panelOpen === which ? 'none' : which);
    menuOpenStore.set(false);
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
        ocrContext,
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
          // Clear OCR context after successful message
          ocrContext = null;
        }
      });
    } catch (e: any) {
      updateMessage(answerId, { text: `Error: ${e.message || e}` });
    } finally {
      setThinking(false);
    }
  }

  async function handleFileUpload(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file');
      return;
    }

    ocrProcessing = true;
    try {
      const result = await extractTextFromImage(file);
      ocrContext = result;
      
      // Auto-insert prompt suggestion if text area is empty
      if (!prompt.trim() && result.text) {
        prompt = 'What does this image say?';
      }
    } catch (e: any) {
      alert(`OCR failed: ${e.message || e}`);
    } finally {
      ocrProcessing = false;
      // Reset input so same file can be re-uploaded
      input.value = '';
    }
  }

  function clearOcrContext() {
    ocrContext = null;
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

  async function selectConversation(id: string) {
    const turns = await loadConversation(id);
    if (!turns) {
      alert('Failed to load conversation');
      return;
    }
    // Clear current messages and load conversation
    messages.set([]);
    setConversationId(id);
    // Convert turns to messages
    for (const turn of turns) {
      pushMessage({
        id: uuid(),
        role: turn.role as Role,
        text: turn.text
      });
    }
    panelOpenStore.set('none');
    scrollMessages();
  }

  function newConversation() {
    messages.set([]);
    setConversationId(uuid());
    prompt = '';
    conversationIdInput = '';
    conversationIdError = '';
    conversationIdEditing = false;
    showAddMemory = false;
  }

  async function updateConversationId() {
    const newId = conversationIdInput.trim();
    if (!newId) {
      conversationIdError = 'ID cannot be empty';
      return;
    }
    
    // Check if this ID already exists
    const convos = get(conversations);
    const exists = convos.some(c => c.id === newId);
    
    if (exists && newId !== get(conversationId)) {
      conversationIdError = 'This conversation ID already exists';
      return;
    }
    
    // Valid ID, update it
    conversationIdError = '';
    setConversationId(newId);
    conversationIdEditing = false;
  }

  // Sync input with store
  $: if ($conversationId && !conversationIdInput) {
    conversationIdInput = $conversationId;
  }

  async function addMemory() {
    let text = (memText || '').trim();
    const lower = text.toLowerCase();
    const hasRolePrefix = lower.startsWith('assistant:') || lower.startsWith('user:') || lower.startsWith('system:');
    if (!hasRolePrefix && text) {
      text = `assistant: ${text}`;
    }
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
    panelOpenStore.set('mem');
    memText = text ? `assistant: ${text}` : '';
    memEntity = entity || memEntity;
    menuOpenStore.set(false);
    showAddMemory = true;
  }
</script>

<svelte:window on:click={(e) => {
  const menuEl = document.getElementById('panelMenu');
  const btnEl = document.getElementById('panelMenuButton');
  if (!menuEl || !btnEl) return;
  if (!menuOpen) return;
  if (menuEl.contains(e.target as Node) || btnEl.contains(e.target as Node)) return;
  menuOpenStore.set(false);
}} />

<div class="app">
  <header>
    <div class="brand">
      <div class="dot {healthOk === true ? 'ok' : healthOk === false ? 'bad' : ''}" aria-hidden="true"></div>
      <h1>ADA · Chat</h1>
    </div>
    {#if $conversationId}
      <div class="conversation-id" style="display: flex; align-items: center; gap: 8px;">
        <span class="muted" style="font-size: 0.85em;">ID:</span>
        {#if !conversationIdEditing}
          <span style="font-size: 0.85em; font-family: monospace;">{$conversationId}</span>
          <button class="ghost" type="button" title="Edit conversation ID" on:click={() => { conversationIdInput = $conversationId; conversationIdEditing = true; }}>
            ✎
          </button>
        {:else}
          <input
            type="text"
            bind:value={conversationIdInput}
            style="width: clamp(16ch, 50vw, 36ch); font-size: 0.95em; padding: 6px 10px;"
            placeholder="conversation-id"
            aria-invalid={!!conversationIdError}
          />
          <button class="ghost" type="button" title="Save ID" on:click={updateConversationId}>OK</button>
          <button class="ghost" type="button" title="Cancel" on:click={() => { conversationIdEditing = false; conversationIdInput = $conversationId; conversationIdError = ''; }}>Cancel</button>
          {#if conversationIdError}
            <span class="muted" style="color: var(--danger, #ef4444); font-size: 0.8em;">{conversationIdError}</span>
          {/if}
        {/if}
      </div>
    {/if}
    <div class="grow"></div>
    <button class="ghost" type="button" on:click={newConversation} title="Start new conversation">New Chat</button>
    <PanelMenu open={menuOpen} setOpen={(v) => menuOpenStore.set(v)} onToggle={togglePanel} />
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
    {#if ocrContext}
      <div class="ocr-pill">
        📄 OCR: {ocrContext.filename} ({ocrContext.char_count} chars{#if ocrContext.confidence}, {ocrContext.confidence.toFixed(0)}% confidence{/if})
        <button type="button" class="ocr-clear" on:click={clearOcrContext} title="Remove OCR context">×</button>
      </div>
    {/if}
    <div class="input-row">
      <textarea bind:value={prompt} placeholder="Type your message..." autocomplete="off" on:keydown={(e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          handleSubmit();
        }
      }}></textarea>
      <label class="upload-btn" title="Upload image for OCR">
        <input type="file" accept="image/*" on:change={handleFileUpload} hidden disabled={ocrProcessing || $thinking} />
        {#if ocrProcessing}
          <span class="spinner-small"></span>
        {:else}
          📷
        {/if}
      </label>
      <button type="submit" disabled={$thinking || !prompt.trim()}>Send</button>
    </div>
    <button type="button" class="composer-divider" title="Toggle composer options" on:click={() => showComposerControls = !showComposerControls}>
      <span class="chevron" class:open={showComposerControls}>▼</span>
    </button>
    {#if showComposerControls}
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
    {/if}
  </form>

  {#if panelOpen === 'debug'}
    <DebugPanel health={health} healthOk={healthOk} clientLibs={clientLibs} onRefreshHealth={refreshHealth} onRefreshLibs={updateClientLibStatus} onClose={() => panelOpenStore.set('none')} />
  {/if}

  {#if panelOpen === 'mem'}
    <MemoriesPanel
      memFilter={memFilter}
      onSetMemFilter={(v) => memFilter = v}
      onRefresh={refreshMemList}
      onDelete={(id) => deleteMemory(id)}
      memText={memText}
      onSetMemText={(v) => memText = v}
      memImportance={memImportance}
      onSetMemImportance={(v) => memImportance = v}
      memEntityScoped={memEntityScoped}
      onSetMemEntityScoped={(v) => memEntityScoped = v}
      memEntity={memEntity}
      onSetMemEntity={(v) => memEntity = v}
      onAddMemory={addMemory}
      showAddMemory={showAddMemory}
      onToggleAddMemory={(v) => showAddMemory = v}
      onClose={() => panelOpenStore.set('none')}
    />
  {/if}

  {#if panelOpen === 'conversations'}
    <ConversationsPanel onClose={() => panelOpenStore.set('none')} />
  {/if}

  {#if panelOpen === 'notices'}
    <NoticesPanel onClose={() => panelOpenStore.set('none')} />
  {/if}

  {#if panelOpen === 'prompt'}
    <PromptPanel
      promptDebug={promptDebug}
      promptDebugError={promptDebugError}
      promptDebugLoading={promptDebugLoading}
      lastUserText={lastOfRole('user')?.text}
      lastAssistantText={lastOfRole('assistant')?.text}
      onRefresh={fetchPromptDebug}
      onClose={() => panelOpenStore.set('none')}
    />
  {/if}
</div>

