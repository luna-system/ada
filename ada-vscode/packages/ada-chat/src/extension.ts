/**
 * Ada Chat Extension - Entry Point
 * 
 * Provides conversational AI chat with MCP tool integration
 * Part of the unified Ada Code monorepo
 * 
 * December 2025 - luna+ada
 */

import * as vscode from 'vscode';
import { ChatViewProvider } from './chatViewProvider';

/**
 * Minimal Ada Brain API client for chat streaming
 */
interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface StreamChunk {
  content: string;
  done: boolean;
}

class AdaBrainClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async checkConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/v1/healthz`, {
        method: 'GET'
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  async *chat(messages: Message[], options: Record<string, unknown>): AsyncGenerator<StreamChunk> {
    try {
      console.log('[Ada Brain Client] Sending chat request to:', `${this.baseUrl}/v1/chat/stream`);
      console.log('[Ada Brain Client] Messages:', JSON.stringify(messages).slice(0, 200));
      
      // Brain now accepts OpenAI-style messages array natively!
      let response: Response;
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
          console.error('[Ada Brain Client] Request timed out after 30s');
          controller.abort();
        }, 30000);
        
        console.log('[Ada Brain Client] Starting fetch...');
        response = await fetch(`${this.baseUrl}/v1/chat/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream',
            'X-Client-Type': 'vscode'
          },
          body: JSON.stringify({
            messages,
            ...options
          }),
          signal: controller.signal
        });
        clearTimeout(timeoutId);
        console.log('[Ada Brain Client] Fetch completed!');
      } catch (fetchError) {
        console.error('[Ada Brain Client] Fetch failed:', fetchError);
        throw fetchError;
      }

      console.log('[Ada Brain Client] Response status:', response.status, response.statusText);

      if (!response.ok) {
        throw new Error(`Brain API error: ${response.statusText}`);
      }

      // Handle Server-Sent Events from brain
      const reader = response.body?.getReader();
      if (!reader) {
        console.error('[Ada Brain Client] No response body reader!');
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';
      let yieldCount = 0;

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            console.log('[Ada Brain Client] Reader done, total yields:', yieldCount);
            break;
          }

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const json = JSON.parse(line.slice(6));
                // Brain sends: {type: 'token', content: '...'} or {type: 'done', ...}
                if (json.type === 'token') {
                  yieldCount++;
                  yield {
                    content: json.content || '',
                    done: false
                  };
                } else if (json.type === 'done') {
                  yield {
                    content: '',
                    done: true
                  };
                }
                // Ignore 'thinking' and 'specialist_result' for now
              } catch (parseError) {
                console.error('[Ada Brain Client] JSON parse error:', parseError, 'line:', line);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }
    } catch (error) {
      console.error('[Ada Brain Client] Error:', error);
      yield {
        content: `Error communicating with Ada Brain: ${error instanceof Error ? error.message : 'Unknown error'}`,
        done: true
      };
    }
  }
}

export async function activate(context: vscode.ExtensionContext) {
  console.log('[Ada Chat] Activating...');

  // Initialize Ada Brain client
  const config = vscode.workspace.getConfiguration('ada');
  const brainUrl = config.get<string>('brainUrl', 'http://localhost:8000');
  const brainClient = new AdaBrainClient(brainUrl);

  // Register chat view provider
  const chatProvider = new ChatViewProvider(
    context.extensionUri,
    brainClient
  );

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(
      ChatViewProvider.viewType,
      chatProvider
    )
  );

  // Register commands
  context.subscriptions.push(
    vscode.commands.registerCommand('ada.openChat', () => {
      vscode.commands.executeCommand('ada.chatView.focus');
    })
  );

  console.log('[Ada Chat] Activated successfully!');
}

export function deactivate() {
  console.log('[Ada Chat] Deactivating...');
}

