<script lang="ts">
  import { memList, memLoading, memError } from '../stores/memory';
  export let memFilter: string;
  export let onSetMemFilter: (val: string) => void;
  export let onRefresh: () => void;
  export let onDelete: (id: string) => void;
  export let memText: string;
  export let onSetMemText: (val: string) => void;
  export let memImportance: number;
  export let onSetMemImportance: (val: number) => void;
  export let memEntityScoped: boolean;
  export let onSetMemEntityScoped: (val: boolean) => void;
  export let memEntity: string;
  export let onSetMemEntity: (val: string) => void;
  export let onAddMemory: () => void;
  export let showAddMemory: boolean;
  export let onToggleAddMemory: (val: boolean) => void;
  export let onClose: () => void;
</script>

<aside class="panel" id="memPanel">
  <div class="panel-header">
    <strong>Memories</strong>
    <button class="icon" type="button" aria-label="Close" on:click={() => onClose?.()}>✕</button>
  </div>
  <div class="panel-body mem-body">
    <div class="panel-controls">
      <label class="field small">
        <span>Filter by entity</span>
        <input type="text" bind:value={memFilter} on:input={(e) => onSetMemFilter((e.target as HTMLInputElement).value)} placeholder="entity (optional)" />
      </label>
      <button class="ghost" type="button" on:click={onRefresh}>Refresh</button>
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
            <div class="mem-item-header">
              <div class="mem-meta">
                <span class="pill">{it.meta?.scope || 'global'}</span>
                {#if it.meta?.importance}
                  <span class="pill pill-muted">Imp {it.meta.importance}</span>
                {/if}
              </div>
              {#if it.id}
                <button class="icon danger" title="Delete memory" on:click={() => onDelete(it.id || '')}>🗑</button>
              {/if}
            </div>
            <div class="mem-text">{it.text}</div>
          </div>
        {/each}
      {/if}
    </div>
    {#if showAddMemory}
      <div class="panel-add">
        <label class="field">
          <span>New memory text</span>
          <textarea rows="5" bind:value={memText} on:input={(e) => onSetMemText((e.target as HTMLTextAreaElement).value)} placeholder="Enter memory text..."></textarea>
        </label>
        <div class="row">
          <label class="field small">
            <span>Importance</span>
            <select bind:value={memImportance} on:change={(e) => onSetMemImportance(parseInt((e.target as HTMLSelectElement).value))}>
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
              <input type="checkbox" bind:checked={memEntityScoped} on:change={(e) => onSetMemEntityScoped((e.target as HTMLInputElement).checked)} />
              <span class="knob"></span>
            </span>
          </label>
        </div>
        {#if memEntityScoped}
          <label class="field">
            <span>Entity</span>
            <input type="text" bind:value={memEntity} on:input={(e) => onSetMemEntity((e.target as HTMLInputElement).value)} placeholder="e.g., project-x" />
          </label>
        {/if}
        <button type="button" on:click={onAddMemory}>Add memory</button>
      </div>
    {:else}
      <div class="panel-add-collapsed">
        <button class="ghost" type="button" on:click={() => onToggleAddMemory?.(true)}>Add memory</button>
      </div>
    {/if}
  </div>
</aside>
