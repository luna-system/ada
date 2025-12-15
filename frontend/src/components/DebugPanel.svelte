<script lang="ts">
  export let health: string;
  export let healthOk: boolean | null;
  export let clientLibs: string;
  export let onRefreshHealth: () => void;
  export let onRefreshLibs: () => void;
  export let onClose: () => void;
</script>

<aside class="panel" id="debugPanel">
  <div class="panel-header">
    <strong>Debug</strong>
    <button class="icon" type="button" aria-label="Close" on:click={() => onClose?.()}>✕</button>
  </div>
  <div class="panel-body">
    <div class="panel-status">
      <div class="row" style="justify-content: space-between;">
        <strong>Status</strong>
        <button class="ghost" type="button" title="Refresh health" on:click={onRefreshHealth}>Refresh</button>
      </div>
      <div class={`status-box muted ${healthOk === false ? 'bad' : ''}`} aria-live="polite">{health}</div>
    </div>
    <div class="panel-status">
      <div class="row" style="justify-content: space-between;">
        <strong>Client libraries</strong>
        <button class="ghost" type="button" title="Refresh client libraries" on:click={onRefreshLibs}>Refresh</button>
      </div>
      <div class="status-box muted" aria-live="polite">{clientLibs || 'Loading…'}</div>
    </div>
  </div>
</aside>
