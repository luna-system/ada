/**
 * Message Handler Registry
 * Decouples message routing from business logic
 */

import { WebviewToExtensionMessage } from '../types/messages';

type MessageHandler = (data: any) => Promise<void> | void;

export class MessageHandlerRegistry {
    private handlers = new Map<string, MessageHandler>();
    
    register(type: string, handler: MessageHandler): void {
        this.handlers.set(type, handler);
    }
    
    async handle(data: WebviewToExtensionMessage): Promise<void> {
        const handler = this.handlers.get(data.type);
        if (handler) {
            await handler(data);
        } else {
            console.warn(`No handler registered for message type: ${data.type}`);
        }
    }
    
    hasHandler(type: string): boolean {
        return this.handlers.has(type);
    }
}
