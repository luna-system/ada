/**
 * ChatViewProvider - manages the webview for chat UI
 * 
 * Responsibilities:
 * - WebView panel lifecycle
 * - Message routing between extension and webview
 * - Streaming response handling
 * - Metadata extraction and rendering
 * 
 * To be moved from: ../../src/chatViewProvider.ts
 */

import * as vscode from 'vscode';
import { AdaBrainClient } from '@ada-code/shared/clients';

export class ChatViewProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = 'ada.chatView';
  private _view?: vscode.WebviewView;

  constructor(
    private readonly _extensionUri: vscode.Uri,
    private readonly _adaBrainClient: AdaBrainClient
  ) {}

  public resolveWebviewView(
    webviewView: vscode.WebviewView,
    context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken,
  ) {
    this._view = webviewView;

    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [this._extensionUri]
    };

    webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

    webviewView.webview.onDidReceiveMessage(data => {
      this._handleMessage(data);
    });
  }

  private _getHtmlForWebview(webview: vscode.Webview) {
    // TODO: Move HTML/CSS/JS from main extension
    return `
      <!DOCTYPE html>
      <html>
        <head>
          <style>
            body { font-family: sans-serif; padding: 10px; }
          </style>
        </head>
        <body>
          <div id="chat"></div>
          <script src="${webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'chat.js'))}"></script>
        </body>
      </html>
    `;
  }

  private _handleMessage(message: any) {
    // TODO: Move message handling logic here
    switch (message.command) {
      case 'chat':
        this._streamResponse(message.text);
        break;
    }
  }

  private async _streamResponse(userMessage: string) {
    // TODO: Implement streaming response handling
    // Include metadata extraction
  }
}
