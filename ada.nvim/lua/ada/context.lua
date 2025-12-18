-- Context extraction from editor state
local M = {}

function M.get_visual_selection()
  -- Get visual selection range
  local start_pos = vim.fn.getpos("'<")
  local end_pos = vim.fn.getpos("'>")
  
  if start_pos[2] == 0 or end_pos[2] == 0 then
    return nil
  end
  
  local lines = vim.fn.getline(start_pos[2], end_pos[2])
  
  if #lines == 0 then
    return nil
  end
  
  -- Handle single line selection
  if #lines == 1 then
    local line = lines[1]
    local start_col = start_pos[3]
    local end_col = end_pos[3]
    lines[1] = line:sub(start_col, end_col)
  else
    -- Handle multi-line: trim first and last
    lines[1] = lines[1]:sub(start_pos[3])
    lines[#lines] = lines[#lines]:sub(1, end_pos[3])
  end
  
  return table.concat(lines, "\n")
end

function M.get_current_line()
  return vim.fn.getline('.')
end

function M.get_surrounding_lines(count)
  local current_line = vim.fn.line('.')
  local start_line = math.max(1, current_line - count)
  local end_line = math.min(vim.fn.line('$'), current_line + count)
  
  local lines = vim.fn.getline(start_line, end_line)
  return table.concat(lines, "\n")
end

function M.get_file_context()
  local filepath = vim.fn.expand('%:p')
  local filename = vim.fn.expand('%:t')
  local filetype = vim.bo.filetype
  local line_count = vim.fn.line('$')
  local cursor_line = vim.fn.line('.')
  local cursor_col = vim.fn.col('.')
  
  return {
    filepath = filepath,
    filename = filename,
    filetype = filetype,
    language = filetype,
    line_count = line_count,
    cursor_line = cursor_line,
    cursor_col = cursor_col,
  }
end

function M.build_code_message(user_message, code, file_ctx)
  if not code then
    return user_message
  end
  
  local parts = {user_message, ""}
  
  if file_ctx then
    table.insert(parts, string.format("Context from %s (line %d):", 
      file_ctx.filename or "file", 
      file_ctx.cursor_line or 0))
  else
    table.insert(parts, "Code context:")
  end
  
  local lang = (file_ctx and file_ctx.language) or ""
  table.insert(parts, "```" .. lang)
  table.insert(parts, code)
  table.insert(parts, "```")
  
  return table.concat(parts, "\n")
end

return M
