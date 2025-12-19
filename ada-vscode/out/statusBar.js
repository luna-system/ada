"use strict";
/**
 * Status bar item for Ada
 *
 * Shows connection status and latency in the VS Code status bar.
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
exports.StatusBar = void 0;
const vscode = __importStar(require("vscode"));
class StatusBar {
    item;
    enabled = true;
    constructor() {
        this.item = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
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
        if (!this.enabled)
            return;
        this.item.text = '$(loading~spin) Ada';
        this.item.backgroundColor = undefined;
    }
    setLatency(ms) {
        if (!this.enabled) {
            this.setDisabled();
            return;
        }
        // Color code by latency
        if (ms < 200) {
            this.item.text = `$(zap) Ada ${ms}ms`;
        }
        else if (ms < 500) {
            this.item.text = `$(check) Ada ${ms}ms`;
        }
        else {
            this.item.text = `$(watch) Ada ${ms}ms`;
        }
        this.item.backgroundColor = undefined;
    }
    setError() {
        this.item.text = '$(error) Ada';
        this.item.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
    }
    setEnabled(enabled) {
        this.enabled = enabled;
        if (!enabled) {
            this.setDisabled();
        }
        else {
            this.setConnected();
        }
    }
    setDisabled() {
        this.item.text = '$(circle-slash) Ada';
        this.item.backgroundColor = undefined;
    }
    dispose() {
        this.item.dispose();
    }
}
exports.StatusBar = StatusBar;
//# sourceMappingURL=statusBar.js.map