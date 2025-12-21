// Message types for webview/extension communication
export interface ExtensionMessage {
  type: string;
  payload?: any;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  metadata?: any;
  timestamp: number;
}

export interface MetadataMessage {
  type: 'metadata';
  metadata: {
    files_accessed?: string[];
    actions_taken?: string[];
    duration_ms?: number;
  };
}
