-- Ada MCP Server configuration for Neovim
-- Requires: https://github.com/anthropics/mcp.nvim (or similar MCP client)

-- Example configuration for lazy.nvim
return {
  {
    "anthropics/mcp.nvim",
    config = function()
      require("mcp").setup({
        servers = {
          ada = {
            command = "ada-mcp",  -- Assumes ada-mcp is in PATH
            -- Or use absolute path:
            -- command = "/path/to/ada-v1/ada-mcp/.venv/bin/ada-mcp",
            env = {
              ADA_BASE_URL = "http://localhost:8000",
            },
          },
        },
      })
    end,
  },
}

-- Basic usage examples:
-- :McpListTools          -- List available Ada tools
-- :McpCallTool ada_chat {"message": "hello"}
-- :McpCallTool ada_search_memory {"query": "project notes"}

-- You can also bind to keymaps:
-- vim.keymap.set("n", "<leader>ac", function()
--   require("mcp").call_tool("ada", "ada_chat", {
--     message = vim.fn.input("Ask Ada: ")
--   })
-- end, { desc = "Chat with Ada" })
