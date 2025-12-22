# Phase Handoff: Monorepo Structure Complete (December 21, 2025)

**Date:** December 21, 2025  
**Branch:** `feature/tool-framework-architecture` (15 commits)  
**Status:** ✅ MONOREPO STRUCTURE READY - CODE MIGRATION NEXT

## What Just Happened

luna made the call: **"MONOREPO NOW! later? we split."**

✅ **Established pnpm workspaces structure for VSCode extensions**
- Separates chat from completions (independent development paths)
- Shares clients + types via `@ada-code/shared` package
- Supports future splitting into separate repos without rearchitecting
- Uses pnpm workspaces (simple, clean, scalable)

## The Monorepo Architecture

```
ada-vscode/
├── pnpm-workspace.yaml              # Workspace definition
├── package.json                     # Root workspace config (no "main")
├── MONOREPO.md                      # Architecture guide (NEW - READ THIS!)
│
├── packages/
│   ├── shared/                      # ✨ Shared utilities & types
│   │   ├── src/
│   │   │   ├── clients/             # HTTP clients
│   │   │   │   ├── adaBrainClient.ts
│   │   │   │   ├── mcpClient.ts
│   │   │   │   └── ollamaClient.ts
│   │   │   ├── types/
│   │   │   │   ├── messageTypes.ts
│   │   │   │   └── index.ts
│   │   │   └── utils/
│   │   │       └── index.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── ada-chat/                    # 💬 Chat extension
│   │   ├── src/
│   │   │   ├── extension.ts         # Main entry point (stub)
│   │   │   └── chatViewProvider.ts  # Webview provider (stub)
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   └── ada-completions/             # ⚡ Code completion extension
│       ├── src/
│       │   ├── extension.ts         # Main entry point (stub)
│       │   ├── completionProvider.ts
│       │   └── modelWarmer.ts
│       ├── package.json
│       └── tsconfig.json
│
└── [APPROACH.md, DEVELOPMENT.md, etc remain at root]
```

## Why This Works (For Now + Later)

**NOW (Monorepo):**
- ✅ All code in one repo = easy for team collaboration
- ✅ Shared code in `@ada-code/shared` = DRY principle
- ✅ `pnpm install` = all packages ready to go
- ✅ Single `pnpm build` command

**LATER (Splitting):**
- ✅ `packages/ada-chat/` → can move to `github.com/luna-system/ada-chat`
- ✅ `packages/ada-completions/` → can move to `github.com/luna-system/ada-completions`
- ✅ `@ada-code/shared` → published to npm registry
- ✅ Each extension: independent CI/CD, marketplace listing, version management
- ✅ **Zero rearchitecting needed** - structure already supports this

## What's Ready

✅ **Monorepo structure created**
- 22 files changed (21 new, 1 modified)
- Workspace configuration in place
- Package.json files for all 3 packages
- TypeScript config for all packages
- Stub files with TODO comments

✅ **Scaffold files in place:**
- `ada-vscode/packages/shared/src/clients/` - Stubs for AdaBrain, MCP, Ollama clients
- `ada-vscode/packages/shared/src/types/` - Message types, tool types
- `ada-vscode/packages/ada-chat/src/` - ChatViewProvider stub
- `ada-vscode/packages/ada-completions/src/` - CompletionProvider, ModelWarmer stubs

✅ **Documentation:**
- `ada-vscode/MONOREPO.md` - Complete architecture guide
- Handoff protocol maintained in `.ai/handoffs/`

## What Needs to Happen Next (Phase 5: Code Migration)

### Priority 1: Move Actual Code Into Packages

```
Root src/ → packages/

ada-vscode/src/chatViewProvider.ts 
  → packages/ada-chat/src/chatViewProvider.ts

ada-vscode/src/completionProvider.ts 
  → packages/ada-completions/src/completionProvider.ts

ada-vscode/src/adaBrainClient.ts 
  → packages/shared/src/clients/adaBrainClient.ts

ada-vscode/src/mcpClient.ts 
  → packages/shared/src/clients/mcpClient.ts

ada-vscode/src/ollamaClient.ts 
  → packages/shared/src/clients/ollamaClient.ts
```

### Priority 2: Update Imports

**Before:**
```typescript
import { AdaBrainClient } from '../adaBrainClient';
import { ChatViewProvider } from './chatViewProvider';
```

**After:**
```typescript
import { AdaBrainClient } from '@ada-code/shared/clients';
import { ChatViewProvider } from './chatViewProvider';
```

### Priority 3: Wire Up Extension Entry Points

**ada-chat/src/extension.ts:**
- Import ChatViewProvider
- Register with `context.subscriptions`
- Initialize AdaBrainClient
- Subscribe to webview messages

**ada-completions/src/extension.ts:**
- Import CompletionProvider
- Register inline completions
- Import OllamaClient
- Warm model on startup

### Priority 4: Test the Monorepo

```bash
cd ada-vscode

# Install all packages
pnpm install

# Build all packages
pnpm build

# Test all packages
pnpm test

# Watch mode
pnpm watch
```

## Integration with Tool Framework

**Already Done (from Phase 3):**
- ✅ Python backend: TwoPhaseRouter (classifies queries)
- ✅ Python backend: ToolResult envelope + metadata embedding
- ✅ Python backend: MetadataParser (extracts 📂 Files, ⚡ Time markers)
- ✅ Tests: 21/21 passing in backend

**Next (Phase 6: Router Integration):**
- Import TwoPhaseRouter into chatViewProvider.ts
- Classify queries BEFORE making tool calls
- Route to appropriate handler (TOOL, REASONING, or CHAT)
- Render metadata in webview
- Route Phase 2 responses back through LLM

## Future Splitting Strategy

When ready to split (no rush!):

**Step 1: Create separate repos**
```bash
# Create new repos on GitHub:
# - github.com/luna-system/ada-chat
# - github.com/luna-system/ada-completions
# - github.com/luna-system/ada-shared (for npm package)
```

**Step 2: Move packages**
```bash
# Move packages/ada-chat → new repo root
# Move packages/ada-completions → new repo root
# Publish @ada-code/shared to npm registry
```

**Step 3: Update imports**
```typescript
// Instead of:
import { AdaBrainClient } from '@ada-code/shared';

// Use:
import { AdaBrainClient } from '@ada-code/shared'; // from npm!
```

**Step 4: Independent CI/CD**
- Each repo has own GitHub Actions workflows
- Each repo publishes independently to marketplace
- Each repo manages own version numbers

**Key insight:** This is just moving files around. Zero code changes needed because the structure is already set up for it.

## Entry Points for Next Model

1. **Understand the context:**
   - Read this handoff (5 min)
   - Read `ada-vscode/MONOREPO.md` (10 min)
   - Look at package structure (5 min)

2. **Understand the backend:**
   - Read `.ai/handoffs/phase-handoff-3-4.md` (backend context)
   - Run Python demos to see tool framework in action

3. **Start Phase 5:**
   - Move `src/chatViewProvider.ts` to `packages/ada-chat/src/`
   - Move `src/completionProvider.ts` to `packages/ada-completions/src/`
   - Move client files to `packages/shared/src/clients/`
   - Update imports to use `@ada-code/shared`
   - Run `pnpm install && pnpm build`
   - Verify no errors

## Current Status Summary

**What's Done:**
- ✅ Monorepo structure (pnpm workspaces)
- ✅ Package scaffolding (all 3 packages with configs)
- ✅ Type stubs (clients, types, utils stubbed out)
- ✅ Documentation (MONOREPO.md + handoff)
- ✅ Git committed (15 commits on feature branch)

**What's In Progress:**
- 🔄 Code migration from root src/ to packages/
- 🔄 Import updates to use @ada-code/shared
- 🔄 Extension entry point wiring

**What's Next:**
- Phase 6: Router integration (after code migration)
- Phase 7: Tool transparency UI enhancement
- Phase 8: Testing + marketplace publishing

## Key Files

- **[ada-vscode/MONOREPO.md](../ada-vscode/MONOREPO.md)** - Full architecture guide (READ THIS!)
- **ada-vscode/pnpm-workspace.yaml** - Workspace config
- **ada-vscode/package.json** - Root workspace (updated)
- **ada-vscode/packages/*/package.json** - Package definitions
- **.ai/handoffs/phase-handoff-3-4.md** - Backend context (tool framework)

## Questions/Decisions for Next Phase

1. Should we publish `@ada-code/shared` to npm now or wait until actually splitting?
   - **Recommendation:** Wait until split, use workspace reference for now

2. Keep configuration at root level or migrate to per-extension?
   - **Recommendation:** Root level for now, migrate during split

3. Should each package have its own GitHub Actions workflow?
   - **Recommendation:** When splitting, yes. For now, single workflow for all

## Timeline to Big Second Debut

```
Current: Monorepo structure complete ✅
Phase 5: Code migration (1-2 days)
Phase 6: Router integration + transparency UI (2-3 days)
Phase 7: Testing + bug fixes (1-2 days)
Phase 8: Publishing + marketplace listings (1 day)

→ READY FOR BIG SECOND DEBUT 🚀
```

---

**Branch:** `feature/tool-framework-architecture` (15 commits)  
**Tests:** 21/21 passing (backend)  
**Status:** MONOREPO READY - CODE MIGRATION NEXT

**Session ended with:** luna excited to ship, monorepo structure complete, ready for Phase 5 code migration.
