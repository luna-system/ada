import { writable } from 'svelte/store';

export type MemoryItem = {
  id?: string;
  text: string;
  meta?: { importance?: number; scope?: string };
};

export const memList = writable<MemoryItem[]>([]);
export const memLoading = writable(false);
export const memError = writable<string | null>(null);

export async function fetchMemories(filterEntity: string, limit = 50) {
  memLoading.set(true);
  memError.set(null);
  try {
    const q = new URLSearchParams();
    q.set('limit', String(limit));
    if (filterEntity.trim()) q.set('entity', filterEntity.trim());
    const res = await fetch(`/api/memory?${q.toString()}`);
    const data = await res.json();
    if (!res.ok || data.error) throw new Error(data.error || `HTTP ${res.status}`);
    memList.set(data.items || []);
  } catch (e: any) {
    memError.set(e.message || 'Failed to load memories');
    memList.set([]);
  } finally {
    memLoading.set(false);
  }
}

export async function addMemoryItem(body: Record<string, any>) {
  const res = await fetch('/api/memory', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  const data = await res.json();
  if (!res.ok || data.error) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

export async function deleteMemoryItem(id: string) {
  const res = await fetch(`/api/memory/${encodeURIComponent(id)}`, { method: 'DELETE' });
  const data = await res.json();
  if (!res.ok || data.error) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}