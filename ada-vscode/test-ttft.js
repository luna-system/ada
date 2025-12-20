#!/usr/bin/env node
/**
 * Quick TTFT test for Ada Brain SSE streaming
 * Measures time to first token from VS Code extension perspective
 */

const http = require('http');

const payload = JSON.stringify({
    message: "hi",
    conversation_id: "test",
    stream: true
});

const options = {
    hostname: 'localhost',
    port: 8000,
    path: '/v1/chat/stream',
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Content-Length': payload.length,
        'Accept': 'text/event-stream'
    }
};

const startTime = Date.now();
let firstTokenTime = null;
let tokenCount = 0;
let buffer = '';

console.log('🚀 Testing TTFT to Ada Brain...\n');

const req = http.request(options, (res) => {
    res.on('data', (chunk) => {
        if (!firstTokenTime) {
            firstTokenTime = Date.now() - startTime;
            console.log(`⚡ TTFT: ${firstTokenTime}ms`);
        }
        
        buffer += chunk.toString();
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = line.slice(6);
                
                if (data === '[DONE]') {
                    const totalTime = Date.now() - startTime;
                    console.log(`\n✅ Complete: ${tokenCount} tokens in ${totalTime}ms`);
                    console.log(`📊 Avg: ${(totalTime / tokenCount).toFixed(1)}ms/token`);
                    process.exit(0);
                }
                
                try {
                    const parsed = JSON.parse(data);
                    if (parsed.type === 'done' || parsed.done === true) {
                        const totalTime = Date.now() - startTime;
                        console.log(`\n✅ Complete: ${tokenCount} tokens in ${totalTime}ms`);
                        console.log(`📊 Avg: ${(totalTime / tokenCount).toFixed(1)}ms/token`);
                        process.exit(0);
                    }
                    if (parsed.content) {
                        tokenCount++;
                        process.stdout.write(parsed.content);
                    }
                } catch (e) {
                    // Skip invalid JSON
                }
            }
        }
    });
    
    res.on('end', () => {
        if (!firstTokenTime) {
            console.log('❌ No tokens received!');
            process.exit(1);
        }
    });
});

req.on('error', (error) => {
    console.error('❌ Error:', error.message);
    process.exit(1);
});

req.write(payload);
req.end();

// Timeout after 30 seconds
setTimeout(() => {
    console.log('\n❌ Timeout!');
    process.exit(1);
}, 30000);
