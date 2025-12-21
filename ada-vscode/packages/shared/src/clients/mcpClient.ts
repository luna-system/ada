/**
 * MCP (Model Context Protocol) Client for Tool Integration
 * Handles tool execution and metadata embedding
 */
export class MCPClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async executeTool(toolName: string, params: any) {
    // Implementation to be moved from main extension
    throw new Error('Not yet implemented - move from tools.ts');
  }

  async listTools() {
    // Implementation to be moved from main extension
    throw new Error('Not yet implemented');
  }
}
