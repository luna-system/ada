"use strict";
/**
 * Message Handler Registry
 * Decouples message routing from business logic
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.MessageHandlerRegistry = void 0;
class MessageHandlerRegistry {
    handlers = new Map();
    register(type, handler) {
        this.handlers.set(type, handler);
    }
    async handle(data) {
        const handler = this.handlers.get(data.type);
        if (handler) {
            await handler(data);
        }
        else {
            console.warn(`No handler registered for message type: ${data.type}`);
        }
    }
    hasHandler(type) {
        return this.handlers.has(type);
    }
}
exports.MessageHandlerRegistry = MessageHandlerRegistry;
//# sourceMappingURL=MessageHandlerRegistry.js.map