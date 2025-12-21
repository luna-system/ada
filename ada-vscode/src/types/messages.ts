/**
 * Type-safe message contracts for webview communication
 * Ensures compile-time checking of all messages between extension and webview
 */

// Messages FROM webview TO extension
export type WebviewToExtensionMessage = 
    | { type: 'sendMessage'; message: string }
    | { type: 'clearChat' }
    | { type: 'stopGeneration' };

// Messages FROM extension TO webview
export type ExtensionToWebviewMessage =
    | { type: 'connectionStatus'; connected: boolean; modelCount: number; currentModel: string }
    | { type: 'userMessage'; content: string }
    | { type: 'assistantChunk'; content: string; done?: boolean }
    | { type: 'toolFiles'; files: string[] }
    | { type: 'finalResult'; content: string }
    | { type: 'error'; message: string }
    | { type: 'cleared' }
    | { type: 'generationStart' }
    | { type: 'generationEnd' };
