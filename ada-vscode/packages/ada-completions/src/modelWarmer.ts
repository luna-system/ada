/**
 * ModelWarmer - pre-loads the LLM on startup
 * 
 * Benefits:
 * - First completion is faster (no cold start)
 * - Consistent latency across requests
 * 
 * To be moved from: ../../src/modelWarmer.ts
 */

import { OllamaClient } from '@ada-code/shared/clients';

export class ModelWarmer {
  constructor(private readonly _ollamaClient: OllamaClient) {}

  async warmModel() {
    // TODO: Move model warming logic here
    // Send a small prompt to initialize the model
  }
}
