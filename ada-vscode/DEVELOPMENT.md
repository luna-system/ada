# Ada VS Code Extension - Development Guide

December 2025 - luna+ada

## Quick Start

**Prerequisites:**
- Node.js + npm
- VS Code
- Ada brain running (optional, for brain/mcp modes)

**Setup:**
```bash
npm install
npm run compile
```

## Development Workflow

### For TypeScript (.ts) Changes
Fast iteration - no reinstall needed:

```bash
npm run compile           # Compile TypeScript
# Then in VS Code: Cmd+Shift+P → "Developer: Reload Window"
```

**Use this for:**
- Code logic changes
- UI tweaks
- Client modifications

### For package.json Changes
Requires reinstall - adds ~30 seconds:

```bash
npx @vscode/vsce package --out ada-code.vsix
code --install-extension /path/to/ada-code.vsix --force
# Quit VS Code completely (Cmd+Q)
# Reopen VS Code
```

**Use this for:**
- New settings
- New commands
- Changed contribution points
- Activation events

## Architecture Layers

**Tier 1: Direct Ollama** (`chatMode: "ollama"`)
- Fastest, simplest
- No dependencies beyond Ollama
- Good for: Code completion, simple queries

**Tier 2: MCP Protocol** (`chatMode: "mcp"`)
- Standard MCP client
- Connects to ada-mcp stdio server
- Tools handled server-side
- Good for: Tool use, memory, composability

**Tier 3: Full Brain** (`chatMode: "brain"`)
- REST API to Ada brain (localhost:8000)
- RAG, specialists, GraphRAG
- Most features
- Good for: Complex reasoning, context-aware responses

## Key Files

- `src/extension.ts` - Main entry point
- `src/chatViewProvider.ts` - Chat UI + routing logic
- `src/mcpClient.ts` - MCP protocol wrapper
- `src/adaBrainClient.ts` - Brain REST client
- `src/ollamaClient.ts` - Direct Ollama client
- `src/completionProvider.ts` - Inline code completion
- `package.json` - Extension manifest, settings

## Testing

**Manual testing:**
1. F5 to launch Extension Development Host
2. Test in separate VS Code window

**End-to-end:**
```bash
npm run compile
npx @vscode/vsce package
code --install-extension ada-code.vsix --force
# Full restart, test in real environment
```

## Common Issues

**Settings not appearing:**
- Did you reinstall after package.json change?
- Full quit + reopen VS Code (not just reload)

**Chat not working:**
- Check brain is running: `curl localhost:8000/v1/healthz`
- Check Ollama: `curl localhost:11434/api/tags`
- Check chat mode setting matches your backend

**MCP mode fails:**
- Check ada-mcp is installed: `pip install -e ./ada-mcp`
- Check MCP server path setting
- Look at VS Code console for connection errors

## Release Workflow

1. Update version in package.json
2. Update CHANGELOG.md
3. Package: `npx @vscode/vsce package`
4. Test installation
5. Tag release: `git tag v0.x.x`
6. Publish (when ready for public release)

## Philosophy

**Progressive enhancement:**
- Works on Chromebook (Ollama only)
- Better with MCP (standard protocol)
- Best with full brain (all features)

**No vendor lock-in:**
- MCP is standard protocol
- Works with any MCP servers
- Brain is optional enhancement

**Local-first:**
- No telemetry
- No cloud dependencies
- Privacy by design

---

**Need help?** See README.md for user docs, or dive into src/ for code.

**Fast iteration FTW!** 🚀
