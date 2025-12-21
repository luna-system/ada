"use strict";
/**
 * Ada - MINIMAL TEST VERSION
 * Just the chat sidebar, nothing else.
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
class MinimalChatProvider {
    _extensionUri;
    static viewType = 'ada.chatView';
    constructor(_extensionUri) {
        this._extensionUri = _extensionUri;
    }
    resolveWebviewView(webviewView) {
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
function activate(context) {
    console.log('Ada MINIMAL: Starting activation...');
    vscode.window.showInformationMessage('Ada MINIMAL: Activating!');
    try {
        const provider = new MinimalChatProvider(context.extensionUri);
        // Use string directly, not static property
        const disposable = vscode.window.registerWebviewViewProvider('ada.chatView', provider);
        context.subscriptions.push(disposable);
        console.log('Ada MINIMAL: Chat view registered!');
        vscode.window.showInformationMessage('Ada MINIMAL: Ready!');
    }
    catch (error) {
        console.error('Ada MINIMAL ERROR:', error);
        vscode.window.showErrorMessage(`Ada MINIMAL ERROR: ${error}`);
    }
}
function deactivate() { }
//# sourceMappingURL=extension-minimal-working.js.map