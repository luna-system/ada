"use strict";
/**
 * Tool Transparency Formatter
 * Extracts and formats tool usage markers from Ada's responses
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.ToolTransparencyFormatter = void 0;
class ToolTransparencyFormatter {
    /**
     * Extract tool markers from content
     * Looks for patterns like: [🔧 read_file: path/to/file]
     * Also detects introspection reports like "📂 Files Analyzed: context.md, codebase-map.json"
     */
    static extractToolMarkers(content) {
        const markers = [];
        // Pattern 1: Explicit tool markers [🔧 tool: path]
        const toolRegex = /\[🔧 ([^:]+): ([^\]]+)\]/g;
        let match;
        while ((match = toolRegex.exec(content)) !== null) {
            markers.push({
                tool: match[1],
                path: match[2]
            });
        }
        // Pattern 2: Introspection reports "� Files Analyzed: file1, file2, file3"
        // Note: 📁 (U+1F4C1) is file folder, 📂 (U+1F4C2) is open file folder - match both!
        const filesAnalyzedRegex = /[📁📂]\s*Files Analyzed:\s*([^\n]+)/i;
        const filesMatch = content.match(filesAnalyzedRegex);
        if (filesMatch) {
            const files = filesMatch[1].split(',').map(f => f.trim()).filter(f => f);
            for (const file of files) {
                markers.push({
                    tool: 'introspect',
                    path: file
                });
            }
        }
        // Pattern 3: Read file markers like "reading file.py..." or "analyzed file.py"
        const readFileRegex = /(?:reading|analyzed|checked|examined)\s+[`"]?([a-zA-Z0-9_\-./]+\.[a-zA-Z]+)[`"]?/gi;
        while ((match = readFileRegex.exec(content)) !== null) {
            markers.push({
                tool: 'read_file',
                path: match[1]
            });
        }
        return markers;
    }
    /**
     * Format tool markers as HTML badges
     */
    static formatToolResults(markers) {
        if (markers.length === 0) {
            return '';
        }
        const uniqueFiles = [...new Set(markers.map(m => m.path))];
        const badges = uniqueFiles
            .map(file => `<span class="tool-file-badge">${file}</span>`)
            .join(' ');
        return `
            <div class="tool-results">
                <details>
                    <summary>🔧 Tools Used (${uniqueFiles.length} files)</summary>
                    <div class="tool-file-list">${badges}</div>
                </details>
            </div>
        `;
    }
    /**
     * Clean tool markers from displayed content
     */
    static stripToolMarkers(content) {
        return content.replace(/\[🔧 [^\]]+\]/g, '');
    }
}
exports.ToolTransparencyFormatter = ToolTransparencyFormatter;
//# sourceMappingURL=ToolTransparencyFormatter.js.map