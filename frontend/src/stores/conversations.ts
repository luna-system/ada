import { writable } from 'svelte/store';

export type Conversation = {
  id: string;
  preview: string;
  timestamp: string;
  turn_count: number;
};

export const conversations = writable<Conversation[]>([]);
export const conversationsLoading = writable(false);
export const conversationsError = writable<string | null>(null);

export async function fetchConversations(limit = 10): Promise<void> {
  conversationsLoading.set(true);
  conversationsError.set(null);
  try {
    const res = await fetch(`/api/conversations/recent?limit=${limit}`, { cache: 'no-store' });
    if (!res.ok) {
      throw new Error(`Failed to fetch conversations: ${res.statusText}`);
    }
    const data = await res.json();
    conversations.set(data);
  } catch (err: any) {
    conversationsError.set(err.message || 'Failed to load conversations');
    conversations.set([]);
  } finally {
    conversationsLoading.set(false);
  }
}

export async function loadConversation(id: string): Promise<{ role: string; text: string; timestamp: string }[] | null> {
  try {
    const res = await fetch(`/api/conversations/${id}`, { cache: 'no-store' });
    if (!res.ok) {
      throw new Error(`Failed to load conversation: ${res.statusText}`);
    }
    const data = await res.json();
    return data.turns || [];
  } catch (err: any) {
    console.error('Failed to load conversation:', err);
    return null;
  }
}
