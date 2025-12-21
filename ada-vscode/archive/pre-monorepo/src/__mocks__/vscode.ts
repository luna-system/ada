/**
 * VS Code API Mock
 * 
 * Minimal mock for testing code that imports vscode.
 * Only mock what we actually need for tests.
 */

export const workspace = {
    getConfiguration: jest.fn(() => ({
        get: jest.fn((key: string, defaultValue?: any) => defaultValue)
    })),
    workspaceFolders: []
};

export const window = {
    showInformationMessage: jest.fn(),
    showErrorMessage: jest.fn(),
    showWarningMessage: jest.fn(),
    createOutputChannel: jest.fn(() => ({
        appendLine: jest.fn(),
        show: jest.fn(),
        dispose: jest.fn()
    }))
};

export const commands = {
    registerCommand: jest.fn(),
    executeCommand: jest.fn()
};

export const Uri = {
    parse: jest.fn((str: string) => ({ toString: () => str })),
    file: jest.fn((path: string) => ({ fsPath: path, toString: () => `file://${path}` }))
};

export class EventEmitter {
    private listeners: Function[] = [];
    event = (listener: Function) => {
        this.listeners.push(listener);
        return { dispose: () => {} };
    };
    fire = (data: any) => this.listeners.forEach(l => l(data));
    dispose = () => { this.listeners = []; };
}

export class Disposable {
    static from(...disposables: { dispose: () => any }[]) {
        return { dispose: () => disposables.forEach(d => d.dispose()) };
    }
}

// Extension context mock
export const ExtensionContext = jest.fn();
