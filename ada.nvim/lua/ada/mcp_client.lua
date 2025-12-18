-- MCP Client - Handles communication with ada-mcp server via stdio
local M = {}

M.server_job = nil
M.request_id = 0
M.pending_requests = {}
M.response_buffer = ""
M.initialized = false

function M.start_server(config)
  if M.server_job then
    vim.notify("Ada MCP server already running", vim.log.levels.INFO)
    return
  end

  local cmd = config.ada_mcp_command or {'python', '-m', 'ada_mcp'}
  
  vim.notify("Starting Ada MCP server...", vim.log.levels.INFO)
  
  M.server_job = vim.fn.jobstart(cmd, {
    on_stdout = M.on_message,
    on_stderr = M.on_error,
    on_exit = M.on_exit,
    stdout_buffered = false,
    stderr_buffered = true,
  })
  
  if M.server_job <= 0 then
    vim.notify("Failed to start Ada MCP server", vim.log.levels.ERROR)
    M.server_job = nil
    return false
  end
  
  vim.notify("Ada MCP server started (job " .. M.server_job .. ")", vim.log.levels.INFO)
  
  -- Initialize MCP session (REQUIRED before any tool calls!)
  vim.defer_fn(function()
    -- Force capabilities to be encoded as object, not array
    local init_params = {
      protocolVersion = "2024-11-05",
      capabilities = vim.empty_dict(),  -- Explicitly empty object, not array
      clientInfo = {
        name = "ada.nvim",
        version = "0.1.0"
      }
    }
    M.send_request('initialize', init_params, function(result)
      -- Send initialized notification (required by protocol)
      M.send_notification('notifications/initialized', {})
      M.initialized = true
    end)
  end, 500)  -- Wait 500ms for server to be ready
  
  return true
end

function M.stop_server()
  if M.server_job then
    vim.fn.jobstop(M.server_job)
    M.server_job = nil
    M.pending_requests = {}
    M.initialized = false
    vim.notify("Ada MCP server stopped", vim.log.levels.INFO)
  end
end

function M.send_request(method, params, callback)
  if not M.server_job then
    vim.notify("Ada MCP server not running. Start with :AdaStart", vim.log.levels.ERROR)
    return
  end
  
  -- For tool calls, wait for initialization
  if method ~= 'initialize' and not M.initialized then
    vim.notify("Waiting for MCP initialization...", vim.log.levels.WARN)
    vim.defer_fn(function()
      M.send_request(method, params, callback)
    end, 1000)
    return
  end
  
  M.request_id = M.request_id + 1
  local request = {
    jsonrpc = "2.0",
    id = M.request_id,
    method = method,
    params = params
  }
  
  M.pending_requests[M.request_id] = callback
  
  local encoded = vim.fn.json_encode(request) .. "\n"
  vim.fn.chansend(M.server_job, encoded)
end

function M.send_notification(method, params)
  if not M.server_job then
    return
  end
  
  local notification = {
    jsonrpc = "2.0",
    method = method,
    params = params
  }
  
  local encoded = vim.fn.json_encode(notification) .. "\n"
  vim.fn.chansend(M.server_job, encoded)
end

function M.on_message(job_id, data, event)
  for _, line in ipairs(data) do
    if line ~= "" then
      -- Buffer incomplete JSON
      M.response_buffer = M.response_buffer .. line
      
      -- Try to decode
      local ok, response = pcall(vim.fn.json_decode, M.response_buffer)
      
      if ok and response then
        M.response_buffer = "" -- Clear buffer on success
        
        if response.id and M.pending_requests[response.id] then
          local callback = M.pending_requests[response.id]
          M.pending_requests[response.id] = nil
          
          if response.error then
            vim.notify("Ada error: " .. vim.inspect(response.error), vim.log.levels.ERROR)
          else
            -- Call callback with result
            vim.schedule(function()
              callback(response.result)
            end)
          end
        end
      end
    end
  end
end

function M.on_error(job_id, data, event)
  for _, line in ipairs(data) do
    if line ~= "" then
      vim.notify("Ada MCP stderr: " .. line, vim.log.levels.WARN)
    end
  end
end

function M.on_exit(job_id, exit_code, event)
  M.server_job = nil
  M.pending_requests = {}
  
  if exit_code ~= 0 then
    vim.notify("Ada MCP server exited with code " .. exit_code, vim.log.levels.ERROR)
  else
    vim.notify("Ada MCP server stopped", vim.log.levels.INFO)
  end
end

return M
