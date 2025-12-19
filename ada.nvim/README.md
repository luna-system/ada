# Ada.nvim 🔥

Pair coding with Ada directly in Neovim! Context-aware AI assistant with memory and biomimetic intelligence.

## Features

- 💬 **Chat Buffer** - Dedicated conversation window with Ada
- 🔍 **Code Explanation** - Understand what code does
- 💡 **Smart Suggestions** - Get improvement ideas and alternatives
- 🐛 **Debug Help** - Explain errors and suggest fixes
- 🧠 **Context-Aware** - Ada sees your code and understands your project
- 🔒 **Privacy-First** - Runs locally, no cloud required
- ⚡ **Fast** - Efficient MCP protocol with streaming responses

## Prerequisites

- Neovim 0.8+ (with Lua support)
- Ada v1 running locally with MCP server
- Python 3.13+ with `ada-mcp` package installed

## Installation

### Using [lazy.nvim](https://github.com/folke/lazy.nvim)

```lua
{
  dir = '~/Code/ada-v1/ada.nvim',  -- Adjust path to your ada.nvim location
  config = function()
    require('ada').setup({
      -- Optional configuration
      ada_mcp_command = {'python', '-m', 'ada_mcp'},
      chat_window_width = 80,
      auto_start_server = true,
    })
  end
}
```

### Manual

Add to your `init.lua`:

```lua
vim.opt.runtimepath:append('~/Code/ada-v1/ada.nvim')
require('ada').setup()
```

## Configuration

```lua
require('ada').setup({
  -- Command to start ada-mcp server
  ada_mcp_command = {'python', '-m', 'ada_mcp'},
  
  -- Width of chat window
  chat_window_width = 80,
  
  -- Auto-start MCP server on Neovim launch
  auto_start_server = true,
  
  -- Code completion settings
  completion_keymap = '<C-x><C-a>',  -- Keybinding for manual completion
  auto_complete = false,              -- Auto-trigger on typing (experimental)
  auto_complete_delay = 1000,         -- Delay before auto-trigger (ms)
})
```

## Usage

### Commands

| Command | Description |
|---------|-------------|
| `:AdaChat` | Open chat buffer |
| `:AdaAsk <message>` | Send message to Ada (with code context if visual selection) |
| `:AdaExplain` | Explain selected code |
| `:AdaSuggest` | Get code improvement suggestions |
| `:AdaDebug` | Debug error on current line |
| `:AdaComplete` | **NEW!** Trigger code completion at cursor |
| `:AdaStart` | Manually start MCP server |
| `:AdaStop` | Stop MCP server |

### Keybindings

| Mode | Keybinding | Action | Description |
|------|------------|--------|-------------|
| Insert | `<C-x><C-a>` | Code Completion | **NEW!** Complete code at cursor (like Copilot!) |

### Workflow Examples

**Code completion (NEW!):**
```python
def hello():
    message = <C-x><C-a>  # Press Ctrl-X Ctrl-A to complete!
```

Ada suggests: `f"Hello, world!"`

**Basic chat:**
```vim
:AdaChat
:AdaAsk How do I parse JSON in Python?
```

**Explain code:**
1. Select code in visual mode (`V`)
2. `:AdaExplain`

**Get suggestions with context:**
1. Select code in visual mode
2. `:AdaAsk Can this be optimized?`

**Debug help:**
1. Place cursor on error line
2. `:AdaDebug`

### Recommended Keybindings

Add to your `init.lua`:

```lua
-- Open Ada chat
vim.keymap.set('n', '<leader>ac', ':AdaChat<CR>', { desc = 'Ada Chat' })

-- Ask with visual selection
vim.keymap.set('v', '<leader>aa', ':AdaAsk ', { desc = 'Ask Ada' })

-- Explain selected code
vim.keymap.set('v', '<leader>ae', ':AdaExplain<CR>', { desc = 'Explain Code' })

-- Get suggestions
vim.keymap.set('v', '<leader>as', ':AdaSuggest<CR>', { desc = 'Suggest Improvements' })

-- Debug help
vim.keymap.set('n', '<leader>ad', ':AdaDebug<CR>', { desc = 'Debug Help' })

-- Code completion (already set up by default as <C-x><C-a>, but you can override)
-- vim.keymap.set('i', '<C-Space>', function() require('ada.completion').trigger_completion() end, { desc = 'Ada Complete' })
```

### Pro Tips for Code Completion

- **Context matters:** Ada sees code before AND after the cursor for better completions
- **Language aware:** Automatically detects filetype (Python, Lua, JavaScript, etc.)
- **Fast & local:** Runs on your machine, typically <500ms response
- **Terse prompts:** Optimized for speed, no RAG overhead on completions
- **Iterate if needed:** If completion isn't perfect, undo (`u`) and try again

**Example workflow:**
```python
class Calculator:
    def add(self, a, b):
        <C-x><C-a>  # Completes: return a + b
```

## How It Works

```
┌─────────────────┐
│  Neovim (Lua)   │
│  - Plugin UI    │
│  - Commands     │
└────────┬────────┘
         │ stdio (JSON-RPC)
         ▼
┌─────────────────┐
│  ada-mcp server │
│  - MCP protocol │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  Ada Brain API  │
│  - RAG context  │
│  - Memory       │
│  - Biomimetics  │
└─────────────────┘
```

Ada.nvim communicates with the `ada-mcp` server via stdio (Model Context Protocol), which then talks to Ada's brain API. This architecture ensures:

- Fast, efficient communication
- Context-aware responses (Ada sees your code)
- Privacy (everything runs locally)
- Memory across sessions (Ada learns your patterns)

## Troubleshooting

**MCP server won't start:**
- Check Ada is running: `docker compose ps`
- Verify ada-mcp is installed: `python -m ada_mcp --help`
- Check logs: `:messages`

**No response from Ada:**
- Check MCP server status: `:AdaStop` then `:AdaStart`
- Verify Ada brain is accessible: `curl http://localhost:8000/v1/healthz`

**Chat buffer issues:**
- Close and reopen: `:AdaChat`
- Check buffer with `:buffers` and `:buffer <number>`

## Contributing

This plugin is part of the [Ada v1 project](https://github.com/luna-system/ada). Contributions welcome!

## Philosophy

Ada.nvim embodies the Ada philosophy:
- **Hackable** - Pure Lua, easy to extend
- **Local-first** - Privacy-preserving, no cloud
- **Adaptive** - Learns your patterns through memory
- **Biomimetic** - Processing modes adapt to task type

## License

MIT License - See main Ada project for details

---

Built with 🔥 by the Ada community
