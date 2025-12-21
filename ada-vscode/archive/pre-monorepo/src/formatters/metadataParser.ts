/**
 * Tool Metadata Parser
 * 
 * Extracts structured metadata from MCP tool responses.
 * 
 * The envelope pattern: responses contain both content and metadata markers.
 * This parser extracts the metadata for rendering tool transparency badges.
 */

import { ToolMetadata } from '../types/messages';

/**
 * Extract metadata from response text using the emoji marker pattern
 * 
 * Pattern: "📂 Files Analyzed: file1, file2, file3\n⚡ Introspection time: 142ms"
 */
export function extractMetadataFromResponse(responseText: string, toolName: string): ToolMetadata | null {
    // Pattern 1: Files Analyzed marker (📂 or 📁)
    const filesAnalyzedRegex = /[📁📂]\s*Files Analyzed:\s*([^\n]+)/i;
    const filesMatch = responseText.match(filesAnalyzedRegex);
    
    if (!filesMatch) {
        return null;
    }
    
    // Parse files
    const filesStr = filesMatch[1];
    const filesAccessed = filesStr.split(',').map(f => f.trim()).filter(f => f);
    
    // Pattern 2: Timing information (⚡ Introspection time: 142ms)
    const timingRegex = /⚡\s*(?:Introspection time|Time):\s*(\d+)ms/i;
    const timingMatch = responseText.match(timingRegex);
    const durationMs = timingMatch ? parseInt(timingMatch[1], 10) : undefined;
    
    // Pattern 3: Actions taken (optional, for future expansion)
    const actionsRegex = /Actions?:\s*([^\n]+)/i;
    const actionsMatch = responseText.match(actionsRegex);
    const actionsTaken = actionsMatch 
        ? actionsMatch[1].split(',').map(a => a.trim()).filter(a => a)
        : [];
    
    return {
        toolName,
        filesAccessed,
        actionsTaken,
        durationMs
    };
}

/**
 * Format metadata as human-readable text for display
 */
export function formatMetadataForDisplay(metadata: ToolMetadata): string {
    const parts: string[] = [];
    
    if (metadata.filesAccessed.length > 0) {
        parts.push(`📂 Files: ${metadata.filesAccessed.join(', ')}`);
    }
    
    if (metadata.actionsTaken.length > 0) {
        parts.push(`⚙️  Actions: ${metadata.actionsTaken.join(', ')}`);
    }
    
    if (metadata.durationMs !== undefined) {
        parts.push(`⚡ ${metadata.durationMs}ms`);
    }
    
    return parts.join(' • ');
}

/**
 * Remove metadata markers from response text for cleaner display
 * 
 * The metadata is extracted and sent separately, so we can remove
 * the markers from the main content text.
 */
export function stripMetadataMarkersFromResponse(responseText: string): string {
    return responseText
        .replace(/\n*📂\s*Files Analyzed:[^\n]+/gi, '')  // Remove Files Analyzed
        .replace(/\n*⚡\s*(?:Introspection time|Time):[^\n]+/gi, '')  // Remove timing
        .trim();
}
