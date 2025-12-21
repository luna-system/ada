/**
 * Ada Chat Extension
 * 
 * Provides conversational AI chat in VSCode
 * - ChatViewProvider manages the webview
 * - Streams responses from Ada Brain API
 * - Renders tool metadata and transparency
 */

import * as vscode from 'vscode';
import { AdaBrainClient } from '@ada-code/shared/clients';

export async function activate(context: vscode.ExtensionContext) {
  console.log('Ada Chat extension activating...');
  
  // Initialize shared clients
  const adaBrainClient = new AdaBrainClient();
  
  // Register chat view provider
  // TODO: Move ChatViewProvider from main extension here
  
  console.log('Ada Chat extension activated');
}

export function deactivate() {
  // Cleanup
}
