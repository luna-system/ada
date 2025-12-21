import * as vscode from 'vscode';

/**
 * Client for Ada Brain REST API
 * Handles chat, streaming, and introspection
 */
export class AdaBrainClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async chat(message: string, context?: any) {
    // Implementation to be moved from main extension
    throw new Error('Not yet implemented - move from chatViewProvider.ts');
  }

  async streamChat(message: string, context?: any) {
    // Implementation to be moved from main extension
    throw new Error('Not yet implemented - move from chatViewProvider.ts');
  }
}
