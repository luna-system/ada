-- Ada.nvim - Pair coding with Ada in Neovim
local M = {}

M.config = {
  ada_mcp_command = {vim.fn.expand('~/.venv/bin/ada-mcp')},  -- Default venv path (user should customize)
  chat_window_width = 80,
  auto_start_server = true,
  -- Code completion settings
  completion_keymap = '<C-x><C-a>',  -- Manual completion keybinding
  auto_complete = false,              -- Auto-trigger on typing (experimental)
  auto_complete_delay = 1000,         -- Delay before auto-trigger (ms)
}

function M.setup(user_config)
  -- Merge user config with defaults
  M.config = vim.tbl_deep_extend('force', M.config, user_config or {})
  
  -- Load modules
  local mcp = require('ada.mcp_client')
  local commands = require('ada.commands')
  local completion = require('ada.completion')
  
  -- Register commands
  commands.setup(M.config)
  
  -- Setup completion
  completion.setup(M.config)
  
  -- Auto-start MCP server if configured
  if M.config.auto_start_server then
    vim.defer_fn(function()
      mcp.start_server(M.config)
    end, 100)
  end
  
  vim.notify("Ada.nvim loaded! 🔥 Use :AdaChat to start, <C-x><C-a> to complete", vim.log.levels.INFO)
end

return M
