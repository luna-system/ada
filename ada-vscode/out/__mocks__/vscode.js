"use strict";
/**
 * VS Code API Mock
 *
 * Minimal mock for testing code that imports vscode.
 * Only mock what we actually need for tests.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.ExtensionContext = exports.Disposable = exports.EventEmitter = exports.Uri = exports.commands = exports.window = exports.workspace = void 0;
exports.workspace = {
    getConfiguration: jest.fn(() => ({
        get: jest.fn((key, defaultValue) => defaultValue)
    })),
    workspaceFolders: []
};
exports.window = {
    showInformationMessage: jest.fn(),
    showErrorMessage: jest.fn(),
    showWarningMessage: jest.fn(),
    createOutputChannel: jest.fn(() => ({
        appendLine: jest.fn(),
        show: jest.fn(),
        dispose: jest.fn()
    }))
};
exports.commands = {
    registerCommand: jest.fn(),
    executeCommand: jest.fn()
};
exports.Uri = {
    parse: jest.fn((str) => ({ toString: () => str })),
    file: jest.fn((path) => ({ fsPath: path, toString: () => `file://${path}` }))
};
class EventEmitter {
    listeners = [];
    event = (listener) => {
        this.listeners.push(listener);
        return { dispose: () => { } };
    };
    fire = (data) => this.listeners.forEach(l => l(data));
    dispose = () => { this.listeners = []; };
}
exports.EventEmitter = EventEmitter;
class Disposable {
    static from(...disposables) {
        return { dispose: () => disposables.forEach(d => d.dispose()) };
    }
}
exports.Disposable = Disposable;
// Extension context mock
exports.ExtensionContext = jest.fn();
//# sourceMappingURL=vscode.js.map