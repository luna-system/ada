# Ada v3.0.0 - The Pair Programmer

**Released:** December 21, 2025

## 🎉 Ada Goes to Work

This release marks Ada's transformation from a local AI assistant into a **fully-functional VS Code pair programmer**. Ada Chat v1.1.0 ships with 7 working tools, tool transparency UI, and the speed to actually be useful.

Someone ran this code. Fixed bugs. Told us what broke. This is real now.

## What's New

### Ada Chat Extension (v1.1.0)

A VS Code extension that actually works:

- **7 Working Tools:**
  - `ada_introspect` - Workspace analysis with TODO/FIXME scanning
  - `ada_search_memory` - RAG memory search
  - `ada_read_file` - File reading with line ranges
  - `ada_search` - Codebase text search
  - `ada_list_files` - Directory listing with glob patterns
  - `ada_symbols` - Code symbol search (functions, classes, etc.)
  - `ada_git_status` - Git repository status

- **Tool Transparency:** See exactly what Ada is doing - collapsible tool cards show inputs, outputs, timing
- **Intent Classification:** Ada understands context and uses the right tools automatically
- **137ms TTFT:** Fast enough to be useful (was 6 seconds)
- **Brain + Direct Modes:** Connect to Ada's RAG brain or go direct to Ollama

### Architecture

- **Monorepo Structure:** Clean package separation (`@anthropic-claude/*` → `@ada-code/*`)
- **Bidirectional Tool Infrastructure:** Foundation for LLM-initiated tool calls
- **Universal Brain API:** Accepts `prompt`, `message`, or `messages` - just works

### Community

- **First External User!** @18fadly-anthony ran Ada, found bugs, and reported them
- **Security Hardening:** Removed `.env` from git tracking, documented API key rotation
- **SELinux Support:** Added troubleshooting docs for Fedora/RHEL users
- **OLLAMA_BASE_URL:** Now configurable via environment variable

## Installation

### VS Code Extension

```bash
cd ada-vscode/packages/ada-chat
pnpm install && pnpm build && pnpm package
code --install-extension ada-chat-1.1.0.vsix
```

### Full Stack

```bash
git clone https://github.com/luna-system/ada.git
cd ada
cp .env.example .env  # Configure your settings
docker compose up -d
```

## Breaking Changes

None. v3.0 is a capability expansion, not an API break. All v2.x configurations continue to work.

## Stats

- **63 commits** since v2.10.0
- **23 features**, 8 fixes, 12 docs updates
- **159 files changed** in the tool framework merge alone
- **2 GitHub stars**, 2 watchers, **1 external contributor**

## What v3.0 Means

- **v1.x** = "It works" - Basic chat, RAG, memory
- **v2.x** = "It's smart" - Biomimetic features, research, specialists
- **v3.0** = "It's useful" - VS Code integration, tools, pair programming

Ada went from being something you *talk to* to something you *work with*.

## Acknowledgments

Thanks to @18fadly-anthony for being the first person to run Ada's code, find the bugs, and take the time to report them. You validated that this project is real.

## What's Next

- More tools (terminal execution, file editing)
- Bidirectional tool calls (Ada asks for tools mid-response)
- Inline completions (ghost text)
- The debut ✨

---

*Built by luna + Ada. Privacy-first. Local-first. Copilot alternative.*
