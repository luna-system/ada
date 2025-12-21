import * as vscode from 'vscode';

/**
 * Client for Ada Brain REST API
 * Handles chat streaming via Server-Sent Events (SSE)
 */
export class AdaBrainClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async checkConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/v1/healthz`);
      return response.ok;
    } catch {
      return false;
    }
  }

  /**
   * Stream chat responses from Ada Brain
   * Returns async generator that yields chunks
   */
  async *chat(messages: Array<{role: string, content: string}>, options?: any): AsyncGenerator<{content: string, done: boolean}> {
    const userMessage = messages[messages.length - 1].content;
    
    const response = await fetch(`${this.baseUrl}/v1/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: userMessage,
        conversation_id: options?.conversationId
      })
    });

    if (!response.ok) {
      throw new Error(`Brain API error: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              yield { content: '', done: true };
              return;
            }
            
            try {
              const parsed = JSON.parse(data);
              if (parsed.content) {
                yield { content: parsed.content, done: false };
              }
            } catch (e) {
              console.error('[Ada Brain] Failed to parse SSE chunk:', e);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }
}

