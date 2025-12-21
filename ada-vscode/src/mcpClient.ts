// December 2025 - luna+ada - MCP client for Ada brain
// Uses child_process to avoid ESM/CommonJS issues
import * as vscode from 'vscode';
import { spawn, ChildProcess } from 'child_process';

export interface MCPChatOptions {
    message: string;
    conversationId?: string;
    onToken?: (token: string) => void;
}

interface MCPRequest {
    jsonrpc: string;
    id: number;
    method: string;
    params: any;
}

interface MCPResponse {
    jsonrpc: string;
    id: number;
    result?: any;
    error?: any;
}

export class AdaMCPClient {
    private process: ChildProcess | null = null;
    private requestId = 0;
    private pendingRequests = new Map<number, { resolve: (value: any) => void; reject: (error: any) => void }>();

    async connect(): Promise<void> {
        if (this.process) {
            return; // Already connected
        }

        try {
            const config = vscode.workspace.getConfiguration('ada');
            let mcpServerPath = config.get<string>('mcpServerPath', 'ada-mcp/ada-mcp.sh');

            // Resolve relative paths from workspace root
            if (!mcpServerPath.startsWith('/')) {
                const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
                if (workspaceRoot) {
                    mcpServerPath = `${workspaceRoot}/${mcpServerPath}`;
                }
            }

            console.log('[ADA MCP] Spawning MCP server:', mcpServerPath);

            this.process = spawn(mcpServerPath, [], {
                stdio: ['pipe', 'pipe', 'pipe'],
            });

            // Handle stdout (JSON-RPC responses)
            let buffer = '';
            this.process.stdout?.on('data', (data) => {
                buffer += data.toString();
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.trim()) {
                        try {
                            const response: MCPResponse = JSON.parse(line);
                            const pending = this.pendingRequests.get(response.id);
                            if (pending) {
                                this.pendingRequests.delete(response.id);
                                if (response.error) {
                                    pending.reject(new Error(response.error.message || 'MCP error'));
                                } else {
                                    pending.resolve(response.result);
                                }
                            }
                        } catch (e) {
                            console.error('[ADA MCP] Failed to parse response:', line, e);
                        }
                    }
                }
            });

            // Handle stderr
            this.process.stderr?.on('data', (data) => {
                console.error('[ADA MCP] stderr:', data.toString());
            });

            // Handle exit
            this.process.on('exit', (code) => {
                console.log('[ADA MCP] Process exited with code:', code);
                this.process = null;
            });

            // Perform MCP initialization handshake
            console.log('[ADA MCP] Performing initialization handshake...');
            const initResult = await this.sendRequest('initialize', {
                protocolVersion: '2024-11-05',
                capabilities: {},
                clientInfo: {
                    name: 'ada-vscode',
                    version: '0.1.0',
                },
            });
            console.log('[ADA MCP] Server capabilities:', initResult);

            // Send initialized notification (no response expected)
            if (this.process && this.process.stdin) {
                const notification = {
                    jsonrpc: '2.0',
                    method: 'notifications/initialized',
                };
                this.process.stdin.write(JSON.stringify(notification) + '\n');
            }

            console.log('[ADA MCP] Connected successfully!');
        } catch (error) {
            console.error('[ADA MCP] Connection failed:', error);
            throw new Error(`MCP connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }

    private async sendRequest(method: string, params: any): Promise<any> {
        if (!this.process || !this.process.stdin) {
            throw new Error('MCP client not connected');
        }

        const id = ++this.requestId;
        const request: MCPRequest = {
            jsonrpc: '2.0',
            id,
            method,
            params,
        };

        console.log(`[ADA MCP] Sending request ${id}: ${method}`);
        console.log(`[ADA MCP] Request params:`, JSON.stringify(params, null, 2));

        return new Promise((resolve, reject) => {
            this.pendingRequests.set(id, { resolve, reject });
            this.process!.stdin!.write(JSON.stringify(request) + '\n');

            // Timeout after 120s (matches AdaClient default)
            const timeoutMs = 120000;
            const timeoutHandle = setTimeout(() => {
                if (this.pendingRequests.has(id)) {
                    this.pendingRequests.delete(id);
                    console.error(`[ADA MCP] Request ${id} timed out after ${timeoutMs}ms`);
                    reject(new Error('Request timeout'));
                }
            }, timeoutMs);

            // Clear timeout on resolution
            const originalResolve = this.pendingRequests.get(id)!.resolve;
            const originalReject = this.pendingRequests.get(id)!.reject;
            this.pendingRequests.set(id, {
                resolve: (value: any) => {
                    clearTimeout(timeoutHandle);
                    console.log(`[ADA MCP] Request ${id} completed successfully`);
                    originalResolve(value);
                },
                reject: (error: any) => {
                    clearTimeout(timeoutHandle);
                    console.error(`[ADA MCP] Request ${id} failed:`, error);
                    originalReject(error);
                }
            });
        });
    }

    async chat(options: MCPChatOptions): Promise<string> {
        if (!this.process) {
            await this.connect();
        }

        // Call ada_chat tool via MCP
        // MCP protocol: method is tools/call, params has name and arguments
        const result = await this.sendRequest('tools/call', {
            name: 'ada_chat',
            arguments: {
                message: options.message,
                conversation_id: options.conversationId || undefined,
                // Note: MCP ada_chat doesn't support streaming
            },
        });

        // Extract response text from tool result
        console.log('[ADA MCP] Result structure:', JSON.stringify(result, null, 2));
        
        if (result.content && Array.isArray(result.content) && result.content.length > 0) {
            if (result.content[0].text) {
                return result.content[0].text;
            }
            // Sometimes content might be at top level
            if (typeof result.content === 'string') {
                return result.content;
            }
        }
        
        // Try to extract any text we can find
        if (typeof result === 'string') {
            return result;
        }

        throw new Error(`Unexpected response format from MCP tool. Got: ${JSON.stringify(result)}`);
    }

    async callTool(toolName: string, args: any): Promise<string> {
        if (!this.process) {
            await this.connect();
        }

        // Call any MCP tool directly
        const result = await this.sendRequest('tools/call', {
            name: toolName,
            arguments: args,
        });

        // Extract response text from tool result
        console.log(`[ADA MCP] Tool ${toolName} result:`, JSON.stringify(result, null, 2));
        
        if (result.content && Array.isArray(result.content) && result.content.length > 0) {
            if (result.content[0].text) {
                return result.content[0].text;
            }
        }
        
        throw new Error(`Tool ${toolName} returned unexpected format: ${JSON.stringify(result)}`);
    }

    async disconnect(): Promise<void> {
        if (this.process) {
            this.process.kill();
            this.process = null;
        }
    }
}
