"use strict";
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
exports.preloadAiFolder = preloadAiFolder;
exports.getPreloadSummary = getPreloadSummary;
const vscode = __importStar(require("vscode"));
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
async function preloadAiFolder(client, workspaceFolder) {
    try {
        const aiDir = vscode.Uri.joinPath(workspaceFolder.uri, '.ai');
        // Check if .ai/ folder exists
        let files;
        try {
            files = await vscode.workspace.fs.readDirectory(aiDir);
        }
        catch {
            // No .ai/ folder - that's okay!
            console.log('No .ai/ folder detected (optional)');
            return false;
        }
        console.log(`Found .ai/ folder with ${files.length} items`);
        // Read all markdown and JSON files
        const context = {};
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
                }
                catch (err) {
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
    }
    catch (error) {
        console.error('Error preloading .ai/ folder:', error);
        return false;
    }
}
/**
 * Get a summary of what was loaded from .ai/ folder.
 * Useful for displaying to users.
 */
function getPreloadSummary(fileCount, fileNames) {
    if (fileCount === 0) {
        return 'No .ai/ folder found (Ada will learn organically)';
    }
    const keyFiles = fileNames.filter(f => ['context.md', 'codebase-map.json', 'QUICKSTART.md'].includes(f));
    if (keyFiles.length > 0) {
        return `Loaded ${fileCount} files from .ai/ (${keyFiles.join(', ')})`;
    }
    return `Loaded ${fileCount} files from .ai/ folder`;
}
//# sourceMappingURL=aiPreload.js.map