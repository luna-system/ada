# Ada VS Code Extensions

**Your own AI assistant. Local. Private. Fast.**

Ada brings AI capabilities to VS Code without cloud dependencies, subscriptions, or sending your code anywhere.

## Extensions

### Ada Chat (`ada-chat`)
Conversational AI in VS Code sidebar with **tool transparency**.

- 💬 Chat with Ada about your code
- 🔧 See exactly what tools Ada uses (files read, TODOs found)
- 🧠 Real-time workspace introspection
- 🌐 Connects to Ada Brain for RAG-powered responses

### Ada Complete (`ada-complete`)
Inline code completions with ghost text.

- ⚡ **103ms** time to first token
- 👻 Ghost text suggestions as you type
- 🔒 100% local - your code never leaves your machine

## Quick Start

### Requirements

1. **Ada Brain** running (for chat):
   ```bash
   cd ada-v1
   docker compose up brain
   ```

2. **Ollama** running (for completions):
   ```bash
   ollama serve
   ollama pull qwen2.5-coder:7b
   ```

### Install Extensions

```bash
# Build and install Ada Chat
cd ada-vscode/packages/ada-chat
pnpm build
npx @vscode/vsce package --no-dependencies
# Install the .vsix in VS Code

# Build and install Ada Complete
cd ada-vscode/packages/ada-completions
pnpm build
npx @vscode/vsce package --no-dependencies
# Install the .vsix in VS Code
```

## Configuration

### Ada Chat
| Setting | Default | Description |
|---------|---------|-------------|
| `ada.brainUrl` | `http://localhost:8000` | Ada Brain server URL |
| `ada.enableTools` | `true` | Enable tool transparency |

### Ada Complete
| Setting | Default | Description |
|---------|---------|-------------|
| `ada.ollamaUrl` | `http://localhost:11434` | Ollama server URL |
| `ada.model` | `qwen2.5-coder:7b` | Model to use |
| `ada.maxTokens` | `128` | Max tokens to generate |
| `ada.temperature` | `0.2` | Generation temperature |

## Architecture

```
VS Code
├── Ada Chat     → Ada Brain (RAG, memory, specialists)
└── Ada Complete → Ollama (direct, fast completions)
```

Both extensions share common utilities via the internal `shared` package.

## Development

```bash
cd ada-vscode

# Install dependencies
pnpm install

# Build all packages
pnpm build

# Build and watch specific package
cd packages/ada-chat
pnpm watch
```

## Part of the Ada Project

Ada is a local-first AI assistant with:
- **ada-brain**: FastAPI backend with RAG and memory
- **ada-cli**: Terminal interface  
- **ada-chat**: VS Code chat (this extension)
- **ada-complete**: VS Code completions (this extension)
- **ada-nvim**: Neovim plugin
- **ada-mcp**: Model Context Protocol server

See the [main Ada repository](https://github.com/luna-system/ada) for more.

## License

**CC0 (Public Domain)** - Do whatever you want with this.

## Credits

Built with 💜 by [luna-system](https://github.com/luna-system) and Ada.

*The revolution will not be cloud-hosted.*
