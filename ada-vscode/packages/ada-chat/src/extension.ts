/**
 * Ada Chat Extension - Entry Point
 * 
 * Provides conversational AI chat with MCP tool integration
 * Part of the unified Ada Code monorepo
 * 
 * December 2025 - luna+ada
 */

import * as vscode from 'vscode';
import { AdaBrainClient } from '@ada-code/shared/clients';
import { ChatViewProvider } from './chatViewProvider';

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

