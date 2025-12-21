/**
 * Ada Completions Extension
 * 
 * Provides inline code completion and ghost text in VSCode
 * - CompletionProvider delivers code completions
 * - GhostTextProvider shows ghost text suggestions
 * - ModelWarmer pre-loads the LLM
 */

import * as vscode from 'vscode';
import { OllamaClient } from '@ada-code/shared/clients';

export async function activate(context: vscode.ExtensionContext) {
  console.log('Ada Completions extension activating...');
  
  // Initialize shared clients
  const ollamaClient = new OllamaClient();
  
  // Register completion providers
  // TODO: Move CompletionProvider and GhostTextProvider here
  
  // Warm the model on startup
  // TODO: Move ModelWarmer logic here
  
  console.log('Ada Completions extension activated');
}

export function deactivate() {
  // Cleanup
}
