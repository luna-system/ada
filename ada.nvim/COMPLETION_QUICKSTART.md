# Ada Code Completion - Quick Start Guide

Get GitHub Copilot-style completions running **locally** in under 5 minutes!

## Prerequisites ✅

- Ada v1 running (`docker compose up -d brain chroma ollama`)
- Neovim 0.8+
- `ada.nvim` plugin installed

## Installation

### 1. Make sure ada.nvim is loaded

In your Neovim config:

```lua
-- lazy.nvim
{
  dir = '~/Code/ada-v1/ada.nvim',
  config = function()
    require('ada').setup({
      completion_keymap = '<C-x><C-a>',  -- Or your preferred binding
    })
  end
}

-- Or vanilla Neovim
vim.opt.runtimepath:append('~/Code/ada-v1/ada.nvim')
require('ada').setup()
```

### 2. Restart Neovim

```bash
nvim
```

You should see: `Ada.nvim loaded! 🔥 Use :AdaChat to start, <C-x><C-a> to complete`

## Usage 🚀

### Basic Completion

1. Open a Python/Lua/JavaScript file
2. Start typing:
   ```python
   def greet(name):
       message = 
   ```
3. Press `<C-x><C-a>` (Ctrl-X, then Ctrl-A)
4. Ada completes: `f"Hello, {name}!"`

### It Just Works™

**Function returns:**
```python
def add(a, b):
    <C-x><C-a>
```
→ Completes: `return a + b`

**Imports:**
```python
from pathlib import <C-x><C-a>
```
→ Completes: `Path`

**Method bodies:**
```python
class Calculator:
    def multiply(self, x, y):
        <C-x><C-a>
```
→ Completes: `return x * y`

**Comments:**
```python
# Calculate the factorial of n
def factorial(n):
    <C-x><C-a>
```
→ Ada reads the comment and implements it!

## Configuration Options

### Change Keybinding

```lua
require('ada').setup({
  completion_keymap = '<C-Space>',  -- Use Ctrl-Space instead
})
```

### Enable Auto-Complete (Experimental)

```lua
require('ada').setup({
  auto_complete = true,           -- Trigger automatically on typing
  auto_complete_delay = 1000,     -- Wait 1 second after typing stops
})
```

**Note:** Auto-complete is experimental and may be distracting. Manual trigger is recommended for now.

## How It Works Under The Hood 🔧

```
Your Code → Neovim → MCP Server → Ada Brain → LLM → Completion
   (Lua)     (stdio)    (HTTP)      (RAG)    (DeepSeek)
```

**Magic ingredients:**
- **Context-aware:** Ada sees code before AND after cursor
- **Terse prompts:** No RAG, pure speed (<50 tokens)
- **Smart extraction:** Handles markdown/plain LLM responses
- **Local-first:** Everything runs on your machine

## Performance Expectations

| Metric | Expected |
|--------|----------|
| First completion | 2-5s (model loading) |
| Subsequent | <500ms |
| Token usage | 30-80 per completion |
| Success rate | ~80% useful completions |

## Troubleshooting 🔧

### "Ada completion error: Connection refused"

**Fix:** Start Ada brain first:
```bash
docker compose up -d brain chroma ollama
curl http://localhost:8000/v1/healthz  # Should return "healthy"
```

### "No completion available"

**Causes:**
- Not enough context (code_before too short)
- Ada brain still loading model (wait ~30s)
- MCP server not connected

**Fix:** Check MCP status:
```vim
:AdaStop
:AdaStart
:messages  " Check for errors
```

### Completions are slow (>2s)

**Normal** on first request (model loading).  
**If persistent:**
- Check system load: `docker stats`
- Try smaller model (edit `compose.yaml`, use `deepseek-r1:7b`)
- Increase `max_tokens` limit (currently 150)

### Completions are wrong/irrelevant

**This is AI** - it won't be perfect every time!

**Tips for better completions:**
- Add comments explaining what you want
- Include type hints (Python) for context
- Make sure there's code after cursor (helps Ada understand scope)
- Try multiple times (undo with `u`, retry with `<C-x><C-a>`)

## Comparison to GitHub Copilot

| Feature | Ada (Local) | GitHub Copilot |
|---------|-------------|----------------|
| **Privacy** | ✅ 100% local | ❌ Cloud-based |
| **Speed** | ⚡ <500ms (warm) | ⚡ ~200ms |
| **Cost** | 🆓 Free | 💰 $10-19/month |
| **Context** | ✅ Code before+after | ✅ Entire file |
| **Quality** | 🎯 ~80% useful | 🎯 ~85% useful |
| **Hackable** | ✅ Full control | ❌ Black box |
| **Multi-file** | 🚧 Coming soon | ✅ Yes |

**TL;DR:** Ada is like Copilot but runs on YOUR hardware, respects YOUR privacy, and YOU can hack it!

## What's Next?

Phase 1 (current):
- ✅ Basic inline completion
- ✅ Manual trigger keybinding
- ✅ Context-aware prompts

Phase 2 (coming):
- 🚧 Multi-line completions
- 🚧 Project-wide context (RAG)
- 🚧 Virtual text preview (like Copilot ghost text)
- 🚧 Tab-to-accept workflow

Phase 3 (future):
- 🔮 Refactoring suggestions
- 🔮 Test generation
- 🔮 Documentation generation
- 🔮 Intelligent editing (Fill-in-the-Middle)

## Getting Help

- **Docs:** `ada.nvim/README.md`
- **Issues:** https://github.com/luna-system/ada/issues
- **Testing:** Run `./test_completion_integration.py`
- **Logs:** `:messages` in Neovim

---

**Status:** Phase 1 MVP complete - basic completions working! 🎉

Built with 🔥 by the Ada community
