/**
 * CompletionProvider - delivers inline code completions
 * 
 * Responsibilities:
 * - Completion item generation
 * - FIM (Fill-In-Middle) prompt formatting
 * - Filtering and ranking
 * 
 * To be moved from: ../../src/completionProvider.ts
 */

import * as vscode from 'vscode';
import { OllamaClient } from 'shared/clients';

export class CompletionProvider implements vscode.InlineCompletionItemProvider {
  constructor(private readonly _ollamaClient: OllamaClient) {}

  async provideInlineCompletionItems(
    document: vscode.TextDocument,
    position: vscode.Position,
    context: vscode.InlineCompletionContext,
    token: vscode.CancellationToken,
  ): Promise<vscode.InlineCompletionItem[]> {
    // TODO: Move completion logic here
    return [];
  }
}

export class GhostTextProvider {
  constructor(private readonly _ollamaClient: OllamaClient) {}

  // TODO: Move ghost text logic here
}
