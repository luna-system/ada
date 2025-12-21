"use strict";
/**
 * Model Warmer Client for Ada VS Code Extension
 *
 * Biomimetic feature: Like motor cortex pre-activation, registers
 * VS Code's connection with Ada Brain to keep code models warm.
 *
 * This ensures <200ms TTFT for chat and completions.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.ModelWarmer = void 0;
class ModelWarmer {
    brainUrl;
    adapterId;
    heartbeatInterval;
    registered = false;
    constructor(brainUrl) {
        this.brainUrl = brainUrl;
        // Unique session ID
        this.adapterId = `vscode-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
    }
    /**
     * Register this VS Code session with Ada Brain.
     * Brain will warm qwen2.5-coder:7b with 4h keep_alive.
     */
    async register() {
        try {
            const response = await fetch(`${this.brainUrl}/v1/adapters/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    adapter_type: 'vscode',
                    adapter_id: this.adapterId
                })
            });
            if (response.ok) {
                const data = await response.json();
                console.log(`Ada: Registered with brain, warming ${data.warm_model}`);
                this.registered = true;
                // Start heartbeat every 60 seconds
                this.heartbeatInterval = setInterval(() => this.heartbeat(), 60000);
            }
        }
        catch (error) {
            console.warn('Ada: Model warmer registration failed (brain may be offline):', error);
            // Don't fail extension activation if brain is offline
        }
    }
    /**
     * Send periodic heartbeat to keep session alive.
     */
    async heartbeat() {
        if (!this.registered) {
            return;
        }
        try {
            await fetch(`${this.brainUrl}/v1/adapters/heartbeat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    adapter_id: this.adapterId
                })
            });
        }
        catch (error) {
            // Silent fail - don't spam console with heartbeat errors
        }
    }
    /**
     * Unregister on extension deactivation.
     */
    async unregister() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = undefined;
        }
        if (!this.registered) {
            return;
        }
        try {
            await fetch(`${this.brainUrl}/v1/adapters/unregister`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    adapter_id: this.adapterId
                })
            });
            console.log('Ada: Unregistered from brain');
            this.registered = false;
        }
        catch (error) {
            // Silent fail on cleanup
        }
    }
    /**
     * Dispose method for VS Code subscription
     */
    dispose() {
        this.unregister();
    }
}
exports.ModelWarmer = ModelWarmer;
//# sourceMappingURL=modelWarmer.js.map