<script lang="ts">
  import { conversations, conversationsLoading, conversationsError, fetchConversations, loadConversation } from '../stores/conversations';
  import { messages, setConversationId, pushMessage, type Role } from '../stores/chat';

  const uuid = () => crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2);

  export let onClose: () => void;

  async function selectConversation(id: string) {
    const turns = await loadConversation(id);
    if (!turns) {
      alert('Failed to load conversation');
      return;
    }
    messages.set([]);
    setConversationId(id);
    for (const turn of turns) {
      pushMessage({ id: uuid(), role: turn.role as Role, text: turn.text });
    }
    onClose?.();
  }
</script>

<aside class="panel" id="conversationsPanel">
  <div class="panel-header">
    <strong>Recent Conversations</strong>
    <button class="icon" type="button" aria-label="Close" on:click={() => onClose?.()}>✕</button>
  </div>
  <div class="panel-body">
    <div class="panel-controls">
      <button class="ghost" type="button" on:click={() => fetchConversations()}>Refresh</button>
    </div>
    <div class="mem-list" aria-live="polite">
      {#if $conversationsLoading}
        <div class="muted">Loading…</div>
      {:else if $conversationsError}
        <div class="muted">{$conversationsError}</div>
      {:else if !$conversations || $conversations.length === 0}
        <div class="muted">No conversations found.</div>
      {:else}
        {#each $conversations as convo}
          <button class="mem-item" style="cursor: pointer; flex-direction: column; align-items: flex-start; gap: 4px; text-align: left; width: 100%;" type="button" on:click={() => selectConversation(convo.id)}>
            <div class="mem-text" style="font-weight: 500;">{convo.preview || '(no preview)'}</div>
            <div class="muted" style="font-size: 0.75em; font-family: monospace; word-break: break-all;">
              ID: {convo.id}
            </div>
            <div class="muted" style="font-size: 0.85em;">
              {new Date(convo.timestamp).toLocaleString()} • {convo.turn_count} turns
            </div>
          </button>
        {/each}
      {/if}
    </div>
  </div>
</aside>
