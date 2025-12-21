/**
 * InlineCompletionItemProvider for VS Code
 * 
 * This is the core of Ada's code completion - provides ghost text
 * suggestions as you type, just like GitHub Copilot.
 */

import * as vscode from 'vscode';
import { OllamaClient } from './ollamaClient';
import { StatusBar } from './statusBar';

interface CompletionStats {
    completions: number;
    accepted: number;
    totalLatency: number;
    avgLatency: number;
}

export class AdaCompletionProvider implements vscode.InlineCompletionItemProvider {
    private client: OllamaClient;
    private statusBar: StatusBar;
    private debounceTimer: NodeJS.Timeout | null = null;
    private lastCompletion: string = '';
    private stats: CompletionStats = {
        completions: 0,
        accepted: 0,
        totalLatency: 0,
        avgLatency: 0,
    };

    constructor(client: OllamaClient, statusBar: StatusBar) {
        this.client = client;
        this.statusBar = statusBar;
    }

    async provideInlineCompletionItems(
        document: vscode.TextDocument,
        position: vscode.Position,
        context: vscode.InlineCompletionContext,
        token: vscode.CancellationToken
    ): Promise<vscode.InlineCompletionItem[] | null> {
        // Check if enabled
        const config = vscode.workspace.getConfiguration('ada');
        if (!config.get('enabled', true)) {
            return null;
        }

        // Clear previous debounce
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }

        // Debounce to avoid hammering the model
        const debounceMs = config.get('debounceMs', 300);
        
        return new Promise((resolve) => {
            this.debounceTimer = setTimeout(async () => {
                if (token.isCancellationRequested) {
                    resolve(null);
                    return;
                }

                const result = await this.getCompletion(document, position, token);
                resolve(result);
            }, debounceMs);
        });
    }

    private async getCompletion(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken
    ): Promise<vscode.InlineCompletionItem[] | null> {
        this.statusBar.setLoading();

        const config = vscode.workspace.getConfiguration('ada');

        // Get code before cursor (up to ~2000 chars for context)
        const beforeRange = new vscode.Range(
            new vscode.Position(Math.max(0, position.line - 50), 0),
            position
        );
        const codeBefore = document.getText(beforeRange);

        // Get code after cursor (helps with context)
        const afterRange = new vscode.Range(
            position,
            new vscode.Position(Math.min(document.lineCount - 1, position.line + 10), 0)
        );
        const codeAfter = document.getText(afterRange);

        // Skip if line is empty or just whitespace
        const currentLine = document.lineAt(position.line).text;
        const beforeCursor = currentLine.substring(0, position.character);
        if (beforeCursor.trim().length === 0 && position.character < 2) {
            this.statusBar.setConnected();
            return null;
        }

        try {
            const result = await this.client.complete(codeBefore, codeAfter, {
                maxTokens: config.get('maxTokens', 128),
                temperature: config.get('temperature', 0.2),
            });

            if (token.isCancellationRequested) {
                this.statusBar.setConnected();
                return null;
            }

            if (!result || !result.text || result.text.trim().length === 0) {
                this.statusBar.setConnected();
                return null;
            }

            // Update stats
            this.stats.completions++;
            this.stats.totalLatency += result.latencyMs;
            this.stats.avgLatency = this.stats.totalLatency / this.stats.completions;
            this.lastCompletion = result.text;

            this.statusBar.setLatency(result.latencyMs);

            // Create completion item
            const completionItem = new vscode.InlineCompletionItem(
                result.text,
                new vscode.Range(position, position)
            );

            return [completionItem];
        } catch (error) {
            console.error('Ada: Completion error:', error);
            this.statusBar.setError();
            return null;
        }
    }

    getStats(): CompletionStats {
        return { ...this.stats };
    }

    incrementAccepted() {
        this.stats.accepted++;
    }
}
