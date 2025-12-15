<script lang="ts">
  export let promptDebug: any;
  export let promptDebugError: string | null;
  export let promptDebugLoading: boolean;
  export let lastUserText: string | undefined;
  export let lastAssistantText: string | undefined;
  export let onRefresh: () => void;
  export let onClose: () => void;
</script>

<aside class="panel" id="promptPanel">
  <div class="panel-header">
    <strong>Prompt Debug</strong>
    <button class="icon" type="button" aria-label="Close" on:click={() => onClose?.()}>✕</button>
  </div>
  <div class="panel-body">
    <div class="panel-status">
      <div class="row" style="justify-content: space-between;">
        <strong>Most recent turn</strong>
        <button class="ghost" type="button" on:click={onRefresh}>Refresh</button>
      </div>
      <div class="status-box muted">
        <div><strong>User:</strong> {lastUserText || '—'}</div>
        <div><strong>Assistant:</strong> {lastAssistantText || '—'}</div>
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
