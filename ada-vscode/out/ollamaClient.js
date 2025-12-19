"use strict";
/**
 * Ollama HTTP client for code completion
 *
 * Uses the FIM (Fill-In-Middle) format for qwen2.5-coder
 * which achieves 103ms TTFT on local hardware.
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
exports.OllamaClient = void 0;
const https = __importStar(require("https"));
const http = __importStar(require("http"));
class OllamaClient {
    baseUrl;
    model;
    constructor(baseUrl, model) {
        this.baseUrl = baseUrl;
        this.model = model;
    }
    updateConfig(baseUrl, model) {
        this.baseUrl = baseUrl;
        this.model = model;
    }
    async checkConnection() {
        try {
            const response = await this.fetch('/api/tags', 'GET');
            return response !== null;
        }
        catch {
            return false;
        }
    }
    /**
     * Generate completion using FIM format
     *
     * The FIM (Fill-In-Middle) format is:
     * <|fim_prefix|>code_before<|fim_suffix|>code_after<|fim_middle|>
     *
     * This is what qwen2.5-coder was trained on and produces fast, terse completions.
     */
    async complete(codeBefore, codeAfter, options = {}) {
        const startTime = Date.now();
        // Build FIM prompt
        const prompt = `<|fim_prefix|>${codeBefore}<|fim_suffix|>${codeAfter}<|fim_middle|>`;
        try {
            const response = await this.fetch('/api/generate', 'POST', {
                model: this.model,
                prompt: prompt,
                stream: false,
                options: {
                    temperature: options.temperature ?? 0.2,
                    num_predict: options.maxTokens ?? 128,
                    stop: options.stopSequences ?? ['\n\n', '<|fim', '<|end'],
                },
            });
            if (!response || !response.response) {
                return null;
            }
            const latencyMs = Date.now() - startTime;
            const text = this.cleanCompletion(response.response);
            return {
                text,
                latencyMs,
                tokensGenerated: response.eval_count ?? 0,
            };
        }
        catch (error) {
            console.error('Ada: Completion error:', error);
            return null;
        }
    }
    /**
     * Stream completion for lower perceived latency
     */
    async *streamComplete(codeBefore, codeAfter, options = {}) {
        const prompt = `<|fim_prefix|>${codeBefore}<|fim_suffix|>${codeAfter}<|fim_middle|>`;
        const response = await this.fetchStream('/api/generate', {
            model: this.model,
            prompt: prompt,
            stream: true,
            options: {
                temperature: options.temperature ?? 0.2,
                num_predict: options.maxTokens ?? 128,
                stop: ['\n\n', '<|fim', '<|end'],
            },
        });
        for await (const chunk of response) {
            if (chunk.response) {
                yield chunk.response;
            }
            if (chunk.done) {
                break;
            }
        }
    }
    cleanCompletion(text) {
        // Remove any FIM tokens that leaked through
        let cleaned = text
            .replace(/<\|fim_prefix\|>/g, '')
            .replace(/<\|fim_suffix\|>/g, '')
            .replace(/<\|fim_middle\|>/g, '')
            .replace(/<\|endoftext\|>/g, '')
            .replace(/<\|end\|>/g, '');
        // Trim trailing whitespace but preserve leading (indentation)
        cleaned = cleaned.trimEnd();
        return cleaned;
    }
    async fetch(path, method, body) {
        return new Promise((resolve, reject) => {
            const url = new URL(path, this.baseUrl);
            const isHttps = url.protocol === 'https:';
            const lib = isHttps ? https : http;
            const options = {
                hostname: url.hostname,
                port: url.port || (isHttps ? 443 : 80),
                path: url.pathname,
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                timeout: 30000,
            };
            const req = lib.request(options, (res) => {
                let data = '';
                res.on('data', (chunk) => data += chunk);
                res.on('end', () => {
                    try {
                        resolve(JSON.parse(data));
                    }
                    catch {
                        resolve(data);
                    }
                });
            });
            req.on('error', reject);
            req.on('timeout', () => reject(new Error('Request timeout')));
            if (body) {
                req.write(JSON.stringify(body));
            }
            req.end();
        });
    }
    async *fetchStream(path, body) {
        const url = new URL(path, this.baseUrl);
        const isHttps = url.protocol === 'https:';
        const lib = isHttps ? https : http;
        const options = {
            hostname: url.hostname,
            port: url.port || (isHttps ? 443 : 80),
            path: url.pathname,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: 30000,
        };
        const response = await new Promise((resolve, reject) => {
            const req = lib.request(options, resolve);
            req.on('error', reject);
            req.write(JSON.stringify(body));
            req.end();
        });
        for await (const chunk of response) {
            const lines = chunk.toString().split('\n').filter((l) => l.trim());
            for (const line of lines) {
                try {
                    yield JSON.parse(line);
                }
                catch {
                    // Skip malformed JSON
                }
            }
        }
    }
}
exports.OllamaClient = OllamaClient;
//# sourceMappingURL=ollamaClient.js.map