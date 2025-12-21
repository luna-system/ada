/**
 * Tests for MCPToolHandler - intent classification and tool routing
 */
import { MCPToolHandler } from '../src/mcpToolHandler';

describe('MCPToolHandler', () => {
  let handler: MCPToolHandler;

  beforeEach(() => {
    handler = new MCPToolHandler();
  });

  describe('classifyIntent', () => {
    it('should detect pure tool calls', () => {
      const message = 'use introspection to list all files';
      const intent = handler.classifyIntent(message);

      expect(intent.requiresTool).toBe(true);
      expect(intent.tool).toBe('ada_introspect');
    });

    it('should detect compound queries needing tool + reasoning', () => {
      const message = 'introspect and then suggest improvements';
      const intent = handler.classifyIntent(message);

      expect(intent.requiresTool).toBe(true);
      expect(intent.requiresReasoning).toBe(true);
    });

    it('should detect pure chat queries', () => {
      const message = 'hello ada, how are you?';
      const intent = handler.classifyIntent(message);

      expect(intent.requiresTool).toBe(false);
      expect(intent.requiresReasoning).toBe(true);
    });
  });

  describe('buildAugmentedPrompt', () => {
    it('should inject tool results into prompt', () => {
      const original = 'analyze the architecture';
      const toolResult = {
        content: 'Found 15 modules...',
        metadata: {
          tool_name: 'ada_introspect',
          files_accessed: ['context.md'],
          actions_taken: ['analyzed'],
        },
        success: true,
      };

      const augmented = handler.buildAugmentedPrompt(original, toolResult);

      expect(augmented).toContain('Found 15 modules');
      expect(augmented).toContain('analyze the architecture');
    });
  });
});
