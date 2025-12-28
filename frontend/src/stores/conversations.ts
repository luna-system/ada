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

// Helper to get API endpoint URL
function getApiUrl(endpoint: string): string {
  const baseUrl = (window as any).API_BASE_URL || '/api';
  return baseUrl.startsWith('http') ? `${baseUrl}${endpoint}` : `/api${endpoint}`;
}

export async function fetchConversations(limit = 10): Promise<void> {
  conversationsLoading.set(true);
  conversationsError.set(null);
  try {
    const res = await fetch(getApiUrl(`/conversations/recent?limit=${limit}`), { cache: 'no-store' });
    if (!res.ok) {
      throw new Error(`Failed to fetch conversations: ${res.statusText}`);
    }
    const data = await res.json();
    
    // Handle RAG not available gracefully
    if (data.error && data.error === 'RAG not available') {
      conversations.set([]);
      return;
    }
    
    conversations.set(data);
  } catch (err: any) {
    // Don't show error for RAG unavailable - just use empty conversations
    console.log('Conversations unavailable (RAG not configured):', err.message);
    conversations.set([]);
  } finally {
    conversationsLoading.set(false);
  }
}

export async function loadConversation(id: string): Promise<{ role: string; text: string; timestamp: string }[] | null> {
  try {
    const res = await fetch(getApiUrl(`/conversations/${id}`), { cache: 'no-store' });
    if (!res.ok) {
      throw new Error(`Failed to load conversation: ${res.statusText}`);
    }
    const data = await res.json();
    
    // Handle RAG not available gracefully
    if (data.error && data.error === 'RAG not available') {
      return [];
    }
    
    return data.turns || [];
  } catch (err: any) {
    console.log('Conversation unavailable (RAG not configured):', err.message);
    return null;
  }
}
