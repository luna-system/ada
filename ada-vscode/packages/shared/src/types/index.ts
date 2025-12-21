// Type definitions shared across packages
export interface ToolMetadata {
  files_accessed?: string[];
  actions_taken?: string[];
  duration_ms?: number;
  [key: string]: any;
}

export interface ToolResult {
  content: string;
  metadata?: ToolMetadata;
  success: boolean;
}

export interface AdaRequest {
  message: string;
  context?: any;
  userId?: string;
}

export interface AdaResponse {
  content: string;
  metadata?: ToolMetadata;
  timestamp: number;
}

export * from './messageTypes';
