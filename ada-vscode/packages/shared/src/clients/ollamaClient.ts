/**
 * Ollama Client for Direct LLM Access
 * Used for code completion, model warming, ghost text
 */
export class OllamaClient {
  private baseUrl: string;
  private model: string;

  constructor(baseUrl: string = 'http://localhost:11434', model: string = 'qwen2.5-coder:7b') {
    this.baseUrl = baseUrl;
    this.model = model;
  }

  async generate(prompt: string, options?: any) {
    // Implementation to be moved from main extension
    throw new Error('Not yet implemented - move from ollamaClient.ts');
  }

  async warmModel() {
    // Implementation to be moved from main extension
    throw new Error('Not yet implemented - move from modelWarmer.ts');
  }
}
