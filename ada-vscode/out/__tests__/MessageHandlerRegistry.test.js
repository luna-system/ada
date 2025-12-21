"use strict";
/**
 * Tests for MessageHandlerRegistry
 *
 * These are pure TypeScript unit tests - no VS Code dependencies!
 * Run with: npm test
 */
Object.defineProperty(exports, "__esModule", { value: true });
const MessageHandlerRegistry_1 = require("../handlers/MessageHandlerRegistry");
describe('MessageHandlerRegistry', () => {
    let registry;
    beforeEach(() => {
        registry = new MessageHandlerRegistry_1.MessageHandlerRegistry();
    });
    describe('register', () => {
        it('should register a handler for a message type', () => {
            const handler = jest.fn();
            registry.register('testMessage', handler);
            expect(registry.hasHandler('testMessage')).toBe(true);
        });
        it('should return false for unregistered types', () => {
            expect(registry.hasHandler('nonexistent')).toBe(false);
        });
    });
    describe('handle', () => {
        it('should call the registered handler with data', async () => {
            const handler = jest.fn();
            registry.register('sendMessage', handler);
            await registry.handle({ type: 'sendMessage', message: 'hello' });
            expect(handler).toHaveBeenCalledWith({ type: 'sendMessage', message: 'hello' });
        });
        it('should handle async handlers', async () => {
            let resolved = false;
            const asyncHandler = jest.fn(async () => {
                await new Promise(r => setTimeout(r, 10));
                resolved = true;
            });
            registry.register('asyncTest', asyncHandler);
            await registry.handle({ type: 'asyncTest' });
            expect(resolved).toBe(true);
        });
        it('should not throw for unregistered message types', async () => {
            // Should just log warning, not throw
            await expect(registry.handle({ type: 'unknown' })).resolves.not.toThrow();
        });
        it('should handle multiple handlers independently', async () => {
            const handler1 = jest.fn();
            const handler2 = jest.fn();
            registry.register('type1', handler1);
            registry.register('type2', handler2);
            await registry.handle({ type: 'type1' });
            expect(handler1).toHaveBeenCalled();
            expect(handler2).not.toHaveBeenCalled();
        });
    });
    describe('real-world message types', () => {
        it('should handle sendMessage type', async () => {
            const handler = jest.fn();
            registry.register('sendMessage', handler);
            await registry.handle({ type: 'sendMessage', message: 'explain this code' });
            expect(handler).toHaveBeenCalledWith({
                type: 'sendMessage',
                message: 'explain this code'
            });
        });
        it('should handle clearChat type', async () => {
            const handler = jest.fn();
            registry.register('clearChat', handler);
            await registry.handle({ type: 'clearChat' });
            expect(handler).toHaveBeenCalled();
        });
        it('should handle stopGeneration type', async () => {
            const handler = jest.fn();
            registry.register('stopGeneration', handler);
            await registry.handle({ type: 'stopGeneration' });
            expect(handler).toHaveBeenCalled();
        });
    });
});
//# sourceMappingURL=MessageHandlerRegistry.test.js.map