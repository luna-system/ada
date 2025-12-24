export type ReasoningStreamMessage =
  | { type: 'reasoning_start'; metadata?: any }
  | { type: 'reasoning_step'; content: string; phase?: string; step?: number }
  | { type: 'thought_chunk'; content: string }
  | { type: 'tool_request'; tool_name: string; arguments?: any }
  | { type: 'tool_result'; tool_name: string; result?: any }
  | { type: 'parallel_tools'; tools?: string[] }
  | { type: 'convergence'; solution?: string }
  | { type: 'warning'; message?: string }
  | { type: 'reasoning_complete'; summary?: string; conversation_id?: string }
  | { type: 'error'; error?: string };

export type ReasoningCallbacks = {
  onReasoningStart?: (metadata?: any) => void;
  onReasoningStep?: (content: string, phase?: string, step?: number) => void;
  onThoughtChunk?: (content: string) => void;
  onToolRequest?: (toolName: string, args?: any) => void;
  onToolResult?: (toolName: string, result?: any) => void;
  onParallelTools?: (tools?: string[]) => void;
  onConvergence?: (solution?: string) => void;
  onWarning?: (message?: string) => void;
  onReasoningComplete?: (summary?: string, conversationId?: string) => void;
  onError?: (err: Error) => void;
};

export async function streamReasoning(params: {
  message: string;
  conversationId: string;
  maxIterations?: number;
  availableTools?: string[];
  entity?: string;
  signal?: AbortSignal;
} & ReasoningCallbacks) {
  const { 
    message, 
    conversationId, 
    maxIterations = 10,
    availableTools,
    entity,
    signal,
    onReasoningStart,
    onReasoningStep,
    onThoughtChunk,
    onToolRequest,
    onToolResult,
    onParallelTools,
    onConvergence,
    onWarning,
    onReasoningComplete,
    onError
  } = params;

  const res = await fetch('/api/chat/reason', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
      max_iterations: maxIterations,
      available_tools: availableTools,
      entity: entity || undefined
    }),
    signal
  });
  
  if (!res.ok) {
    throw new Error(`Reasoning request failed: ${res.status} ${res.statusText}`);
  }
  
  if (!res.body) {
    throw new Error('No response body');
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() ?? '';
    
    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;
      
      const dataStr = line.slice(6);
      let data: ReasoningStreamMessage;
      
      try {
        data = JSON.parse(dataStr);
      } catch {
        continue;
      }
      
      switch (data.type) {
        case 'reasoning_start':
          onReasoningStart?.(data.metadata);
          break;
        case 'reasoning_step':
          onReasoningStep?.(data.content, data.phase, data.step);
          break;
        case 'thought_chunk':
          onThoughtChunk?.(data.content);
          break;
        case 'tool_request':
          onToolRequest?.(data.tool_name, data.arguments);
          break;
        case 'tool_result':
          onToolResult?.(data.tool_name, data.result);
          break;
        case 'parallel_tools':
          onParallelTools?.(data.tools);
          break;
        case 'convergence':
          onConvergence?.(data.solution);
          break;
        case 'warning':
          onWarning?.(data.message);
          break;
        case 'reasoning_complete':
          onReasoningComplete?.(data.summary, data.conversation_id);
          break;
        case 'error':
          const err = new Error(data.error || 'Reasoning stream error');
          onError?.(err);
          throw err;
      }
    }
  }
}