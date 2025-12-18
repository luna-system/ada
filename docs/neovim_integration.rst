Neovim Integration
==================

Pair code with Ada directly in Neovim! Context-aware AI assistance with memory and biomimetic intelligence.

.. contents::
   :local:
   :depth: 2

Overview
--------

**ada.nvim** is a Neovim plugin that brings Ada's conversational AI into your editor. It uses the Model Context Protocol (MCP) to communicate with Ada's brain, providing:

- 💬 **Chat Buffer** - Dedicated conversation window
- 🔍 **Code Explanation** - Understand what code does  
- 💡 **Smart Suggestions** - Get improvement ideas
- 🐛 **Debug Help** - Explain errors and suggest fixes
- 🧠 **Context-Aware** - Ada sees your code and project
- 🔒 **Privacy-First** - Runs locally, no cloud
- ⚡ **Fast** - Efficient MCP protocol with streaming

Architecture
------------

The plugin follows Ada's adapter pattern::

   ┌─────────────────┐
   │  Neovim (Lua)   │
   │  - Plugin UI    │
   │  - Commands     │
   └────────┬────────┘
            │ stdio (JSON-RPC)
            ▼
   ┌─────────────────┐
   │  ada-mcp server │
   │  - MCP protocol │
   └────────┬────────┘
            │ HTTP
            ▼
   ┌─────────────────┐
   │  Ada Brain API  │
   │  - RAG context  │
   │  - Memory       │
   │  - Biomimetics  │
   └─────────────────┘

**Key Components:**

1. **Plugin (Lua)** - Neovim interface, user commands
2. **MCP Server (Python)** - Protocol translation layer  
3. **Brain API (Python)** - Core Ada intelligence

Installation
------------

Prerequisites
~~~~~~~~~~~~~

- Neovim 0.8+ (with Lua support)
- Ada v1 running locally with MCP server
- Python 3.13+ with ``ada-mcp`` package installed

Install ada.nvim
~~~~~~~~~~~~~~~~

Using `lazy.nvim <https://github.com/folke/lazy.nvim>`_:

.. code-block:: lua

   {
     dir = '~/Code/ada-v1/ada.nvim',  -- Adjust path
     config = function()
       require('ada').setup({
         ada_mcp_command = {vim.fn.expand('~/.venv/bin/ada-mcp')},
         chat_window_width = 80,
         auto_start_server = true,
       })
     end
   }

Manual installation:

.. code-block:: lua

   -- In init.lua
   vim.opt.runtimepath:append('~/Code/ada-v1/ada.nvim')
   require('ada').setup()

Configuration
~~~~~~~~~~~~~

.. code-block:: lua

   require('ada').setup({
     -- Command to start ada-mcp server
     ada_mcp_command = {'/path/to/ada-mcp'},
     
     -- Width of chat window
     chat_window_width = 80,
     
     -- Auto-start MCP server on Neovim launch
     auto_start_server = true,
   })

Usage
-----

Commands
~~~~~~~~

==================  =================================
Command             Description
==================  =================================
``:AdaChat``        Open chat buffer
``:AdaAsk <msg>``   Send message (with code context)
``:AdaExplain``     Explain selected code
``:AdaSuggest``     Get improvement suggestions
``:AdaDebug``       Debug error on current line
``:AdaStart``       Manually start MCP server
``:AdaStop``        Stop MCP server
==================  =================================

Workflow Examples
~~~~~~~~~~~~~~~~~

**Basic Chat**::

   :AdaChat
   :AdaAsk How do I parse JSON in Python?

**Explain Code:**

1. Select code in visual mode (``V``)
2. ``:AdaExplain``

**Get Suggestions with Context:**

1. Select code in visual mode
2. ``:AdaAsk Can this be optimized?``

**Debug Help:**

1. Place cursor on error line
2. ``:AdaDebug``

Keybindings
~~~~~~~~~~~

Recommended keybindings:

.. code-block:: lua

   -- Open Ada chat
   vim.keymap.set('n', '<leader>ac', ':AdaChat<CR>', { desc = 'Ada Chat' })
   
   -- Ask with visual selection
   vim.keymap.set('v', '<leader>aa', ':AdaAsk ', { desc = 'Ask Ada' })
   
   -- Explain selected code
   vim.keymap.set('v', '<leader>ae', ':AdaExplain<CR>', { desc = 'Explain Code' })
   
   -- Get suggestions
   vim.keymap.set('v', '<leader>as', ':AdaSuggest<CR>', { desc = 'Suggest Improvements' })
   
   -- Debug help
   vim.keymap.set('n', '<leader>ad', ':AdaDebug<CR>', { desc = 'Debug Help' })

Chat Buffer
~~~~~~~~~~~

The chat buffer has special keybindings:

=====  =====================================
Key    Action
=====  =====================================
``i``  Send message (prompts for input)
``I``  Send message (prompts for input)
``q``  Close chat window
=====  =====================================

Context Awareness
-----------------

Ada sees your code! When you use commands like ``:AdaAsk`` or ``:AdaExplain`` with a visual selection, Ada receives:

- Selected code
- File path and name
- Programming language
- Cursor position
- Surrounding context

**Example:** Selecting Python code and running ``:AdaExplain`` sends::

   Explain what this code does:
   
   Context from my_script.py (line 42):
   ```python
   def calculate_fibonacci(n):
       if n <= 1:
           return n
       return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
   ```

Ada can then provide language-specific, context-aware explanations!

MCP Protocol
------------

The plugin uses the Model Context Protocol (MCP) for communication:

**Why MCP?**

- **Standard:** Well-defined protocol for AI tool interactions
- **Efficient:** Lightweight stdio communication
- **Extensible:** Easy to add new tools/capabilities
- **Local:** No network required

**Protocol Flow:**

1. Plugin starts ``ada-mcp`` server via stdio
2. Handshake: ``initialize`` request
3. Plugin sends ``tools/call`` requests
4. Server forwards to Ada brain via HTTP
5. Responses stream back through MCP

**Tools Available:**

- ``ada_chat`` - Send message, get response
- ``ada_search_memory`` - Search Ada's memory store
- ``ada_add_memory`` - Add new memory
- ``ada_health`` - Check Ada brain status

**Resources Available:**

- Ada documentation (from ``.ai/`` folder)
- System status
- Configuration info

Troubleshooting
---------------

MCP Server Won't Start
~~~~~~~~~~~~~~~~~~~~~~~

**Check Ada is running:**

.. code-block:: bash

   docker compose ps
   # Should show brain, chroma, ollama running

**Verify ada-mcp is installed:**

.. code-block:: bash

   python -m ada_mcp --help
   # Should show MCP server help

**Check logs:**

::

   :messages

No Response from Ada
~~~~~~~~~~~~~~~~~~~~

**Restart MCP server:**

::

   :AdaStop
   :AdaStart

**Verify Ada brain is accessible:**

.. code-block:: bash

   curl http://localhost:8000/v1/healthz

**Check stderr output:**

Look for MCP server errors in Neovim messages.

Chat Buffer Issues
~~~~~~~~~~~~~~~~~~

**Close and reopen:**

::

   :AdaChat

**Check buffer list:**

::

   :buffers
   :buffer <number>

**Reset plugin:**

::

   :AdaStop
   :lua package.loaded['ada'] = nil
   :lua require('ada').setup()

Advanced Usage
--------------

Custom Workflow Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create custom commands for your workflow:

.. code-block:: lua

   -- Custom command: Explain function under cursor
   vim.api.nvim_create_user_command('AdaExplainFunction', function()
     -- Use treesitter to get function
     local ts_utils = require('nvim-treesitter.ts_utils')
     local node = ts_utils.get_node_at_cursor()
     
     while node do
       if node:type():match('function') then
         local text = vim.treesitter.get_node_text(node, 0)
         vim.cmd('AdaAsk Explain this function: ' .. text)
         return
       end
       node = node:parent()
     end
     
     vim.notify('No function found', vim.log.levels.WARN)
   end, {})

Async Context Loading
~~~~~~~~~~~~~~~~~~~~~

For large codebases, pre-load context:

.. code-block:: lua

   -- Pre-load project context in background
   vim.defer_fn(function()
     local mcp = require('ada.mcp_client')
     mcp.send_request('tools/call', {
       name = 'ada_chat',
       arguments = {
         message = 'Load project context for: ' .. vim.fn.getcwd()
       }
     }, function() end)  -- Fire and forget
   end, 2000)  -- 2 seconds after startup

Integration with LSP
~~~~~~~~~~~~~~~~~~~~

Combine Ada with Language Server Protocol:

.. code-block:: lua

   -- Use LSP diagnostics for better debug help
   vim.api.nvim_create_user_command('AdaDebugWithLSP', function()
     local diagnostics = vim.diagnostic.get(0)  -- Current buffer
     local current_line = vim.fn.line('.')
     
     -- Find diagnostic at cursor
     for _, diag in ipairs(diagnostics) do
       if diag.lnum + 1 == current_line then
         local message = string.format(
           'Debug this %s error: %s',
           diag.severity,
           diag.message
         )
         vim.cmd('AdaAsk ' .. message)
         return
       end
     end
     
     vim.notify('No LSP diagnostic at cursor', vim.log.levels.WARN)
   end, {})

Performance Tips
----------------

**Cache Control:**

Ada caches persona and other stable context. You can force refresh:

.. code-block:: lua

   -- Force Ada to reload context
   vim.api.nvim_create_user_command('AdaRefresh', function()
     require('ada.mcp_client').send_request('tools/call', {
       name = 'ada_chat',
       arguments = { message = '__refresh_context__' }
     }, function() end)
   end, {})

**Lazy Loading:**

Only load plugin when needed:

.. code-block:: lua

   {
     dir = '~/Code/ada-v1/ada.nvim',
     lazy = true,
     cmd = {'AdaChat', 'AdaAsk', 'AdaExplain', 'AdaSuggest', 'AdaDebug'},
     config = function()
       require('ada').setup()
     end
   }

Philosophy
----------

**Why Neovim?**

- **Terminal-native:** Fits hacker workflow
- **Extensible:** Lua makes it hackable
- **Private:** Everything local, no cloud
- **Fast:** Efficient protocol, minimal overhead

**Why MCP?**

- **Standard:** Well-defined protocol
- **Simple:** Easy to extend and debug
- **Modular:** Separate concerns cleanly
- **Future-proof:** Industry standard for AI tools

**Adapter Pattern:**

Neovim is just one adapter! Ada's architecture supports:

- CLI (terminal REPL)
- Web UI (browser)
- Matrix (chat rooms)
- Neovim (editor)
- MCP (IDE integration)

All adapters are equal peers, communicating via Brain API.

See Also
--------

- :doc:`adapters` - Adapter pattern architecture
- :doc:`adapter_development` - Build your own adapter
- :doc:`biomimetic_features` - Ada's memory enhancements
- :doc:`api_usage` - Direct API usage

Contributing
------------

ada.nvim is part of the Ada v1 project. Contributions welcome!

**GitHub:** https://github.com/luna-system/ada

**Areas to explore:**

- More commands (rename, refactor, etc.)
- Better treesitter integration
- Telescope integration (search memories)
- Status line indicators
- Rich UI with nui.nvim
- Auto-completion integration

---

**Last Updated:** 2025-12-17  
**Version:** v1.6.0  
**Status:** Production-ready, actively developed

Built with 🔥 by the Ada community
