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

    try {
        const provider = new MinimalChatProvider(context.extensionUri);
        
        // Use string directly, not static property
        const disposable = vscode.window.registerWebviewViewProvider('ada.chatView', provider);
        context.subscriptions.push(disposable);
        
        console.log('Ada MINIMAL: Chat view registered!');
        vscode.window.showInformationMessage('Ada MINIMAL: Ready!');
    } catch (error) {
        console.error('Ada MINIMAL ERROR:', error);
        vscode.window.showErrorMessage(`Ada MINIMAL ERROR: ${error}`);
    }
}

export function deactivate() {}
