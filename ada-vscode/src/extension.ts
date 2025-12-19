/**
 * Ada - Local AI Code Completion
 * 
 * GitHub Copilot alternative that runs 100% locally.
 * 103ms Time to First Token. $0/month. Your code never leaves your machine.
 * 
 * December 2025 - luna-system
 * License: CC0 (Public Domain)
 */

import * as vscode from 'vscode';
import { AdaCompletionProvider } from './completionProvider';
import { OllamaClient } from './ollamaClient';
import { StatusBar } from './statusBar';

let completionProvider: AdaCompletionProvider;
let ollamaClient: OllamaClient;
let statusBar: StatusBar;

export async function activate(context: vscode.ExtensionContext) {
    console.log('Ada: Activating local AI code completion...');

    // Initialize Ollama client
    const config = vscode.workspace.getConfiguration('ada');
    ollamaClient = new OllamaClient(
        config.get('ollamaUrl', 'http://localhost:11434'),
        config.get('model', 'qwen2.5-coder:7b')
    );

    // Initialize status bar
    statusBar = new StatusBar();
    context.subscriptions.push(statusBar);

    // Check Ollama connection
    const connected = await ollamaClient.checkConnection();
    if (connected) {
        statusBar.setConnected();
        vscode.window.showInformationMessage('Ada: Connected to Ollama ✓');
    } else {
        statusBar.setDisconnected();
        vscode.window.showWarningMessage(
            'Ada: Cannot connect to Ollama. Make sure Ollama is running at ' + 
            config.get('ollamaUrl', 'http://localhost:11434')
        );
    }

    // Initialize completion provider
    completionProvider = new AdaCompletionProvider(ollamaClient, statusBar);

    // Register for all languages
    const disposable = vscode.languages.registerInlineCompletionItemProvider(
        { pattern: '**' },  // All files
        completionProvider
    );
    context.subscriptions.push(disposable);

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('ada.triggerCompletion', async () => {
            await vscode.commands.executeCommand('editor.action.inlineSuggest.trigger');
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('ada.toggleEnabled', () => {
            const config = vscode.workspace.getConfiguration('ada');
            const enabled = config.get('enabled', true);
            config.update('enabled', !enabled, true);
            vscode.window.showInformationMessage(`Ada: ${!enabled ? 'Enabled' : 'Disabled'}`);
            statusBar.setEnabled(!enabled);
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('ada.showStats', () => {
            const stats = completionProvider.getStats();
            vscode.window.showInformationMessage(
                `Ada Stats: ${stats.completions} completions, ` +
                `${stats.avgLatency.toFixed(0)}ms avg latency, ` +
                `${stats.accepted} accepted`
            );
        })
    );

    // Listen for config changes
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('ada')) {
                const newConfig = vscode.workspace.getConfiguration('ada');
                ollamaClient.updateConfig(
                    newConfig.get('ollamaUrl', 'http://localhost:11434'),
                    newConfig.get('model', 'qwen2.5-coder:7b')
                );
                statusBar.setEnabled(newConfig.get('enabled', true));
            }
        })
    );

    console.log('Ada: Extension activated! 🔥');
}

export function deactivate() {
    console.log('Ada: Deactivating...');
}
