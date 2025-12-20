"use strict";
/**
 * Ada Brain HTTP client for VS Code extension
 *
 * Connects to Ada's brain service (http://localhost:8000) to get:
 * - RAG context (memories, persona, FAQs)
 * - Specialist capabilities (web search, OCR, etc.)
 * - Persistent conversation memory
 * - Biomimetic features (memory graph, context priming, decay)
 *
 * Replaces standalone Ollama calls to provide full Ada experience in VS Code.
 *
 * December 2025 - luna-system
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.AdaBrainClient = void 0;
const https = __importStar(require("https"));
const http = __importStar(require("http"));
/**
 * Ada Brain client - provides the same interface as OllamaClient
 * but talks to Ada's brain service for full RAG/memory capabilities
 */
class AdaBrainClient {
    baseUrl;
    conversationId;
    model = 'ada-brain'; // Public for compatibility with OllamaClient
    constructor(baseUrl = 'http://localhost:8000', conversationId = 'vscode') {
        this.baseUrl = baseUrl;
        this.conversationId = conversationId;
    }
    updateConfig(baseUrl, _model) {
        // Note: Ada Brain manages its own model configuration
        // We just update the base URL here
        this.baseUrl = baseUrl;
    }
    /**
     * Check if Ada Brain is available
     */
    async checkConnection() {
        try {
            const response = await this.fetch('/v1/healthz', 'GET');
            return response !== null && response.ok === true;
        }
        catch {
            return false;
        }
    }
    /**
     * List available models (proxied from Ada Brain's Ollama connection)
     */
    async listModels() {
        try {
            const response = await this.fetch('/v1/info', 'GET');
            if (!response || !response.llm || !response.llm.model) {
                return [];
            }
            // Ada Brain manages its own model, return that info
            return [{
                    name: response.llm.model,
                    size: 0, // Ada doesn't expose size
                    modifiedAt: new Date().toISOString(),
                }];
        }
        catch {
            return [];
        }
    }
    /**
     * Find the best available model (Ada Brain manages this internally)
     */
    async findBestModel() {
        try {
            const response = await this.fetch('/v1/info', 'GET');
            return response?.llm?.model || null;
        }
        catch {
            return null;
        }
    }
    /**
     * Generate FIM completion (for code completion)
     * Ada Brain can use a specialized model for code completion
     */
    async complete(codeBefore, codeAfter, options) {
        const start = Date.now();
        // Build FIM prompt for Ada Brain
        const prompt = `<｜fim▁begin｜>${codeBefore}<｜fim▁hole｜>${codeAfter}<｜fim▁end｜>`;
        try {
            // Use chat endpoint with code-specialized model
            let fullResponse = '';
            const generator = await this.streamChat(prompt, {
                model: 'qwen2.5-coder:7b', // Use code model for FIM
                maxTokens: options?.maxTokens || 100,
                temperature: options?.temperature || 0.2,
            });
            for await (const chunk of generator) {
                fullResponse += chunk.content;
            }
            const latencyMs = Date.now() - start;
            return {
                text: fullResponse,
                latencyMs,
                tokensGenerated: Math.ceil(fullResponse.length / 4), // Rough estimate
            };
        }
        catch (error) {
            console.error('Ada Brain: Completion error:', error);
            return null;
        }
    }
    /**
     * Chat with streaming response - compatible with OllamaClient interface
     */
    async *chat(messages, options = {}) {
        // Convert messages array to a single prompt string
        let prompt = '';
        if (options.systemPrompt) {
            prompt += `${options.systemPrompt}\n\n`;
        }
        for (const msg of messages) {
            if (msg.role === 'user') {
                prompt += `User: ${msg.content}\n`;
            }
            else if (msg.role === 'assistant') {
                prompt += `Assistant: ${msg.content}\n`;
            }
            else if (msg.role === 'system') {
                prompt += `${msg.content}\n`;
            }
        }
        // Stream from Ada Brain
        const generator = await this.streamChat(prompt, {
            maxTokens: options.maxTokens,
            temperature: options.temperature,
        });
        for await (const chunk of generator) {
            yield chunk;
        }
    }
    /**
     * Generate text from a prompt (non-streaming) - compatible with OllamaClient
     * Used for inline edit where we need the full response at once
     */
    async generate(prompt, options = {}) {
        let fullResponse = '';
        const generator = await this.streamChat(prompt, {
            maxTokens: options.maxTokens,
            temperature: options.temperature,
        });
        for await (const chunk of generator) {
            if (!chunk.done) {
                fullResponse += chunk.content;
            }
        }
        return fullResponse;
    }
    /**
     * Internal method to stream chat from Ada Brain
     */
    streamChat(prompt, options) {
        const payload = {
            prompt,
            conversation_id: options?.conversationId || this.conversationId,
            stream: true,
        };
        // Add optional parameters
        if (options?.model) {
            payload.model = options.model;
        }
        if (options?.maxTokens !== undefined) {
            payload.max_tokens = options.maxTokens;
        }
        if (options?.temperature !== undefined) {
            payload.temperature = options.temperature;
        }
        const url = new URL('/v1/chat/stream', this.baseUrl);
        const isHttps = url.protocol === 'https:';
        const httpModule = isHttps ? https : http;
        return new Promise((resolve, reject) => {
            const requestOptions = {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream',
                },
            };
            const req = httpModule.request(url, requestOptions, (res) => {
                if (res.statusCode !== 200) {
                    reject(new Error(`Ada Brain returned status ${res.statusCode}`));
                    return;
                }
                let buffer = '';
                async function* streamChunks() {
                    for await (const chunk of res) {
                        buffer += chunk.toString();
                        const lines = buffer.split('\n');
                        buffer = lines.pop() || '';
                        for (const line of lines) {
                            if (line.startsWith('data: ')) {
                                const data = line.slice(6);
                                if (data === '[DONE]') {
                                    yield { content: '', done: true };
                                    return;
                                }
                                try {
                                    const parsed = JSON.parse(data);
                                    // Brain API returns {"type": "token", "content": "..."}
                                    // We extract just the content field
                                    const content = parsed.content || '';
                                    if (content) {
                                        yield { content, done: false };
                                    }
                                }
                                catch (e) {
                                    // Skip invalid JSON
                                }
                            }
                        }
                    }
                    // Final chunk
                    yield { content: '', done: true };
                }
                resolve(streamChunks());
            });
            req.on('error', (error) => {
                reject(new Error(`Ada Brain connection error: ${error.message}`));
            });
            req.write(JSON.stringify(payload));
            req.end();
        });
    }
    /**
     * Simple HTTP fetch helper
     */
    async fetch(path, method, body) {
        const url = new URL(path, this.baseUrl);
        const isHttps = url.protocol === 'https:';
        const httpModule = isHttps ? https : http;
        return new Promise((resolve, reject) => {
            const options = {
                method,
                headers: {
                    'Content-Type': 'application/json',
                },
            };
            const req = httpModule.request(url, options, (res) => {
                let data = '';
                res.on('data', (chunk) => {
                    data += chunk;
                });
                res.on('end', () => {
                    if (res.statusCode === 200) {
                        try {
                            resolve(JSON.parse(data));
                        }
                        catch {
                            resolve(data);
                        }
                    }
                    else {
                        reject(new Error(`Request failed with status ${res.statusCode}`));
                    }
                });
            });
            req.on('error', reject);
            if (body) {
                req.write(JSON.stringify(body));
            }
            req.end();
        });
    }
    /**
     * Ingest .ai/ folder contents into Ada Brain's memory.
     * This preloads project context for instant codebase knowledge.
     *
     * @param context Map of filename -> file content
     */
    async ingestProjectContext(context) {
        const response = await this.fetch('/v1/context/ingest', 'POST', { context });
        console.log(`Ingested ${response.files_ingested} files into Ada Brain`);
    }
}
exports.AdaBrainClient = AdaBrainClient;
//# sourceMappingURL=adaBrainClient.js.map