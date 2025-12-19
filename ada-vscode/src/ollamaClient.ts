/**
 * Ollama HTTP client for code completion
 * 
 * Uses the FIM (Fill-In-Middle) format for qwen2.5-coder
 * which achieves 103ms TTFT on local hardware.
 */

import * as https from 'https';
import * as http from 'http';

export interface CompletionResult {
    text: string;
    latencyMs: number;
    tokensGenerated: number;
}

export class OllamaClient {
    private baseUrl: string;
    private model: string;

    constructor(baseUrl: string, model: string) {
        this.baseUrl = baseUrl;
        this.model = model;
    }

    updateConfig(baseUrl: string, model: string) {
        this.baseUrl = baseUrl;
        this.model = model;
    }

    async checkConnection(): Promise<boolean> {
        try {
            const response = await this.fetch('/api/tags', 'GET');
            return response !== null;
        } catch {
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
    async complete(
        codeBefore: string,
        codeAfter: string,
        options: {
            maxTokens?: number;
            temperature?: number;
            stopSequences?: string[];
        } = {}
    ): Promise<CompletionResult | null> {
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
        } catch (error) {
            console.error('Ada: Completion error:', error);
            return null;
        }
    }

    /**
     * Stream completion for lower perceived latency
     */
    async *streamComplete(
        codeBefore: string,
        codeAfter: string,
        options: {
            maxTokens?: number;
            temperature?: number;
        } = {}
    ): AsyncGenerator<string, void, unknown> {
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

    private cleanCompletion(text: string): string {
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

    private async fetch(path: string, method: string, body?: object): Promise<any> {
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
                    } catch {
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

    private async *fetchStream(path: string, body: object): AsyncGenerator<any, void, unknown> {
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

        const response = await new Promise<http.IncomingMessage>((resolve, reject) => {
            const req = lib.request(options, resolve);
            req.on('error', reject);
            req.write(JSON.stringify(body));
            req.end();
        });

        for await (const chunk of response) {
            const lines = chunk.toString().split('\n').filter((l: string) => l.trim());
            for (const line of lines) {
                try {
                    yield JSON.parse(line);
                } catch {
                    // Skip malformed JSON
                }
            }
        }
    }
}
