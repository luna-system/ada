"use strict";
/**
 * Tests for ToolTransparencyFormatter
 *
 * Pure function tests - these verify tool marker extraction and formatting
 */
Object.defineProperty(exports, "__esModule", { value: true });
const ToolTransparencyFormatter_1 = require("../formatters/ToolTransparencyFormatter");
describe('ToolTransparencyFormatter', () => {
    describe('extractToolMarkers', () => {
        it('should extract single tool marker', () => {
            const content = 'Some text [🔧 read_file: src/index.ts] more text';
            const markers = ToolTransparencyFormatter_1.ToolTransparencyFormatter.extractToolMarkers(content);
            expect(markers).toHaveLength(1);
            expect(markers[0]).toEqual({
                tool: 'read_file',
                path: 'src/index.ts'
            });
        });
        it('should extract multiple tool markers', () => {
            const content = `
                [🔧 read_file: src/app.ts]
                Some analysis here
                [🔧 read_file: src/utils.ts]
                [🔧 grep_search: function]
            `;
            const markers = ToolTransparencyFormatter_1.ToolTransparencyFormatter.extractToolMarkers(content);
            expect(markers).toHaveLength(3);
            expect(markers[0].path).toBe('src/app.ts');
            expect(markers[1].path).toBe('src/utils.ts');
            expect(markers[2].tool).toBe('grep_search');
        });
        it('should return empty array when no markers present', () => {
            const content = 'Just regular text without any tool markers';
            const markers = ToolTransparencyFormatter_1.ToolTransparencyFormatter.extractToolMarkers(content);
            expect(markers).toHaveLength(0);
        });
        it('should handle paths with special characters', () => {
            const content = '[🔧 read_file: src/my-file.test.ts]';
            const markers = ToolTransparencyFormatter_1.ToolTransparencyFormatter.extractToolMarkers(content);
            expect(markers[0].path).toBe('src/my-file.test.ts');
        });
        it('should handle various tool types', () => {
            const content = `
                [🔧 read_file: file.ts]
                [🔧 grep_search: pattern]
                [🔧 semantic_search: query here]
                [🔧 list_dir: ./src]
            `;
            const markers = ToolTransparencyFormatter_1.ToolTransparencyFormatter.extractToolMarkers(content);
            expect(markers.map(m => m.tool)).toEqual([
                'read_file',
                'grep_search',
                'semantic_search',
                'list_dir'
            ]);
        });
    });
    describe('formatToolResults', () => {
        it('should return empty string for no markers', () => {
            const result = ToolTransparencyFormatter_1.ToolTransparencyFormatter.formatToolResults([]);
            expect(result).toBe('');
        });
        it('should format single file badge', () => {
            const markers = [
                { tool: 'read_file', path: 'src/index.ts' }
            ];
            const result = ToolTransparencyFormatter_1.ToolTransparencyFormatter.formatToolResults(markers);
            expect(result).toContain('🔧 Tools Used');
            expect(result).toContain('1 files');
            expect(result).toContain('src/index.ts');
            expect(result).toContain('tool-file-badge');
        });
        it('should deduplicate files read multiple times', () => {
            const markers = [
                { tool: 'read_file', path: 'src/index.ts' },
                { tool: 'read_file', path: 'src/index.ts' }, // duplicate
                { tool: 'read_file', path: 'src/other.ts' }
            ];
            const result = ToolTransparencyFormatter_1.ToolTransparencyFormatter.formatToolResults(markers);
            expect(result).toContain('2 files'); // not 3!
        });
        it('should include details/summary for collapsibility', () => {
            const markers = [
                { tool: 'read_file', path: 'file.ts' }
            ];
            const result = ToolTransparencyFormatter_1.ToolTransparencyFormatter.formatToolResults(markers);
            expect(result).toContain('<details>');
            expect(result).toContain('<summary>');
            expect(result).toContain('</details>');
        });
    });
    describe('stripToolMarkers', () => {
        it('should remove tool markers from content', () => {
            const content = 'Here is [🔧 read_file: test.ts] some text';
            const stripped = ToolTransparencyFormatter_1.ToolTransparencyFormatter.stripToolMarkers(content);
            expect(stripped).toBe('Here is  some text');
            expect(stripped).not.toContain('🔧');
        });
        it('should remove multiple markers', () => {
            const content = '[🔧 a: b] text [🔧 c: d] more';
            const stripped = ToolTransparencyFormatter_1.ToolTransparencyFormatter.stripToolMarkers(content);
            expect(stripped).toBe(' text  more');
        });
        it('should preserve content without markers', () => {
            const content = 'Just regular content here';
            const stripped = ToolTransparencyFormatter_1.ToolTransparencyFormatter.stripToolMarkers(content);
            expect(stripped).toBe(content);
        });
    });
});
//# sourceMappingURL=ToolTransparencyFormatter.test.js.map