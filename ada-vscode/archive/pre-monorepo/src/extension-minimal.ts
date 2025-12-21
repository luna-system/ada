/**
 * Ada - MINIMAL TEST VERSION
 * Just the chat sidebar, nothing else.
 */

import * as vscode from 'vscode';

class MinimalChatProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'ada.chatView';

    constructor(private readonly _extensionUri: vscode.Uri) {}

    public resolveWebviewView(webviewView: vscode.WebviewView) {
        webviewView.webview.options = { enableScripts: true };
        webviewView.webview.html = `
            <!DOCTYPE html>
            <html>
            <body style="background:#1a1a1a;color:#00ff00;padding:20px;font-family:monospace;">
                <h2>🤖 Ada Chat</h2>
                <p>Minimal test version - IT WORKS!</p>
                <p>Time: ${new Date().toISOString()}</p>
            </body>
            </html>
        `;
    }
}

export function activate(context: vscode.ExtensionContext) {
    console.log('Ada MINIMAL: Starting activation...');
    vscode.window.showInformationMessage('Ada MINIMAL: Activating!');

    const provider = new MinimalChatProvider(context.extensionUri);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(MinimalChatProvider.viewType, provider)
    );

    console.log('Ada MINIMAL: Chat view registered!');
    vscode.window.showInformationMessage('Ada MINIMAL: Ready!');
}

export function deactivate() {}
