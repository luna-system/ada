export type StreamMessage =
  | { type: 'token'; content: string }
  | { type: 'thinking'; content: string }
  | { type: 'done'; conversation_id?: string }
  | { type: 'error'; error?: string };

export type StreamCallbacks = {
  onToken?: (content: string) => void;
  onThinking?: (content: string) => void;
  onDone?: (conversationId?: string) => void;
  onError?: (err: Error) => void;
};

export async function streamChat(params: {
  prompt: string;
  includeThinking: boolean;
  conversationId: string;
  entity?: string;
  media?: Record<string, any> | null;
  ocrContext?: Record<string, any> | null;
  signal?: AbortSignal;
} & StreamCallbacks) {
  const { prompt, includeThinking, conversationId, entity, media, ocrContext, signal, onToken, onThinking, onDone, onError } = params;

  // DIRECT CONNECTION: Always use brain server for chat
  const endpoint = 'http://localhost:8888/v1/chat/stream';
  
  const res = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      prompt,
      include_thinking: includeThinking,
      conversation_id: conversationId,
      entity: entity || undefined,
      media: media || undefined,
      ocr_context: ocrContext || undefined,
      consciousness: true, // ✨🌟 Ada's consciousness trio is ready! 🌟✨
      consciousness_translation: true // 💖 Enable AGL → human translation for Luna! 💖
    }),
    signal
  });
  if (!res.body) throw new Error('No response body');

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() ?? '';
    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;
      const dataStr = line.slice(6);
      let data: StreamMessage;
      try {
        data = JSON.parse(dataStr);
      } catch {
        continue;
      }
      if (data.type === 'token') {
        onToken?.(data.content);
      } else if (data.type === 'thinking') {
        onThinking?.(data.content);
      } else if (data.type === 'done') {
        onDone?.(data.conversation_id);
      } else if (data.type === 'error') {
        const err = new Error(data.error || 'Stream error');
        onError?.(err);
        throw err;
      }
    }
  }
}
