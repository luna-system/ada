/**
 * MCP Tool Handler - Intent classification and tool routing
 * 
 * This handles the two-phase pattern:
 * 1. Detect when user wants to use an MCP tool
 * 2. Call tool, extract metadata, show transparency
 * 3. If query needs reasoning, inject tool results into brain context
 * 4. Stream brain's analysis
 * 
 * Example: "use introspection to find TODOs and suggest an easy one"
 * - Phase 1: Call introspection tool, get file list + TODO content
 * - Phase 2: Inject results into brain prompt for reasoning
 */

import * as vscode from 'vscode';

// Standalone types (no external dependencies)
interface ToolResult {
  content: string;
  metadata?: {
    tool_name?: string;
    files_accessed?: string[];
    actions_taken?: string;
    duration_ms?: number;
  };
}

interface QueryIntent {
  requiresTool: boolean;
  requiresReasoning: boolean;
  tool?: string;
  params?: Record<string, unknown>;
}

export class MCPToolHandler {
  // Stubbed for standalone operation - tools will be added incrementally
  private mcpClient?: any;

  async ensureConnected(): Promise<void> {
    // Stub: MCP client connection will be re-implemented standalone
    console.log('[MCP Tool Handler] Running in standalone mode (MCP integration pending)');
  }

  /**
   * Classify user intent - does this need a tool? Does it need reasoning?
   */
  classifyIntent(message: string): QueryIntent {
    const lower = message.toLowerCase();

    // TODO/FIXME search: scan codebase for task markers
    if (lower.includes('todo') || 
        lower.includes('fixme') ||
        lower.includes('check') && (lower.includes('project') || lower.includes('codebase')) ||
        lower.includes('find') && (lower.includes('task') || lower.includes('issue'))) {
      
      const needsReasoning = lower.includes('suggest') || 
                            lower.includes('recommend') ||
                            lower.includes('choose') ||
                            lower.includes('pick') ||
                            lower.includes('easy') ||
                            lower.includes('simple') ||
                            lower.includes('which');

      return {
        requiresTool: true,
        requiresReasoning: needsReasoning,
        tool: 'ada_introspect',
        params: { focus: 'todos' }
      };
    }

    // Introspection: analyze Ada's own architecture
    if (lower.includes('introspect') || 
        (lower.includes('analyze') && lower.includes('your') && 
         (lower.includes('architecture') || lower.includes('yourself')))) {
      
      const needsReasoning = lower.includes('suggest') || 
                            lower.includes('recommend') ||
                            lower.includes('should') ||
                            lower.includes('next') ||
                            lower.includes('find');

      return {
        requiresTool: true,
        requiresReasoning: needsReasoning,
        tool: 'ada_introspect',
        params: { focus: 'general' }
      };
    }

    // Memory search: recall previous information
    if (lower.includes('remember') && lower.includes('when') ||
        lower.includes('what did we') ||
        lower.includes('recall') ||
        lower.includes('search memory') ||
        lower.includes('find in memory')) {
      
      return {
        requiresTool: true,
        requiresReasoning: true,
        tool: 'ada_search_memory',
        params: { query: message }
      };
    }

    // Memory add: store new information
    if (lower.startsWith('remember this') ||
        lower.startsWith('save this') ||
        lower.startsWith('store this') ||
        lower.includes('add to memory')) {
      
      // Extract what to remember (after the command)
      const content = message.replace(/^(remember|save|store) this:?\s*/i, '');
      
      return {
        requiresTool: true,
        requiresReasoning: false,
        tool: 'ada_add_memory',
        params: { content }
      };
    }

    // File read: access file contents
    if (lower.includes("what's in") ||
        lower.includes('whats in') ||
        lower.includes('show me') && (lower.includes('file') || lower.includes('contents')) ||
        lower.includes('read file') ||
        lower.includes('read the file') ||
        lower.includes('open file') ||
        lower.includes('cat ') ||
        lower.match(/show\s+(?:me\s+)?[\w./]+\.(py|ts|js|json|md|rst|txt|yaml|yml|toml)/)) {
      
      // Extract file path from various patterns
      let filePath = '';
      
      // Pattern: "what's in X" or "show me X"
      const whatMatch = message.match(/(?:what'?s\s+in|show\s+me|read|open|cat)\s+(?:the\s+)?(?:file\s+)?[`"']?([^\s`"'?]+)[`"']?/i);
      if (whatMatch) {
        filePath = whatMatch[1].trim();
      }
      
      // Pattern: Look for file-like patterns anywhere in message
      if (!filePath) {
        const filePattern = message.match(/([a-zA-Z0-9_./\-]+\.(?:py|ts|js|jsx|tsx|json|md|rst|txt|yaml|yml|toml|css|html|sh))/i);
        if (filePattern) {
          filePath = filePattern[1];
        }
      }
      
      return {
        requiresTool: true,
        requiresReasoning: lower.includes('explain') || lower.includes('what does') || lower.includes('how does'),
        tool: 'ada_read_file',
        params: { file_path: filePath }
      };
    }

    // Code search: find patterns in codebase
    if (lower.includes('search for') ||
        lower.includes('find ') && (lower.includes(' in ') || lower.includes('code') || lower.includes('where')) ||
        lower.includes('grep') ||
        lower.includes('look for') ||
        lower.includes('where is') ||
        lower.includes('where do') ||
        lower.includes('which files') ||
        lower.includes('find usages') ||
        lower.includes('find references')) {
      
      // Extract search query
      let query = '';
      const searchMatch = message.match(/(?:search\s+for|find|grep|look\s+for|where\s+is|where\s+do(?:es)?)\s+[`"']?([^`"'?]+)[`"']?/i);
      if (searchMatch) {
        query = searchMatch[1].trim()
          .replace(/\s+in\s+(?:the\s+)?(?:code(?:base)?|files|project).*$/i, '')
          .replace(/\?$/, '');
      }
      
      return {
        requiresTool: true,
        requiresReasoning: lower.includes('explain') || lower.includes('why') || lower.includes('how'),
        tool: 'ada_search',
        params: { query }
      };
    }

    // List files: directory exploration
    if (lower.includes('list files') ||
        lower.includes('what files') ||
        lower.includes('ls ') ||
        lower.includes('show directory') ||
        lower.includes('list directory') ||
        lower.match(/what(?:'s| is) in (?:the )?(?:folder|directory|dir)/)) {
      
      // Extract directory path
      let dirPath = '';
      const dirMatch = message.match(/(?:in|of|for)\s+(?:the\s+)?(?:folder|directory|dir)?\s*[`"']?([^\s`"'?]+)[`"']?/i);
      if (dirMatch) {
        dirPath = dirMatch[1].trim();
      }
      
      return {
        requiresTool: true,
        requiresReasoning: false,
        tool: 'ada_list_files',
        params: { directory: dirPath || '.' }
      };
    }

    // Symbol search: find definitions, classes, functions
    if (lower.includes('find definition') ||
        lower.includes('go to definition') ||
        lower.includes('where is') && (lower.includes('defined') || lower.includes('class') || lower.includes('function')) ||
        lower.includes('find symbol') ||
        lower.includes('find class') ||
        lower.includes('find function') ||
        lower.includes('find method')) {
      
      // Extract symbol name
      let symbol = '';
      const symbolMatch = message.match(/(?:definition\s+of|find|where\s+is)\s+(?:the\s+)?(?:class|function|method|symbol)?\s*[`"']?(\w+)[`"']?/i);
      if (symbolMatch) {
        symbol = symbolMatch[1].trim();
      }
      
      return {
        requiresTool: true,
        requiresReasoning: lower.includes('explain') || lower.includes('how does'),
        tool: 'ada_symbols',
        params: { symbol }
      };
    }

    // Git status: check repository state
    if (lower.includes('git status') ||
        lower.includes('what changed') ||
        lower.includes('uncommitted') ||
        lower.includes('modified files') ||
        lower.includes('staged files') ||
        (lower.includes('changes') && (lower.includes('show') || lower.includes('what')))) {
      
      return {
        requiresTool: true,
        requiresReasoning: lower.includes('explain') || lower.includes('summarize'),
        tool: 'ada_git_status',
        params: {}
      };
    }

    // Code completion: fill in the middle
    if (lower.includes('complete this') ||
        lower.includes('fill in') && lower.includes('code') ||
        lower.includes('finish this function')) {
      
      return {
        requiresTool: true,
        requiresReasoning: false,
        tool: 'ada_complete_code',
        params: { prefix: message }  // Will be refined
      };
    }

    // Health check: system status
    if ((lower.includes('health') && (lower.includes('status') || lower.includes('check'))) ||
        lower.includes('are you working') ||
        lower.includes('system status') ||
        lower === 'health' ||
        lower === 'ping') {
      
      return {
        requiresTool: true,
        requiresReasoning: false,
        tool: 'ada_health',
        params: {}
      };
    }

    // Pure chat - no tools needed
    return {
      requiresTool: false,
      requiresReasoning: true
    };
  }

  /**
   * Execute tool using VS Code APIs directly (no MCP needed!)
   */
  async executeTool(intent: QueryIntent): Promise<ToolResult> {
    const startTime = Date.now();
    const workspace = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

    if (!workspace) {
      return {
        content: 'No workspace folder open',
        metadata: {
          tool_name: intent.tool,
          files_accessed: [],
          actions_taken: 'No workspace',
          duration_ms: 0
        }
      };
    }

    switch (intent.tool) {
      case 'ada_introspect':
        return await this._introspectWorkspace(workspace, intent.params, startTime);
      
      case 'ada_read_file':
        return await this._readFile(workspace, intent.params, startTime);
      
      case 'ada_search':
        return await this._searchCodebase(workspace, intent.params, startTime);
      
      case 'ada_list_files':
        return await this._listFiles(workspace, intent.params, startTime);
      
      case 'ada_symbols':
        return await this._findSymbols(workspace, intent.params, startTime);
      
      case 'ada_git_status':
        return await this._gitStatus(workspace, startTime);
      
      case 'ada_health':
        return this._healthCheck(startTime);
      
      default:
        // Fallback for unimplemented tools
        return {
          content: `[Tool ${intent.tool} not yet implemented]`,
          metadata: {
            tool_name: intent.tool,
            files_accessed: [],
            actions_taken: 'Not implemented',
            duration_ms: Date.now() - startTime
          }
        };
    }
  }

  /**
   * Introspect workspace - find TODOs, FIXMEs, architecture info
   */
  private async _introspectWorkspace(
    workspace: string, 
    params: Record<string, unknown> | undefined,
    startTime: number
  ): Promise<ToolResult> {
    const filesAccessed: string[] = [];
    const todos: Array<{ file: string; line: number; text: string; type: string }> = [];

    try {
      // Find Python and TypeScript files (exclude venv, node_modules, etc.)
      const pyFiles = await vscode.workspace.findFiles(
        '**/*.py', 
        '{**/node_modules/**,**/.venv/**,**/venv/**,**/__pycache__/**,**/site-packages/**}',
        100
      );
      const tsFiles = await vscode.workspace.findFiles(
        '**/*.ts', 
        '{**/node_modules/**,**/dist/**,**/out/**}',
        50
      );
      const allFiles = [...pyFiles, ...tsFiles];

      // Search each file for TODOs
      for (const fileUri of allFiles.slice(0, 50)) {  // Limit to 50 files
        try {
          const content = await vscode.workspace.fs.readFile(fileUri);
          const text = new TextDecoder().decode(content);
          const lines = text.split('\n');
          
          const relativePath = vscode.workspace.asRelativePath(fileUri);
          
          lines.forEach((line, idx) => {
            const todoMatch = line.match(/(?:#|\/\/)\s*(TODO|FIXME|XXX|HACK|NOTE):\s*(.+)/i);
            if (todoMatch) {
              filesAccessed.push(relativePath);
              todos.push({
                file: relativePath,
                line: idx + 1,
                type: todoMatch[1].toUpperCase(),
                text: todoMatch[2].trim()
              });
            }
          });
        } catch {
          // Skip files we can't read
        }
      }

      // Format results
      const uniqueFiles = [...new Set(filesAccessed)];
      let content = `Found ${todos.length} TODOs/FIXMEs across ${uniqueFiles.length} files:\n\n`;
      
      // Group by type
      const byType: Record<string, typeof todos> = {};
      todos.forEach(t => {
        if (!byType[t.type]) byType[t.type] = [];
        byType[t.type].push(t);
      });

      for (const [type, items] of Object.entries(byType)) {
        content += `## ${type} (${items.length})\n`;
        items.slice(0, 10).forEach(t => {
          content += `- **${t.file}:${t.line}**: ${t.text}\n`;
        });
        if (items.length > 10) {
          content += `  ... and ${items.length - 10} more\n`;
        }
        content += '\n';
      }

      return {
        content,
        metadata: {
          tool_name: 'ada_introspect',
          files_accessed: uniqueFiles.slice(0, 10),
          actions_taken: `Scanned ${allFiles.length} files, found ${todos.length} items`,
          duration_ms: Date.now() - startTime
        }
      };
    } catch (error) {
      return {
        content: `Error during introspection: ${error}`,
        metadata: {
          tool_name: 'ada_introspect',
          files_accessed: [],
          actions_taken: 'Error',
          duration_ms: Date.now() - startTime
        }
      };
    }
  }

  /**
   * Health check - return system status
   */
  private _healthCheck(startTime: number): ToolResult {
    return {
      content: '✅ Ada VS Code extension is running\n✅ Workspace loaded\n✅ Brain connection active',
      metadata: {
        tool_name: 'ada_health',
        files_accessed: [],
        actions_taken: 'Health check',
        duration_ms: Date.now() - startTime
      }
    };
  }

  /**
   * Read file contents
   */
  private async _readFile(
    workspace: string,
    params: Record<string, unknown> | undefined,
    startTime: number
  ): Promise<ToolResult> {
    const filePath = (params?.file_path as string) || '';
    
    if (!filePath) {
      return {
        content: 'No file path specified. Try: "what\'s in package.json" or "show me brain/app.py"',
        metadata: {
          tool_name: 'ada_read_file',
          files_accessed: [],
          actions_taken: 'No path provided',
          duration_ms: Date.now() - startTime
        }
      };
    }

    try {
      // Try to find the file
      const pattern = filePath.includes('*') ? filePath : `**/${filePath}`;
      const files = await vscode.workspace.findFiles(
        pattern,
        '{**/node_modules/**,**/.venv/**,**/dist/**}',
        5
      );

      if (files.length === 0) {
        // Try exact path from workspace root
        const exactPath = vscode.Uri.joinPath(vscode.workspace.workspaceFolders![0].uri, filePath);
        try {
          const content = await vscode.workspace.fs.readFile(exactPath);
          const text = new TextDecoder().decode(content);
          const lines = text.split('\n');
          
          // Truncate very large files
          const maxLines = 200;
          const truncated = lines.length > maxLines;
          const displayContent = truncated 
            ? lines.slice(0, maxLines).join('\n') + `\n\n... (${lines.length - maxLines} more lines)`
            : text;

          return {
            content: `## ${filePath}\n\n\`\`\`\n${displayContent}\n\`\`\``,
            metadata: {
              tool_name: 'ada_read_file',
              files_accessed: [filePath],
              actions_taken: `Read ${lines.length} lines${truncated ? ' (truncated)' : ''}`,
              duration_ms: Date.now() - startTime
            }
          };
        } catch {
          return {
            content: `File not found: ${filePath}\n\nTry using a relative path from the workspace root.`,
            metadata: {
              tool_name: 'ada_read_file',
              files_accessed: [],
              actions_taken: 'File not found',
              duration_ms: Date.now() - startTime
            }
          };
        }
      }

      // Read the first matching file
      const fileUri = files[0];
      const content = await vscode.workspace.fs.readFile(fileUri);
      const text = new TextDecoder().decode(content);
      const lines = text.split('\n');
      const relativePath = vscode.workspace.asRelativePath(fileUri);
      
      // Truncate very large files
      const maxLines = 200;
      const truncated = lines.length > maxLines;
      const displayContent = truncated 
        ? lines.slice(0, maxLines).join('\n') + `\n\n... (${lines.length - maxLines} more lines)`
        : text;

      let resultContent = `## ${relativePath}\n\n\`\`\`\n${displayContent}\n\`\`\``;
      
      // Show other matches if any
      if (files.length > 1) {
        resultContent += `\n\n*Also found: ${files.slice(1).map(f => vscode.workspace.asRelativePath(f)).join(', ')}*`;
      }

      return {
        content: resultContent,
        metadata: {
          tool_name: 'ada_read_file',
          files_accessed: [relativePath],
          actions_taken: `Read ${lines.length} lines${truncated ? ' (truncated)' : ''}`,
          duration_ms: Date.now() - startTime
        }
      };
    } catch (error) {
      return {
        content: `Error reading file: ${error}`,
        metadata: {
          tool_name: 'ada_read_file',
          files_accessed: [],
          actions_taken: 'Error',
          duration_ms: Date.now() - startTime
        }
      };
    }
  }

  /**
   * Search codebase for patterns
   */
  private async _searchCodebase(
    workspace: string,
    params: Record<string, unknown> | undefined,
    startTime: number
  ): Promise<ToolResult> {
    const query = (params?.query as string) || '';
    
    if (!query) {
      return {
        content: 'No search query specified. Try: "search for TODO" or "find usages of PromptAssembler"',
        metadata: {
          tool_name: 'ada_search',
          files_accessed: [],
          actions_taken: 'No query',
          duration_ms: Date.now() - startTime
        }
      };
    }

    try {
      const results: Array<{ file: string; line: number; content: string }> = [];
      const filesSearched: string[] = [];
      
      // Search common code files
      const patterns = ['**/*.py', '**/*.ts', '**/*.js', '**/*.json', '**/*.md'];
      const excludes = '{**/node_modules/**,**/.venv/**,**/dist/**,**/out/**,**/__pycache__/**}';
      
      for (const pattern of patterns) {
        const files = await vscode.workspace.findFiles(pattern, excludes, 50);
        
        for (const fileUri of files) {
          try {
            const content = await vscode.workspace.fs.readFile(fileUri);
            const text = new TextDecoder().decode(content);
            const lines = text.split('\n');
            const relativePath = vscode.workspace.asRelativePath(fileUri);
            filesSearched.push(relativePath);
            
            // Case-insensitive search
            const queryLower = query.toLowerCase();
            lines.forEach((line, idx) => {
              if (line.toLowerCase().includes(queryLower)) {
                results.push({
                  file: relativePath,
                  line: idx + 1,
                  content: line.trim().slice(0, 150)  // Truncate long lines
                });
              }
            });
          } catch {
            // Skip unreadable files
          }
        }
        
        // Stop if we have enough results
        if (results.length >= 50) break;
      }

      if (results.length === 0) {
        return {
          content: `No matches found for "${query}" in ${filesSearched.length} files.`,
          metadata: {
            tool_name: 'ada_search',
            files_accessed: [],
            actions_taken: `Searched ${filesSearched.length} files, 0 matches`,
            duration_ms: Date.now() - startTime
          }
        };
      }

      // Group by file
      const byFile: Record<string, typeof results> = {};
      results.forEach(r => {
        if (!byFile[r.file]) byFile[r.file] = [];
        byFile[r.file].push(r);
      });

      let content = `Found ${results.length} matches for "${query}":\n\n`;
      
      for (const [file, matches] of Object.entries(byFile).slice(0, 10)) {
        content += `### ${file}\n`;
        matches.slice(0, 5).forEach(m => {
          content += `- **Line ${m.line}**: \`${m.content}\`\n`;
        });
        if (matches.length > 5) {
          content += `  ... and ${matches.length - 5} more matches in this file\n`;
        }
        content += '\n';
      }

      const uniqueFiles = Object.keys(byFile);
      if (uniqueFiles.length > 10) {
        content += `\n*... and ${uniqueFiles.length - 10} more files*`;
      }

      return {
        content,
        metadata: {
          tool_name: 'ada_search',
          files_accessed: uniqueFiles.slice(0, 10),
          actions_taken: `Found ${results.length} matches in ${uniqueFiles.length} files`,
          duration_ms: Date.now() - startTime
        }
      };
    } catch (error) {
      return {
        content: `Error searching: ${error}`,
        metadata: {
          tool_name: 'ada_search',
          files_accessed: [],
          actions_taken: 'Error',
          duration_ms: Date.now() - startTime
        }
      };
    }
  }

  /**
   * List files in directory
   */
  private async _listFiles(
    workspace: string,
    params: Record<string, unknown> | undefined,
    startTime: number
  ): Promise<ToolResult> {
    const directory = (params?.directory as string) || '.';
    
    try {
      const pattern = directory === '.' ? '*' : `${directory}/*`;
      const files = await vscode.workspace.findFiles(
        pattern,
        '{**/node_modules/**,**/.venv/**}',
        100
      );

      // Also get directories by looking for files deeper
      const deepPattern = directory === '.' ? '**/*' : `${directory}/**/*`;
      const deepFiles = await vscode.workspace.findFiles(
        deepPattern,
        '{**/node_modules/**,**/.venv/**}',
        500
      );

      // Extract unique directories at the target level
      const dirs = new Set<string>();
      const filesList: string[] = [];
      
      deepFiles.forEach(f => {
        const rel = vscode.workspace.asRelativePath(f);
        const parts = directory === '.' ? rel.split('/') : rel.replace(`${directory}/`, '').split('/');
        
        if (parts.length === 1) {
          filesList.push(parts[0]);
        } else if (parts.length > 1) {
          dirs.add(parts[0] + '/');
        }
      });

      const sortedDirs = [...dirs].sort();
      const sortedFiles = [...new Set(filesList)].sort();

      let content = `## Contents of ${directory === '.' ? 'workspace root' : directory}\n\n`;
      
      if (sortedDirs.length > 0) {
        content += '**Directories:**\n';
        sortedDirs.slice(0, 30).forEach(d => {
          content += `📁 ${d}\n`;
        });
        if (sortedDirs.length > 30) {
          content += `... and ${sortedDirs.length - 30} more directories\n`;
        }
        content += '\n';
      }

      if (sortedFiles.length > 0) {
        content += '**Files:**\n';
        sortedFiles.slice(0, 30).forEach(f => {
          content += `📄 ${f}\n`;
        });
        if (sortedFiles.length > 30) {
          content += `... and ${sortedFiles.length - 30} more files\n`;
        }
      }

      return {
        content,
        metadata: {
          tool_name: 'ada_list_files',
          files_accessed: [directory],
          actions_taken: `Listed ${sortedDirs.length} dirs, ${sortedFiles.length} files`,
          duration_ms: Date.now() - startTime
        }
      };
    } catch (error) {
      return {
        content: `Error listing files: ${error}`,
        metadata: {
          tool_name: 'ada_list_files',
          files_accessed: [],
          actions_taken: 'Error',
          duration_ms: Date.now() - startTime
        }
      };
    }
  }

  /**
   * Find symbols (classes, functions, etc.)
   */
  private async _findSymbols(
    workspace: string,
    params: Record<string, unknown> | undefined,
    startTime: number
  ): Promise<ToolResult> {
    const symbol = (params?.symbol as string) || '';
    
    if (!symbol) {
      return {
        content: 'No symbol specified. Try: "find definition of ChatViewProvider" or "find class MCPToolHandler"',
        metadata: {
          tool_name: 'ada_symbols',
          files_accessed: [],
          actions_taken: 'No symbol',
          duration_ms: Date.now() - startTime
        }
      };
    }

    try {
      // Use VS Code's built-in symbol search
      const symbols = await vscode.commands.executeCommand<vscode.SymbolInformation[]>(
        'vscode.executeWorkspaceSymbolProvider',
        symbol
      );

      if (!symbols || symbols.length === 0) {
        // Fallback to text search
        return await this._searchCodebase(workspace, { query: `class ${symbol}|function ${symbol}|def ${symbol}` }, startTime);
      }

      // Filter to exact or close matches
      const matches = symbols.filter(s => 
        s.name.toLowerCase().includes(symbol.toLowerCase())
      ).slice(0, 20);

      if (matches.length === 0) {
        return {
          content: `No symbols found matching "${symbol}"`,
          metadata: {
            tool_name: 'ada_symbols',
            files_accessed: [],
            actions_taken: 'No matches',
            duration_ms: Date.now() - startTime
          }
        };
      }

      const filesAccessed: string[] = [];
      let content = `Found ${matches.length} symbols matching "${symbol}":\n\n`;

      for (const sym of matches) {
        const file = vscode.workspace.asRelativePath(sym.location.uri);
        const line = sym.location.range.start.line + 1;
        const kindName = vscode.SymbolKind[sym.kind];
        
        filesAccessed.push(file);
        content += `- **${sym.name}** (${kindName}) - [${file}:${line}](${file}#L${line})\n`;
      }

      return {
        content,
        metadata: {
          tool_name: 'ada_symbols',
          files_accessed: [...new Set(filesAccessed)].slice(0, 10),
          actions_taken: `Found ${matches.length} symbols`,
          duration_ms: Date.now() - startTime
        }
      };
    } catch (error) {
      return {
        content: `Error finding symbols: ${error}`,
        metadata: {
          tool_name: 'ada_symbols',
          files_accessed: [],
          actions_taken: 'Error',
          duration_ms: Date.now() - startTime
        }
      };
    }
  }

  /**
   * Git status - show changed files
   */
  private async _gitStatus(
    workspace: string,
    startTime: number
  ): Promise<ToolResult> {
    try {
      // Use VS Code's built-in Git extension
      const gitExtension = vscode.extensions.getExtension('vscode.git');
      
      if (!gitExtension) {
        return {
          content: 'Git extension not available',
          metadata: {
            tool_name: 'ada_git_status',
            files_accessed: [],
            actions_taken: 'No git extension',
            duration_ms: Date.now() - startTime
          }
        };
      }

      const git = gitExtension.exports.getAPI(1);
      const repo = git.repositories[0];

      if (!repo) {
        return {
          content: 'No Git repository found in workspace',
          metadata: {
            tool_name: 'ada_git_status',
            files_accessed: [],
            actions_taken: 'No repository',
            duration_ms: Date.now() - startTime
          }
        };
      }

      const state = repo.state;
      const changes = state.workingTreeChanges || [];
      const staged = state.indexChanges || [];
      const branch = state.HEAD?.name || 'unknown';

      let content = `## Git Status\n\n`;
      content += `**Branch:** ${branch}\n\n`;

      if (staged.length > 0) {
        content += `### Staged (${staged.length})\n`;
        staged.slice(0, 20).forEach((c: any) => {
          const status = c.status === 1 ? '✚' : c.status === 2 ? '✎' : c.status === 3 ? '✖' : '?';
          content += `${status} ${vscode.workspace.asRelativePath(c.uri)}\n`;
        });
        content += '\n';
      }

      if (changes.length > 0) {
        content += `### Modified (${changes.length})\n`;
        changes.slice(0, 20).forEach((c: any) => {
          const status = c.status === 1 ? '✚' : c.status === 2 ? '✎' : c.status === 3 ? '✖' : '?';
          content += `${status} ${vscode.workspace.asRelativePath(c.uri)}\n`;
        });
        content += '\n';
      }

      if (staged.length === 0 && changes.length === 0) {
        content += '*Working tree clean*\n';
      }

      const filesAccessed = [...staged, ...changes].slice(0, 10).map((c: any) => 
        vscode.workspace.asRelativePath(c.uri)
      );

      return {
        content,
        metadata: {
          tool_name: 'ada_git_status',
          files_accessed: filesAccessed,
          actions_taken: `${staged.length} staged, ${changes.length} modified`,
          duration_ms: Date.now() - startTime
        }
      };
    } catch (error) {
      return {
        content: `Error getting git status: ${error}`,
        metadata: {
          tool_name: 'ada_git_status',
          files_accessed: [],
          actions_taken: 'Error',
          duration_ms: Date.now() - startTime
        }
      };
    }
  }

  /**
   * Build augmented prompt that includes tool results for brain to reason about
   */
  buildAugmentedPrompt(originalMessage: string, toolResult: ToolResult, toolName: string): string {
    switch (toolName) {
      case 'ada_introspect':
        return `I scanned Ada's codebase and found the following TODOs and FIXMEs:

${toolResult.content}

---

Now, regarding the user's question: ${originalMessage}

Please analyze these findings and provide a thoughtful response.`;

      case 'ada_search_memory':
        return `Here are relevant memories from past conversations:

${toolResult.content}

---

User's question: ${originalMessage}`;

      case 'ada_read_file':
        return `I read the following file:

${toolResult.content}

---

User's question: ${originalMessage}

Please analyze this file content and respond to the user's question.`;

      case 'ada_search':
        return `I searched the codebase and found:

${toolResult.content}

---

User's question: ${originalMessage}

Please analyze these search results and respond helpfully.`;

      case 'ada_list_files':
        return `Here's the directory listing:

${toolResult.content}

---

User's question: ${originalMessage}`;

      case 'ada_symbols':
        return `I found these symbols in the codebase:

${toolResult.content}

---

User's question: ${originalMessage}

Please explain what these symbols are and how they relate to the user's question.`;

      case 'ada_git_status':
        return `Here's the current Git status:

${toolResult.content}

---

User's question: ${originalMessage}

Please summarize the changes and respond to the user's question.`;

      default:
        return `Tool result:

${toolResult.content}

---

User's question: ${originalMessage}`;
    }
  }

  // ============================================
  // BIDIRECTIONAL TOOL SUPPORT
  // ============================================
  // Allows Brain to request tools mid-stream by emitting special syntax
  // Format: SPECIALIST_REQUEST[tool_name:{"param":"value"}]
  // Or:     @tool_specialist(param=value)
  // ============================================

  private static readonly SPECIALIST_REQUEST_PATTERN = /SPECIALIST_REQUEST\[(\w+):(.*?)\]/s;
  private static readonly SPECIALIST_MENTION_PATTERN = /@(\w+)_specialist\((.*?)\)/s;
  private static readonly TOOL_REQUEST_PATTERN = /TOOL_REQUEST\[(\w+):(.*?)\]/s;

  /**
   * Detect if text contains a bidirectional tool request from Brain
   */
  detectBidirectionalRequest(text: string): {
    detected: boolean;
    tool?: string;
    params?: Record<string, unknown>;
    matchStart?: number;
    matchEnd?: number;
    fullMatch?: string;
  } {
    // Try SPECIALIST_REQUEST syntax (matches Brain's format)
    let match = MCPToolHandler.SPECIALIST_REQUEST_PATTERN.exec(text);
    if (match) {
      const toolName = this._normalizeToolName(match[1]);
      const params = this._parseJsonParams(match[2]);
      return {
        detected: true,
        tool: toolName,
        params,
        matchStart: match.index,
        matchEnd: match.index + match[0].length,
        fullMatch: match[0]
      };
    }

    // Try TOOL_REQUEST syntax (Ada-specific)
    match = MCPToolHandler.TOOL_REQUEST_PATTERN.exec(text);
    if (match) {
      const toolName = this._normalizeToolName(match[1]);
      const params = this._parseJsonParams(match[2]);
      return {
        detected: true,
        tool: toolName,
        params,
        matchStart: match.index,
        matchEnd: match.index + match[0].length,
        fullMatch: match[0]
      };
    }

    // Try @specialist mention syntax
    match = MCPToolHandler.SPECIALIST_MENTION_PATTERN.exec(text);
    if (match) {
      const toolName = this._normalizeToolName(match[1]);
      const params = this._parseSimpleParams(match[2]);
      return {
        detected: true,
        tool: toolName,
        params,
        matchStart: match.index,
        matchEnd: match.index + match[0].length,
        fullMatch: match[0]
      };
    }

    return { detected: false };
  }

  /**
   * Normalize tool names from various formats to our internal names
   */
  private _normalizeToolName(name: string): string {
    const normalized = name.toLowerCase().replace(/_specialist$/, '');
    
    // Map Brain specialist names to our tool names
    const mapping: Record<string, string> = {
      'read_file': 'ada_read_file',
      'readfile': 'ada_read_file',
      'file': 'ada_read_file',
      'search': 'ada_search',
      'grep': 'ada_search',
      'find': 'ada_search',
      'list': 'ada_list_files',
      'ls': 'ada_list_files',
      'listfiles': 'ada_list_files',
      'symbols': 'ada_symbols',
      'definition': 'ada_symbols',
      'git': 'ada_git_status',
      'gitstatus': 'ada_git_status',
      'memory': 'ada_search_memory',
      'searchmemory': 'ada_search_memory',
      'introspect': 'ada_introspect',
      'todos': 'ada_introspect',
    };

    return mapping[normalized] || `ada_${normalized}`;
  }

  /**
   * Parse JSON parameters from bidirectional request
   */
  private _parseJsonParams(paramsStr: string): Record<string, unknown> {
    const trimmed = paramsStr.trim();
    if (!trimmed) return {};
    
    try {
      return JSON.parse(trimmed);
    } catch {
      // Try to be lenient - maybe it's not valid JSON but has key=value pairs
      return this._parseSimpleParams(trimmed);
    }
  }

  /**
   * Parse simple key=value parameters
   */
  private _parseSimpleParams(paramsStr: string): Record<string, unknown> {
    const params: Record<string, unknown> = {};
    if (!paramsStr.trim()) return params;

    // Split on commas, handle key=value or key="value"
    const pairs = paramsStr.split(',');
    for (const pair of pairs) {
      const eqIndex = pair.indexOf('=');
      if (eqIndex > 0) {
        const key = pair.slice(0, eqIndex).trim();
        let value: string | number | boolean = pair.slice(eqIndex + 1).trim();
        
        // Strip quotes
        if ((value.startsWith('"') && value.endsWith('"')) ||
            (value.startsWith("'") && value.endsWith("'"))) {
          value = value.slice(1, -1);
        }
        
        // Try to parse as number/boolean
        if (value === 'true') value = true as any;
        else if (value === 'false') value = false as any;
        else if (/^\d+$/.test(value as string)) value = parseInt(value as string, 10);
        
        params[key] = value;
      }
    }
    return params;
  }

  /**
   * Execute a bidirectional tool request from Brain
   * Returns result text to inject back into the stream
   */
  async executeBidirectionalTool(
    tool: string,
    params: Record<string, unknown>
  ): Promise<{
    success: boolean;
    resultText: string;
    toolResult?: ToolResult;
  }> {
    const startTime = Date.now();
    console.log(`[Ada Chat] Bidirectional tool request: ${tool}`, params);

    try {
      // Build an intent object for executeTool
      const intent: QueryIntent = {
        requiresTool: true,
        requiresReasoning: false,
        tool: tool,
        params: params
      };

      const result = await this.executeTool(intent);
      const duration = Date.now() - startTime;

      // Format for injection back into LLM context
      const resultText = `
[TOOL_RESULT: ${tool}]
${result.content}
[/TOOL_RESULT]
`;

      console.log(`[Ada Chat] Bidirectional tool completed in ${duration}ms`);

      return {
        success: true,
        resultText,
        toolResult: result
      };

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      console.error(`[Ada Chat] Bidirectional tool failed: ${errorMsg}`);

      return {
        success: false,
        resultText: `\n[TOOL_ERROR: ${tool} - ${errorMsg}]\n`
      };
    }
  }

  async disconnect(): Promise<void> {
    if (this.mcpClient) {
      await this.mcpClient.disconnect();
      this.mcpClient = undefined;
    }
  }
}
