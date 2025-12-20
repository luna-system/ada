"use strict";
/**
 * Ada Tools - Agent capabilities for pair programming
 *
 * Tools let Ada read, write, and navigate your codebase.
 * The model outputs XML tool calls, we execute them, loop until done.
 *
 * December 2025 - luna-system
 * License: CC0 (Public Domain)
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.TOOL_DEFINITIONS = void 0;
exports.parseToolCalls = parseToolCalls;
exports.hasToolCalls = hasToolCalls;
exports.extractNonToolText = extractNonToolText;
exports.executeTool = executeTool;
exports.executeToolCalls = executeToolCalls;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
// ============================================================================
// Tool Definitions (for system prompt)
// ============================================================================
exports.TOOL_DEFINITIONS = `
You have tools to interact with the workspace. When you need information, call a tool, then ANSWER THE USER with the results.

TOOL FORMAT:
<tool_call>
<name>TOOL_NAME</name>
<parameters>
<param_name>value</param_name>
</parameters>
</tool_call>

AVAILABLE TOOLS:
- list_files: List files matching pattern (params: pattern, maxResults)
- read_file: Read file contents (params: path)
- search_files: Search for text in files (params: query, pattern)
- edit_file: Replace text in file (params: path, old_text, new_text)
- create_file: Create new file (params: path, content)
- get_errors: Get diagnostics (params: path)

WORKFLOW:
1. Use tool to get information
2. Wait for <tool_result> with the data
3. ANSWER THE USER'S QUESTION using that data

Do NOT call the same tool repeatedly. Once you get results, respond to the user!
`.trim();
function parseToolCalls(text) {
    const calls = [];
    // AGGRESSIVE: Strip ALL markdown code fences, no matter what language
    // Handles: ```xml, ```plaintext, ```, ```typescript, etc.
    let cleanedText = text.replace(/```[\w]*\n?([\s\S]*?)```/g, '$1');
    console.log('[ADA DEBUG parseToolCalls] Input length:', text.length, 'Cleaned length:', cleanedText.length);
    console.log('[ADA DEBUG parseToolCalls] Cleaned text:', cleanedText.substring(0, 500));
    // Try BOTH formats:
    // Format 1: <tool_call><name>...</name><parameters>...</parameters></tool_call>
    // Format 2: <name>...</name><parameters>...</parameters> (no wrapper)
    // First try with <tool_call> wrapper
    let toolCallRegex = /<tool_call>([\s\S]*?)<\/tool_call>/g;
    let match;
    while ((match = toolCallRegex.exec(cleanedText)) !== null) {
        const content = match[1];
        const parsed = parseToolCallContent(content);
        if (parsed)
            calls.push(parsed);
    }
    // If no matches with wrapper, try WITHOUT wrapper (just <name>)
    if (calls.length === 0) {
        console.log('[ADA DEBUG] No <tool_call> wrapper found, trying without wrapper...');
        // Match pattern: <name>...</name><parameters>...</parameters>
        const noWrapperRegex = /<name>([\s\S]*?)<\/name>\s*<parameters>([\s\S]*?)<\/parameters>/g;
        while ((match = noWrapperRegex.exec(cleanedText)) !== null) {
            const name = match[1].trim();
            const paramsContent = match[2];
            const parameters = {};
            const paramRegex = /<(\w+)>([\s\S]*?)<\/\1>/g;
            let paramMatch;
            while ((paramMatch = paramRegex.exec(paramsContent)) !== null) {
                parameters[paramMatch[1]] = paramMatch[2].trim();
            }
            calls.push({ name, parameters });
            console.log('[ADA DEBUG] Parsed tool call without wrapper:', name, parameters);
        }
    }
    // If STILL no matches, try Format 3: <tool_name>params</tool_name>
    if (calls.length === 0) {
        console.log('[ADA DEBUG] Trying tool-name-as-tag format...');
        const toolNames = ['list_files', 'read_file', 'search_files', 'edit_file', 'create_file', 'get_errors'];
        for (const toolName of toolNames) {
            const regex = new RegExp(`<${toolName}([\\s\\S]*?)<\\/${toolName}>`, 'g');
            while ((match = regex.exec(cleanedText)) !== null) {
                const content = match[1];
                const parameters = {};
                const paramRegex = /<(\w+)>([\s\S]*?)<\/\1>/g;
                let paramMatch;
                while ((paramMatch = paramRegex.exec(content)) !== null) {
                    parameters[paramMatch[1]] = paramMatch[2].trim();
                }
                calls.push({ name: toolName, parameters });
                console.log('[ADA DEBUG] Parsed tool-name-as-tag format:', toolName, parameters);
            }
        }
    }
    return calls;
}
// Helper to parse content inside <tool_call> tags
function parseToolCallContent(content) {
    // Extract name
    const nameMatch = content.match(/<name>([\s\S]*?)<\/name>/);
    if (!nameMatch)
        return null;
    const name = nameMatch[1].trim();
    // Extract parameters
    const parameters = {};
    const paramsMatch = content.match(/<parameters>([\s\S]*?)<\/parameters>/);
    if (paramsMatch) {
        const paramsContent = paramsMatch[1];
        // Match each parameter tag
        const paramRegex = /<(\w+)>([\s\S]*?)<\/\1>/g;
        let paramMatch;
        while ((paramMatch = paramRegex.exec(paramsContent)) !== null) {
            parameters[paramMatch[1]] = paramMatch[2].trim();
        }
    }
    return { name, parameters };
}
/**
 * Check if text contains tool calls
 */
function hasToolCalls(text) {
    // Strip markdown FIRST before checking
    const cleanedText = text.replace(/```[\w]*\n?([\s\S]*?)```/g, '$1');
    // Accept: <tool_call>, <name>, OR any tool name as tag
    const result = /<tool_call>/.test(cleanedText) ||
        /<name>/.test(cleanedText) ||
        /<(list_files|read_file|search_files|edit_file|create_file|get_errors)>/.test(cleanedText);
    console.log('[ADA DEBUG hasToolCalls] Original length:', text.length, 'Cleaned length:', cleanedText.length, 'Result:', result);
    console.log('[ADA DEBUG hasToolCalls] First 300 chars of cleaned:', cleanedText.substring(0, 300));
    return result;
}
/**
 * Extract the non-tool-call part of the response (the "thinking" or final answer)
 */
function extractNonToolText(text) {
    return text.replace(/<tool_call>[\s\S]*?<\/tool_call>/g, '').trim();
}
function getWorkspaceRoot() {
    const folders = vscode.workspace.workspaceFolders;
    return folders && folders.length > 0 ? folders[0].uri.fsPath : null;
}
function resolvePath(relativePath) {
    const root = getWorkspaceRoot();
    if (!root)
        return null;
    return vscode.Uri.file(path.join(root, relativePath));
}
/**
 * Read a file's contents
 */
async function readFile(params) {
    const filePath = params.path;
    if (!filePath) {
        return { success: false, output: '', error: 'Missing required parameter: path' };
    }
    const uri = resolvePath(filePath);
    if (!uri) {
        return { success: false, output: '', error: 'No workspace folder open' };
    }
    try {
        const content = await vscode.workspace.fs.readFile(uri);
        const text = new TextDecoder().decode(content);
        // Truncate if too large
        const maxLength = 10000;
        if (text.length > maxLength) {
            return {
                success: true,
                output: text.substring(0, maxLength) + `\n\n... [truncated, ${text.length - maxLength} more characters]`
            };
        }
        return { success: true, output: text };
    }
    catch (error) {
        return { success: false, output: '', error: `Failed to read file: ${error}` };
    }
}
/**
 * List files matching a glob pattern
 */
async function listFiles(params) {
    const pattern = params.pattern;
    if (!pattern) {
        return { success: false, output: '', error: 'Missing required parameter: pattern' };
    }
    const maxResults = parseInt(params.maxResults || '20', 10);
    try {
        const files = await vscode.workspace.findFiles(pattern, '**/node_modules/**', maxResults);
        const paths = files.map(f => vscode.workspace.asRelativePath(f));
        if (paths.length === 0) {
            return { success: true, output: 'No files found matching pattern.' };
        }
        return { success: true, output: paths.join('\n') };
    }
    catch (error) {
        return { success: false, output: '', error: `Failed to list files: ${error}` };
    }
}
/**
 * Edit a file by replacing text
 */
async function editFile(params) {
    const { path: filePath, old_text, new_text } = params;
    if (!filePath) {
        return { success: false, output: '', error: 'Missing required parameter: path' };
    }
    if (old_text === undefined) {
        return { success: false, output: '', error: 'Missing required parameter: old_text' };
    }
    if (new_text === undefined) {
        return { success: false, output: '', error: 'Missing required parameter: new_text' };
    }
    const uri = resolvePath(filePath);
    if (!uri) {
        return { success: false, output: '', error: 'No workspace folder open' };
    }
    try {
        // Read current content
        const content = await vscode.workspace.fs.readFile(uri);
        const text = new TextDecoder().decode(content);
        // Check if old_text exists
        if (!text.includes(old_text)) {
            return {
                success: false,
                output: '',
                error: `Could not find the specified text in ${filePath}. Make sure old_text matches exactly.`
            };
        }
        // Replace
        const newContent = text.replace(old_text, new_text);
        // Open document and apply edit (allows undo)
        const doc = await vscode.workspace.openTextDocument(uri);
        const edit = new vscode.WorkspaceEdit();
        // Find the range to replace
        const startIndex = text.indexOf(old_text);
        const startPos = doc.positionAt(startIndex);
        const endPos = doc.positionAt(startIndex + old_text.length);
        edit.replace(uri, new vscode.Range(startPos, endPos), new_text);
        const success = await vscode.workspace.applyEdit(edit);
        if (success) {
            // Save the file
            await doc.save();
            return { success: true, output: `Successfully edited ${filePath}` };
        }
        else {
            return { success: false, output: '', error: 'Failed to apply edit' };
        }
    }
    catch (error) {
        return { success: false, output: '', error: `Failed to edit file: ${error}` };
    }
}
/**
 * Create a new file
 */
async function createFile(params) {
    const { path: filePath, content } = params;
    if (!filePath) {
        return { success: false, output: '', error: 'Missing required parameter: path' };
    }
    if (content === undefined) {
        return { success: false, output: '', error: 'Missing required parameter: content' };
    }
    const uri = resolvePath(filePath);
    if (!uri) {
        return { success: false, output: '', error: 'No workspace folder open' };
    }
    try {
        // Check if file already exists
        try {
            await vscode.workspace.fs.stat(uri);
            return { success: false, output: '', error: `File already exists: ${filePath}. Use edit_file to modify it.` };
        }
        catch {
            // File doesn't exist, good
        }
        // Create the file
        const encoder = new TextEncoder();
        await vscode.workspace.fs.writeFile(uri, encoder.encode(content));
        // Open it
        const doc = await vscode.workspace.openTextDocument(uri);
        await vscode.window.showTextDocument(doc);
        return { success: true, output: `Created ${filePath}` };
    }
    catch (error) {
        return { success: false, output: '', error: `Failed to create file: ${error}` };
    }
}
/**
 * Search for text across files
 */
async function searchFiles(params) {
    const { query, pattern } = params;
    if (!query) {
        return { success: false, output: '', error: 'Missing required parameter: query' };
    }
    try {
        const results = [];
        const searchPattern = pattern || '**/*';
        const files = await vscode.workspace.findFiles(searchPattern, '**/node_modules/**', 50);
        for (const file of files) {
            try {
                const content = await vscode.workspace.fs.readFile(file);
                const text = new TextDecoder().decode(content);
                if (text.includes(query)) {
                    const relativePath = vscode.workspace.asRelativePath(file);
                    // Find line numbers where query appears
                    const lines = text.split('\n');
                    const matchingLines = [];
                    lines.forEach((line, index) => {
                        if (line.includes(query)) {
                            matchingLines.push(`  L${index + 1}: ${line.trim().substring(0, 100)}`);
                        }
                    });
                    if (matchingLines.length > 0) {
                        results.push(`${relativePath}:\n${matchingLines.slice(0, 5).join('\n')}`);
                    }
                }
            }
            catch {
                // Skip files we can't read
            }
        }
        if (results.length === 0) {
            return { success: true, output: `No matches found for "${query}"` };
        }
        return { success: true, output: results.slice(0, 10).join('\n\n') };
    }
    catch (error) {
        return { success: false, output: '', error: `Search failed: ${error}` };
    }
}
/**
 * Get diagnostics (errors/warnings)
 */
async function getErrors(params) {
    const filePath = params.path;
    let diagnostics;
    if (filePath) {
        const uri = resolvePath(filePath);
        if (!uri) {
            return { success: false, output: '', error: 'No workspace folder open' };
        }
        const fileDiags = vscode.languages.getDiagnostics(uri);
        diagnostics = [[uri, fileDiags]];
    }
    else {
        diagnostics = vscode.languages.getDiagnostics();
    }
    const results = [];
    for (const [uri, diags] of diagnostics) {
        const errors = diags.filter(d => d.severity === vscode.DiagnosticSeverity.Error);
        const warnings = diags.filter(d => d.severity === vscode.DiagnosticSeverity.Warning);
        if (errors.length > 0 || warnings.length > 0) {
            const relativePath = vscode.workspace.asRelativePath(uri);
            const items = [];
            for (const d of errors.slice(0, 5)) {
                items.push(`  ERROR L${d.range.start.line + 1}: ${d.message}`);
            }
            for (const d of warnings.slice(0, 3)) {
                items.push(`  WARN L${d.range.start.line + 1}: ${d.message}`);
            }
            results.push(`${relativePath}:\n${items.join('\n')}`);
        }
    }
    if (results.length === 0) {
        return { success: true, output: 'No errors or warnings found.' };
    }
    return { success: true, output: results.join('\n\n') };
}
// ============================================================================
// Tool Dispatcher
// ============================================================================
const TOOL_HANDLERS = {
    read_file: readFile,
    list_files: listFiles,
    edit_file: editFile,
    create_file: createFile,
    search_files: searchFiles,
    get_errors: getErrors,
};
/**
 * Execute a single tool call
 */
async function executeTool(call) {
    const handler = TOOL_HANDLERS[call.name];
    if (!handler) {
        return {
            success: false,
            output: '',
            error: `Unknown tool: ${call.name}. Available tools: ${Object.keys(TOOL_HANDLERS).join(', ')}`
        };
    }
    return await handler(call.parameters);
}
/**
 * Execute multiple tool calls and format results
 */
async function executeToolCalls(calls) {
    const results = [];
    for (const call of calls) {
        const result = await executeTool(call);
        if (result.success) {
            results.push(`<tool_result name="${call.name}">\n${result.output}\n</tool_result>`);
        }
        else {
            results.push(`<tool_result name="${call.name}" error="true">\n${result.error}\n</tool_result>`);
        }
    }
    const formatted = results.join('\n\n');
    return formatted + '\n\nNow answer the user\'s question using the above results.';
}
//# sourceMappingURL=tools.js.map