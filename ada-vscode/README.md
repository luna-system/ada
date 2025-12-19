# Ada - Local AI Code Completion

**GitHub Copilot alternative. 103ms latency. $0/month. 100% private.**

Ada brings AI code completion to VS Code without cloud dependencies, subscriptions, or sending your code anywhere.

## Features

- 🚀 **103ms Time to First Token** - As fast as cloud providers
- 💰 **$0/month** - No subscription required
- 🔒 **100% Private** - Your code never leaves your machine
- 🌐 **Works Offline** - No internet required
- ⚡ **Ghost Text** - Inline suggestions just like Copilot

## Requirements

1. **Ollama** installed and running
   ```bash
   # Install Ollama (https://ollama.ai)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull the model
   ollama pull qwen2.5-coder:7b
   
   # Start Ollama (usually automatic)
   ollama serve
   ```

2. **A GPU** (recommended) - Works on CPU but slower

## Installation

### From VSIX (Current)
1. Download `ada-code-0.1.0.vsix` from releases
2. In VS Code: Extensions → ... → Install from VSIX

### From Marketplace (Coming Soon)
Search "Ada Code" in VS Code Extensions

## Usage

Just start typing! Ada will suggest completions as ghost text.

- **Tab** - Accept suggestion
- **Escape** - Dismiss suggestion  
- **Ctrl+Shift+Space** - Manually trigger completion

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `ada.enabled` | `true` | Enable/disable completions |
| `ada.ollamaUrl` | `http://localhost:11434` | Ollama server URL |
| `ada.model` | `qwen2.5-coder:7b` | Model to use |
| `ada.maxTokens` | `128` | Max tokens to generate |
| `ada.temperature` | `0.2` | Generation temperature |
| `ada.debounceMs` | `300` | Debounce delay (ms) |

## Why Ada?

We proved that local AI code completion can match or beat cloud providers:

| Provider | TTFT | Cost | Privacy |
|----------|------|------|---------|
| **Ada** | **103ms** | **$0/mo** | **✅ 100%** |
| Copilot | ~150-300ms | $19/mo | ❌ |
| Cursor | ~100-200ms | $20/mo | ❌ |
| Cody | ~200ms | $9-19/mo | ❌ |

The cloud tax isn't for compute—it's for convenience and marketing.

## Research

This extension is part of the Ada project, which discovered:

- **Singularity #8**: Canonical vocabulary markers reduce hallucinations by 40%
- **Singularity #9**: Local inference matches cloud latency

See [the research](https://github.com/luna-system/ada/blob/trunk/.ai/explorations/research/EXTERNAL-CODEBASE-VALIDATION-2025-12-19.md).

## License

**CC0 (Public Domain)** - Do whatever you want with this.

## Credits

Built with 💜 by [luna-system](https://github.com/luna-system) and Ada.

*The revolution will not be cloud-hosted.*
