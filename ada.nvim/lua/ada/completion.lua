-- Ada.nvim - Code completion module
local M = {}

local mcp = require('ada.mcp_client')

-- Cache for debouncing
local completion_timer = nil
local last_completion = nil

--- Get code context around cursor
--- @return table {code_before, code_after, language}
local function get_cursor_context()
  local bufnr = vim.api.nvim_get_current_buf()
  local cursor = vim.api.nvim_win_get_cursor(0)
  local row = cursor[1] - 1  -- 0-indexed
  local col = cursor[2]
  
  -- Get all lines
  local lines = vim.api.nvim_buf_get_lines(bufnr, 0, -1, false)
  local total_lines = #lines
  
  -- Build code_before (everything up to cursor)
  local before_lines = {}
  for i = 1, row do
    table.insert(before_lines, lines[i])
  end
  -- Add current line up to cursor
  if row + 1 <= total_lines then
    local current_line = lines[row + 1]
    table.insert(before_lines, current_line:sub(1, col))
  end
  local code_before = table.concat(before_lines, '\n')
  
  -- Build code_after (everything after cursor)
  local after_lines = {}
  if row + 1 <= total_lines then
    local current_line = lines[row + 1]
    local after_part = current_line:sub(col + 1)
    if #after_part > 0 then
      table.insert(after_lines, after_part)
    end
  end
  for i = row + 2, total_lines do
    table.insert(after_lines, lines[i])
  end
  local code_after = table.concat(after_lines, '\n')
  
  -- Get filetype
  local filetype = vim.bo[bufnr].filetype
  -- Map vim filetypes to common language names
  local language_map = {
    python = 'python',
    lua = 'lua',
    javascript = 'javascript',
    typescript = 'typescript',
    rust = 'rust',
    go = 'go',
    c = 'c',
    cpp = 'cpp',
    java = 'java',
    ruby = 'ruby',
    sh = 'bash',
    bash = 'bash',
    zsh = 'bash',
  }
  local language = language_map[filetype] or filetype
  
  return {
    code_before = code_before,
    code_after = code_after,
    language = language,
  }
end

--- Request code completion from Ada
--- @param callback function(completion: string|nil)
function M.complete(callback)
  local context = get_cursor_context()
  
  -- Don't complete if code_before is empty or very short
  if #context.code_before < 2 then
    callback(nil)
    return
  end
  
  -- Call MCP tool
  mcp.call_tool('ada_complete_code', {
    code_before = context.code_before,
    code_after = context.code_after,
    language = context.language,
    max_tokens = 150,
  }, function(result, err)
    if err then
      vim.notify('Ada completion error: ' .. err, vim.log.levels.WARN)
      callback(nil)
      return
    end
    
    if result and result.content then
      -- Store for potential reuse
      last_completion = result.content
      callback(result.content)
    else
      callback(nil)
    end
  end)
end

--- Insert completion at cursor
--- @param completion string
local function insert_completion(completion)
  local cursor = vim.api.nvim_win_get_cursor(0)
  local row = cursor[1] - 1
  local col = cursor[2]
  
  -- Split completion into lines
  local lines = vim.split(completion, '\n', {plain = true})
  
  if #lines == 1 then
    -- Single line - insert at cursor
    vim.api.nvim_buf_set_text(0, row, col, row, col, {completion})
    -- Move cursor to end of completion
    vim.api.nvim_win_set_cursor(0, {row + 1, col + #completion})
  else
    -- Multi-line - insert lines
    vim.api.nvim_buf_set_text(0, row, col, row, col, lines)
    -- Move cursor to end of last line
    vim.api.nvim_win_set_cursor(0, {row + #lines, #lines[#lines]})
  end
end

--- Trigger completion manually (keybinding)
function M.trigger_completion()
  vim.notify('🤖 Ada is thinking...', vim.log.levels.INFO)
  
  M.complete(function(completion)
    if completion then
      insert_completion(completion)
      vim.notify('✨ Completion inserted!', vim.log.levels.INFO)
    else
      vim.notify('No completion available', vim.log.levels.WARN)
    end
  end)
end

--- Setup completion with optional auto-trigger
--- @param config table Configuration options
function M.setup(config)
  config = config or {}
  
  -- Register manual completion command
  vim.api.nvim_create_user_command('AdaComplete', function()
    M.trigger_completion()
  end, {
    desc = 'Trigger Ada code completion'
  })
  
  -- Set up keybinding (default: <C-x><C-a>)
  local keymap = config.completion_keymap or '<C-x><C-a>'
  vim.keymap.set('i', keymap, function()
    M.trigger_completion()
  end, {
    desc = 'Ada code completion',
    noremap = true,
    silent = true,
  })
  
  -- Optional: Auto-trigger on idle (if configured)
  if config.auto_complete then
    vim.api.nvim_create_autocmd({'TextChangedI', 'TextChangedP'}, {
      callback = function()
        -- Debounce: Only trigger after idle period
        if completion_timer then
          vim.fn.timer_stop(completion_timer)
        end
        
        completion_timer = vim.fn.timer_start(config.auto_complete_delay or 1000, function()
          -- Only auto-complete in code buffers
          local ft = vim.bo.filetype
          if ft ~= '' and ft ~= 'text' and ft ~= 'markdown' then
            M.complete(function(completion)
              if completion then
                -- Show as virtual text suggestion
                -- (User can accept with Tab or ignore)
                -- TODO: Implement virtual text preview
              end
            end)
          end
        end)
      end,
    })
  end
end

return M
