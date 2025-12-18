-- Chat buffer management
local M = {}

M.chat_bufnr = nil
M.chat_winid = nil

function M.open(config)
  -- Create or reuse chat buffer
  if not M.chat_bufnr or not vim.api.nvim_buf_is_valid(M.chat_bufnr) then
    M.chat_bufnr = vim.api.nvim_create_buf(false, true)
    vim.api.nvim_buf_set_option(M.chat_bufnr, 'buftype', 'nofile')
    vim.api.nvim_buf_set_option(M.chat_bufnr, 'bufhidden', 'hide')
    vim.api.nvim_buf_set_option(M.chat_bufnr, 'swapfile', false)
    vim.api.nvim_buf_set_option(M.chat_bufnr, 'filetype', 'markdown')
    vim.api.nvim_buf_set_name(M.chat_bufnr, 'Ada Chat')
    
    -- Initial welcome message
    vim.api.nvim_buf_set_lines(M.chat_bufnr, 0, -1, false, {
      '# Ada Chat 🔥',
      '',
      'Press `i` or `I` in this buffer to send a message!',
      'Or use `:AdaAsk <message>` from command mode.',
      '',
      '**Keybindings in this buffer:**',
      '- `i` or `I` - Send message',
      '- `q` - Close chat window',
      '',
      '**Commands:**',
      '- `:AdaAsk <message>` - Send message',
      '- `:AdaExplain` - Explain selected code',
      '- `:AdaSuggest` - Get code suggestions',
      '- `:AdaDebug` - Debug help',
      '',
      '---',
      ''
    })
    
    -- Set up buffer-local keybindings
    M.setup_keybindings()
  end
  
  -- Create or focus window
  if not M.chat_winid or not vim.api.nvim_win_is_valid(M.chat_winid) then
    vim.cmd('vsplit')
    M.chat_winid = vim.api.nvim_get_current_win()
    vim.api.nvim_win_set_buf(M.chat_winid, M.chat_bufnr)
    
    local width = config.chat_window_width or 80
    vim.api.nvim_win_set_width(M.chat_winid, width)
  else
    vim.api.nvim_set_current_win(M.chat_winid)
  end
end

function M.append_message(role, content)
  if not M.chat_bufnr or not vim.api.nvim_buf_is_valid(M.chat_bufnr) then
    return
  end
  
  local lines = {
    '',
    '## ' .. role,
    '',
  }
  
  -- Split content by newlines
  for line in content:gmatch("[^\n]+") do
    table.insert(lines, line)
  end
  
  table.insert(lines, '')
  table.insert(lines, '---')
  
  vim.api.nvim_buf_set_lines(
    M.chat_bufnr,
    -1,
    -1,
    false,
    lines
  )
  
  -- Scroll to bottom
  M.scroll_to_bottom()
end

function M.scroll_to_bottom()
  if M.chat_winid and vim.api.nvim_win_is_valid(M.chat_winid) then
    local line_count = vim.api.nvim_buf_line_count(M.chat_bufnr)
    vim.api.nvim_win_set_cursor(M.chat_winid, {line_count, 0})
  end
end

function M.close()
  if M.chat_winid and vim.api.nvim_win_is_valid(M.chat_winid) then
    vim.api.nvim_win_close(M.chat_winid, false)
    M.chat_winid = nil
  end
end

function M.setup_keybindings()
  if not M.chat_bufnr then
    return
  end
  
  -- Press 'i' or 'I' to send a message
  vim.api.nvim_buf_set_keymap(M.chat_bufnr, 'n', 'i', '', {
    noremap = true,
    silent = true,
    callback = function()
      M.prompt_for_message()
    end,
    desc = 'Send message to Ada'
  })
  
  vim.api.nvim_buf_set_keymap(M.chat_bufnr, 'n', 'I', '', {
    noremap = true,
    silent = true,
    callback = function()
      M.prompt_for_message()
    end,
    desc = 'Send message to Ada'
  })
  
  -- Press 'q' to close chat window
  vim.api.nvim_buf_set_keymap(M.chat_bufnr, 'n', 'q', '', {
    noremap = true,
    silent = true,
    callback = function()
      M.close()
    end,
    desc = 'Close chat window'
  })
end

function M.prompt_for_message()
  vim.ui.input({
    prompt = 'Ask Ada: ',
    default = '',
  }, function(input)
    if input and input ~= '' then
      -- Call AdaAsk command with the input
      vim.cmd('AdaAsk ' .. input)
    end
  end)
end

return M
