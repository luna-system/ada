/**
 * Status bar item for Ada
 * 
 * Shows connection status and latency in the VS Code status bar.
 */

import * as vscode from 'vscode';

export class StatusBar implements vscode.Disposable {
    private item: vscode.StatusBarItem;
    private enabled: boolean = true;

    constructor() {
        this.item = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            100
        );
        this.item.command = 'ada.toggleEnabled';
        this.item.tooltip = 'Click to toggle Ada code completion';
        this.setDisconnected();
        this.item.show();
    }

    setConnected() {
        if (!this.enabled) {
            this.setDisabled();
            return;
        }
        this.item.text = '$(check) Ada';
        this.item.backgroundColor = undefined;
    }

    setDisconnected() {
        this.item.text = '$(x) Ada';
        this.item.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
    }

    setLoading() {
        if (!this.enabled) return;
        this.item.text = '$(loading~spin) Ada';
        this.item.backgroundColor = undefined;
    }

    setLatency(ms: number) {
        if (!this.enabled) {
            this.setDisabled();
            return;
        }
        
        // Color code by latency
        if (ms < 200) {
            this.item.text = `$(zap) Ada ${ms}ms`;
        } else if (ms < 500) {
            this.item.text = `$(check) Ada ${ms}ms`;
        } else {
            this.item.text = `$(watch) Ada ${ms}ms`;
        }
        this.item.backgroundColor = undefined;
    }

    setError() {
        this.item.text = '$(error) Ada';
        this.item.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
    }

    setEnabled(enabled: boolean) {
        this.enabled = enabled;
        if (!enabled) {
            this.setDisabled();
        } else {
            this.setConnected();
        }
    }

    private setDisabled() {
        this.item.text = '$(circle-slash) Ada';
        this.item.backgroundColor = undefined;
    }

    dispose() {
        this.item.dispose();
    }
}
