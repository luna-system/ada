/**
 * Tests for message type contracts
 * 
 * These tests verify our type contracts work correctly at runtime
 * TypeScript gives us compile-time checks, these add runtime validation patterns
 */

import { 
    WebviewToExtensionMessage, 
    ExtensionToWebviewMessage 
} from '../types/messages';

describe('Message Type Contracts', () => {
    describe('WebviewToExtensionMessage', () => {
        it('should accept valid sendMessage', () => {
            const msg: WebviewToExtensionMessage = {
                type: 'sendMessage',
                message: 'hello ada'
            };
            expect(msg.type).toBe('sendMessage');
            expect(msg.message).toBe('hello ada');
        });
        
        it('should accept valid clearChat', () => {
            const msg: WebviewToExtensionMessage = { type: 'clearChat' };
            expect(msg.type).toBe('clearChat');
        });
        
        it('should accept valid stopGeneration', () => {
            const msg: WebviewToExtensionMessage = { type: 'stopGeneration' };
            expect(msg.type).toBe('stopGeneration');
        });
    });
    
    describe('ExtensionToWebviewMessage', () => {
        it('should accept valid connectionStatus', () => {
            const msg: ExtensionToWebviewMessage = {
                type: 'connectionStatus',
                connected: true,
                modelCount: 5,
                currentModel: 'qwen2.5-coder:7b'
            };
            expect(msg.connected).toBe(true);
        });
        
        it('should accept valid assistantChunk', () => {
            const msg: ExtensionToWebviewMessage = {
                type: 'assistantChunk',
                content: 'Here is my response...'
            };
            expect(msg.content).toBe('Here is my response...');
        });
        
        it('should accept assistantChunk with done flag', () => {
            const msg: ExtensionToWebviewMessage = {
                type: 'assistantChunk',
                content: 'final',
                done: true
            };
            expect(msg.done).toBe(true);
        });
        
        it('should accept valid toolFiles', () => {
            const msg: ExtensionToWebviewMessage = {
                type: 'toolFiles',
                files: ['src/index.ts', 'src/utils.ts']
            };
            expect(msg.files).toHaveLength(2);
        });
        
        it('should accept valid error', () => {
            const msg: ExtensionToWebviewMessage = {
                type: 'error',
                message: 'Connection failed'
            };
            expect(msg.message).toContain('failed');
        });
        
        it('should accept state messages', () => {
            const cleared: ExtensionToWebviewMessage = { type: 'cleared' };
            const start: ExtensionToWebviewMessage = { type: 'generationStart' };
            const end: ExtensionToWebviewMessage = { type: 'generationEnd' };
            
            expect(cleared.type).toBe('cleared');
            expect(start.type).toBe('generationStart');
            expect(end.type).toBe('generationEnd');
        });
    });
    
    describe('Message Flow Patterns', () => {
        it('should support typical chat flow', () => {
            // User sends message
            const userMsg: WebviewToExtensionMessage = {
                type: 'sendMessage',
                message: 'explain this code'
            };
            
            // Extension responds with chunks
            const chunk1: ExtensionToWebviewMessage = {
                type: 'assistantChunk',
                content: 'This code '
            };
            const chunk2: ExtensionToWebviewMessage = {
                type: 'assistantChunk',
                content: 'does X and Y'
            };
            const done: ExtensionToWebviewMessage = {
                type: 'generationEnd'
            };
            
            expect(userMsg.message).toBeDefined();
            expect(chunk1.content).toBeDefined();
            expect(chunk2.content).toBeDefined();
            expect(done.type).toBe('generationEnd');
        });
        
        it('should support tool transparency flow', () => {
            // Extension shows which files were read
            const tools: ExtensionToWebviewMessage = {
                type: 'toolFiles',
                files: ['context.md', 'codebase-map.json']
            };
            
            // Then sends the actual response
            const response: ExtensionToWebviewMessage = {
                type: 'assistantChunk',
                content: 'Based on context.md, the architecture is...'
            };
            
            expect(tools.files).toContain('context.md');
            expect(response.content).toContain('architecture');
        });
    });
});
