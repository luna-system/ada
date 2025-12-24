import { writable, get } from 'svelte/store';

export type Role = 'user' | 'assistant';
export type Message = { 
  id: string; 
  role: Role; 
  text: string; 
  thinking?: string;
  reasoning?: {
    steps: Array<{ phase: string; content: string; step: number }>;
    tools: Array<{ name: string; args?: any; result?: any }>;
    warnings: string[];
    isComplete: boolean;
  };
};

const initialConversationId =
  typeof window !== 'undefined' && typeof localStorage !== 'undefined'
    ? localStorage.getItem('conversation_id')
    : null;

const initialReasoningMode =
  typeof window !== 'undefined' && typeof localStorage !== 'undefined'
    ? localStorage.getItem('reasoning_mode') === 'true'
    : false;

export const messages = writable<Message[]>([]);
export const thinking = writable(false);
export const conversationId = writable<string | null>(initialConversationId);
export const reasoningMode = writable<boolean>(initialReasoningMode);
export const currentReasoning = writable<{
  active: boolean;
  messageId?: string;
  steps: Array<{ phase: string; content: string; step: number }>;
  tools: Array<{ name: string; args?: any; result?: any }>;
  warnings: string[];
}>({
  active: false,
  steps: [],
  tools: [],
  warnings: []
});

export function setConversationId(id: string) {
  conversationId.set(id);
  if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
    localStorage.setItem('conversation_id', id);
  }
}

export function setReasoningMode(enabled: boolean) {
  reasoningMode.set(enabled);
  if (typeof window !== 'undefined' && typeof localStorage !== 'undefined') {
    localStorage.setItem('reasoning_mode', String(enabled));
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

export function setCurrentReasoning(update: Partial<{
  active: boolean;
  messageId?: string;
  steps: Array<{ phase: string; content: string; step: number }>;
  tools: Array<{ name: string; args?: any; result?: any }>;
  warnings: string[];
}>) {
  currentReasoning.update(current => ({ ...current, ...update }));
}

export function addReasoningStep(phase: string, content: string, step: number) {
  currentReasoning.update(current => ({
    ...current,
    steps: [...current.steps, { phase, content, step }]
  }));
}

export function addReasoningTool(name: string, args?: any, result?: any) {
  currentReasoning.update(current => {
    const existingIndex = current.tools.findIndex(t => t.name === name && !t.result);
    if (existingIndex >= 0 && result) {
      // Update existing tool with result
      const updatedTools = [...current.tools];
      updatedTools[existingIndex] = { ...updatedTools[existingIndex], result };
      return { ...current, tools: updatedTools };
    } else {
      // Add new tool request
      return { ...current, tools: [...current.tools, { name, args, result }] };
    }
  });
}

export function addReasoningWarning(message: string) {
  currentReasoning.update(current => ({
    ...current,
    warnings: [...current.warnings, message]
  }));
}

export function resetReasoning() {
  currentReasoning.set({
    active: false,
    steps: [],
    tools: [],
    warnings: []
  });
}

export function resetChat() {
  messages.set([]);
  resetReasoning();
}
