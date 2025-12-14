import { writable, get } from 'svelte/store';

export type Role = 'user' | 'assistant';
export type Message = { id: string; role: Role; text: string; thinking?: string };

const initialConversationId =
  typeof window !== 'undefined' && typeof localStorage !== 'undefined'
    ? localStorage.getItem('conversation_id')
    : null;

export const messages = writable<Message[]>([]);
export const thinking = writable(false);
export const conversationId = writable<string | null>(initialConversationId);

export function setConversationId(id: string) {
  conversationId.set(id);
  if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
    localStorage.setItem('conversation_id', id);
  }
}

export function ensureConversationId(makeId: () => string) {
  let id = get(conversationId);
  if (!id) {
    id = makeId();
    setConversationId(id);
  }
  return id;
}

export function pushMessage(msg: Message) {
  messages.update((list) => [...list, msg]);
}

export function updateMessage(id: string, patch: Partial<Message>) {
  messages.update((list) => list.map((m) => (m.id === id ? { ...m, ...patch } : m)));
}

export function setThinking(value: boolean) {
  thinking.set(value);
}

export function resetChat() {
  messages.set([]);
}
