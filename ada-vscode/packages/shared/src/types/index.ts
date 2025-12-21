// Type definitions shared across packages
export * from './toolTypes';
export * from './messageTypes';

import { ToolMetadata } from './toolTypes';

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
