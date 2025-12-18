# Ada-Neovim Integration - Design Document

> **Goal:** Pair coding with Ada directly in Neovim using MCP protocol  
> **Vibe:** 🔥 Peak hacker workflow, LSP-style integration, context-aware assistance  
> **Status:** Design → Implementation phase

## Architecture Overview

```
┌─────────────────┐
│  Neovim (Lua)   │
│  - Plugin UI    │
│  - Keybindings  │
│  - Buffer mgmt  │
└────────┬────────┘
         │ stdio (JSON-RPC)
         ▼
┌─────────────────┐
│  ada-mcp server │
│  - MCP protocol │
│  - Tools        │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  Ada Brain API  │
│  - RAG context  │
│  - Biomimetics  │
│  - Specialists  │
└─────────────────┘
```

## Core Features (MVP)

### 1. Chat Buffer 💬
**What:** Dedicated buffer for conversation with Ada  
**Commands:**
- `:AdaChat` - Open chat buffer
- `:AdaAsk <message>` - Send message, show response in chat buffer
- Visual mode: Select code → `:AdaAsk` sends with context

**Implementation:**
- Create floating window or split
- Format as markdown
- Stream responses (update buffer as chunks arrive)
- Keep conversation history in buffer

### 2. Code Explanation 🔍
**What:** Explain selected code or function under cursor  
**Commands:**
- `:AdaExplain` - Explain selection or current function
- Hover: Show brief explanation in floating window

**Context sent:**
- Selected code or function body
- File type / language
- Surrounding code (scope)
- File path for project context

### 3. Code Suggestions 💡
**What:** Get improvement suggestions or alternative approaches  
**Commands:**
- `:AdaSuggest` - Get suggestions for selection
- `:AdaRefactor` - Suggest refactoring options

**Uses:** Creative processing mode from biomimetics!

### 4. Debug Help 🐛
**What:** Debug errors, explain stack traces  
**Commands:**
- `:AdaDebug` - Analyze error under cursor
- `:AdaFix` - Suggest fixes

**Context sent:**
- Error message
- Stack trace
- Relevant code
- File context

### 5. Context-Aware Completions 🎯
**What:** Inline suggestions based on project context (future: LSP integration)  
**For now:** Manual trigger, later: automatic

## Technical Design

### Plugin Structure
```
ada.nvim/
├── lua/
│   └── ada/
│       ├── init.lua          # Main entry point
│       ├── mcp_client.lua    # MCP protocol client (stdio)
│       ├── chat.lua          # Chat buffer management
│       ├── context.lua       # Extract editor context
│       ├── ui.lua            # Floating windows, formatting
│       ├── commands.lua      # Vim commands
│       └── config.lua        # User configuration
├── plugin/
│   └── ada.vim               # Vim plugin registration
└── doc/
    └── ada.txt               # Help documentation
```

### MCP Client (Lua)

**Challenge:** Neovim needs to talk to ada-mcp server (stdio + JSON-RPC)

**Solution:** Use Neovim's `vim.fn.jobstart()` for process management

```lua
-- lua/ada/mcp_client.lua
local M = {}

M.server_job = nil
M.request_id = 0
M.pending_requests = {}

function M.start_server()
  -- Start ada-mcp server as subprocess
  M.server_job = vim.fn.jobstart(
    {'python', '-m', 'ada_mcp'},
    {
      on_stdout = M.on_message,
      on_stderr = M.on_error,
      on_exit = M.on_exit,
      rpc = false,
      stdout_buffered = false,
    }
  )
end

function M.send_request(method, params, callback)
  M.request_id = M.request_id + 1
  local request = {
    jsonrpc = "2.0",
    id = M.request_id,
    method = method,
    params = params
  }
  
  M.pending_requests[M.request_id] = callback
  
  -- Send JSON-RPC request via stdin
  vim.fn.chansend(M.server_job, vim.fn.json_encode(request) .. "\n")
end

function M.on_message(job_id, data, event)
  for _, line in ipairs(data) do
    if line ~= "" then
      local response = vim.fn.json_decode(line)
      
      if response.id and M.pending_requests[response.id] then
        M.pending_requests[response.id](response.result)
        M.pending_requests[response.id] = nil
      end
    end
  end
end

return M
```

### Context Extraction

```lua
-- lua/ada/context.lua
local M = {}

function M.get_selection()
  local start_pos = vim.fn.getpos("'<")
  local end_pos = vim.fn.getpos("'>")
  local lines = vim.fn.getline(start_pos[2], end_pos[2])
  return table.concat(lines, "\n")
end

function M.get_current_function()
  -- Use treesitter to find function under cursor
  local ts = vim.treesitter
  local node = ts.get_node()
  
  while node do
    local node_type = node:type()
    if node_type:match("function") or node_type:match("method") then
      return ts.get_node_text(node, 0)
    end
    node = node:parent()
  end
  
  return nil
end

function M.get_file_context()
  return {
    filepath = vim.fn.expand('%:p'),
    filetype = vim.bo.filetype,
    language = vim.bo.filetype,
    line_count = vim.fn.line('$'),
    cursor_line = vim.fn.line('.'),
  }
end

function M.build_code_context(include_code)
  local ctx = M.get_file_context()
  
  if include_code then
    ctx.code = vim.fn.getline(1, '$')
  end
  
  return ctx
end

return M
```

### Chat Buffer

```lua
-- lua/ada/chat.lua
local M = {}

M.chat_bufnr = nil
M.chat_winid = nil

function M.open()
  -- Create or reuse chat buffer
  if not M.chat_bufnr or not vim.api.nvim_buf_is_valid(M.chat_bufnr) then
    M.chat_bufnr = vim.api.nvim_create_buf(false, true)
    vim.api.nvim_buf_set_option(M.chat_bufnr, 'buftype', 'nofile')
    vim.api.nvim_buf_set_option(M.chat_bufnr, 'filetype', 'markdown')
    vim.api.nvim_buf_set_name(M.chat_bufnr, 'Ada Chat')
  end
  
  -- Create split window
  vim.cmd('vsplit')
  M.chat_winid = vim.api.nvim_get_current_win()
  vim.api.nvim_win_set_buf(M.chat_winid, M.chat_bufnr)
  vim.api.nvim_win_set_width(M.chat_winid, 80)
end

function M.append_message(role, content)
  local lines = {
    '',
    '## ' .. role,
    '',
    content,
    '',
    '---',
  }
  
  vim.api.nvim_buf_set_lines(
    M.chat_bufnr,
    -1,
    -1,
    false,
    lines
  )
  
  -- Scroll to bottom
  if M.chat_winid and vim.api.nvim_win_is_valid(M.chat_winid) then
    local line_count = vim.api.nvim_buf_line_count(M.chat_bufnr)
    vim.api.nvim_win_set_cursor(M.chat_winid, {line_count, 0})
  end
end

function M.append_streaming_chunk(chunk)
  -- Append to last line (streaming response)
  local line_count = vim.api.nvim_buf_line_count(M.chat_bufnr)
  local last_line = vim.api.nvim_buf_get_lines(M.chat_bufnr, line_count - 1, line_count, false)[1]
  
  vim.api.nvim_buf_set_lines(
    M.chat_bufnr,
    line_count - 1,
    line_count,
    false,
    {last_line .. chunk}
  )
end

return M
```

### Commands

```lua
-- lua/ada/commands.lua
local mcp = require('ada.mcp_client')
local chat = require('ada.chat')
local context = require('ada.context')

local M = {}

function M.setup()
  vim.api.nvim_create_user_command('AdaChat', function()
    chat.open()
  end, {})
  
  vim.api.nvim_create_user_command('AdaAsk', function(opts)
    M.ask(opts.args)
  end, { nargs = '*', range = true })
  
  vim.api.nvim_create_user_command('AdaExplain', function()
    M.explain()
  end, { range = true })
  
  vim.api.nvim_create_user_command('AdaSuggest', function()
    M.suggest()
  end, { range = true })
  
  vim.api.nvim_create_user_command('AdaDebug', function()
    M.debug()
  end, {})
end

function M.ask(message)
  chat.open()
  
  -- Get code context if in visual mode
  local code = nil
  if vim.fn.mode() == 'v' or vim.fn.mode() == 'V' then
    code = context.get_selection()
  end
  
  -- Build full message
  local full_message = message
  if code then
    local file_ctx = context.get_file_context()
    full_message = string.format(
      "%s\n\nContext (from %s):\n```%s\n%s\n```",
      message,
      file_ctx.filepath,
      file_ctx.language,
      code
    )
  end
  
  -- Show user message
  chat.append_message('You', full_message)
  
  -- Send to Ada
  mcp.send_request('tools/call', {
    name = 'ada_chat',
    arguments = {
      message = full_message
    }
  }, function(result)
    chat.append_message('Ada', result.content[1].text)
  end)
end

function M.explain()
  local code = context.get_selection() or context.get_current_function()
  
  if not code then
    vim.notify("No code to explain. Select code or place cursor in function.", vim.log.levels.WARN)
    return
  end
  
  M.ask("Explain this code:\n\n```\n" .. code .. "\n```")
end

function M.suggest()
  local code = context.get_selection()
  
  if not code then
    vim.notify("Select code to get suggestions for.", vim.log.levels.WARN)
    return
  end
  
  M.ask("Suggest improvements or alternative approaches for this code:\n\n```\n" .. code .. "\n```")
end

function M.debug()
  -- Get current line (likely an error)
  local current_line = vim.fn.getline('.')
  local file_ctx = context.get_file_context()
  
  M.ask(string.format(
    "Help debug this error at line %d:\n\n%s",
    file_ctx.cursor_line,
    current_line
  ))
end

return M
```

### Main Entry Point

```lua
-- lua/ada/init.lua
local M = {}

M.config = {
  ada_mcp_command = {'python', '-m', 'ada_mcp'},
  chat_window_width = 80,
  auto_start_server = true,
}

function M.setup(user_config)
  M.config = vim.tbl_deep_extend('force', M.config, user_config or {})
  
  local mcp = require('ada.mcp_client')
  local commands = require('ada.commands')
  
  -- Start MCP server
  if M.config.auto_start_server then
    mcp.start_server()
  end
  
  -- Register commands
  commands.setup()
  
  vim.notify("Ada: Ready for pair coding! 🔥", vim.log.levels.INFO)
end

return M
```

## User Configuration

```lua
-- In user's init.lua or init.vim
require('ada').setup({
  ada_mcp_command = {'python', '-m', 'ada_mcp'},
  chat_window_width = 80,
  auto_start_server = true,
})

-- Optional keybindings
vim.keymap.set('n', '<leader>ac', ':AdaChat<CR>', { desc = 'Open Ada chat' })
vim.keymap.set('v', '<leader>ae', ':AdaExplain<CR>', { desc = 'Explain code' })
vim.keymap.set('v', '<leader>as', ':AdaSuggest<CR>', { desc = 'Get suggestions' })
vim.keymap.set('n', '<leader>ad', ':AdaDebug<CR>', { desc = 'Debug help' })
vim.keymap.set('v', '<leader>aa', ':AdaAsk ', { desc = 'Ask Ada with context' })
```

## Implementation Phases

### Phase 1: Basic Chat (MVP) ✅ This session
- [ ] MCP client (stdio communication)
- [ ] Chat buffer management
- [ ] Basic commands (AdaChat, AdaAsk)
- [ ] Context extraction (selection, file info)
- [ ] Test with simple queries

### Phase 2: Code Intelligence (Next session)
- [ ] AdaExplain with treesitter
- [ ] AdaSuggest with processing modes
- [ ] AdaDebug with error context
- [ ] Floating windows for quick help
- [ ] Better markdown rendering

### Phase 3: Advanced Features (Future)
- [ ] Inline completions (LSP-style)
- [ ] Project-wide context (via specialists)
- [ ] Code actions (quick fixes)
- [ ] Diff view for suggested changes
- [ ] Memory: Learn user's codebase patterns

### Phase 4: Polish (Future)
- [ ] Configuration UI
- [ ] Status line integration
- [ ] Telescope integration (search memories)
- [ ] Rich UI with nui.nvim
- [ ] Documentation + help files

## Testing Strategy

**Manual testing:**
1. Start Neovim with plugin loaded
2. `:AdaChat` - Opens chat window
3. `:AdaAsk "Hello Ada!"` - Gets response
4. Select code → `:AdaExplain` - Explains selection
5. Check MCP server logs for communication

**Edge cases:**
- MCP server crash/restart
- Large code selections
- Network issues (Ada brain down)
- Multiple buffers/windows

## Installation (for users)

### Using lazy.nvim:
```lua
{
  'luna-system/ada.nvim',
  dependencies = {
    'nvim-treesitter/nvim-treesitter', -- For code parsing
  },
  config = function()
    require('ada').setup()
  end
}
```

### Manual:
```bash
git clone https://github.com/luna-system/ada.nvim ~/.config/nvim/pack/plugins/start/ada.nvim
```

## Why This Is Awesome 🔥

1. **Context-aware:** Ada sees your code, understands your project
2. **Biomimetics:** Processing modes adapt to task (debug vs design)
3. **Memory:** Learns your codebase patterns over time
4. **Local-first:** Privacy-preserving, no cloud needed
5. **Hackable:** Pure Lua, easy to extend
6. **Modular:** Works with treesitter, LSP, telescope
7. **Fast:** MCP protocol is efficient, streaming responses

## Comparison to Copilot

| Feature | GitHub Copilot | Ada in Neovim |
|---------|----------------|---------------|
| Completions | ✅ Inline | 🔄 (Future) |
| Chat | ✅ Panel | ✅ Buffer |
| Context | File-level | Project + Memory |
| Privacy | Cloud | Local |
| Cost | $10/mo | Free |
| Customization | Limited | Fully hackable |
| Memory | None | Learns patterns |
| Biomimetics | ❌ | ✅ Adaptive modes |

## Next Steps

1. **Create plugin directory:** `ada.nvim/`
2. **Implement MVP:** Chat + basic commands
3. **Test with real Ada instance**
4. **Iterate:** Add features based on usage
5. **Document:** Help files, README, demos
6. **Share:** GitHub repo, demos, r/neovim post

---

**Status:** Design complete, ready to implement!  
**Vibe:** 🔥🎸 Peak hacker workflow incoming  
**Estimated time:** 2-3 hours for MVP, 1 day for polish  

Let's build this! 🚀
