<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { fetchNotices, acknowledgeNotice, type Notice } from '../services/notices';

  export let onClose: () => void;

  let notices: Notice[] = [];
  let loading = false;
  let error: string | null = null;
  let pollInterval: number;

  async function loadNotices() {
    try {
      loading = true;
      error = null;
      notices = await fetchNotices();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load notices';
    } finally {
      loading = false;
    }
  }

  async function handleAcknowledge(noticeId: string) {
    try {
      await acknowledgeNotice(noticeId, 'luna');
      notices = notices.filter(n => n.id !== noticeId);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to acknowledge notice';
    }
  }

  function getSeverityColor(severity: string): string {
    switch (severity) {
      case 'error': return '#ef4444';
      case 'warning': return '#f59e0b';
      case 'info': return '#3b82f6';
      default: return '#6b7280';
    }
  }

  function getSeverityIcon(severity: string): string {
    switch (severity) {
      case 'error': return '❌';
      case 'warning': return '⚠️';
      case 'info': return 'ℹ️';
      default: return '📢';
    }
  }

  function formatTime(timestamp: number): string {
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
  }

  onMount(() => {
    loadNotices();
    // Poll every 30 seconds
    pollInterval = setInterval(loadNotices, 30000) as any;
  });

  onDestroy(() => {
    if (pollInterval) clearInterval(pollInterval);
  });
</script>

<aside class="panel" id="noticesPanel">
  <div class="panel-header">
    <strong>System Notices</strong>
    <button class="icon" type="button" aria-label="Close" on:click={onClose}>✕</button>
  </div>
  <div class="panel-body notices-body">

  {#if error}
    <div class="error-banner">{error}</div>
  {/if}

  {#if notices.length === 0 && !loading}
    <div class="empty-state">
      <p>✅ No active notices</p>
    </div>
  {:else}
    <div class="notices-list">
      {#each notices as notice (notice.id)}
        <div class="notice-card" style="--severity-color: {getSeverityColor(notice.severity)}">
          <div class="notice-header">
            <span class="severity-pill" style="background: {getSeverityColor(notice.severity)}20; color: {getSeverityColor(notice.severity)}; border-color: {getSeverityColor(notice.severity)}">
              {getSeverityIcon(notice.severity)} {notice.severity.toUpperCase()}
            </span>
            <span class="component-pill">{notice.component}.{notice.code}</span>
          </div>
          <div class="notice-message">{notice.message}</div>
          <div class="notice-footer">
            <span class="notice-time">{formatTime(notice.created_at)}</span>
            <button class="ack-btn" on:click={() => handleAcknowledge(notice.id)}>
              Acknowledge
            </button>
          </div>
        </div>
      {/each}
    </div>
  {/if}
  </div>
</aside>

<style>
  .notices-body {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
  }



  .error-banner {
    background: #ef4444;
    color: white;
    padding: 0.75rem;
    margin: 1rem;
    border-radius: 4px;
  }

  .empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    flex: 1;
    color: #666;
    padding: 2rem;
    text-align: center;
  }

  .notices-list {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .notice-card {
    background: linear-gradient(135deg, #1a1a1a 0%, #151515 100%);
    border: 1px solid #333;
    border-left: 4px solid var(--severity-color);
    border-radius: 8px;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    transition: all 0.2s ease;
  }

  .notice-card:hover {
    border-color: #444;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    transform: translateY(-2px);
  }

  .notice-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .severity-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    border: 1px solid;
  }

  .component-pill {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.75rem;
    background: #2a2a2a;
    border: 1px solid #444;
    border-radius: 12px;
    color: #999;
    font-family: 'Courier New', monospace;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .notice-message {
    color: #e5e5e5;
    line-height: 1.6;
    padding: 0.5rem 0;
  }

  .notice-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 0.25rem;
    padding-top: 0.75rem;
    border-top: 1px solid #2a2a2a;
  }

  .notice-time {
    color: #666;
    font-size: 0.8rem;
    font-style: italic;
  }

  .ack-btn {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0.5rem 1rem;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 600;
    transition: all 0.2s ease;
    box-shadow: 0 2px 4px rgba(37, 99, 235, 0.3);
  }

  .ack-btn:hover {
    background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
    box-shadow: 0 4px 8px rgba(37, 99, 235, 0.4);
    transform: translateY(-1px);
  }

  .ack-btn:active {
    background: #1e40af;
    transform: translateY(0);
  }
</style>
