import * as vscode from 'vscode';
import { AdaBrainClient } from './adaBrainClient';

/**
 * Preload .ai/ folder contents into Ada Brain's memory.
 * 
 * This gives Ada instant knowledge of project structure, architecture,
 * conventions, and relationships - like reading the manual before work!
 * 
 * @param client Ada Brain client instance
 * @param workspaceFolder The workspace to scan for .ai/ folder
 * @returns true if .ai/ folder found and loaded, false otherwise
 */
export async function preloadAiFolder(
    client: AdaBrainClient,
    workspaceFolder: vscode.WorkspaceFolder
): Promise<boolean> {
    try {
        const aiDir = vscode.Uri.joinPath(workspaceFolder.uri, '.ai');
        
        // Check if .ai/ folder exists
        let files: [string, vscode.FileType][];
        try {
            files = await vscode.workspace.fs.readDirectory(aiDir);
        } catch {
            // No .ai/ folder - that's okay!
            console.log('No .ai/ folder detected (optional)');
            return false;
        }
        
        console.log(`Found .ai/ folder with ${files.length} items`);
        
        // Read all markdown and JSON files
        const context: { [key: string]: string } = {};
        let fileCount = 0;
        
        for (const [filename, type] of files) {
            if (type === vscode.FileType.File && 
                (filename.endsWith('.md') || filename.endsWith('.json'))) {
                
                try {
                    const fileUri = vscode.Uri.joinPath(aiDir, filename);
                    const content = await vscode.workspace.fs.readFile(fileUri);
                    const text = new TextDecoder().decode(content);
                    
                    context[filename] = text;
                    fileCount++;
                    console.log(`Loaded .ai/${filename} (${text.length} chars)`);
                } catch (err) {
                    console.warn(`Failed to read .ai/${filename}:`, err);
                }
            }
        }
        
        if (fileCount === 0) {
            console.log('No .md or .json files found in .ai/ folder');
            return false;
        }
        
        // Send to Ada Brain for indexing
        console.log(`Ingesting ${fileCount} files into Ada Brain...`);
        await client.ingestProjectContext(context);
        console.log('✨ Project context loaded successfully!');
        
        return true;
        
    } catch (error) {
        console.error('Error preloading .ai/ folder:', error);
        return false;
    }
}

/**
 * Get a summary of what was loaded from .ai/ folder.
 * Useful for displaying to users.
 */
export function getPreloadSummary(fileCount: number, fileNames: string[]): string {
    if (fileCount === 0) {
        return 'No .ai/ folder found (Ada will learn organically)';
    }
    
    const keyFiles = fileNames.filter(f => 
        ['context.md', 'codebase-map.json', 'QUICKSTART.md'].includes(f)
    );
    
    if (keyFiles.length > 0) {
        return `Loaded ${fileCount} files from .ai/ (${keyFiles.join(', ')})`;
    }
    
    return `Loaded ${fileCount} files from .ai/ folder`;
}
