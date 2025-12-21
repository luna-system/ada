# Ada Code Monorepo

This is a pnpm workspace monorepo for Ada VSCode extensions. It's structured to allow independent development, testing, and publishing of separate extensions while sharing common code.

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
│   │   │   ├── handlers/
│   │   │   ├── views/
│   │   │   └── __tests__/
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── media/                   # Webview HTML/CSS/JS (to be created)
│   │
│   └── ada-completions/             # ⚡ Code completion extension
│       ├── src/
│       │   ├── extension.ts         # Main entry point
│       │   ├── completionProvider.ts
│       │   ├── modelWarmer.ts       # Warm model on startup
│       │   ├── formatters/
│       │   ├── tools/
│       │   └── __tests__/
│       ├── package.json
│       ├── tsconfig.json
│       └── media/                   # Ghost text assets (to be created)
│
└── [docs, tests, CI/CD config files remain at root]
```

## Packages

### `@ada-code/shared`
Shared utilities, clients, and type definitions used by both extensions.

**Exports:**
- `clients/` - HTTP clients for Ada Brain, MCP, Ollama
- `types/` - TypeScript interfaces and message types
- `utils/` - Helper functions (metadata parsing, formatting)

**Used by:** Both `ada-chat` and `ada-completions`

### `@ada-code/ada-chat`
Conversational AI chat for VSCode sidebar.

**Features:**
- Chat webview in activity bar
- Streams responses from Ada Brain API
- Tool transparency (shows files accessed, execution time)
- Metadata rendering (📂 Files, ⚡ Time)

**Configuration:**
- `ada.brainUrl` - Ada Brain server URL
- `ada.chatUseBrain` - Use Brain for chat
- `ada.enableTools` - Enable tool calling

### `@ada-code/ada-completions`
Inline code completion and ghost text suggestions.

**Features:**
- Inline completion items
- Ghost text (ghostText feature in VSCode)
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

### Publishing ada-completions independently

```bash
cd packages/ada-completions

# Update version
npm version minor

# Package the extension
pnpm run build
npm exec vsce package

# Publish to marketplace
npm exec vsce publish
```

### Future: Separate Repositories

This structure supports eventually splitting into separate repos:

```
# Option 1: Git Submodules (not recommended)
# Clunky, poor CI/CD integration

# Option 2: pnpm workspaces + independent CI/CD (recommended)
# Each package has its own:
# - GitHub Actions workflows
# - NPM publishing
# - Separate marketplace listings
# - Independent version management
```

When ready to split:
1. Create `github.com/luna-system/ada-chat` repo
2. Move `packages/ada-chat/` to new repo root
3. Create separate GitHub Actions for publishing
4. Keep `@ada-code/shared` as npm registry dependency
5. Update publishing workflows to use `@ada-code/shared@latest`

## Architecture Benefits

✅ **Separate Concerns** - Chat and completions developed independently  
✅ **Shared Code** - Clients and types reused across extensions  
✅ **Independent Testing** - Each extension has own test suite  
✅ **Independent Publishing** - Publish updates without touching other extensions  
✅ **Future Splitting** - Can move to separate repos without rearchitecting  
✅ **Team Scalability** - Different teams can own different extensions  

## Configuration

Configuration is handled at root package.json level for the monorepo. Settings are contributed by individual packages:

- **ada-chat:** `ada.brainUrl`, `ada.chatUseBrain`, `ada.enableTools`
- **ada-completions:** `ada.ollamaUrl`, `ada.model`, `ada.maxTokens`, `ada.temperature`

Individual extensions will need to contribute their own configurations when split.

## Current Status

**Phase: Reorganization (Pre-Phase 4)**

- ✅ Monorepo structure created
- ✅ `@ada-code/shared` package scaffolded
- ✅ `@ada-code/ada-chat` package scaffolded
- ✅ `@ada-code/ada-completions` package scaffolded
- 🔄 TODO: Move actual code from root `src/` to packages
- 🔄 TODO: Update imports to use `@ada-code/shared`
- 🔄 TODO: Wire up extension entry points
- 🔄 TODO: Merge with root extension.ts configuration

**Phase 4 Priority:** After code migration, integrate TwoPhaseRouter into chatViewProvider.ts

## See Also

- [../DEVELOPMENT.md](../DEVELOPMENT.md) - Extension development guide
- [../APPROACH.md](../APPROACH.md) - Design philosophy
- Phase handoff: `.ai/handoffs/phase-handoff-3-4.md`
