"use strict";
/**
 * Ada - Local AI Code Completion
 *
 * GitHub Copilot alternative that runs 100% locally.
 * 103ms Time to First Token. $0/month. Your code never leaves your machine.
 *
 * December 2025 - luna-system
 * License: CC0 (Public Domain)
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
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const completionProvider_1 = require("./completionProvider");
const ollamaClient_1 = require("./ollamaClient");
const statusBar_1 = require("./statusBar");
let completionProvider;
let ollamaClient;
let statusBar;
async function activate(context) {
    console.log('Ada: Activating local AI code completion...');
    // Initialize Ollama client
    const config = vscode.workspace.getConfiguration('ada');
    ollamaClient = new ollamaClient_1.OllamaClient(config.get('ollamaUrl', 'http://localhost:11434'), config.get('model', 'qwen2.5-coder:7b'));
    // Initialize status bar
    statusBar = new statusBar_1.StatusBar();
    context.subscriptions.push(statusBar);
    // Check Ollama connection
    const connected = await ollamaClient.checkConnection();
    if (connected) {
        statusBar.setConnected();
        vscode.window.showInformationMessage('Ada: Connected to Ollama ✓');
    }
    else {
        statusBar.setDisconnected();
        vscode.window.showWarningMessage('Ada: Cannot connect to Ollama. Make sure Ollama is running at ' +
            config.get('ollamaUrl', 'http://localhost:11434'));
    }
    // Initialize completion provider
    completionProvider = new completionProvider_1.AdaCompletionProvider(ollamaClient, statusBar);
    // Register for all languages
    const disposable = vscode.languages.registerInlineCompletionItemProvider({ pattern: '**' }, // All files
    completionProvider);
    context.subscriptions.push(disposable);
    // Register commands
    context.subscriptions.push(vscode.commands.registerCommand('ada.triggerCompletion', async () => {
        await vscode.commands.executeCommand('editor.action.inlineSuggest.trigger');
    }));
    context.subscriptions.push(vscode.commands.registerCommand('ada.toggleEnabled', () => {
        const config = vscode.workspace.getConfiguration('ada');
        const enabled = config.get('enabled', true);
        config.update('enabled', !enabled, true);
        vscode.window.showInformationMessage(`Ada: ${!enabled ? 'Enabled' : 'Disabled'}`);
        statusBar.setEnabled(!enabled);
    }));
    context.subscriptions.push(vscode.commands.registerCommand('ada.showStats', () => {
        const stats = completionProvider.getStats();
        vscode.window.showInformationMessage(`Ada Stats: ${stats.completions} completions, ` +
            `${stats.avgLatency.toFixed(0)}ms avg latency, ` +
            `${stats.accepted} accepted`);
    }));
    // Listen for config changes
    context.subscriptions.push(vscode.workspace.onDidChangeConfiguration(e => {
        if (e.affectsConfiguration('ada')) {
            const newConfig = vscode.workspace.getConfiguration('ada');
            ollamaClient.updateConfig(newConfig.get('ollamaUrl', 'http://localhost:11434'), newConfig.get('model', 'qwen2.5-coder:7b'));
            statusBar.setEnabled(newConfig.get('enabled', true));
        }
    }));
    console.log('Ada: Extension activated! 🔥');
}
function deactivate() {
    console.log('Ada: Deactivating...');
}
//# sourceMappingURL=extension.js.map