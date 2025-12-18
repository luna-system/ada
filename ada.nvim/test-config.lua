-- Test configuration for ada.nvim
-- Put this in ~/.config/nvim/lua/test-ada.lua or use directly in init.lua

-- Add ada.nvim to runtime path
local ada_path = vim.fn.expand('~/Code/ada-v1/ada.nvim')
vim.opt.runtimepath:prepend(ada_path)

-- Setup Ada
local venv_path = vim.fn.expand('~/Code/ada-v1/.venv/bin/ada-mcp')
require('ada').setup({
  ada_mcp_command = {venv_path},  -- Use venv ada-mcp
  chat_window_width = 80,
  auto_start_server = true,
})

-- Recommended keybindings
vim.keymap.set('n', '<leader>ac', ':AdaChat<CR>', { desc = 'Ada Chat', silent = true })
vim.keymap.set('v', '<leader>aa', ':AdaAsk ', { desc = 'Ask Ada' })
vim.keymap.set('v', '<leader>ae', ':AdaExplain<CR>', { desc = 'Explain Code', silent = true })
vim.keymap.set('v', '<leader>as', ':AdaSuggest<CR>', { desc = 'Suggest Improvements', silent = true })
vim.keymap.set('n', '<leader>ad', ':AdaDebug<CR>', { desc = 'Debug Help', silent = true })

print("Ada.nvim test config loaded! 🔥")
print("Try: :AdaChat")
