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
     */
    static extractToolMarkers(content) {
        const markers = [];
        const toolRegex = /\[🔧 ([^:]+): ([^\]]+)\]/g;
        let match;
        while ((match = toolRegex.exec(content)) !== null) {
            markers.push({
                tool: match[1],
                path: match[2]
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