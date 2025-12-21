# Ada VS Code Extensions

This is a pnpm workspace monorepo for Ada VS Code extensions. It's structured to allow independent development, testing, and publishing of separate extensions while sharing common code.

## Package Names

| Package | Purpose | Published As |
|---------|---------|--------------|
| `ada-chat` | Conversational chat panel | VS Code Extension |
| `ada-complete` | Inline code completions | VS Code Extension |
| `shared` | Internal utilities | Not published |

## Architecture

```
ada-vscode/                          # Monorepo root
├── pnpm-workspace.yaml              # Workspace configuration
├── package.json                     # Root workspace config (no "main")
├── tsconfig.json                    # Shared TypeScript config
├── jest.config.js                   # Shared Jest config
│
├── packages/
│   ├── shared/                      # ✨ Shared utilities & types
│   │   ├── src/
│   │   │   ├── clients/             # HTTP clients
│   │   │   │   ├── adaBrainClient.ts
│   │   │   │   ├── mcpClient.ts
│   │   │   │   └── ollamaClient.ts
│   │   │   ├── types/               # Shared TypeScript types
│   │   │   │   ├── messageTypes.ts
│   │   │   │   └── index.ts
│   │   │   └── utils/               # Helper functions
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── ada-chat/                    # 💬 Chat extension
│   │   ├── src/
│   │   │   ├── extension.ts         # Main entry point
│   │   │   ├── chatViewProvider.ts  # Webview provider
│   │   │   ├── mcpToolHandler.ts    # Tool execution
│   │   │   └── __tests__/
│   │   ├── resources/webview/       # Webview HTML/CSS/JS
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   └── ada-completions/             # ⚡ ada-complete extension
│       ├── src/
│       │   ├── extension.ts         # Main entry point
│       │   ├── completionProvider.ts
│       │   └── modelWarmer.ts       # Warm model on startup
│       ├── package.json
│       └── tsconfig.json
│
└── [docs, tests, CI/CD config files remain at root]
```

## Packages

### `shared`
Shared utilities, clients, and type definitions used by both extensions.

**Exports:**
- `clients/` - HTTP clients for Ada Brain, MCP, Ollama
- `types/` - TypeScript interfaces and message types
- `utils/` - Helper functions (metadata parsing, formatting)

**Used by:** Both `ada-chat` and `ada-complete`

### `ada-chat`
Conversational AI chat for VS Code sidebar.

**Features:**
- Chat webview in activity bar
- Streams responses from Ada Brain API
- Tool transparency (shows files accessed, execution time)
- Intent classification → tool execution → brain reasoning

**Configuration:**
- `ada.brainUrl` - Ada Brain server URL (default: localhost:8000)
- `ada.enableTools` - Enable tool calling

### `ada-complete`
Inline code completion and ghost text suggestions.

**Features:**
- Inline completion items
- Ghost text (ghostText feature in VS Code)
- Model warming on startup
- qwen2.5-coder:7b with FIM format

**Configuration:**
- `ada.ollamaUrl` - Ollama server URL
- `ada.model` - Model to use
- `ada.maxTokens` - Completion length
- `ada.temperature` - Generation temperature

## Development

### Installation

```bash
# Install dependencies for all packages
pnpm install

# Or install in a specific package
cd packages/ada-chat
pnpm install
```

### Building

```bash
# Build all packages
pnpm build

# Watch mode (all packages)
pnpm watch

# Build specific package
cd packages/ada-chat && pnpm build
```

### Testing

```bash
# Run tests in all packages
pnpm test

# Watch mode
pnpm test:watch

# Specific package
cd packages/ada-completions && pnpm test
```

### Linting

```bash
# Lint all packages
pnpm lint

# Specific package
cd packages/ada-chat && pnpm lint
```

## Publishing

### Publishing ada-chat independently

```bash
cd packages/ada-chat

# Update version
npm version minor

# Package the extension
pnpm run build
npm exec vsce package

# Publish to marketplace
npm exec vsce publish
```

### Publishing ada-complete independently

```bash
cd packages/ada-completions  # folder name (keeping it stable)

# Update version
npm version minor

# Package the extension
pnpm run build
npm exec vsce package

# Publish to marketplace
npm exec vsce publish
```

## Architecture Benefits

✅ **Separate Concerns** - Chat and completions developed independently  
✅ **Shared Code** - Clients and types reused across extensions  
✅ **Independent Testing** - Each extension has own test suite  
✅ **Independent Publishing** - Publish updates without touching other extensions  
✅ **Future Splitting** - Can move to separate repos without rearchitecting  

## Configuration

Configuration is handled at root package.json level for the monorepo. Settings are contributed by individual packages:

- **ada-chat:** `ada.brainUrl`, `ada.enableTools`
- **ada-complete:** `ada.ollamaUrl`, `ada.model`, `ada.maxTokens`, `ada.temperature`

## Current Status

**Phase: v1.1 Tool Transparency**

- ✅ Monorepo structure created
- ✅ `shared` package with clients/types
- ✅ `ada-chat` v1.1 with tool transparency
- ✅ `ada-complete` inline completions
- 🔄 TODO: More tools (file read, search)

## See Also

- [../DEVELOPMENT.md](../DEVELOPMENT.md) - Extension development guide
- [../APPROACH.md](../APPROACH.md) - Design philosophy
