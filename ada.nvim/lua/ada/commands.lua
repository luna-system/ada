-- Command implementations
local M = {}

local mcp = require('ada.mcp_client')
local chat = require('ada.chat')
local context = require('ada.context')

function M.setup(config)
  M.config = config
  
  -- AdaStart - Start MCP server
  vim.api.nvim_create_user_command('AdaStart', function()
    mcp.start_server(config)
  end, {})
  
  -- AdaStop - Stop MCP server
  vim.api.nvim_create_user_command('AdaStop', function()
    mcp.stop_server()
  end, {})
  
  -- AdaChat - Open chat buffer
  vim.api.nvim_create_user_command('AdaChat', function()
    chat.open(config)
  end, {})
  
  -- AdaAsk - Send message (with optional visual selection)
  vim.api.nvim_create_user_command('AdaAsk', function(opts)
    M.ask(opts.args, opts.range > 0)
  end, { nargs = '*', range = true })
  
  -- AdaExplain - Explain code
  vim.api.nvim_create_user_command('AdaExplain', function(opts)
    M.explain(opts.range > 0)
  end, { range = true })
  
  -- AdaSuggest - Get suggestions
  vim.api.nvim_create_user_command('AdaSuggest', function(opts)
    M.suggest(opts.range > 0)
  end, { range = true })
  
  -- AdaDebug - Debug help
  vim.api.nvim_create_user_command('AdaDebug', function()
    M.debug()
  end, {})
end

function M.ask(message, has_range)
  if not message or message == "" then
    vim.notify("Usage: :AdaAsk <your message>", vim.log.levels.WARN)
    return
  end
  
  chat.open(M.config)
  
  -- Get code context if range provided (visual selection)
  local code = nil
  local file_ctx = nil
  
  if has_range then
    code = context.get_visual_selection()
    file_ctx = context.get_file_context()
  end
  
  -- Build full message with code context
  local full_message = context.build_code_message(message, code, file_ctx)
  
  -- Show user message in chat
  chat.append_message('You', full_message)
  
  -- Send to Ada
  vim.notify("Asking Ada...", vim.log.levels.INFO)
  
  mcp.send_request('tools/call', {
    name = 'ada_chat',
    arguments = {
      message = full_message
    }
  }, function(result)
    if result and result.content and result.content[1] then
      local response = result.content[1].text
      chat.append_message('Ada', response)
      vim.notify("Ada responded!", vim.log.levels.INFO)
    else
      chat.append_message('Ada', '(No response received)')
      vim.notify("Empty response from Ada", vim.log.levels.WARN)
    end
  end)
end

function M.explain(has_range)
  if not has_range then
    vim.notify("Select code first, then :AdaExplain", vim.log.levels.WARN)
    return
  end
  
  local code = context.get_visual_selection()
  
  if not code or code == "" then
    vim.notify("No code selected", vim.log.levels.WARN)
    return
  end
  
  M.ask("Explain what this code does:", true)
end

function M.suggest(has_range)
  if not has_range then
    vim.notify("Select code first, then :AdaSuggest", vim.log.levels.WARN)
    return
  end
  
  local code = context.get_visual_selection()
  
  if not code or code == "" then
    vim.notify("No code selected", vim.log.levels.WARN)
    return
  end
  
  M.ask("Suggest improvements or alternative approaches for this code:", true)
end

function M.debug()
  local current_line = context.get_current_line()
  local file_ctx = context.get_file_context()
  local surrounding = context.get_surrounding_lines(5)
  
  chat.open(M.config)
  
  local message = string.format(
    "Help debug this error at line %d:\n\n%s\n\nSurrounding code:\n```%s\n%s\n```",
    file_ctx.cursor_line,
    current_line,
    file_ctx.language,
    surrounding
  )
  
  chat.append_message('You', message)
  
  mcp.send_request('tools/call', {
    name = 'ada_chat',
    arguments = {
      message = message
    }
  }, function(result)
    if result and result.content and result.content[1] then
      chat.append_message('Ada', result.content[1].text)
    end
  end)
end

return M
