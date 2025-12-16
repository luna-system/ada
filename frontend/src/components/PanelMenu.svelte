<script lang="ts">
  export let onToggle: (panel: 'debug' | 'mem' | 'prompt' | 'conversations' | 'notices') => void;
  export let open: boolean = false;
  export let setOpen: (val: boolean) => void;
</script>

<div class="menu" id="panelMenu">
  <button id="panelMenuButton" class="ghost" type="button" aria-haspopup="true" aria-expanded={open} on:click={() => setOpen(!open)}>Panels ▾</button>
  {#if open}
    <div class="menu-list">
      <button type="button" class="menu-item" on:click={() => onToggle('conversations')}>Conversations</button>
      <button type="button" class="menu-item" on:click={() => onToggle('notices')}>Notices</button>
      <button type="button" class="menu-item" on:click={() => onToggle('mem')}>Memories</button>
      <button type="button" class="menu-item" on:click={() => onToggle('prompt')}>Prompt Debug</button>
      <button type="button" class="menu-item" on:click={() => onToggle('debug')}>Debug</button>
    </div>
  {/if}
</div>
