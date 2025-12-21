/**
 * Type-safe message contracts for webview communication
 * Ensures compile-time checking of all messages between extension and webview
 */

/**
 * Tool Metadata - extracted from MCP tool responses
 * Provides transparency about what files/actions a tool accessed
 */
export interface ToolMetadata {
    toolName: string;
    filesAccessed: string[];
    actionsTaken: string[];
    durationMs?: number;
}

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
    | { type: 'toolMetadata'; metadata: ToolMetadata }  // NEW: Structured metadata from envelope
    | { type: 'finalResult'; content: string }
    | { type: 'error'; message: string }
    | { type: 'cleared' }
    | { type: 'generationStart' }
    | { type: 'generationEnd' };
