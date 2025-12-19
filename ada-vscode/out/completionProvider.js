"use strict";
/**
 * InlineCompletionItemProvider for VS Code
 *
 * This is the core of Ada's code completion - provides ghost text
 * suggestions as you type, just like GitHub Copilot.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.AdaCompletionProvider = void 0;
const vscode = __importStar(require("vscode"));
class AdaCompletionProvider {
    client;
    statusBar;
    debounceTimer = null;
    lastCompletion = '';
    stats = {
        completions: 0,
        accepted: 0,
        totalLatency: 0,
        avgLatency: 0,
    };
    constructor(client, statusBar) {
        this.client = client;
        this.statusBar = statusBar;
    }
    async provideInlineCompletionItems(document, position, context, token) {
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
    async getCompletion(document, position, token) {
        this.statusBar.setLoading();
        const config = vscode.workspace.getConfiguration('ada');
        // Get code before cursor (up to ~2000 chars for context)
        const beforeRange = new vscode.Range(new vscode.Position(Math.max(0, position.line - 50), 0), position);
        const codeBefore = document.getText(beforeRange);
        // Get code after cursor (helps with context)
        const afterRange = new vscode.Range(position, new vscode.Position(Math.min(document.lineCount - 1, position.line + 10), 0));
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
            const completionItem = new vscode.InlineCompletionItem(result.text, new vscode.Range(position, position));
            return [completionItem];
        }
        catch (error) {
            console.error('Ada: Completion error:', error);
            this.statusBar.setError();
            return null;
        }
    }
    getStats() {
        return { ...this.stats };
    }
    incrementAccepted() {
        this.stats.accepted++;
    }
}
exports.AdaCompletionProvider = AdaCompletionProvider;
//# sourceMappingURL=completionProvider.js.map